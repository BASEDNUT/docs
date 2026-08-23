import os, re, difflib, sys

SRC, DST = 'based-nut', 'v2'
patterns = {
    'credit protocol': r'credit\s+protocol',
    'inscription': r'inscription', 'inference gateway': r'inference\s+gateway', 'discourse': r'discourse',
    'treasury': r'treasury', 'clob': r'\bclob\b', 'prd/ard': r'\bprd\b|\bard-\d',
    'pns/cns': r'\bpns\b|\bcns\b', 'cron/supervisor': r'\bcron\b|supervisord', 'akash': r'akash',
    'self-heal/bootstrap': r'self-?heal|bootstrap', 'kill switch': r'kill\s+switch',
    'dry-run': r'dry.?run', 'operator approval': r'operator\s+approval', 'hot wallet': r'hot\s+wallet',
    'cdp/vault': r'cdp\s+(managed\s+)?wallet|coinbase\s+developer', 'profit pipeline': r'profit\s+sweep|profit\s+vault', 'escrow/acp job': r'(?<!non-)escrow|job\s*70\d\d\d',
    'ports': r':\s*(9000|8017|8090)\b', 'cost': r'\$0/day|\$0\.\d\d.\d\d/day',
    'internal profiles': r'nut-(coordinator|architect|engineer|analyst|validator|executor|editor|operator|librarian)|nine specialist',
    'phasing': r'\bp2\b|\bp3\b|\bp4\b|phasing',
}

def scan(text, label, src=None):
    hits = []
    for name, pat in patterns.items():
        for m in re.finditer(pat, text, re.I):
            hits.append((label, name, text[max(0,m.start()-40):m.end()+40].replace('\n',' ')))
    return hits

viol = []
for root, dirs, files in os.walk(DST):
    for fn in sorted(files):
        if not fn.endswith('.md'): continue
        fp = os.path.join(root, fn)
        v2t = open(fp, encoding='utf-8').read()
        src = os.path.join(SRC, os.path.relpath(fp, DST))
        if os.path.exists(src):
            v1t = open(src, encoding='utf-8').read()
            # strip llms header from v1 for fair diff
            v1l = v1t.split('\n')
            if v1l and v1l[0].startswith('> For the complete'): v1l = v1l[1:]
            if v1l and not v1l[0].strip(): v1l = v1l[1:]
            v1t = '\n'.join(v1l)
            sm = difflib.SequenceMatcher(None, v1t, v2t)
            newtext = ''.join(v2t[i1:i2] for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag in ('insert','replace'))
            viol += scan(newtext, fp + ' [NEW LINES ONLY]')
        else:
            viol += scan(v2t, fp + ' [ENTIRELY NEW FILE]')

if viol:
    print('LEAK GATE FAILED — new content contains flagged terms:')
    for f,p,c in viol: print(f'  {f} [{p}] ...{c}...')
    sys.exit(1)
print('LEAK GATE CLEAN — 0 violations in all new content')
print('v2 pages:', sum(len(f) for _,_,f in os.walk(DST)), '| v1 carried verbatim + corrections + smart-agents fulfilled + index')
