"""Procedural 16x16 block textures."""
import math
import random
from pix import *

SLATE = [rgb('#2f2e44'), rgb('#3b3a54'), rgb('#47466a'), rgb('#56547c')]


def noise_fill(cv, colors, seed, scale=3.0):
    for y in range(cv.h):
        for x in range(cv.w):
            n = fbm(x / scale, y / scale, seed, 3, tile=int(cv.w / scale) if cv.w / scale == int(cv.w / scale) else None)
            cv.put(x, y, colors[min(len(colors) - 1, int(n * len(colors)))])


def riftstone(seed=1):
    cv = Canvas()
    noise_fill(cv, SLATE, seed, 4.0)
    r = random.Random(seed)
    for _ in range(5):
        x, y = r.randrange(16), r.randrange(16)
        cv.put(x, y, rgb('#8f7cff') if r.random() < 0.6 else rgb('#7ff4ff'))
    for _ in range(2):  # violet veins
        x, y = r.randrange(16), r.randrange(16)
        for _k in range(5):
            cv.put(x, y, rgb('#5e46b0'))
            x = (x + r.choice([-1, 0, 1])) % 16
            y = (y + 1) % 16
    return cv


def bricks(base_cols, mortar, seed, rows=4, glow=None, glow_n=0, crackcol=None):
    cv = Canvas()
    r = random.Random(seed)
    bh = 16 // rows
    for row in range(rows):
        off = (row % 2) * 4
        for x in range(16):
            for y in range(row * bh, (row + 1) * bh):
                xx = (x + off) % 16
                brick = ((x + off) // 8) % 2
                lx = xx % 8
                ly = y - row * bh
                col = base_cols[(brick + row) % len(base_cols)]
                if ly == bh - 1 or lx == 7:
                    col = mortar
                else:
                    f = (0.1 if ly == 0 else 0) + (r.random() - 0.5) * 0.12
                    col = shade(col, f)
                cv.put(x, y, col)
    for _ in range(glow_n):
        x, y = r.randrange(16), r.randrange(16)
        for _k in range(r.randrange(2, 5)):
            cv.put(x, y, glow)
            x = (x + r.choice([-1, 0, 1])) % 16
            y = (y + r.choice([0, 1])) % 16
    return cv


def element_bricks(element):
    p = ELEMENT_PAL[element]
    if element == 'flame':
        return bricks([rgb('#2b2528'), rgb('#363034'), rgb('#3e3236')], rgb('#17121a'), 11, glow=rgb('#ff8a24'), glow_n=4)
    if element == 'frost':
        return bricks([rgb('#a9d8f0'), rgb('#bfe6f8'), rgb('#94c6e4')], rgb('#5a8cb4'), 12, glow=rgb('#ffffff'), glow_n=3)
    if element == 'storm':
        return bricks([rgb('#6d7ea0'), rgb('#7b8cad'), rgb('#5f7090')], rgb('#2e3a58'), 13, glow=rgb('#ffe85a'), glow_n=3)
    if element == 'verdant':
        cv = bricks([rgb('#4a5a3a'), rgb('#55663f'), rgb('#3e4e32')], rgb('#243020'), 14, glow=rgb('#c8ff7e'), glow_n=2)
        r = random.Random(3)
        for _ in range(40):
            cv.put(r.randrange(16), r.randrange(16), rgb('#5fb04a') if r.random() < 0.6 else rgb('#8fd45a'))
        return cv
    return bricks([rgb('#1c1230'), rgb('#251840'), rgb('#2e1e50')], rgb('#0c0618'), 15, glow=rgb('#c05aff'), glow_n=4)


def rune_block(element, seed):
    p = ELEMENT_PAL[element]
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            cv.put(x, y, shade(p['dark'], -0.5) if edge else shade(p['dark'], -0.25 + (fbm(x / 3, y / 3, seed) - 0.5) * 0.2))
    r = random.Random(seed)
    # symmetric glyph
    for _ in range(12):
        x, y = r.randrange(3, 8), r.randrange(3, 13)
        for _k in range(r.randrange(2, 4)):
            for xx in (x, 15 - x):
                cv.put(xx, y, p['glow'])
                cv.put(xx, y + 1, shade(p['main'], 0.0)) if r.random() < 0.3 else None
            if r.random() < 0.5:
                x = min(7, x + 1)
            else:
                y = min(12, y + 1)
    for y in range(4, 12):
        cv.put(7, y, p['glow']); cv.put(8, y, p['glow'])
    cv.put(7, 7, (255, 255, 255)); cv.put(8, 8, (255, 255, 255))
    return cv


def turf_top(seed=2):
    cv = Canvas()
    cols = [rgb('#2fb5a0'), rgb('#3fcf9c'), rgb('#5de0a8'), rgb('#7a6ae8')]
    for y in range(16):
        for x in range(16):
            n = fbm(x / 2.5, y / 2.5, seed, 3, tile=6) if False else vnoise(x / 2.2, y / 2.2, seed, 7)
            cv.put(x, y, cols[min(3, int(n * 3.2))] if n < 0.92 else cols[3])
    r = random.Random(seed)
    for _ in range(6):
        cv.put(r.randrange(16), r.randrange(16), rgb('#d8fff0'))
    return cv


def soil(seed=3):
    cv = Canvas()
    noise_fill(cv, [rgb('#3a2c40'), rgb('#46344c'), rgb('#52405a'), rgb('#2e2234')], seed, 3.0)
    return cv


def turf_side(seed=4):
    cv = soil(seed)
    top = turf_top(seed)
    r = random.Random(seed)
    for x in range(16):
        d = 3 + r.randrange(0, 3)
        for y in range(d):
            cv.put(x, y, tuple(top.a[y, x, :3]))
    return cv


def crystal_block(seed=5):
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            u = (x + y) / 30.0
            col = mix(rgb('#5a3ad0'), rgb('#7ff4ff'), u)
            facet = ((x // 4) + (y // 4)) % 2
            col = shade(col, 0.12 if facet else -0.08)
            edge = x in (0, 15) or y in (0, 15)
            cv.put(x, y, shade(col, -0.3) if edge else col)
    for (x, y) in ((3, 3), (4, 3), (3, 4), (10, 9), (11, 9), (10, 10), (12, 4)):
        cv.put(x, y, (255, 255, 255))
    return cv


def ore(seed=6):
    cv = riftstone(seed)
    r = random.Random(seed)
    for _ in range(4):
        cx, cy = r.randrange(2, 14), r.randrange(2, 14)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0)):
            col = rgb('#7a5cf0') if (dx + dy) % 2 == 0 else rgb('#bfb0ff')
            cv.put(cx + dx, cy + dy, col)
        cv.put(cx, cy, rgb('#7ff4ff'))
    return cv


def log_side(seed=7):
    cv = Canvas()
    cols = [rgb('#c8cfe4'), rgb('#aab4d0'), rgb('#8c98bc'), rgb('#6f7ca4')]
    for y in range(16):
        for x in range(16):
            n = vnoise(x / 1.2, y / 5.0, seed, 8)
            col = cols[min(3, int(n * 4))]
            if x % 4 == 0:
                col = shade(col, -0.18)
            cv.put(x, y, col)
    r = random.Random(seed)
    for _ in range(14):
        cv.put(r.randrange(16), r.randrange(16), rgb('#3fe0b0') if r.random() < 0.5 else rgb('#7ff4ff'))
    return cv


def log_top(seed=8):
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            ring = int(d) % 2
            col = rgb('#e8ecfa') if ring == 0 else rgb('#c4cce6')
            if d > 6.6:
                col = rgb('#8c98bc')
            cv.put(x, y, col)
    cv.put(7, 7, rgb('#7ff4ff')); cv.put(8, 8, rgb('#7ff4ff'))
    return cv


def planks(seed=9):
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            row = y // 4
            col = [rgb('#d6d0f0'), rgb('#c8c0e8'), rgb('#dcd6f4'), rgb('#cac2ea')][row]
            col = shade(col, (vnoise(x / 3.0 + row * 5, y / 1.5, seed, 9) - 0.5) * 0.16)
            if y % 4 == 3:
                col = rgb('#8a82b8')
            if (x + row * 7) % 16 == 0 and y % 4 != 3:
                col = rgb('#9c94c8')
            cv.put(x, y, col)
    return cv


def leaves(seed=10):
    cv = Canvas()
    r = random.Random(seed)
    cols = [rgb('#1f9a8c'), rgb('#2fc0a0'), rgb('#62e0b0'), rgb('#d86ad0'), rgb('#ff9ae8')]
    for y in range(16):
        for x in range(16):
            n = vnoise(x / 1.8, y / 1.8, seed, 9)
            if n < 0.16 and r.random() < 0.8:
                continue
            idx = min(4, int(n * 5))
            if idx >= 3 and r.random() < 0.65:
                idx = r.randrange(0, 3)
            cv.put(x, y, cols[idx])
    return cv


def bloom(seed=11):
    cv = Canvas()
    for y in range(7, 16):
        cv.put(7, y, rgb('#2fa070')); cv.put(8 if y > 11 else 7, y, rgb('#1f7a56'))
    for (cx, cy, c1, c2) in ((5, 6, '#7ff4ff', '#d8ffff'), (10, 4, '#ff9ae8', '#ffe0f8'), (7, 8, '#b890ff', '#efe4ff')):
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            cv.put(cx + dx, cy + dy, rgb(c1))
        cv.put(cx, cy, rgb(c2))
    cv.put(4, 12, rgb('#2fa070')); cv.put(5, 11, rgb('#2fa070')); cv.put(10, 11, rgb('#2fa070')); cv.put(11, 10, rgb('#2fa070'))
    return cv


def portal_frames(n=16):
    cv = Canvas(16, 16 * n)
    for f in range(n):
        ph = f / n * math.tau
        for y in range(16):
            for x in range(16):
                dx, dy = (x - 7.5) / 8.0, (y - 7.5) / 8.0
                ang = math.atan2(dy, dx)
                rad = math.hypot(dx, dy)
                v = 0.5 + 0.5 * math.sin(ang * 3 + rad * 7 - ph) * (1 - rad * 0.5)
                v2 = fbm(x / 3.0 + math.cos(ph) * 1.5, y / 3.0 + math.sin(ph) * 1.5 + f * 0.0, 4, 3, tile=None)
                t = max(0, min(1, v * 0.6 + v2 * 0.6))
                col = mix(rgb('#3a1c9a'), rgb('#7ff4ff'), t)
                col = mix(col, rgb('#e060ff'), max(0, (v - 0.7) * 2))
                cv.put(x, f * 16 + y, col, int(140 + 90 * t))
    return cv


def landmark_side(seed=12):
    cv = bricks([rgb('#44445c'), rgb('#4e4e68')], rgb('#22222e'), seed, rows=4)
    for y in range(3, 13):
        for x in (7, 8):
            cv.put(x, y, rgb('#ffd86a'))
    for x in range(5, 11):
        cv.put(x, 5, rgb('#ffd86a'))
    cv.put(6, 9, rgb('#ffd86a')); cv.put(9, 9, rgb('#ffd86a'))
    cv.put(7, 7, (255, 255, 255)); cv.put(8, 8, (255, 255, 255))
    return cv


def landmark_top(seed=13):
    cv = Canvas()
    noise_fill(cv, SLATE, seed, 4.0)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.0 < d < 6.2 or d < 1.8:
                cv.put(x, y, rgb('#ffd86a'))
            elif 3.0 < d < 3.6 and (x + y) % 2 == 0:
                cv.put(x, y, rgb('#7ff4ff'))
    return cv


def altar_top(seed=14):
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.put(x, y, rgb('#17101f') if (x + y) % 7 else rgb('#1f1730'))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 6.0 < d < 7.2 or 3.4 < d < 4.2:
                cv.put(x, y, rgb('#e8c2ff'))
            elif d < 1.6:
                cv.put(x, y, (255, 255, 255))
    for ang in range(0, 360, 45):
        cv.put(round(7.5 + math.cos(math.radians(ang)) * 5.0), round(7.5 + math.sin(math.radians(ang)) * 5.0), rgb('#ff8ae8'))
    return cv


def altar_side(seed=15):
    cv = bricks([rgb('#251a36'), rgb('#2e2146')], rgb('#100a1a'), seed, rows=4, glow=rgb('#c05aff'), glow_n=3)
    for x in range(16):
        cv.put(x, 0, rgb('#e8c2ff')); cv.put(x, 15, rgb('#6a4a90'))
    return cv


def pillar_side(seed=16):
    cv = riftstone(seed)
    for x in (0, 7, 8, 15):
        for y in range(16):
            cv.put(x, y, shade(SLATE[0], -0.3) if x in (0, 15) else shade(SLATE[3], 0.1))
    for y in (0, 15):
        for x in range(16):
            cv.put(x, y, rgb('#7a78a8'))
    return cv


def pillar_top(seed=17):
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            cv.put(x, y, rgb('#56547c') if int(d) % 3 else rgb('#3b3a54'))
    cv.put(7, 7, rgb('#7ff4ff')); cv.put(8, 8, rgb('#7ff4ff')); cv.put(7, 8, rgb('#7ff4ff')); cv.put(8, 7, rgb('#7ff4ff'))
    return cv


def chiseled(seed=18):
    cv = riftstone(seed)
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                cv.put(x, y, rgb('#7a78a8'))
            elif x in (1, 14) or y in (1, 14):
                cv.put(x, y, rgb('#22213a'))
            d = math.hypot(x - 7.5, y - 7.5)
            if 3.6 < d < 4.6:
                cv.put(x, y, rgb('#8f7cff'))
            if d < 1.8:
                cv.put(x, y, rgb('#7ff4ff'))
    return cv
