import json, time, urllib.request
from web3 import Web3

FORK = 'http://127.0.0.1:8546'
FACTORY = '0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d'
V1 = '0x663BECd10daE6C4A3Dcd89F1d76c1174199639B9'
CBBTC_FEED = '0x07DA0E54543a844a80ABE69c8A12F22B3aA59f9D'
USDC_FEED = '0x7e860098F58bBFC8648a4311b374B1D669a2bc6B'
SALT = bytes.fromhex('6e7574555344' + '00' * 25 + '01')
ZERO = '0x' + '00' * 20


def rpcq(method, params):
    req = urllib.request.Request(FORK,
        data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method,
                         'params': params}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def call(to, data):
    return rpcq('eth_call', [{'to': to, 'data': data}, 'latest'])['result']


def w_addr(a):
    return bytes.fromhex(a[2:].lower().rjust(64, '0'))


def w_uint(n):
    return n.to_bytes(32, 'big')


sel_create = Web3.keccak(text='createMorphoChainlinkOracleV2(address,uint256,address,address,uint256,address,uint256,address,address,uint256,bytes32)')[:4]
body = (w_addr(ZERO) + w_uint(1)
        + w_addr(CBBTC_FEED) + w_addr(ZERO) + w_uint(8)
        + w_addr(ZERO) + w_uint(1)
        + w_addr(USDC_FEED) + w_addr(ZERO) + w_uint(6)
        + SALT)
data = '0x' + (sel_create + body).hex()
print('calldata len:', len(data) // 2 - 1, 'bytes | selector:', sel_create.hex())

accts = rpcq('eth_accounts', [])['result']
frm = accts[0]
print('sender:', frm)

gas_price = int(rpcq('eth_gasPrice', [])['result'], 16)
print('gasPrice:', gas_price, 'wei')

nonce = int(rpcq('eth_getTransactionCount', [frm, 'latest'])['result'], 16)
tx = {'from': frm, 'to': FACTORY, 'data': data,
      'gas': hex(1200000), 'gasPrice': hex(gas_price), 'nonce': hex(nonce)}
h = rpcq('eth_sendTransaction', [tx])['result']
print('txHash:', h)

receipt = None
for _ in range(40):
    time.sleep(0.5)
    r = rpcq('eth_getTransactionReceipt', [h])
    if 'result' in r and r['result']:
        receipt = r['result']
        break
print('status:', receipt['status'], '| block:', int(receipt['blockNumber'], 16),
      '| gasUsed:', int(receipt['gasUsed'], 16))

topic_create = Web3.keccak(text='CreateMorphoChainlinkOracleV2(address,address)').hex()
oracle = None
for l in receipt['logs']:
    if l['topics'][0].lower() == ('0x' + topic_create if topic_create.startswith('0x') is False else topic_create).lower():
        b = l['data'][2:]
        caller = '0x' + b[24:64]
        oracle = '0x' + b[88:128]
        print('CREATE EVENT | caller', caller, '| ORACLE', oracle)
assert oracle, 'no create event found'

sel_is = Web3.keccak(text='isMorphoChainlinkOracleV2(address)')[:4].hex()
reg = int(call(FACTORY, '0x' + sel_is + oracle[2:].lower().rjust(64, '0'))[2:66], 16)
print('factory registered:', reg == 1)

sel_sf = Web3.keccak(text='SCALE_FACTOR()')[:4].hex()
sf = int(call(oracle, '0x' + sel_sf)[2:66], 16)
print('SCALE_FACTOR:', sf, '| expect 1e34:', sf == 10 ** 34)

sel_p = Web3.keccak(text='price()')[:4].hex()
pc = int(call(oracle, '0x' + sel_p)[2:66], 16)
pv1 = int(call(V1, '0x' + sel_p)[2:66], 16)


def latest(feed):
    rr = call(feed, '0xfeaf968c')
    return int(rr[66:130], 16), int(rr[194:258], 16)


a_c, u_c = latest(CBBTC_FEED)
a_u, u_u = latest(USDC_FEED)
pred = a_c * 10 ** 34 // a_u
print()
print('cbBTC/USD raw : %d ($%.2f) upd %d' % (a_c, a_c / 1e8, u_c))
print('USDC/USD raw  : %d ($%.4f) upd %d' % (a_u, a_u / 1e8, u_u))
print('candidate price() : %d' % pc)
print('formula pred      : %d | exact: %s' % (pred, pc == pred))
print('V1 price()        : %d' % pv1)
print('ratio cand/V1     : %.8f' % (pc / pv1))
print('USD/cbBTC: cand $%.2f | V1 $%.2f | delta $%.2f' %
      (pc * 1e-34, pv1 * 1e-34, (pc - pv1) * 1e-34))

json.dump({'oracle': oracle, 'txHash': h, 'sender': frm,
           'scale_factor': sf, 'price_candidate': pc, 'price_v1': pv1,
           'cbbtc_feed_raw': a_c, 'cbbtc_feed_upd': u_c,
           'usdc_feed_raw': a_u, 'usdc_feed_upd': u_u,
           'formula_pred': pred, 'formula_exact': pc == pred,
           'factory_registered': reg == 1},
          open('exp11_oracle_candidate.json', 'w'), indent=1)
print('SAVED exp11_oracle_candidate.json')
