import glob, json, time, urllib.request
from web3 import Web3
from eth_abi import encode as abi_encode

FORK='http://127.0.0.1:8546'
MORPHO='0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
USDC='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
CBBTC='0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'
CAND='0xe1cc5c35f568225333e0c6eb1c030c776717660c'
V1='0x663BECd10daE6C4A3Dcd89F1d76c1174199639B9'
IRM='0x46415998764C29aB2a25CbeA6254146D50D22687'
LLTV=385*10**15
WHALE='0xfBB6Eed8e7aa03B138556eeDaF5D271A5E1e43ef'
ACCT0='0xf39Fd6e51aad88F6f4ce6aB8827279cffFb92266'
REAL_MID='0x2990655b2a05c2a067f10b94e28470cd86284f384c52ca71b9dec49f8fe8ef18'
MY_MID='0x42b1be56153b81ad018835119b8b94fb08f274a8e71103059be3faaad5398e0f'
SUPPLY=10_000*10**6
COLL=5_000_000
VS=10**6   # SharesMathLib.VIRTUAL_SHARES
VA=1       # SharesMathLib.VIRTUAL_ASSETS
TUPLE='(address,address,address,address,uint256)'
SRC=[open(f,errors='ignore').read() for f in sorted(glob.glob('sources/*.sol'))]


def rpcq(m,p):
    req=urllib.request.Request(FORK,
        data=json.dumps({'jsonrpc':'2.0','id':1,'method':m,'params':p}).encode(),
        headers={'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(req,timeout=60).read())

def sel(s): return Web3.keccak(text=s)[:4].hex()
def w_addr(a): return a[2:].lower().rjust(64,'0')
def w_uint(n): return '%064x'%n
def words(hx):
    h=hx[2:] if hx.startswith('0x') else hx
    return [int(h[i*64:(i+1)*64],16) for i in range(len(h)//64)]

def call(to,data,frm=None):
    tx={'to':to,'data':data}
    if frm: tx['from']=frm
    return rpcq('eth_call',[tx,'latest'])

def send(frm,to,data,gas=2_000_000):
    gp=int(rpcq('eth_gasPrice',[])['result'],16)
    n=int(rpcq('eth_getTransactionCount',[frm,'latest'])['result'],16)
    r=rpcq('eth_sendTransaction',[{'from':frm,'to':to,'data':data,'gas':hex(gas),
                                    'gasPrice':hex(gp),'nonce':hex(n)}])
    assert 'result' in r, json.dumps(r)[:300]
    h=r['result']; rc=None
    for _ in range(80):
        time.sleep(0.4)
        rr=rpcq('eth_getTransactionReceipt',[h])
        if 'result' in rr and rr['result']: rc=rr['result']; break
    assert rc,'no receipt '+h
    assert rc['status']=='0x1','REVERTED '+h
    return h,rc

def dec_err(d):
    if not d or not d.startswith('0x'): return ''
    if d.startswith('0x08c379a0') and len(d)>10:
        b=bytes.fromhex(d[10:])
        off=int.from_bytes(b[0:32],'big'); ln=int.from_bytes(b[off:off+32],'big')
        try: return b[off+32:off+32+ln].decode()
        except Exception: return 'undecodable'
    return d[:90]


def sig_of(name):
    for src in SRC:
        i=src.find('function '+name+'(')
        if i<0: continue
        j=i+len('function '+name); depth=0; started=False
        while j<len(src):
            c=src[j]
            if c=='(': depth+=1; started=True
            elif c==')':
                depth-=1
                if started and depth==0: break
            j+=1
        inner=' '.join(src[i+len('function '+name)+1:j].split())
        params=[]
        for p in inner.split(','):
            p=' '.join(p.split())
            p=p.replace(' memory ',' ').replace(' calldata ',' ')
            toks=p.split(' ')
            if len(toks)<2: return None
            typ=toks[0]; nm=toks[-1]
            typ=TUPLE if typ=='MarketParams' else typ
            params.append((typ,nm))
        return name+'('+','.join(t for t,_ in params)+')', params
    return None

ACTIONS=['supply','supplyCollateral','borrow','repay','withdraw','withdrawCollateral']
SIGS={}
for a in ACTIONS:
    got=sig_of(a)
    assert got, 'unparsed: '+a
    SIGS[a]=got
print('fork chainId',rpcq('eth_chainId',[])['result'])
for a in ACTIONS:
    print('  %-18s 0x%s'%(a,sel(SIGS[a][0])))


def encode(action,mp,vals):
    full,params=SIGS[action]
    types=[]; values=[]
    for typ,nm in params:
        if typ==TUPLE:
            types.append(TUPLE); values.append(tuple(mp))
        elif typ=='bytes':
            types.append('bytes'); values.append(b'')
        else:
            types.append(typ)
            if nm in vals: values.append(vals[nm])
            elif nm in ('shares','assets'): values.append(0)  # exactly-one-zero mode
            else: raise KeyError('%s.%s missing'%(action,nm))
    return '0x'+sel(full)+abi_encode(types,values).hex()


# ---------- fork prep ----------
rpcq('anvil_impersonateAccount',[WHALE])
rpcq('anvil_setBalance',[WHALE,hex(50*10**18)])
sel_ap=sel('approve(address,uint256)')
send(WHALE,USDC,'0x'+sel_ap+w_addr(MORPHO)+w_uint(2**256-1),gas=300_000)

MP=(USDC,CBBTC,CAND,IRM,LLTV)

def mkt():
    return words(call(MORPHO,'0x'+sel('market(bytes32)')+MY_MID[2:])['result'])
def pos_of(who):
    return words(call(MORPHO,'0x'+sel('position(bytes32,address)')+MY_MID[2:]+w_addr(who))['result'])
def usdc_of(who):
    return int(call(USDC,'0x'+sel('balanceOf(address)')+w_addr(who))['result'],16)
def cbbtc_of(who):
    return int(call(CBBTC,'0x'+sel('balanceOf(address)')+w_addr(who))['result'],16)


# ---------- CLEANUP: drain orphaned o7 supply -> exact zero market ----------
print()
print('== cleanup: withdraw orphaned supply from prior failed run ==')
mw=mkt(); pw=pos_of(WHALE)
print('pre: tsa=%d tss=%d | whale supplyShares=%d'%(mw[0],mw[1],pw[0]))
if pw[0]>0:
    h0,_=send(WHALE,MORPHO,encode('withdraw',MP,{'shares':pw[0],'onBehalf':WHALE,'receiver':WHALE}))
    mw=mkt(); pw=pos_of(WHALE)
    print('post: tsa=%d tss=%d | whale supplyShares=%d'%(mw[0],mw[1],pw[0]))
    assert mw[0]==0 and mw[1]==0 and pw[0]==0, 'cleanup not exact-zero'
    print('CLEANUP EXACT: market returned to zero state (tss=tsa*1e6 identity full-exit)')
else:
    assert mw[0]==0 and mw[1]==0, 'unexpected non-zero market with no whale shares'
    print('already clean')


# ---------- full roundtrip P0-P8 ----------
PH='pre'
try:
    PH='P0'
    p_cand=int(call(CAND,'0x'+sel('price()'))['result'],16)
    p_v1=int(call(V1,'0x'+sel('price()'))['result'],16)
    print('P0 parity: cand=%.4e v1=%.4e ratio=%.6f'%(p_cand,p_v1,p_cand/p_v1))
    assert 0.98<p_cand/p_v1<1.02

    PH='P1'
    mw=mkt()
    print('P1 market: tsa=%d tss=%d tba=%d tbs=%d lastUpdate=%d fee=%d'%tuple(mw))
    assert mw[4]>0 and mw[0]==0 and mw[2]==0

    PH='P2'
    wb=usdc_of(WHALE)
    cb0=cbbtc_of(WHALE)
    assert wb>=SUPPLY
    h2,rc=send(WHALE,MORPHO,encode('supply',MP,{'assets':SUPPLY,'onBehalf':WHALE}))
    sup_shares=None
    for l in rc['logs']:
        if len(l['topics'])>=2 and l['topics'][1].lower()==MY_MID.lower():
            dw=words(l['data'])
            if len(dw)>=2 and dw[-2]==SUPPLY: sup_shares=dw[-1]
    assert sup_shares is not None,'Supply event missing'
    print('P2 supply: assets=%d shares=%d (virtual-shares ratio 1e6)'%(SUPPLY,sup_shares))
    assert sup_shares==SUPPLY*VS, 'first-supply SharesMathLib identity failed'

    PH='P3'
    h3a,_=send(WHALE,CBBTC,'0x'+sel('transfer(address,uint256)')+w_addr(ACCT0)+w_uint(COLL),gas=300_000)
    send(ACCT0,CBBTC,'0x'+sel_ap+w_addr(MORPHO)+w_uint(2**256-1),gas=300_000)
    h3,_=send(ACCT0,MORPHO,encode('supplyCollateral',MP,{'assets':COLL,'onBehalf':ACCT0}))
    p3=pos_of(ACCT0)
    print('P3 position: supplyShares=%d borrowShares=%d collateral=%d'%tuple(p3))
    assert p3[2]==COLL and p3[1]==0 and p3[0]==0

    PH='P4'
    pred_df=(COLL*p_cand//10**36)*LLTV//10**18
    pred_sf=COLL*LLTV*p_cand//10**54
    chain_max=None
    for c in sorted(set([pred_sf,pred_df,pred_sf-1,pred_df-1]),reverse=True):
        if 'result' in call(MORPHO,encode('borrow',MP,{'assets':c,'onBehalf':ACCT0,'receiver':ACCT0}),frm=ACCT0):
            chain_max=c; break
    assert chain_max is not None,'bracket empty'
    r_over=rpcq('eth_call',[{'from':ACCT0,'to':MORPHO,
        'data':encode('borrow',MP,{'assets':chain_max+1,'onBehalf':ACCT0,'receiver':ACCT0})},'latest'])
    over=dec_err(r_over.get('error',{}).get('data') or '')
    print('P4 chain_max=%d ($%.6f) | df=%d sf=%d | over-max: %r'%(chain_max,chain_max/1e6,pred_df,pred_sf,over))
    assert chain_max in (pred_df,pred_sf)
    assert over not in ('','0x'), 'EMPTY revert — encoding regression'
    h4,rc=send(ACCT0,MORPHO,encode('borrow',MP,{'assets':chain_max,'onBehalf':ACCT0,'receiver':ACCT0}))
    bor_assets=bor_shares=bor_recv=None
    for l in rc['logs']:
        if len(l['topics'])>=2 and l['topics'][1].lower()==MY_MID.lower():
            dw=words(l['data'])
            if len(dw)>=2 and dw[-2]==chain_max:
                bor_assets,bor_shares=dw[-2],dw[-1]
                if len(l['topics'])==5: bor_recv='0x'+l['topics'][4][-40:]
    assert bor_assets is not None,'Borrow event missing'
    print('P4 borrow: assets=%d shares=%d receiver=%s'%(bor_assets,bor_shares,bor_recv))
    assert bor_assets==chain_max
    assert bor_shares==chain_max*VS, 'first-borrow SharesMathLib identity failed'
    assert bor_recv is None or bor_recv.lower()==ACCT0.lower()
    print('EXACT-MAX PROVEN on real mainnet fork state')

    PH='P5'
    bts=int(rpcq('eth_getBlockByNumber',[rc['blockNumber'],False])['result']['timestamp'],16)
    repay_mode='assets-frozen'
    fz=rpcq('evm_setNextBlockTimestamp',[hex(bts)])
    if 'error' in fz:
        print('freeze at equal ts rejected -> fallback: +1s, shares-mode repay')
        rpcq('evm_setNextBlockTimestamp',[hex(bts+1)])
        repay_mode='shares-accrued'
    send(ACCT0,USDC,'0x'+sel_ap+w_addr(MORPHO)+w_uint(2**256-1),gas=300_000)
    if repay_mode=='assets-frozen':
        h5,_=send(ACCT0,MORPHO,encode('repay',MP,{'assets':bor_assets,'onBehalf':ACCT0}))
    else:
        send(WHALE,USDC,'0x'+sel('transfer(address,uint256)')+w_addr(ACCT0)+w_uint(1_000_000),gas=300_000)
        h5,_=send(ACCT0,MORPHO,encode('repay',MP,{'shares':bor_shares,'onBehalf':ACCT0}))
    p5=pos_of(ACCT0)
    print('P5 repay(%s): supplyShares=%d borrowShares=%d collateral=%d'%(repay_mode,p5[0],p5[1],p5[2]))
    assert p5[1]==0 and p5[2]==COLL, 'debt not exactly closed'

    PH='P6'
    h6,_=send(ACCT0,MORPHO,encode('withdrawCollateral',MP,{'assets':COLL,'onBehalf':ACCT0,'receiver':WHALE}))
    p6=pos_of(ACCT0)
    assert p6[2]==0
    print('P6 collateral withdrawn to whale: whale cbBTC delta=%d'%(cbbtc_of(WHALE)-cb0))
    assert cbbtc_of(WHALE)-cb0==0

    PH='P7'
    mw=mkt()
    h7,_=send(WHALE,MORPHO,encode('withdraw',MP,{'shares':mw[1],'onBehalf':WHALE,'receiver':WHALE}))
    print('P7 supplier full exit by shares: burned=%d'%mw[1])

    PH='P8'
    fw=mkt()
    wb2=usdc_of(WHALE)
    print('P8 final: tsa=%d tss=%d tba=%d tbs=%d | whale USDC delta=%d | cbBTC delta=%d'
          %(fw[0],fw[1],fw[2],fw[3],wb2-wb,cbbtc_of(WHALE)-cb0))
    assert fw[0]==0 and fw[1]==0 and fw[2]==0 and fw[3]==0
    assert wb2-wb==0
    assert cbbtc_of(WHALE)-cb0==0
except AssertionError as ex:
    print('FAIL at %s: %s'%(PH,ex))
    raise

json.dump({
 'experiment':'XI-O5 production-shape market roundtrip on Base mainnet fork',
 'chain':'base-mainnet fork via anvil :8546 (chainId 0x2105)',
 'morpho_singleton':MORPHO,'market_id':MY_MID,
 'market_params':{'loan':USDC,'collateral':CBBTC,'oracle':CAND,'irm':IRM,'lltv':str(LLTV)},
 'encoding':'eth_abi; signatures parsed from IMorpho.sol/Morpho.sol; bytes-tail offset=32*(6+n_static)',
 'shares_math':{'virtual_shares':VS,'virtual_assets':VA,
   'first_supply_shares':'assets*1e6 exact (measured)',
   'first_borrow_shares':'assets*1e6 exact (measured)',
   'full_exit_by_shares':'burns exact total, assets out exact (measured)'},
 'position_decode':'(supplyShares, borrowShares, collateral)',
 'oracle':{'candidate_v2':CAND,'price':str(p_cand),'real_v1':V1,'price_v1':str(p_v1),
           'parity_ratio':round(p_cand/p_v1,6)},
 'supply':{'assets':SUPPLY,'shares':sup_shares},'collateral':COLL,
 'max_borrow':{'pred_double_floor':pred_df,'pred_single_floor':pred_sf,'chain_max':chain_max,
               'matched':'double-floor' if chain_max==pred_df else 'single-floor',
               'over_max_revert':over},
 'borrow':{'assets':bor_assets,'shares':bor_shares,'receiver':bor_recv},
 'repay':{'mode':repay_mode,'post_borrowShares':0},
 'final_state':{'tsa':fw[0],'tss':fw[1],'tba':fw[2],'tbs':fw[3],'lastUpdate':fw[4],'fee':fw[5]},
 'whale_usdc_delta':wb2-wb,'whale_cbbtc_delta':0,
 'txs':{'cleanup_withdraw':locals().get('h0'),
        'supply':h2,'cbbtc_transfer':h3a,'collateral':h3,'borrow':h4,
        'repay':h5,'withdrawCollateral':h6,'supplierExit':h7},
},open('exp11_market_roundtrip.json','w'),indent=1)
print()
print('SAVED exp11_market_roundtrip.json')
print('XI-O5 COMPLETE: production-shape roundtrip, exact zero-state, all identities measured')
