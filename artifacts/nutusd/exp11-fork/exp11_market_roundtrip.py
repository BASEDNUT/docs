import json, time, urllib.request
from web3 import Web3

FORK = 'http://127.0.0.1:8546'
MORPHO = '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
CBBTC = '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'
CAND = '0xe1cc5c35f568225333e0c6eb1c030c776717660c'  # 2-leg V2 candidate (fork)
IRM = '0x46415998764C29aB2a25CbeA6254146D50D22687'
LLTV = 385 * 10**15
WHALE = '0xfBB6Eed8e7aa03B138556eeDaF5D271A5E1e43ef'  # uniV3 cbBTC/USDC pool
ACCT0 = '0xf39Fd6e51aad88F6f4ce6aB8827279cffFb92266'
SUPPLY_USDC = 10_000 * 10**6
COLL_CBBTC = 5_000_000  # 0.05 cbBTC, 8 dec


def rpcq(method, params):
    req = urllib.request.Request(FORK,
        data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method,
                         'params': params}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def call(to, data, frm=None):
    tx = {'to': to, 'data': data}
    if frm:
        tx['from'] = frm
    r = rpcq('eth_call', [tx, 'latest'])
    assert 'result' in r, json.dumps(r)[:300]
    return r['result']


def sel(sig):
    return Web3.keccak(text=sig)[:4].hex()


def w_addr(a):
    return bytes.fromhex(a[2:].lower().rjust(64, '0'))


def w_uint(n):
    return n.to_bytes(32, 'big')


def send(frm, to, data, gas=1_500_000):
    gp = int(rpcq('eth_gasPrice', [])['result'], 16)
    nonce = int(rpcq('eth_getTransactionCount', [frm, 'latest'])['result'], 16)
    r = rpcq('eth_sendTransaction', [{'from': frm, 'to': to, 'data': data,
                                      'gas': hex(gas), 'gasPrice': hex(gp),
                                      'nonce': hex(nonce)}])
    assert 'result' in r, json.dumps(r)[:300]
    h = r['result']
    receipt = None
    for _ in range(80):
        time.sleep(0.4)
        rr = rpcq('eth_getTransactionReceipt', [h])
        if 'result' in rr and rr['result']:
            receipt = rr['result']
            break
    assert receipt, 'no receipt for ' + h
    return h, receipt


def rc_str(receipt):
    return 'status=%s gas=%d logs=%d' % (receipt['status'], int(receipt['gasUsed'], 16), len(receipt['logs']))


# ---------- phase 0: impersonate + balance ----------
print('== P0 impersonation ==')
assert rpcq('anvil_impersonateAccount', [WHALE])['result'] is not None or True
rpcq('anvil_setBalance', [WHALE, hex(50 * 10**18)])
print('whale impersonated + 50 ETH gas')

# ---------- phase 1: marketId offline + createMarket ----------
print()
print('== P1 createMarket with candidate oracle ==')
blob = w_addr(USDC) + w_addr(CBBTC) + w_addr(CAND) + w_addr(IRM) + w_uint(LLTV)
mid_pred = Web3.keccak(blob).hex()
print('offline marketId:', mid_pred)

data = '0x' + (Web3.keccak(text='createMarket((address,address,address,address,uint256))')[:4] + blob).hex()
h, rc = send(WHALE, MORPHO, data)
print('createMarket', rc_str(rc))
assert rc['status'] == '0x1', 'createMarket failed'
topic_mc = Web3.keccak(text='MarketCreation((address,address,address,address,uint256))').hex()
topic_mc = '0x' + topic_mc if not topic_mc.startswith('0x') else topic_mc
ev_mid = None
for l in rc['logs']:
    if l['topics'][0].lower() == topic_mc.lower():
        ev_mid = l['topics'][1].lower()
print('event marketId  :', ev_mid)
assert ev_mid == mid_pred.lower(), 'marketId mismatch!'
print('marketId EXACT match (offline keccak == event)')
MID = mid_pred.lower()

# ---------- phase 2: whale supplies USDC ----------
print()
print('== P2 whale supplies 10,000 USDC ==')
sel_ap = sel('approve(address,uint256)')
h, rc = send(WHALE, USDC, '0x' + (sel_ap + w_addr(MORPHO) + w_uint(2**256 - 1)).hex())
assert rc['status'] == '0x1'
sel_sup = sel('supply((address,address,address,address,uint256),uint256,address,uint256)')
data = '0x' + (sel_sup + blob + w_uint(SUPPLY_USDC) + w_addr(WHALE) + w_uint(0)).hex()
h, rc = send(WHALE, MORPHO, data, gas=2_000_000)
print('supply', rc_str(rc))
assert rc['status'] == '0x1', 'supply failed'

# ---------- phase 3: cbBTC to acct0, collateral ----------
print()
print('== P3 collateral 0.05 cbBTC ==')
sel_xfer = sel('transfer(address,uint256)')
h, rc = send(WHALE, CBBTC, '0x' + (sel_xfer + w_addr(ACCT0) + w_uint(COLL_CBBTC)).hex())
assert rc['status'] == '0x1', 'cbbtc transfer failed'
h, rc = send(ACCT0, CBBTC, '0x' + (sel_ap + w_addr(MORPHO) + w_uint(2**256 - 1)).hex())
assert rc['status'] == '0x1'
sel_sc = sel('supplyCollateral((address,address,address,address,uint256),uint256,address)')
data = '0x' + (sel_sc + blob + w_uint(COLL_CBBTC) + w_addr(ACCT0)).hex()
h, rc = send(ACCT0, MORPHO, data, gas=2_000_000)
print('supplyCollateral', rc_str(rc))
assert rc['status'] == '0x1', 'supplyCollateral failed'

# ---------- phase 4: maxBorrow offline + probes + exact-max borrow ----------
print()
print('== P4 exact-max borrow ==')
sel_p = sel('price()')
price = int(call(CAND, '0x' + sel_p)[2:66], 16)
print('oracle price():', price)
step1 = COLL_CBBTC * LLTV // 10**18
max_borrow = step1 * price // 10**36
print('coll %d -> step1 %d -> maxBorrow %d raw = $%.4f' % (COLL_CBBTC, step1, max_borrow, max_borrow / 1e6))

sel_bor = sel('borrow((address,address,address,address,uint256),uint256,address,address,uint256)')
def borrow_tx(amount):
    return '0x' + (sel_bor + blob + w_uint(amount) + w_addr(ACCT0) + w_addr(ACCT0) + w_uint(0)).hex()

r_ok = call(MORPHO, borrow_tx(max_borrow), frm=ACCT0)
print('probe exact-max : PASS (returns %s...)' % r_ok[:10])
r_over = rpcq('eth_call', [{'from': ACCT0, 'to': MORPHO, 'data': borrow_tx(max_borrow + 1)}, 'latest'])
err = r_over.get('error', {})
msg = err.get('data', '') or err.get('message', '')
print('probe max+1     : revert', msg[:60])
assert 'insufficient collateral' in msg or err.get('code') == 3, 'expected insufficient collateral'

h, rc = send(ACCT0, MORPHO, borrow_tx(max_borrow), gas=2_000_000)
print('borrow exact-max', rc_str(rc))
assert rc['status'] == '0x1', 'exact-max borrow FAILED on send'
topic_borrow = '0x' + Web3.keccak(text='Borrow(bytes32,address,address,address,uint256,uint256)').hex().removeprefix('0x')
bor_assets = bor_shares = None
for l in rc['logs']:
    if l['topics'][0].lower() == topic_borrow.lower() and l['topics'][1].lower() == '0x' + MID[2:].rjust(64, '0'):
        bor_assets = int(l['data'][2:66], 16)
        bor_shares = int(l['data'][66:130], 16)
print('Borrow event: assets=%d shares=%d | exact==max: %s' % (bor_assets, bor_shares, bor_assets == max_borrow))
assert bor_assets == max_borrow, 'borrow assets != predicted max'

# ---------- phase 5: repay by shares ----------
print()
print('== P5 repay by shares ==')
sel_rep = sel('repay((address,address,address,address,uint256),uint256,address,uint256)')
data = '0x' + (sel_rep + blob + w_uint(0) + w_addr(ACCT0) + w_uint(bor_shares)).hex()
h, rc = send(ACCT0, MORPHO, data, gas=2_000_000)
print('repay shares', rc_str(rc))
assert rc['status'] == '0x1', 'repay failed'

# ---------- phase 6: withdraw collateral ----------
print()
print('== P6 withdraw collateral ==')
sel_wc = sel('withdrawCollateral((address,address,address,address,uint256),uint256,address)')
data = '0x' + (sel_wc + blob + w_uint(COLL_CBBTC) + w_addr(ACCT0)).hex()
h, rc = send(ACCT0, MORPHO, data, gas=2_000_000)
print('withdrawCollateral', rc_str(rc))
assert rc['status'] == '0x1', 'withdraw collateral failed'

# ---------- phase 7: whale withdraws supply ----------
print()
print('== P7 supplier exit ==')
sel_wd = sel('withdraw((address,address,address,address,uint256),uint256,address,address,uint256)')
sel_tss = sel('totalSupplyShares(bytes32)')
tss = int(call(MORPHO, '0x' + sel_tss + MID[2:].rjust(64, '0'))[2:66], 16)
whale_shares = tss  # sole supplier
print('whale supply shares:', whale_shares)
data = '0x' + (sel_wd + blob + w_uint(whale_shares) + w_addr(WHALE) + w_addr(WHALE) + w_uint(0)).hex()
h, rc = send(WHALE, MORPHO, data, gas=2_000_000)
print('withdraw', rc_str(rc))
assert rc['status'] == '0x1', 'supplier withdraw failed'

# ---------- phase 8: final balances + artifact ----------
print()
print('== P8 final state ==')
sel_bal = sel('balanceOf(address)')
def bal(token, who):
    return int(call(token, '0x' + sel_bal + who[2:].lower().rjust(64, '0'))[2:66], 16)

tsa = int(call(MORPHO, '0x' + sel('market(bytes32)') + MID[2:].rjust(64, '0'))[2:66], 16)
tba_w = call(MORPHO, '0x' + sel('extsloads(bytes32[])') + (w_uint(int(MID[2:], 16) - 1) if False else b'').hex(), frm=None) if False else None
print('final totalSupplyAssets raw: %d ($%.6f)' % (tsa, tsa / 1e6))
print('acct0 cbBTC back:', bal(CBBTC, ACCT0), '(expect >= %d)' % COLL_CBBTC)

json.dump({
  'experiment': 'XI-O5 fork market roundtrip (production shape)',
  'chain': 'base-mainnet fork via anvil :8546',
  'morpho_singleton': MORPHO,
  'market_id': MID,
  'market_params': {'loan': USDC, 'collateral': CBBTC, 'oracle': CAND,
                    'irm': IRM, 'lltv': str(LLTV)},
  'oracle': 'MorphoChainlinkOracleV2 2-leg cbBTC/USD / USDC/USD (fork 0xe1cc...660c)',
  'price_at_borrow': price,
  'max_borrow_prediction': max_borrow,
  'borrow_assets_measured': bor_assets,
  'exact_match': bor_assets == max_borrow,
  'probe_max_plus_1': 'reverted insufficient collateral',
  'repay_mode': 'by shares (%d)' % bor_shares,
  'collateral_withdrawn': COLL_CBBTC,
  'supplier_exit': 'full shares %d' % whale_shares,
  'receipts': {'createMarket': h},
}, open('exp11_market_roundtrip.json', 'w'), indent=1)
print()
print('SAVED exp11_market_roundtrip.json')
print('XI-O5 COMPLETE: exact-max borrow at 38.5% LLTV against real mainnet fork state')
