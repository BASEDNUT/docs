import json, time, urllib.request
import eth_abi
from web3 import Web3

FORK='http://127.0.0.1:8546'
MORPHO='0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb'
USDC='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
CBBTC='0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf'
CAND='0xe1cc5c35f568225333e0c6eb1c030c776717660c'
IRM='0x46415998764C29aB2a25CbeA6254146D50D22687'
LLTV=385*10**15
MID='0x42b1be56153b81ad018835119b8b94fb08f274a8e71103059be3faaad5398e0f'
MP=(USDC,CBBTC,CAND,IRM,LLTV)
TUP='(address,address,address,address,uint256)'
MKT6='(uint128,uint128,uint128,uint128,uint128,uint16)'
WHALE='0xfBB6Eed8e7aa03B138556eeDaF5D271A5E1e43ef'
ACCT0='0xf39Fd6e51aad88F6f4ce6aB8827279cffFb92266'
ACCT1='0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
SUPPLY=20_000*10**6
COLL=50_000_000
WARP=7200
WAD=10**18; SCALE=10**36; CURSOR=3*10**17; MAXLIF=115*10**16
MAXAPPROVE=2**256-1

def sel(s): return Web3.keccak(text=s)[:4].hex()

def rpcq(m,p):
    req=urllib.request.Request(FORK,
        data=json.dumps({'jsonrpc':'2.0','id':1,'method':m,'params':p}).encode(),
        headers={'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(req,timeout=60).read())

def call(to,data,frm=None,attempts=4):
    tx={'to':to,'data':data}
    if frm: tx['from']=frm
    r=None
    for i in range(attempts):
        r=rpcq('eth_call',[tx,'latest'])
        if 'result' in r: return r
        print('  call retry %d: %s'%(i+1,json.dumps(r.get('error',r))[:140]))
        time.sleep(1.5)
    return r

def words(h): return [int(h[2+64*i:2+64*(i+1)],16) for i in range((len(h)-2)//64)]
def w_addr(a): return a[2:].lower().rjust(64,'0')
def w_uint(n): return '%064x'%n
blob=w_addr(USDC)+w_addr(CBBTC)+w_addr(CAND)+w_addr(IRM)+w_uint(LLTV)

def enc(fn,types,values):
    return '0x'+sel(fn)+eth_abi.encode(types,values).hex()

SIGS={
 'supply':'supply((address,address,address,address,uint256),uint256,uint256,address,bytes)',
 'supplyCollateral':'supplyCollateral((address,address,address,address,uint256),uint256,address,bytes)',
 'borrow':'borrow((address,address,address,address,uint256),uint256,uint256,address,address)',
 'repay':'repay((address,address,address,address,uint256),uint256,uint256,address,bytes)',
 'withdraw':'withdraw((address,address,address,address,uint256),uint256,uint256,address,address)',
 'withdrawCollateral':'withdrawCollateral((address,address,address,address,uint256),uint256,address,address)',
 'liquidate':'liquidate((address,address,address,address,uint256),address,uint256,uint256,bytes)',
}
KNOWN={'supply':'a99aad89','supplyCollateral':'238d6579','borrow':'50d8cd4b',
 'withdraw':'5c2bea49','withdrawCollateral':'8720316d','repay':'20b76e81'}
for k,v in KNOWN.items():
    assert sel(SIGS[k])==v, 'selector drift '+k
print('live pins verified %d/%d'%(len(KNOWN),len(KNOWN)))

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

def mkt(): return words(call(MORPHO,'0x'+sel('market(bytes32)')+MID[2:])['result'])
def pos_of(who): return words(call(MORPHO,'0x'+sel('position(bytes32,address)')+MID[2:]+w_addr(who))['result'])
def price(): return int(call(CAND,'0x'+sel('price()'))['result'],16)
def wmul(x,y): return x*y//WAD

def ev_from(rc,sigstr):
    t0=Web3.keccak(text=sigstr).hex().lower().removeprefix('0x')
    for l in rc['logs']:
        if l['topics'][0].lower().removeprefix('0x')==t0: return l
    return None

def dwords(l): return words(l['data'])

print('== P0 liveness + zero-state ==')
blk=int(rpcq('eth_blockNumber',[])['result'],16)
mw0=mkt()
print('block %d | tsa=%d tba=%d lastUpdate=%d'%(blk,mw0[0],mw0[2],mw0[4]))
rpcq('anvil_impersonateAccount',[WHALE]); rpcq('anvil_setBalance',[WHALE,hex(50*10**18)])

print('== P0.5 self-heal: clear leftovers from failed runs ==')
pw_a=pos_of(ACCT0)
if pw_a[1]>0:
    send(WHALE,MORPHO,enc(SIGS['repay'],[TUP,'uint256','uint256','address','bytes'],[tuple(MP),0,pw_a[1],ACCT0,b'']))
    print('  acct0 debt repaid by whale: %d shares'%pw_a[1])
pw_w=pos_of(WHALE)
if pw_w[0]>0:
    send(WHALE,MORPHO,enc(SIGS['withdraw'],[TUP,'uint256','uint256','address','address'],[tuple(MP),0,pw_w[0],WHALE,WHALE]))
    print('  whale supply withdrawn: %d shares'%pw_w[0])
pw_a=pos_of(ACCT0)
if pw_a[2]>0:
    send(ACCT0,MORPHO,enc(SIGS['withdrawCollateral'],[TUP,'uint256','address','address'],[tuple(MP),pw_a[2],ACCT0,ACCT0]))
    print('  acct0 collateral withdrawn: %d'%pw_a[2])
mw0=mkt()
print('  post-heal market: tsa=%d tss=%d tba=%d tbs=%d'%tuple(mw0[:4]))

print('== P0.7 dust floor (SharesMathLib virtual offsets 1/1e6) ==')
# A market that has held supply cannot go below tsa=1 with tss=0 via protocol
# ops: full-shares exit leaves 1 unit; full-assets exit at small scale
# overshoots by ceil-rounding and reverts. 1 micro ($0.000001) unclaimable.
assert mw0[2]==0 and mw0[3]==0, ('debt not clear after heal', mw0)
assert mw0[1]==0, ('shares not clear after heal', mw0)
# Floor accumulates +1 micro per full-share exit across runs (measured:
# 1 -> 2 -> 3 across runs 10-13). Bound is generous; the property is the
# share/debt exactness, not the micro-count.
assert mw0[0]<=10_000, ('dust floor violated', mw0)
DUST=mw0[0]
print('  baseline clean: debt 0, shares 0, dust floor tsa=%d micro (+1 per full-share exit, %d prior exits)'%(DUST,DUST-1))

print('== P0.6 fork pin ==')
fork_blk=None; fork_hash=None; fork_url=None
try:
    import subprocess as _sp
    _ps=_sp.run(['ps','-eo','args'],capture_output=True,text=True).stdout
    for _ln in _ps.splitlines():
        if 'anvil' in _ln and '--fork-url' in _ln:
            for _t in _ln.split():
                if _t.startswith('--fork-url='): fork_url=_t[11:]
                if _t.startswith('--fork-block=') and _t[13:].isdigit(): fork_blk=int(_t[13:])
            break
    print('  ps: url=%s block=%s'%(fork_url,fork_blk))
except Exception as e:
    print('  ps scan failed: %s'%str(e)[:60])
try:
    ni_raw=rpcq('anvil_nodeInfo',[])
    print('  nodeInfo raw: %s'%json.dumps(ni_raw)[:220])
    ni=ni_raw.get('result') or {}
    if isinstance(ni,dict):
        fork_blk=ni.get('forkBlockNumber') or ni.get('fork_block_number')
        fork_url=ni.get('forkUrl') or ni.get('fork_url')
        if isinstance(fork_blk,str): fork_blk=int(fork_blk,16)
except Exception as e:
    print('  nodeInfo unavailable: %s'%str(e)[:80])
if not fork_blk:
    try:
        lg=open('anvil_fork.log',errors='ignore').read()[:4000]
        for tok in lg.replace('=',' ').replace(':',' ').split():
            if tok.isdigit() and 8000000<=int(tok)<=60000000:
                fork_blk=int(tok); print('  fork block from log banner: %d'%fork_blk); break
    except Exception: pass
if not fork_blk:
    try:
        rj=json.load(open('exp11_market_roundtrip.json'))
        for k in ('fork_block','block','block_number','forkBlock'):
            if k in rj: fork_blk=rj[k]; break
    except Exception: pass
if fork_blk:
    try:
        fb=rpcq('eth_getBlockByNumber',[hex(int(fork_blk)),False]).get('result')
        if fb: fork_hash=fb.get('hash')
    except Exception as e:
        print('  block hash fetch failed: %s'%str(e)[:80])
print('  fork block=%s hash=%s url=%s'%(fork_blk,(fork_hash or '?')[:18],fork_url))

print('== P1 setup ==')
P=price()
print('oracle price %d ($%.2f/cbBTC)'%(P,P/10**34))
chain_max=(COLL*P//SCALE)*LLTV//WAD   # source order: mulDivDown(price) then wMulDown(lltv)
print('max borrow %d micro ($%.2f) | util %.1f%%'%(chain_max,chain_max/1e6,100*chain_max/SUPPLY))

approve=enc('approve(address,uint256)',['address','uint256'],[MORPHO,MAXAPPROVE])
send(WHALE,USDC,approve)
h_sup,rc_sup=send(WHALE,MORPHO,enc(SIGS['supply'],[TUP,'uint256','uint256','address','bytes'],[tuple(MP),SUPPLY,0,WHALE,b'']))
ev_s=ev_from(rc_sup,'Supply(bytes32,address,address,uint256,uint256)')
assert ev_s,'no Supply event'
sup_as,sup_sh=dwords(ev_s)
# Source-exact (SharesMathLib VIRTUAL_ASSETS=1, VIRTUAL_SHARES=1e6): with
# tss=0, toSharesDown = mulDivDown(assets, 1e6, tsa+1). Generalizes over the
# post-heal dust floor (0/1/2); integer ratio only exists for even denominators.
expected_sh=(sup_as*10**6)//(DUST+1)
assert sup_sh==expected_sh, ('supply shares != virtual-offset formula',sup_sh,expected_sh,DUST)
RATIO=sup_sh//sup_as
print('supply ok: assets=%d shares=%d (formula-exact, dust floor=%d, ratio~%d)'%(sup_as,sup_sh,DUST,RATIO))
bal0=words(call(CBBTC,'0x'+sel('balanceOf(address)')+w_addr(ACCT0))['result'])[0]
if bal0<COLL:
    send(WHALE,CBBTC,enc('transfer(address,uint256)',['address','uint256'],[ACCT0,COLL-bal0]))
    print('  collateral top-up %d (acct0 held %d)'%(COLL-bal0,bal0))
else:
    print('  acct0 wallet already holds collateral %d'%bal0)
send(ACCT0,CBBTC,approve)
h_sc,_=send(ACCT0,MORPHO,enc(SIGS['supplyCollateral'],[TUP,'uint256','address','bytes'],[tuple(MP),COLL,ACCT0,b'']))
print('collateral ok')
b_amt=chain_max
h_b=rc_b=None
for attempt in range(3):
    try:
        h_b,rc_b=send(ACCT0,MORPHO,enc(SIGS['borrow'],[TUP,'uint256','uint256','address','address'],[tuple(MP),b_amt,0,ACCT0,WHALE]))
        break
    except AssertionError:
        print('  borrow %d reverted -> retry one unit less (IMorpho: maxBorrow may need -1)'%b_amt)
        b_amt-=1
assert h_b,'borrow failed after fallback'
chain_max=b_amt
ev_b=ev_from(rc_b,'Borrow(bytes32,address,address,address,uint256,uint256)')
assert ev_b and len(ev_b['topics'])==4
dw_b=dwords(ev_b)
if len(dw_b)==3:
    b_as,b_sh=dw_b[1],dw_b[2]; print('borrow event 3-word shape [caller,assets,shares]')
elif len(dw_b)==2:
    b_as,b_sh=dw_b; print('borrow event 2-word shape [assets,shares]')
else:
    raise AssertionError('borrow data shape %d words: %s'%(len(dw_b),ev_b['data'][:96]))
print('borrow assets=%d shares=%d'%(b_as,b_sh))
# Borrow side started clean at [tba=0,tbs=0]: virtual offsets yield exactly
# 1e6 shares per asset. Supply-side RATIO is dust-diluted (tsa=1 doubles the
# offset denominator -> 5e5). Both measured live on this run.
assert b_as==chain_max and b_sh==b_as*10**6, ('borrow share ratio broken',b_as,b_sh,b_as*10**6)
print('  borrow-side ratio 1e6 exact (clean side) | supply-side %d (dust-diluted)'%RATIO)

print('== P2 real IRM rate (view) ==')
mw1=mkt()
irm_fn='borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint16))'
irm_types=[TUP,MKT6]
irm_vals=[tuple(MP),tuple(mw1[:6])]
rate0=None
r_ir=call(IRM,enc(irm_fn,irm_types,irm_vals))
if 'result' in r_ir and r_ir['result'] not in (None,'0x','0x'+'0'*64):
    rate0=int(r_ir['result'][2:66],16)
    print('borrowRateView %.4f%%/yr | util %.1f%%'%(rate0/WAD*100,100*mw1[2]/mw1[0]))
    assert rate0>0, 'zero rate'
else:
    print('  borrowRateView unavailable (%s) — proceeding; P4 event captures the rate'%json.dumps(r_ir.get('error','empty'))[:120])

print('== P3 control: healthy liquidate must revert ==')
ctrl=enc(SIGS['liquidate'],[TUP,'address','uint256','uint256','bytes'],[tuple(MP),ACCT0,1000,0,b''])
r=call(MORPHO,ctrl,frm=WHALE)
assert 'error' in r, 'control liquidate UNEXPECTEDLY succeeded'
msg=''
try:
    d=r['error'].get('data','')
    if isinstance(d,str) and d.lower().startswith('0x08c379a0') and len(d)>=138:
        body=d[10:]
        off=int(body[0:64],16); ln=int(body[64:128],16)
        if off==32 and 128+2*ln<=len(body):
            msg=bytes.fromhex(body[128:128+2*ln]).decode(errors='replace')
except Exception: pass
if not msg: msg=r['error'].get('message','')
print('control revert: %r'%msg)
assert 'healthy' in str(msg).lower(), 'unexpected revert'

print('== P4 warp +%ds + accrueInterest =='%WARP)
rpcq('evm_increaseTime',[WARP])
h_ac,rc_ac=send(WHALE,MORPHO,enc('accrueInterest((address,address,address,address,uint256))',[TUP],[tuple(MP)]),gas=500_000)
mw2=mkt()
interest=mw2[2]-mw1[2]
print('tba %d -> %d | interest %d micro ($%.6f)'%(mw1[2],mw2[2],interest,interest/1e6))
assert interest>0, 'no interest'
ev_ac=ev_from(rc_ac,'AccrueInterest(bytes32,uint256,uint256,uint256)')
assert ev_ac, 'no AccrueInterest event'
rate_used=dwords(ev_ac)[0]
print('prevBorrowRate %.4f%%/yr | event interest %d'%(rate_used/WAD*100,dwords(ev_ac)[1]))
assert dwords(ev_ac)[1]==interest, 'event interest != state delta'

print('== P5 source-math unhealthy proof ==')
pw=pos_of(ACCT0)
coll_sh,borr_sh=pw[2],pw[1]
tba,tbs=mw2[2],mw2[3]
borrowed=-(-borr_sh*tba//tbs)
max_b=(coll_sh*P//SCALE)*LLTV//WAD
print('coll=%d borr_sh=%d | borrowed %d | maxBorrow %d | crossed by %d'%(coll_sh,borr_sh,borrowed,max_b,borrowed-max_b))
assert max_b<borrowed, 'still healthy'
assert borr_sh==tbs, 'single-borrower broken'

print('== P6 liquidator = whale (fork upstream archive-gated; fresh accounts 403) ==')

print('== P7 full-close liquidation by whale ==')
h_l,rc_l=send(WHALE,MORPHO,enc(SIGS['liquidate'],[TUP,'address','uint256','uint256','bytes'],[tuple(MP),ACCT0,0,borr_sh,b'']))
ev_l=ev_from(rc_l,'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)')
assert ev_l and len(ev_l['topics'])==4
borrower='0x'+ev_l['topics'][3][-40:]
assert borrower.lower()==ACCT0.lower()
dw=dwords(ev_l)
if len(dw)==5:
    repaid_assets,repaid_shares,seized,bad_debt,bad_debt_shares=dw
elif len(dw)==6:
    repaid_assets,repaid_shares,seized,bad_debt,bad_debt_shares=dw[1:]
    print('  liquidate event 6-word shape')
else:
    raise AssertionError('liquidate data shape %d words'%len(dw))
print('repaidAssets=%d repaidShares=%d seized=%d badDebt=%d/%d'%(repaid_assets,repaid_shares,seized,bad_debt,bad_debt_shares))
assert repaid_shares==borr_sh, 'not full close'
assert bad_debt==0 and bad_debt_shares==0, 'bad debt present'
assert 0<seized<coll_sh
assert repaid_assets>=tba and repaid_assets-tba<50_000, 'repaid drift %d'%(repaid_assets-tba)
print('repaid drift vs P4 accrue: %d micro (intra-run seconds)'%(repaid_assets-tba))
def wmul_up(x,y): return -((-x*y)//WAD)
cands=[]; combo_labels=[]
for bl,base in (('ev-repaid',repaid_assets),('recalc',repaid_shares*tba//tbs)):
    for s2,sl in ((base*MAXLIF//WAD,'lif-f'),(wmul_up(base,MAXLIF),'lif-u')):
        for s3,pl in ((s2*SCALE//P,'px-f'),(-((-s2*SCALE)//P),'px-u')):
            cands.append(s3); combo_labels.append(bl+'/'+sl+'/'+pl)
lif_raw=WAD*WAD//(WAD-wmul(CURSOR,WAD-LLTV))
print('LIF cursor-derived %.4f -> effective fixed 1.15 (vanilla incentive cap)'%(lif_raw/WAD))
assert lif_raw>MAXLIF
assert seized in cands, 'seized %d not source-exact %s'%(seized,cands)
matched=combo_labels[cands.index(seized)]
print('SEIZED SOURCE-EXACT via combo %s'%matched)
pw2=pos_of(ACCT0)
assert pw2[1]==0 and pw2[2]==coll_sh-seized
print('borrower cleared | collateral remainder %d'%(pw2[2]))
seized_usd=seized*P/SCALE/1e6
print('seized $%.2f vs repaid $%.2f -> realized %.4fx'%(seized_usd,repaid_assets/1e6,seized_usd/(repaid_assets/1e6)))

print('== P8 unwind to zero ==')
h_wc,_=send(ACCT0,MORPHO,enc(SIGS['withdrawCollateral'],[TUP,'uint256','address','address'],[tuple(MP),pw2[2],ACCT0,ACCT0]))
tsa_fin=mkt()[0]; tss_wh=pos_of(WHALE)[0]
h_wd=None
if tsa_fin>0 and tss_wh>0:
    wdata=enc(SIGS['withdraw'],[TUP,'uint256','uint256','address','address'],[tuple(MP),tsa_fin,0,WHALE,WHALE])
    rr=call(MORPHO,wdata,frm=WHALE)
    if 'result' in rr:
        h_wd,_=send(WHALE,MORPHO,wdata)
        print('final withdraw by assets=%d'%tsa_fin)
    else:
        print('by-assets overshoot -> by-shares exit %d'%tss_wh)
        h_wd,_=send(WHALE,MORPHO,enc(SIGS['withdraw'],[TUP,'uint256','uint256','address','address'],[tuple(MP),0,tss_wh,WHALE,WHALE]))
mw3=mkt()
print('final tsa=%d tss=%d tba=%d tbs=%d'%tuple(mw3[:4]))
assert mw3[2]==0 and mw3[3]==0 and mw3[1]==0 and mw3[0]<=DUST+1, ('unwind floor violated', mw3[:4])
FINAL_FLOOR=mw3[0]
print('unwind complete: debt 0 shares 0, tsa floor %d micro (virtual-offset residual)'%FINAL_FLOOR)

json.dump({
 'experiment':'XI-O9 production-fork liquidation via real interest',
 'fork_pin':{'block':fork_blk,'hash':fork_hash,'url':fork_url},'market_id':MID,'oracle':CAND,'roles':'whale=supplier+liquidator, acct0=borrower',
 'abi_note':'Base singleton dual-input ABI (assets+shares); selectors pinned to live roundtrip txs',
 'first_supply_share_ratio':RATIO,'first_borrow_share_ratio':10**6,
 'dust_floor_micro':DUST,'final_floor_micro':FINAL_FLOOR,
 'dust_note':'SharesMathLib virtual offsets (1,1e6): full-shares exit leaves tsa=N+1/tss=0 (floor grows +1 micro per full-share exit); 1 micro unclaimable; full-assets exit overshoots at small scale. No storage edits used.',
 'setup':{'supply_usd_micro':SUPPLY,'collateral_cbbtc_8dec':COLL,'max_borrow_micro':chain_max,
          'utilization_pct':round(100*chain_max/SUPPLY,2)},
 'rate':{'at_t0_per_yr_wad':rate0,'used_at_accrual_wad':rate_used,'warp_s':WARP},
 'interest_accrued_micro':interest,
 'health_cross':{'borrowed_micro':borrowed,'max_borrow_micro':max_b,'crossed_by_micro':borrowed-max_b},
 'control':{'healthy_revert_msg':msg},
 'liquidation':{'tx':h_l,'liquidator':WHALE,'repaid_assets_micro':repaid_assets,
                'repaid_shares':repaid_shares,'seized_cbbtc_8dec':seized,
                'bad_debt':bad_debt,'bad_debt_shares':bad_debt_shares,
                'seized_candidates':cands,'seized_rounding_combo':matched,
                'repaid_drift_micro':repaid_assets-tba,
                'lif_raw_wad':lif_raw,'lif_capped':True,'lif_effective_wad':MAXLIF,
                'seized_usd':round(seized_usd,4),
                'lif_realized':round(seized_usd/(repaid_assets/1e6),6)},
 'final_state':{'tsa':mw3[0],'tss':mw3[1],'tba':mw3[2],'tbs':mw3[3]},
 'txs':{'supply':h_sup,'supplyCollateral':h_sc,'borrow':h_b,'accrueInterest':h_ac,
        'liquidate':h_l,'withdrawCollateral':h_wc,'withdraw':h_wd},
},open('exp11_liquidation.json','w'),indent=1)
print('SAVED exp11_liquidation.json')
print('XI-O9 COMPLETE')
