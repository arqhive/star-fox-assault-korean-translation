"""배포용 파일 단위 패처 생성기 (게임큐브, disc-file-patcher 스킬의 어설트판).

원본 일본판 ISO와 한글 빌드 ISO를 FST 기준으로 비교해, 바뀐 파일과 DOL마다 xdelta 차분을 만든다.
이 게임은 한글 폰트를 붙여 DOL이 커지므로 빌드(kolib.rebuild_iso)가 디스크를 다시 채운다.
  헤더 → 애플로더 → DOL(원래 자리, 커짐) → FST(DOL 뒤로 이동) → 파일(원래 순서, 4바이트 간격)
DOL을 FST 뒤로 보내면 Wii U VC 주입(UWUVCI)에서 검은 화면이 나오므로 이 순서를 지켜야 한다.
사용자용 patch.ps1 은 같은 규칙으로 디스크를 다시 채우므로, 정본 ISO에 적용하면 빌드와 바이트까지 같은
ISO가 나온다. 생성기는 패처가 계산할 배치가 빌드 ISO와 같은지 먼저 확인한다.

사용:
  python tools/make_patcher.py --orig "Star Fox - Assault (Japan).iso" --build work/StarFoxAssault_KO.iso \\
      --out release/StarFoxAssault-KO-v1.2f --version 1.2f --wit <wit-cygwin64 폴더> --xdelta work/xdelta3.exe \\
      --readme release/README_한국어.txt
"""
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gcfs import read_fst  # noqa: E402

DISC_SIZE = 1459978240
ALIGN = 4
WIT_FILES = ('bin/wit.exe', 'bin/cygwin1.dll', 'bin/cygz.dll', 'bin/cygcrypto-1.1.dll', 'bin/cygncursesw-10.dll')


def md5(b):
    return hashlib.md5(b).hexdigest()


def read_at(path, off, size):
    with open(path, 'rb') as f:
        f.seek(off)
        return f.read(size)


def dol_size(head):
    """DOL 헤더(0x100)의 섹션 18개 중 파일 끝이 가장 먼 곳 = DOL 크기 (build.py 와 같은 계산)"""
    offs = struct.unpack('>18I', head[0:0x48]); sizes = struct.unpack('>18I', head[0x90:0xD8])
    return max(o + s for o, s in zip(offs, sizes))


def disc(path):
    f, gid, name, dol, ents = read_fst(path)
    f.close()
    hdr = read_at(path, 0, 0x440)
    fst_off, fst_size = struct.unpack('>II', hdr[0x424:0x42C])
    dol_bytes = read_at(path, dol, dol_size(read_at(path, dol, 0x100)))
    return dict(path=path, gid=gid, hdr=hdr, dol=dol, dol_bytes=dol_bytes, fst_off=fst_off, fst_size=fst_size,
                ents=ents, by_path={p: (o, s) for p, o, s in ents})


def plan(orig, new_sizes, new_dol_len):
    """patch.ps1·kolib.rebuild_iso 와 같은 배치: (시작 위치, {경로: 새 위치}, 새 FST 위치)"""
    order = sorted(range(len(orig['ents'])), key=lambda i: (orig['ents'][i][1], i))   # 위치순, 같으면 FST 순
    al = lambda v: (v + ALIGN - 1) & ~(ALIGN - 1)
    total = 0
    for i in order:
        total = al(total) + new_sizes[orig['ents'][i][0]]
    first = orig['ents'][order[0]][1]
    start = min(first, (DISC_SIZE - total) & ~(ALIGN - 1))
    new_fst = (orig['dol'] + new_dol_len + 0x7FFF) & ~0x7FFF
    assert start >= new_fst + orig['fst_size'], '디스크 공간 부족'
    pos = {}; cur = start
    for i in order:
        p = orig['ents'][i][0]
        cur = al(cur); pos[p] = cur; cur += new_sizes[p]
    return start, pos, new_fst


def main():
    ap = argparse.ArgumentParser()
    for k in ('orig', 'build', 'out', 'version', 'wit', 'xdelta'):
        ap.add_argument('--' + k, required=True)
    ap.add_argument('--title', default='스타폭스 어설트')
    ap.add_argument('--result', default='Star Fox Assault (Korean)')
    ap.add_argument('--readme')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    o, b = disc(a.orig), disc(a.build)
    out = Path(a.out)
    xdelta = str(Path(a.xdelta).resolve())   # 상대경로 그대로면 Windows에서 실행 파일을 못 찾음

    assert os.path.getsize(a.orig) == DISC_SIZE and os.path.getsize(a.build) == DISC_SIZE
    assert set(o['by_path']) == set(b['by_path']), '파일 목록이 다름(추가·삭제 파일은 지원 안 함)'
    assert len({(x, y) for _, x, y in o['ents']}) == len(o['ents']), '같은 (위치, 크기) 파일이 있음'
    diff = [i for i in range(0x440) if o['hdr'][i] != b['hdr'][i]]
    assert all(0x424 <= i < 0x428 for i in diff), f'FST 위치 밖의 헤더가 다름: {[hex(i) for i in diff[:8]]}'
    assert o['dol'] == b['dol'], 'DOL 위치가 다름'

    changed = [p for p, _, _ in o['ents'] if read_at(a.orig, *o['by_path'][p]) != read_at(a.build, *b['by_path'][p])]
    sizes = {p: b['by_path'][p][1] for p, _, _ in o['ents']}
    start, pos, new_fst = plan(o, sizes, len(b['dol_bytes']))
    # 패처가 계산할 배치가 빌드 ISO와 같은지
    assert new_fst == b['fst_off'], 'FST 위치 규칙이 다름'
    bad = [p for p in pos if pos[p] != b['by_path'][p][0]]
    assert not bad, f'파일 배치 규칙이 다름: {bad[:3]}'
    # 시작 위치 앞은 원본 그대로여야 한다(DOL·FST·헤더 0x424 만 다름)
    keep = [(0, 0x424), (0x428, o['dol']), (o['dol'] + len(b['dol_bytes']), new_fst), (new_fst + o['fst_size'], start)]
    for x, y in keep:
        if x < y:
            assert read_at(a.orig, x, y - x) == read_at(a.build, x, y - x), f'시작 위치 앞 영역이 다름: {x:#x}~{y:#x}'

    if out.exists():
        shutil.rmtree(out)
    (out / 'data').mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp())
    lines = []
    items = [('dol', 'sys/main.dol', o['dol_bytes'], b['dol_bytes'])]
    items += [('raw', p, read_at(a.orig, *o['by_path'][p]), read_at(a.build, *b['by_path'][p])) for p in changed]
    for i, (mode, p, A, B) in enumerate(items):
        (tmp / 'a').write_bytes(A); (tmp / 'b').write_bytes(B)
        patch = f'{i:03d}.xdelta'
        # -A= : 헤더에 파일 경로(PC 사용자 이름 포함)를 적지 않음
        subprocess.run([xdelta, '-e', '-f', '-9', '-S', 'djw', '-A=', '-s', str(tmp / 'a'), str(tmp / 'b'),
                        str(out / 'data' / patch)], check=True)
        lines.append('\t'.join((mode, patch, p, md5(A), md5(B))))
    shutil.rmtree(tmp)
    (out / 'data' / 'manifest.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    fst = read_at(a.orig, o['fst_off'], o['fst_size'])
    h = hashlib.md5()
    with open(a.build, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 24), b''):
            h.update(chunk)
    (out / 'data' / 'config.txt').write_text(
        f'id={o["gid"]}\nrev={o["hdr"][7]}\ntitle={a.title}\nversion={a.version}\nresult={a.result}\n'
        f'disc_size={DISC_SIZE}\nfst_md5={md5(fst)}\nresult_md5={h.hexdigest()}\n', encoding='utf-8')

    tpl = HERE.parent / 'patcher'
    shutil.copy2(tpl / 'patch.ps1', out / 'patch.ps1')
    shutil.copy2(tpl / '패치하기.bat', out / '패치하기.bat')
    if a.readme:
        shutil.copy2(a.readme, out / 'README.txt')
    (out / 'bin').mkdir()
    for f in WIT_FILES:
        shutil.copy2(Path(a.wit) / f, out / 'bin' / Path(f).name)
    shutil.copy2(Path(a.wit) / 'gpl-2.0.txt', out / 'bin' / 'wit-gpl-2.0.txt')
    shutil.copy2(xdelta, out / 'bin' / 'xdelta3.exe')

    zpath = out.parent / (out.name + '.zip')   # with_suffix 는 'v1.2f' 의 '.2f' 를 확장자로 봄
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, _, fs in os.walk(out):
            for f in sorted(fs):
                q = Path(dp) / f
                z.write(q, Path(out.name) / q.relative_to(out))
    size = sum(f.stat().st_size for f in (out / 'data').iterdir())
    print(f'DOL + 파일 {len(changed)}개, 차분 합계 {size / 1e6:.2f} MB, zip {zpath.stat().st_size / 1e6:.2f} MB')
    print(f'배치: 시작 {start:#x}, FST {new_fst:#x} (빌드와 일치)')
    print(f'패처: {out}')


if __name__ == '__main__':
    main()
