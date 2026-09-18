import numpy as np
def runs_of(img, thresh=40, gapmin=2):
    a = img[..., 3] > 100
    lum = img[..., :3].astype(int).mean(-1)
    bgop = a.mean() > 0.6
    content = a & (np.abs(lum - np.median(lum[a])) > thresh) if bgop else a
    cols = content.any(0); runs = []; x = 0; W = len(cols)
    while x < W:
        if cols[x]:
            s = x
            while x < W and (cols[x] or (x + gapmin < W and cols[x:x + gapmin + 1].any() and runs is not None and False)): x += 1
            runs.append([s, x])
        else: x += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= gapmin: merged[-1][1] = r[1]
        else: merged.append(r)
    out = []
    for s, e in merged:
        rr = np.nonzero(content[:, s:e].any(1))[0]; out.append((s, e, int(rr.min()), int(rr.max())))
    return out, content, bgop
