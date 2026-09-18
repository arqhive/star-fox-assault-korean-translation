import struct, sys, os
def read_fst(path):
    f = open(path, 'rb')
    f.seek(0); hdr = f.read(0x440)
    gid = hdr[:6].decode(); name = hdr[0x20:0x60].split(b'\0')[0].decode('shift_jis','replace')
    dol, fst_off, fst_sz = struct.unpack('>III', hdr[0x420:0x42C])
    f.seek(fst_off); fst = f.read(fst_sz)
    n = struct.unpack('>I', fst[8:12])[0]
    strtab = fst[n*12:]
    entries = []
    def nm(o): return strtab[o:strtab.index(b'\0', o)].decode('shift_jis','replace')
    stack = [(n, '')]
    for i in range(1, n):
        while stack and i >= stack[-1][0]: stack.pop()
        t, off, a, b = fst[i*12], struct.unpack('>I', b'\0'+fst[i*12+1:i*12+4])[0], *struct.unpack('>II', fst[i*12+4:i*12+12])
        p = stack[-1][1] + '/' + nm(off)
        if t: stack.append((b, p))
        else: entries.append((p, a, b))
    return f, gid, name, dol, entries
if __name__ == '__main__':
    f, gid, name, dol, e = read_fst(sys.argv[1])
    print(gid, name, 'dol@%X' % dol, len(e), 'files')
    for p, o, s in e: print('%10d %08X %s' % (s, o, p))
