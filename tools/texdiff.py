import json, hashlib
from gcfs import read_fst
import paths
from nut import parse_nutc
def scan(iso):
    f,*_,e = read_fst(iso); res = {}
    for p,o,s in e:
        if s < 32 or p.startswith(('/bgm','/se')) or p.endswith('.sfd'): continue
        f.seek(o); d = f.read(s); k = 0; i = -1
        while True:
            i = d.find(b'NUTC', i+1)
            if i < 0: break
            try: ts = parse_nutc(d[i:])
            except Exception: continue
            for t in ts:
                blob = d[i+t['data_off']:i+t['data_off']+t['dsz']] + d[i+t['pal_off']:i+t['pal_off']+t['pal']]
                gid = d[i+t['off']+0x48:i+t['off']+0x4C].hex()
                res.setdefault((p, gid, t['w'], t['h']), []).append((hashlib.md5(blob).hexdigest(), t['fmt'], k, t['i'], i))
            k += 1
    return res
jp = scan(paths.jp_iso()); us = scan(paths.us_iso())
diff = []; missing = []
for key, vs in jp.items():
    if key not in us:
        missing.append(key); continue
    uh = set(x[0] for x in us[key])
    for v in vs:
        if v[0] not in uh: diff.append((key, v))
print('jp keys', len(jp), 'us keys', len(us), 'diff', len(diff), 'jp-only keys', len(missing))
import collections
print(collections.Counter(k[0] for k,_ in diff))
print(collections.Counter(k[0] for k in missing).most_common(12))
json.dump([[list(k), list(v)] for k,v in diff], open('texdiff.json','w'))
json.dump([list(k) for k in missing], open('texmissing.json','w'))
