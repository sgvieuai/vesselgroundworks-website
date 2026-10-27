"""Job photo tools for the Vessel Landscape site. Needs ffmpeg (with zscale), Pillow and numpy.

  python3 _src/photos.py sheet  VIDEO... --out sheet.jpg           # frame strips to review clips (HDR handled)
  python3 _src/photos.py still  VIDEO START END OUT.png            # sharpest frame between START and END seconds
  python3 _src/photos.py heic   IN.HEIC OUT.png                    # iPhone photo -> PNG (no libheif plugin needed)
  python3 _src/photos.py export SRC NAME --crop x0,y0,x1,y1 [--blur x0,y0,x1,y1 ...] [--color 1.06]
                                                                   # crop, grade, blur, write images/NAME.webp + -sm.webp
  python3 _src/photos.py regrade NAME...                           # light color pass on a photo already on the site

Rules (see CLAUDE.md): only Sergio's own best shots, crop people/faces out, blur house numbers, street signs and
plates, keep the grade light so it looks real, review every photo before it goes live.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(SITE, 'images')
FULL_LONG, SM_LONG = 1300, 720

# iPhone video is HDR (HLG / BT.2020). Without tone mapping, stills come out gray and washed out.
TONEMAP = ('zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,'
           'zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=pc,format=rgb24')


def is_hdr(video):
    trc = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                          '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip().strip(',')
    return trc in ('arib-std-b67', 'smpte2084')


def duration(video):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                                capture_output=True, text=True).stdout.strip())


def sharpness(path):
    g = np.asarray(Image.open(path).convert('L'), dtype=np.float32)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def cmd_sheet(videos, out):
    strips = []
    for v in videos:
        tm = (TONEMAP + ',') if is_hdr(v) else ''
        tmp = tempfile.mktemp(suffix='.jpg')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf',
                        f'{tm}fps=4/{duration(v)},scale=-2:300,tile=4x1:padding=4:color=white', '-frames:v', '1', tmp], check=True)
        strips.append((os.path.basename(v), Image.open(tmp).convert('RGB')))
    from PIL import ImageDraw
    W = max(s.width for _, s in strips)
    S = Image.new('RGB', (W, sum(s.height + 22 for _, s in strips)), 'white')
    d, y = ImageDraw.Draw(S), 0
    for name, s in strips:
        d.text((4, y + 5), name, fill='black'); S.paste(s, (0, y + 20)); y += s.height + 22
    S.thumbnail((1800, 4000)); S.save(out, quality=82); print(out, S.size)


def cmd_still(video, start, end, out):
    tm = (TONEMAP + ',') if is_hdr(video) else ''
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-to', str(end), '-i', video, '-vf', f'{tm}fps=15',
                        os.path.join(tmp, '%03d.png')], check=True)
        frames = [os.path.join(tmp, f) for f in sorted(os.listdir(tmp))]
        best = max(frames, key=sharpness)
        shutil.copy(best, out)
    print(out, Image.open(out).size)


def cmd_heic(src, dst):
    """Decode the primary image of an iPhone HEIC: parse item boxes, decode HEVC tiles with ffmpeg, stitch, rotate."""
    buf = open(src, 'rb').read()

    def boxes(s, e):
        p = s
        while p + 8 <= e:
            size, typ = struct.unpack('>I4s', buf[p:p + 8]); hdr = 8
            if size == 1:
                size = struct.unpack('>Q', buf[p + 8:p + 16])[0]; hdr = 16
            elif size == 0:
                size = e - p
            yield typ.decode('latin1'), p + hdr, p + size
            p += size

    def uint(p, n):
        return (int.from_bytes(buf[p:p + n], 'big') if n else 0), p + n

    ms, me = next((s + 4, e) for t, s, e in boxes(0, len(buf)) if t == 'meta')
    items, iloc, refs, props, ipma, idat, primary = {}, {}, {}, [], {}, None, None
    for t, s, e in boxes(ms, me):
        if t == 'pitm':
            primary = uint(s + 4, 2 if buf[s] == 0 else 4)[0]
        elif t == 'iinf':
            for it, a, _ in boxes(s + 4 + (2 if buf[s] == 0 else 4), e):
                if it == 'infe' and buf[a] >= 2:
                    q = a + 4; n = 2 if buf[a] == 2 else 4
                    iid, q = uint(q, n); items[iid] = buf[q + 2:q + 6].decode('latin1')
        elif t == 'iloc':
            v = buf[s]; p = s + 4
            osz, lsz, bsz = buf[p] >> 4, buf[p] & 15, buf[p + 1] >> 4
            isz = (buf[p + 1] & 15) if v in (1, 2) else 0; p += 2
            cnt, p = uint(p, 2 if v < 2 else 4)
            for _ in range(cnt):
                iid, p = uint(p, 2 if v < 2 else 4)
                method = 0
                if v in (1, 2):
                    method = buf[p + 1] & 15; p += 2
                p += 2
                base, p = uint(p, bsz); n, p = uint(p, 2); ext = []
                for _ in range(n):
                    if isz:
                        _, p = uint(p, isz)
                    eo, p = uint(p, osz); el, p = uint(p, lsz); ext.append((base + eo, el))
                iloc[iid] = (method, ext)
        elif t == 'iref':
            n = 2 if buf[s] == 0 else 4
            for rt, a, _ in boxes(s + 4, e):
                frm, q = uint(a, n); k, q = uint(q, 2); to = []
                for _ in range(k):
                    x, q = uint(q, n); to.append(x)
                refs.setdefault(rt, {})[frm] = to
        elif t == 'iprp':
            for pt, a, b in boxes(s, e):
                if pt == 'ipco':
                    props = list(boxes(a, b))
                elif pt == 'ipma':
                    v, fl = buf[a], int.from_bytes(buf[a + 1:a + 4], 'big'); q = a + 4
                    n, q = uint(q, 4)
                    for _ in range(n):
                        iid, q = uint(q, 2 if v < 1 else 4); k = buf[q]; q += 1; lst = []
                        for _ in range(k):
                            if fl & 1:
                                lst.append(struct.unpack('>H', buf[q:q + 2])[0] & 0x7FFF); q += 2
                            else:
                                lst.append(buf[q] & 0x7F); q += 1
                        ipma[iid] = lst
        elif t == 'idat':
            idat = (s, e)

    def data(iid):
        m, ext = iloc[iid]; base = idat[0] if m == 1 else 0
        return b''.join(buf[base + o:base + o + l] for o, l in ext)

    def iprops(iid):
        return [props[i - 1] for i in ipma.get(iid, []) if i > 0]

    if items[primary] == 'grid':
        g = data(primary); big = g[1] & 1; rows, cols = g[2] + 1, g[3] + 1
        out_w, out_h = struct.unpack('>II' if big else '>HH', g[4:4 + (8 if big else 4)]); tiles = refs['dimg'][primary]
    else:
        rows = cols = 1; tiles = [primary]; out_w = out_h = None
    hs = next(a for t, a, _ in iprops(tiles[0]) if t == 'hvcC')
    nal_len = (buf[hs + 21] & 3) + 1; q = hs + 23; params = b''
    for _ in range(buf[hs + 22]):
        q += 1; n = struct.unpack('>H', buf[q:q + 2])[0]; q += 2
        for _ in range(n):
            ln = struct.unpack('>H', buf[q:q + 2])[0]; q += 2; params += b'\x00\x00\x00\x01' + buf[q:q + ln]; q += ln
    stream = b''
    for tid in tiles:
        d = data(tid); p = 0; stream += params
        while p < len(d):
            ln = int.from_bytes(d[p:p + nal_len], 'big'); p += nal_len; stream += b'\x00\x00\x00\x01' + d[p:p + ln]; p += ln
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, 't.hevc'), 'wb').write(stream)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'hevc', '-i', os.path.join(tmp, 't.hevc'), '-fps_mode', 'passthrough',
                        os.path.join(tmp, 't%04d.png')], check=True)
        fr = sorted(f for f in os.listdir(tmp) if f.endswith('.png'))
        tw, th = Image.open(os.path.join(tmp, fr[0])).size
        canvas = Image.new('RGB', (cols * tw, rows * th))
        for i, f in enumerate(fr[:rows * cols]):
            canvas.paste(Image.open(os.path.join(tmp, f)).convert('RGB'), ((i % cols) * tw, (i // cols) * th))
    if out_w:
        canvas = canvas.crop((0, 0, out_w, out_h))
    for t, a, _ in iprops(primary):
        if t == 'irot' and buf[a] & 3:
            canvas = canvas.rotate((buf[a] & 3) * 90, expand=True)
        elif t == 'imir':
            canvas = canvas.transpose(Image.FLIP_TOP_BOTTOM if (buf[a] & 1) == 0 else Image.FLIP_LEFT_RIGHT)
    canvas.save(dst); print(dst, canvas.size)


def grade(im, color=1.06):
    """The site's light grade: levels, gentle lift for dark shots, warm up cold ones, a touch of contrast and color."""
    im = ImageOps.autocontrast(im, cutoff=0.5, preserve_tone=True)
    m = ImageStat.Stat(im.convert('L')).mean[0]
    if m < 112:
        g = 0.85 if m < 95 else 0.92
        im = im.point(lambda v: round(255 * (v / 255) ** g))
    r, _, b = ImageStat.Stat(im).mean
    if r - b < -10:
        R, G, B = im.split()
        im = Image.merge('RGB', (R.point(lambda v: min(255, round(v * 1.03))), G, B.point(lambda v: round(v * 0.97))))
    if color is None:
        sat = ImageStat.Stat(im.convert('HSV')).mean[1]
        color = 1.0 if sat > 115 else (1.12 if sat < 60 else 1.06)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Color(im).enhance(color)
    return im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=40, threshold=3))


def fit(im, long_side):
    w, h = im.size; s = min(1.0, long_side / max(w, h))
    return im.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else im


def cmd_export(src, name, crop, blurs, color):
    im = Image.open(src).convert('RGB')
    for box in blurs:  # source pixels, before cropping
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
    w, h = im.size; x0, y0, x1, y1 = crop
    im = grade(im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))), color)
    full, sm = fit(im, FULL_LONG), fit(im, SM_LONG)
    full.save(os.path.join(IMG, name + '.webp'), 'WEBP', quality=75, method=6)   # WebP from PIL carries no EXIF/GPS
    sm.save(os.path.join(IMG, name + '-sm.webp'), 'WEBP', quality=80, method=6)
    print(name, full.size, os.path.getsize(os.path.join(IMG, name + '.webp')) // 1024, 'KB')


def cmd_regrade(names):
    for n in names:
        full_p, sm_p = os.path.join(IMG, n + '.webp'), os.path.join(IMG, n + '-sm.webp')
        sm_size = Image.open(sm_p).size
        out = grade(Image.open(full_p).convert('RGB'), None)
        out.save(full_p, 'WEBP', quality=80, method=6); out.resize(sm_size, Image.LANCZOS).save(sm_p, 'WEBP', quality=80, method=6)
        print('regraded', n)


def box(s):
    return tuple(float(v) if '.' in v else int(v) for v in s.split(','))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('sheet'); a.add_argument('videos', nargs='+'); a.add_argument('--out', required=True)
    a = sp.add_parser('still'); a.add_argument('video'); a.add_argument('start', type=float); a.add_argument('end', type=float); a.add_argument('out')
    a = sp.add_parser('heic'); a.add_argument('src'); a.add_argument('dst')
    a = sp.add_parser('export'); a.add_argument('src'); a.add_argument('name')
    a.add_argument('--crop', type=box, default=(0.0, 0.0, 1.0, 1.0)); a.add_argument('--blur', type=box, action='append', default=[])
    a.add_argument('--color', type=float, default=1.06)
    a = sp.add_parser('regrade'); a.add_argument('names', nargs='+')
    args = ap.parse_args()
    if args.cmd == 'sheet': cmd_sheet(args.videos, args.out)
    elif args.cmd == 'still': cmd_still(args.video, args.start, args.end, args.out)
    elif args.cmd == 'heic': cmd_heic(args.src, args.dst)
    elif args.cmd == 'export': cmd_export(args.src, args.name, args.crop, args.blur, args.color)
    elif args.cmd == 'regrade': cmd_regrade(args.names)
