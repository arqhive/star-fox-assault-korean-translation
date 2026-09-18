import sys
from gcfs import read_fst
iso, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv)>3 else 256
f, *_ , e = read_fst(iso)
for p,o,s in e:
    if p == name:
        f.seek(o); sys.stdout.buffer.write(f.read(min(n,s) if n>0 else s))
