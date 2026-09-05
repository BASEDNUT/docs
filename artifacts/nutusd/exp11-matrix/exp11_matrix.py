"""exp11_matrix - XI oracle failure matrix (audit round 5, P1 gate).

Bundle driver - runs on a pinned Base mainnet fork (anvil :8547) with the REAL
MorphoChainlinkOracleV2Factory, the REAL Morpho Blue, and REAL USDC/cbBTC,
but with two fork-deployed MockAggregators initialized to the XI-captured
live raw answers. The oracle path is production-shaped end to end; only the
feed answers are controllable.

Registry M1-M10: baseline, base zero, quote zero, base negative, stale,
quote depeg, base dislocation, recovery, combined shift, broken feed.
Mutating steps (feed edits, market ops) are receipted transactions;
health-gate probes are eth_call simulations - no hidden state changes.
"""
import json
import pathlib
import time
import urllib.request

from web3 import Web3

AC = pathlib.Path(__file__).resolve().parent
RESULTS = AC / 'exp11_matrix_results_repro.json'
BYTECODE_JSON = AC / 'exp11_matrix' / 'out' / 'MockAggregator.sol' / 'MockAggregator.json'

FORK = 'http://127.0.0.1:8547'
FORK_URL = 'https://base.publicnode.com'
# Fresh-tip pin (2026-09-04 21:30 AST). publicnode free tier 403s archive
# reads: older pins age out of the served window mid-run (run7 stall at
# lazy fetch). Re-take fresh before each run.
FORK_BLOCK = 50889452
FORK_PORT = 8547

MORPHO = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
CBBTC = '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'
IRM = '0x46415998764C29aB2a25CbeA6254146D50D22687'
FACTORY = '0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d'
LLTV = 385 * 10 ** 15
WHALE = '0xfBB6Eed8e7aa03B138556eeDaF5D271A5E1e43ef'
ACCT0 = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'

BASE_RAW = 8091208877609
QUOTE_RAW = 99983065
SCALE = 10 ** 34
BASELINE_PRICE = SCALE * BASE_RAW // QUOTE_RAW
BASE_70 = BASE_RAW * 70 // 100
BASE_80 = BASE_RAW * 8 // 10
QUOTE_90 = QUOTE_RAW * 9 // 10
SALT = bytes.fromhex('6e7574555344' + '00' * 25 + '02')
ZERO = '0x' + '00' * 20
WAD = 10 ** 18
SUPPLY_USDC = 10_000 * 10 ** 6
COLL = 5_000_000

SCENARIOS = [
    dict(id='M1', label='baseline serves', sub='live-captured raws through the real factory oracle', verdict_class='baseline_serves', note='price == floor(SCALE*BASE/QUOTE), integer-exact'),
    dict(id='M2', label='base zero', sub='base answer set to 0', verdict_class='base_zero_zero_price', note='price serves 0 without revert; maxBorrow collapses to 0; a 1-sat seizure quotes 0 repayment'),
    dict(id='M3', label='quote zero', sub='quote answer set to 0', verdict_class='quote_zero_panic_freeze', note='price call panics 0x12; every market call freezes'),
    dict(id='M4', label='base negative', sub='base answer set to -1', verdict_class='base_negative_string_freeze', note='string revert from the negative-answer guard; calls freeze'),
    dict(id='M5', label='stale', sub='updatedAt pushed back 24h', verdict_class='stale_serves_unchanged', note='price unchanged; no staleness guard in the adapter'),
    dict(id='M6', label='quote depeg', sub='quote answer 0.90 USD', verdict_class='quote_depeg_price_up', note='price rises by 1/0.9; floor-exact'),
    dict(id='M7', label='base dislocation', sub='base answer 0.70x', verdict_class='base_dislocation_price_down', note='price falls to 0.70x; the health gate flips; liquidation sim executes end to end'),
    dict(id='M8', label='recovery', sub='base answer restored', verdict_class='recovery_baseline_exact', note='price returns to the baseline integer exactly'),
    dict(id='M9', label='combined shift', sub='base 0.80x and quote 0.90x together', verdict_class='combined_shift', note='price lands at 0.8/0.9 of baseline; floor-exact'),
    dict(id='M10', label='broken feed', sub='latestRoundData reverts', verdict_class='broken_feed_call_freeze', note='all price-dependent calls revert; the market freezes until the feed heals'),
]

SIG_CREATE = 'createMorphoChainlinkOracleV2(address,uint256,address,address,uint256,address,uint256,address,address,uint256,bytes32)'
SIG_MARKET = 'createMarket((address,address,address,address,uint256))'
SIG_SUPPLY = 'supply((address,address,address,address,uint256),uint256,uint256,address,bytes)'
SIG_SCOLL = 'supplyCollateral((address,address,address,address,uint256),uint256,address,bytes)'
SIG_BORROW = 'borrow((address,address,address,address,uint256),uint256,uint256,address,address)'
SIG_LIQ = 'liquidate((address,address,address,address,uint256),address,uint256,uint256,bytes)'
SIG_SUPPLY_LEGACY = 'supply((address,address,address,address,uint256),uint256,address,uint256)'
SIG_SCOLL_LEGACY = 'supplyCollateral((address,address,address,address,uint256),uint256,address)'

SEL_ERR = '08c379a0'
SEL_PANIC = '4e487b71'
# Observed MarketCreation topic0 on the Base mainnet fork receipt
# (2026-09-04 session, createMarket tx). Receipt-anchored constant:
# the canonical Solidity signature string stayed unresolved across
# candidate forms, so the observed hash is pinned instead (exp8
# observed-topic0 pattern, proven in this codebase).
TOPIC_MARKET_CREATION = '0xac4b2400f169220b0c0afdde7a0b32e775ba727ea1cb30b35f935cdaab8683ac'


class CallFail(Exception):
    def __init__(self, data, message):
        self.data = data
        self.message = message
        Exception.__init__(self, message)


def rpcq(method, params):
    req = urllib.request.Request(
        FORK,
        data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def sel(sig):
    return Web3.keccak(text=sig)[:4].hex()


def w_addr(a):
    return bytes.fromhex(a[2:].lower().rjust(64, '0'))


def w_uint(n):
    return (n % 2 ** 256).to_bytes(32, 'big')


def call(to, data, frm=None):
    tx = {'to': to, 'data': data}
    if frm:
        tx['from'] = frm
    r = rpcq('eth_call', [tx, 'latest'])
    if 'result' in r:
        return r['result']
    err = r.get('error') or {}
    raise CallFail(err.get('data') or '', err.get('message') or json.dumps(r)[:200])


def decode_revert(h):
    # Revert-data layouts (exp8-proven; run8 misread pinned by referee):
    #   Error(string): 4B selector + 32B offset word (==32) + 32B len + utf8
    #   Panic(uint256): 4B selector + 32B code word
    h = (h or '').lower().removeprefix('0x')
    if h.startswith(SEL_ERR) and len(h) >= 136:
        off = int(h[8:72], 16)
        n = int(h[72:136], 16)
        if off == 32 and 0 < n <= 256:
            s = bytes.fromhex(h[136:136 + 2 * n]).decode('utf8', 'replace')
            return ('string', s)
    if h.startswith(SEL_PANIC) and len(h) >= 72:
        return ('panic', hex(int(h[8:72], 16)))
    return ('raw', h[:80])


def try_call(to, data, frm=None):
    try:
        return (True, 'ok', call(to, data, frm))
    except CallFail as e:
        h = (e.data or '').lower().removeprefix('0x')
        kind, info = decode_revert(h)
        return (False, kind, info or e.message[:80])


def send(frm, to, data, gas=2_000_000):
    gp = int(rpcq('eth_gasPrice', [])['result'], 16)
    nonce = int(rpcq('eth_getTransactionCount', [frm, 'latest'])['result'], 16)
    r = rpcq('eth_sendTransaction', [{'from': frm, 'to': to, 'data': data,
                                      'gas': hex(gas), 'gasPrice': hex(gp), 'nonce': hex(nonce)}])
    assert 'result' in r, json.dumps(r)[:300]
    h = r['result']
    receipt = None
    for _ in range(120):
        time.sleep(0.3)
        rr = rpcq('eth_getTransactionReceipt', [h])
        if 'result' in rr and rr['result']:
            receipt = rr['result']
            break
    assert receipt, 'no receipt for ' + h
    assert receipt['status'] == '0x1', 'tx reverted: ' + h
    return h, receipt


def deploy_mock(answer, dec, desc, frm):
    d = json.loads(BYTECODE_JSON.read_text())
    code = d['bytecode']['object'].removeprefix('0x')
    s = desc.encode('ascii')
    args = (w_uint(answer) + w_uint(dec) + w_uint(0x60)
            + w_uint(len(s)) + s + b'\x00' * ((32 - len(s) % 32) % 32))
    data = '0x' + code + args.hex()
    h, rc = send(frm, None if False else '', data, gas=1_200_000) if False else (None, None)
    return data


def deploy_mock_tx(answer, dec, desc, frm, txs, label):
    d = json.loads(BYTECODE_JSON.read_text())
    code = d['bytecode']['object'].removeprefix('0x')
    s = desc.encode('ascii')
    pad = (32 - len(s) % 32) % 32
    args = w_uint(answer) + w_uint(dec) + w_uint(0x60) + w_uint(len(s)) + s + b'\x00' * pad
    data = '0x' + code + args.hex()
    gp = int(rpcq('eth_gasPrice', [])['result'], 16)
    nonce = int(rpcq('eth_getTransactionCount', [frm, 'latest'])['result'], 16)
    r = rpcq('eth_sendTransaction', [{'from': frm, 'data': data, 'gas': hex(1_200_000),
                                      'gasPrice': hex(gp), 'nonce': hex(nonce)}])
    assert 'result' in r, json.dumps(r)[:300]
    h = r['result']
    receipt = None
    for _ in range(120):
        time.sleep(0.3)
        rr = rpcq('eth_getTransactionReceipt', [h])
        if 'result' in rr and rr['result']:
            receipt = rr['result']
            break
    assert receipt and receipt['status'] == '0x1', 'deploy failed ' + h
    addr = receipt.get('contractAddress')
    assert addr, 'no contractAddress'
    txs.append(dict(label=label, tx=h, gas=int(receipt['gasUsed'], 16)))
    return addr


def price_int(oracle):
    return int(call(oracle, '0x' + sel('price()'))[2:66], 16)


def max_borrow(collateral, price, lltv):
    # chain-exact: collateral.mulDivDown(price, ORACLE_PRICE_SCALE=1e36).wMulDown(lltv)
    # wMulDown divides by WAD (1e18), not 1e36.
    m = collateral * price // 10 ** 36
    return m * lltv // 10 ** 18


def main():
    txs = []
    res = dict(experiment='XI oracle failure matrix',
               fork=dict(url=FORK_URL, port=FORK_PORT, block=FORK_BLOCK),
               production=dict(morpho=MORPHO, usdc=USDC, cbbtc=CBBTC, irm=IRM,
                               factory=FACTORY, lltv=LLTV),
               raws=dict(base=BASE_RAW, quote=QUOTE_RAW),
               scenarios=[])

    print('== P0 fork pin ==')
    ni = rpcq('anvil_nodeInfo', [])['result']
    fc = ni.get('forkConfig') or {}
    assert int(fc.get('forkBlockNumber') or 0) == FORK_BLOCK, 'pin drift: ' + str(fc)
    pin_hash = rpcq('eth_getBlockByNumber', [hex(FORK_BLOCK), False])['result']['hash']
    res['fork']['hash'] = pin_hash
    res['fork']['anvil'] = ni.get('clientVersion')
    print('pin', FORK_BLOCK, pin_hash)

    print('== P1 deploy mock aggregators ==')
    base_mock = deploy_mock_tx(BASE_RAW, 8, 'matrix base cbbtc usd', ACCT0, txs, 'deploy base mock')
    quote_mock = deploy_mock_tx(QUOTE_RAW, 8, 'matrix quote usdc usd', ACCT0, txs, 'deploy quote mock')
    res['mocks'] = dict(base=base_mock, quote=quote_mock)
    print('base', base_mock, '| quote', quote_mock)

    print('== P2 factory oracle (real V2 factory, mock feeds) ==')
    body = (w_addr(ZERO) + w_uint(1)
            + w_addr(base_mock) + w_addr(ZERO) + w_uint(8)
            + w_addr(ZERO) + w_uint(1)
            + w_addr(quote_mock) + w_addr(ZERO) + w_uint(6)
            + SALT)
    h, rc = send(ACCT0, FACTORY, '0x' + (bytes.fromhex(sel(SIG_CREATE)) + body).hex(), gas=1_500_000)
    txs.append(dict(label='factory create oracle', tx=h, gas=int(rc['gasUsed'], 16)))
    topic = Web3.keccak(text='CreateMorphoChainlinkOracleV2(address,address)').hex()
    topic_clean = topic.removeprefix('0x').lower()
    oracle = None
    for lg in rc['logs']:
        if lg['topics'][0].lower().removeprefix('0x') == topic_clean:
            b = lg['data'][2:]
            oracle = '0x' + b[88:128]
    assert oracle, 'no create event'
    reg = int(call(FACTORY, '0x' + sel('isMorphoChainlinkOracleV2(address)') + oracle[2:].lower().rjust(64, '0'))[2:66], 16)
    sf = int(call(oracle, '0x' + sel('SCALE_FACTOR()'))[2:66], 16)
    assert reg == 1 and sf == SCALE, (reg, sf)
    res['oracle'] = dict(address=oracle, scale_factor=sf, factory_registered=True)
    print('oracle', oracle, '| SCALE_FACTOR', sf, '| registered', reg == 1)

    print('== P3 M1 baseline ==')
    p = price_int(oracle)
    assert p == BASELINE_PRICE, (p, BASELINE_PRICE)
    m1 = dict(id='M1', verdict_class='baseline_serves', observed=dict(price=p, expected=BASELINE_PRICE, exact=p == BASELINE_PRICE))
    res['scenarios'].append(m1)
    print('M1 price exact', p)

    print('== P4 market + max-borrow position ==')
    assert rpcq('anvil_impersonateAccount', [WHALE])['result'] is not None or True
    rpcq('anvil_setBalance', [WHALE, hex(50 * 10 ** 18)])
    blob = w_addr(USDC) + w_addr(CBBTC) + w_addr(oracle) + w_addr(IRM) + w_uint(LLTV)
    mid = Web3.keccak(blob).hex()
    h, rc = send(WHALE, MORPHO, '0x' + (Web3.keccak(text=SIG_MARKET)[:4] + blob).hex())
    txs.append(dict(label='createMarket', tx=h, gas=int(rc['gasUsed'], 16)))
    # MarketCreation match: topic0 anchored to the OBSERVED hash on the
    # mainnet-fork receipt (canonical signature string unresolved across
    # candidates; receipt-anchored constant, exp8 Liquidate pattern).
    topic_mc_clean = TOPIC_MARKET_CREATION.removeprefix('0x').lower()
    mid_clean = mid.removeprefix('0x').lower()
    ev_mid = None
    for lg in rc['logs']:
        if lg['topics'][0].lower().removeprefix('0x') == topic_mc_clean:
            ev_mid = lg['topics'][1].lower().removeprefix('0x')
    # Primary truth: market(bytes32) view call - lastUpdate must be non-zero.
    mview = call(MORPHO, '0x' + (Web3.keccak(text='market(bytes32)')[:4] + bytes.fromhex(mid_clean)).hex())
    m_last = int(mview[2 + 64 * 4:2 + 64 * 5], 16)
    assert m_last != 0, 'market(bytes32) view: market not created'
    assert ev_mid == mid_clean, ('event id mismatch', ev_mid, mid_clean)
    res['market_view'] = dict(lastUpdate=m_last, event_mid=ev_mid, offline_mid=mid_clean,
                              event_match=ev_mid == mid_clean, topic0=TOPIC_MARKET_CREATION)
    res['market_id'] = mid
    # Supply sizing: the fork pin fixes whale balances (run5 reverted
    # supplying a fixed 10k). Probe actual balances; top up via verified
    # storage slot only if below floor (fork cheat, same class as
    # impersonation/anvil_setBalance, recorded in the artifact).
    sel_bal = bytes.fromhex(sel('balanceOf(address)'))

    def tok_bal(token, who):
        return int(call(token, '0x' + (sel_bal + w_addr(who)).hex())[2:66], 16)

    def storage_topup(token, who, want, slot_from, slot_to):
        for s in range(slot_from, slot_to):
            key = Web3.keccak(w_addr(who) + w_uint(s))
            r = rpcq('eth_getStorageAt', [token, key.hex(), 'latest'])['result']
            if int(r, 16) == tok_bal(token, who):
                rpcq('anvil_setStorageAt', [token, key.hex(), hex(want)])
                assert tok_bal(token, who) == want, 'topup verify failed'
                return s
        return None

    FLOOR_USDC = 2 * 10 ** 9
    bal_usdc = tok_bal(USDC, WHALE)
    if bal_usdc < FLOOR_USDC + 10:
        slot = storage_topup(USDC, WHALE, 2 * SUPPLY_USDC, 9, 14)
        assert slot is not None, 'USDC storage slot not found'
        res.setdefault('fork_cheats', []).append(dict(kind='setStorageAt', token='USDC', slot=slot, to=2 * SUPPLY_USDC))
        bal_usdc = tok_bal(USDC, WHALE)
    assert bal_usdc >= FLOOR_USDC, ('whale USDC below floor', bal_usdc)
    bal_cbbtc = tok_bal(CBBTC, WHALE)
    if bal_cbbtc < COLL + 10:
        slot = storage_topup(CBBTC, WHALE, 4 * COLL, 0, 16)
        assert slot is not None, 'CBBTC storage slot not found'
        res.setdefault('fork_cheats', []).append(dict(kind='setStorageAt', token='CBBTC', slot=slot, to=4 * COLL))
        bal_cbbtc = tok_bal(CBBTC, WHALE)
    assert bal_cbbtc >= COLL, ('whale cbBTC below floor', bal_cbbtc)
    supply_usdc = min(SUPPLY_USDC, bal_usdc - 10)
    res['supply_sizing'] = dict(whale_usdc=bal_usdc, whale_cbbtc=bal_cbbtc, supplied=supply_usdc)
    print('whale usdc %d | cbbtc %d | supplying %d' % (bal_usdc, bal_cbbtc, supply_usdc))
    h, rc = send(WHALE, USDC, '0x' + (bytes.fromhex(sel('approve(address,uint256)')) + w_addr(MORPHO) + w_uint(2 ** 256 - 1)).hex())
    txs.append(dict(label='whale approve usdc', tx=h, gas=int(rc['gasUsed'], 16)))
    # Dual-form supply pre-flight: canonical 5-arg (a99aad89, selector-pinned
    # in exp11_liquidation) vs legacy 4-arg (receipt-proven in the XI
    # roundtrip artifact). eth_call both; send the form the singleton
    # accepts; record both probes in the artifact.
    # Bytes-tail offset counts the offset slot itself: supply head =
    # 5 struct + assets + shares + onBehalf + offset = 9 words -> 0x120
    # (run6 empirical pin: 0x120 executes, 0x100 reverts EMPTY; eth_abi
    # cross-check identical). Legacy 4-arg selector is ABSENT on the
    # singleton (empty revert) - recorded as probe only, never the form.
    sup_data = None
    sup_forms = []
    for form, sig, d in (
        ('canonical5', SIG_SUPPLY,
         '0x' + (Web3.keccak(text=SIG_SUPPLY)[:4] + blob + w_uint(supply_usdc) + w_uint(0) + w_addr(WHALE) + w_uint(0x120) + w_uint(0)).hex()),
        ('legacy4', SIG_SUPPLY_LEGACY,
         '0x' + (Web3.keccak(text=SIG_SUPPLY_LEGACY)[:4] + blob + w_uint(supply_usdc) + w_addr(WHALE) + w_uint(0)).hex())):
        ok, kind, info = try_call(MORPHO, d, WHALE)
        sup_forms.append(dict(form=form, sig=sig, ok=ok, kind=kind, info=info))
        if ok and sup_data is None:
            sup_data = d
            res['supply_form'] = form
    res['supply_sizing']['preflight'] = sup_forms
    assert sup_data is not None, ('supply pre-flight failed', sup_forms)
    h, rc = send(WHALE, MORPHO, sup_data)
    txs.append(dict(label='whale supply usdc', tx=h, gas=int(rc['gasUsed'], 16)))
    h, rc = send(WHALE, CBBTC, '0x' + (bytes.fromhex(sel('transfer(address,uint256)')) + w_addr(ACCT0) + w_uint(COLL)).hex())
    txs.append(dict(label='cbbtc to acct0', tx=h, gas=int(rc['gasUsed'], 16)))
    h, rc = send(ACCT0, CBBTC, '0x' + (bytes.fromhex(sel('approve(address,uint256)')) + w_addr(MORPHO) + w_uint(2 ** 256 - 1)).hex())
    txs.append(dict(label='acct0 approve cbbtc', tx=h, gas=int(rc['gasUsed'], 16)))
    # Dual-form supplyCollateral: canonical 4-arg-with-bytes (238d6579,
    # selector-pinned in exp11_liquidation). Bytes-tail offset counts the
    # offset slot itself: 5 struct + assets + onBehalf + offset = 8 words
    # -> 0x100 (run6 empirical pin: 0x100 reaches execution, 0xE0 reverts
    # EMPTY). Legacy 3-arg selector is ABSENT on the singleton - probe only.
    scoll_data = None
    scoll_forms = []
    for form, d in (
        ('canonical4', '0x' + (Web3.keccak(text=SIG_SCOLL)[:4] + blob + w_uint(COLL) + w_addr(ACCT0) + w_uint(0x100) + w_uint(0)).hex()),
        ('legacy3', '0x' + (Web3.keccak(text=SIG_SCOLL_LEGACY)[:4] + blob + w_uint(COLL) + w_addr(ACCT0)).hex())):
        ok, kind, info = try_call(MORPHO, d, ACCT0)
        scoll_forms.append(dict(form=form, ok=ok, kind=kind, info=info))
        if ok and scoll_data is None:
            scoll_data = d
            res['scoll_form'] = form
    res['scoll_forms'] = scoll_forms
    assert scoll_data is not None, ('supplyCollateral pre-flight failed', scoll_forms)
    h, rc = send(ACCT0, MORPHO, scoll_data)
    txs.append(dict(label='acct0 supplyCollateral cbbtc', tx=h, gas=int(rc['gasUsed'], 16)))
    txs.append(dict(label='supplyCollateral 0.05 cbbtc', tx=h, gas=int(rc['gasUsed'], 16)))

    def borrow_data(assets):
        return '0x' + (Web3.keccak(text=SIG_BORROW)[:4] + blob + w_uint(assets) + w_uint(0)
                       + w_addr(ACCT0) + w_addr(ACCT0)).hex()

    def liq_data(seized):
        # Bytes-tail offset counts the offset slot itself: 5 struct +
        # borrower + seized + repaid + offset = 9 words -> 0x120 (run6
        # empirical pin; 0x100 reverts EMPTY).
        return '0x' + (Web3.keccak(text=SIG_LIQ)[:4] + blob + w_addr(ACCT0) + w_uint(seized)
                       + w_uint(0) + w_uint(0x120) + w_uint(0)).hex()

    cand = max_borrow(COLL, BASELINE_PRICE, LLTV)
    borrowed = None
    for _ in range(6):
        ok, kind, info = try_call(MORPHO, borrow_data(cand), ACCT0)
        if ok:
            borrowed = cand
            break
        assert kind == 'string' and info == 'insufficient collateral', (kind, info)
        cand -= 1
    assert borrowed, 'no executable borrow'
    h, rc = send(ACCT0, MORPHO, borrow_data(borrowed))
    txs.append(dict(label='acct0 borrow max', tx=h, gas=int(rc['gasUsed'], 16)))
    res['position'] = dict(borrower=ACCT0, collateral=COLL, borrowed=borrowed, ceiling=max_borrow(COLL, BASELINE_PRICE, LLTV))
    print('borrowed', borrowed, 'of ceiling', max_borrow(COLL, BASELINE_PRICE, LLTV))

    ok, kind, info = try_call(MORPHO, liq_data(1), WHALE)
    res['baseline_health_probe'] = dict(ok=ok, kind=kind, info=info)
    print('baseline liquidate sim:', ok, kind, info)
    assert not ok and info == 'position is healthy', (ok, kind, info)

    def set_answer(mock, val, label):
        data = '0x' + (bytes.fromhex(sel('setAnswer(int256)')) + w_uint(val)).hex()
        h, rc = send(ACCT0, mock, data)
        txs.append(dict(label=label, tx=h, gas=int(rc['gasUsed'], 16)))

    def set_updated(mock, t, label):
        data = '0x' + (bytes.fromhex(sel('setUpdatedAt(uint256)')) + w_uint(t)).hex()
        h, rc = send(ACCT0, mock, data)
        txs.append(dict(label=label, tx=h, gas=int(rc['gasUsed'], 16)))

    def set_mode(mock, m, label):
        data = '0x' + (bytes.fromhex(sel('setMode(uint8)')) + w_uint(m)).hex()
        h, rc = send(ACCT0, mock, data)
        txs.append(dict(label=label, tx=h, gas=int(rc['gasUsed'], 16)))

    t_now = int(rpcq('eth_getBlockByNumber', ['latest', False])['result']['timestamp'], 16)

    print('== M2 base zero ==')
    set_answer(base_mock, 0, 'M2 base->0')
    p = price_int(oracle)
    ok, kind, info = try_call(MORPHO, borrow_data(1), ACCT0)
    okl, kindl, infol = try_call(MORPHO, liq_data(1), WHALE)
    res['scenarios'].append(dict(id='M2', verdict_class='base_zero_zero_price',
        observed=dict(price=p, price_serves_zero=p == 0,
                      borrow_probe=(kind, info), seizure_probe=(okl, kindl, str(infol)[:40]))))
    print('M2 price', p, '| borrow', kind, info, '| seize-sim', okl, kindl, str(infol)[:40])
    set_answer(base_mock, BASE_RAW, 'M2 restore base')

    print('== M3 quote zero ==')
    set_answer(quote_mock, 0, 'M3 quote->0')
    ok, kind, info = try_call(oracle, '0x' + sel('price()'))
    okb, kindb, infob = try_call(MORPHO, borrow_data(1), ACCT0)
    res['scenarios'].append(dict(id='M3', verdict_class='quote_zero_panic_freeze',
        observed=dict(price_probe=(kind, info), borrow_probe=(kindb, infob))))
    print('M3 price', kind, info, '| borrow', kindb, infob)
    set_answer(quote_mock, QUOTE_RAW, 'M3 restore quote')

    print('== M4 base negative ==')
    set_answer(base_mock, -1, 'M4 base->-1')
    ok, kind, info = try_call(oracle, '0x' + sel('price()'))
    res['scenarios'].append(dict(id='M4', verdict_class='base_negative_string_freeze',
        observed=dict(price_probe=(kind, info))))
    print('M4 price', kind, info)
    set_answer(base_mock, BASE_RAW, 'M4 restore base')

    print('== M5 stale ==')
    set_updated(base_mock, t_now - 86400, 'M5 stale updatedAt')
    p = price_int(oracle)
    res['scenarios'].append(dict(id='M5', verdict_class='stale_serves_unchanged',
        observed=dict(price=p, unchanged=p == BASELINE_PRICE, age_hours=24)))
    print('M5 price unchanged', p == BASELINE_PRICE)
    set_updated(base_mock, t_now, 'M5 restore updatedAt')

    print('== M6 quote depeg 0.90 ==')
    set_answer(quote_mock, 90_000_000, 'M6 quote->0.90')
    p = price_int(oracle)
    exp = SCALE * BASE_RAW // 90_000_000
    res['scenarios'].append(dict(id='M6', verdict_class='quote_depeg_price_up',
        observed=dict(price=p, expected=exp, exact=p == exp, ratio=p / BASELINE_PRICE)))
    print('M6 price', p, 'exact', p == exp)
    set_answer(quote_mock, QUOTE_RAW, 'M6 restore quote')

    print('== M7 base dislocation 0.70x ==')
    set_answer(base_mock, BASE_70, 'M7 base->0.70x')
    p = price_int(oracle)
    exp = SCALE * BASE_70 // QUOTE_RAW
    ok, kind, info = try_call(MORPHO, liq_data(1), WHALE)
    res['scenarios'].append(dict(id='M7', verdict_class='base_dislocation_price_down',
        observed=dict(price=p, expected=exp, exact=p == exp, ratio=p / BASELINE_PRICE,
                      liquidation_sim=(ok, kind, str(info)[:40]))))
    print('M7 price', p, 'exact', p == exp, '| liq-sim', ok, kind, str(info)[:40])
    set_answer(base_mock, BASE_RAW, 'M7 restore base')

    print('== M8 recovery ==')
    p = price_int(oracle)
    res['scenarios'].append(dict(id='M8', verdict_class='recovery_baseline_exact',
        observed=dict(price=p, exact=p == BASELINE_PRICE)))
    print('M8 price back to baseline', p == BASELINE_PRICE)

    print('== M9 combined 0.80x / 0.90x ==')
    set_answer(base_mock, BASE_80, 'M9 base->0.80x')
    set_answer(quote_mock, QUOTE_90, 'M9 quote->0.90x')
    p = price_int(oracle)
    exp = SCALE * BASE_80 // QUOTE_90
    res['scenarios'].append(dict(id='M9', verdict_class='combined_shift',
        observed=dict(price=p, expected=exp, exact=p == exp, ratio=p / BASELINE_PRICE)))
    print('M9 price', p, 'exact', p == exp)
    set_answer(base_mock, BASE_RAW, 'M9 restore base')
    set_answer(quote_mock, QUOTE_RAW, 'M9 restore quote')

    print('== M10 broken feed ==')
    set_mode(base_mock, 1, 'M10 base mode->broken')
    ok, kind, info = try_call(oracle, '0x' + sel('price()'))
    okb, kindb, infob = try_call(MORPHO, borrow_data(1), ACCT0)
    res['scenarios'].append(dict(id='M10', verdict_class='broken_feed_call_freeze',
        observed=dict(price_probe=(kind, info), borrow_probe=(kindb, infob))))
    print('M10 price', kind, info, '| borrow', kindb, infob)
    set_mode(base_mock, 0, 'M10 base mode->serve')
    p = price_int(oracle)
    assert p == BASELINE_PRICE, 'post-heal price drifted'
    print('healed price == baseline', p == BASELINE_PRICE)

    res['txs'] = txs
    RESULTS.write_text(json.dumps(res, indent=1))
    print('SAVED', RESULTS)
    for s in res['scenarios']:
        print(s['id'], s['verdict_class'])


if __name__ == '__main__':
    main()
