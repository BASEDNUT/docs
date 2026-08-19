import re, os, urllib.request, time

base = 'https://docs.basednut.com'
txt = urllib.request.urlopen(base + '/llms.txt', timeout=30).read().decode()
urls = re.findall(r'\((https://docs\.basednut\.com/[^)]+\.md)\)', txt)
print(f'pages found: {len(urls)}')

for u in urls:
    path = u.replace(base + '/', '')
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        content = urllib.request.urlopen(req, timeout=30).read().decode()
        with open(path, 'w') as f:
            f.write(content)
        print(f'OK {path} ({len(content)} bytes)')
    except Exception as e:
        print(f'FAIL {path}: {e}')
    time.sleep(0.5)
