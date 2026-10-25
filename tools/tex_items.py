"""Procedural 16x16 item icons."""
import math
from pix import *

PALS = dict(ELEMENT_PAL)
PALS['arcane'] = P(main='#b890ff', light='#f0e4ff', dark='#4a2f8a', glow='#ffffff', metal='#6a5a8a', metal_l='#a898c8', accent='#7fe8ff')
PALS[''] = PALS['arcane']


def blade_colors(pal, tint=0.35):
    return (mix(STEEL['dark'], pal['dark'], tint), mix(STEEL['mid'], pal['main'], tint), mix(STEEL['light'], pal['light'], tint), STEEL['hi'])


def sword(pal, big=False):
    c = Canvas()
    dk, md, lt, hi = blade_colors(pal, 0.55 if big else 0.3)
    d = (1, -1)
    n = (1 / math.sqrt(2), 1 / math.sqrt(2))
    w = 3.0 if big else 2.2
    p0, p1 = ((5.5, 9.5), (14, 1)) if not big else ((5, 10), (14.6, 0.4))

    def blade(t, off):
        if off == 0:
            return lt
        s = off[0] * n[0] + off[1] * n[1]
        if t > 0.9:
            return hi
        if abs(s) < 0.35 and big:
            return pal['glow']
        return lt if s < -0.2 else (md if s < 0.55 else dk)
    c.line(p0, p1, md, width=w, fn=blade)
    # guard
    gc = pal['dark'] if not big else GOLD['mid']
    c.line((2.6, 9.0), (6.2, 12.6), gc, width=1.6, fn=lambda t, o: GOLD['light'] if t < 0.3 else (gc if t < 0.8 else GOLD['dark']))
    if big:
        c.put(2, 8, GOLD['light']); c.put(7, 13, GOLD['dark'])
    # grip + pommel
    c.line((4.6, 10.6), (2.0, 13.2), WOOD['mid'], width=1.4, fn=lambda t, o: WOOD['light'] if t < 0.4 else WOOD['mid'])
    c.disc(1.6, 13.6, 1.2, pal['accent'], fn=lambda x, y: pal['glow'] if (x, y) == (1, 13) else pal['main'])
    c.outline(OUTLINE)
    # element glow accents on the blade
    if not big:
        c.put(9, 6, pal['glow']); c.put(11, 4, pal['light'])
    return c


def bow(pal, big=False, pull=0):
    c = Canvas()
    wood = pal['metal'] if not big else mix(WOOD['mid'], pal['dark'], 0.4)
    woodl = pal['metal_l'] if not big else mix(WOOD['light'], pal['main'], 0.3)
    # arc: quadratic bezier tip-to-tip bulging to top-left
    tipA, tipB, ctrl = (12.5, 1.5), (1.5, 12.5), (-0.5, -0.5)
    pts = []
    for i in range(41):
        t = i / 40
        x = (1 - t) ** 2 * tipA[0] + 2 * (1 - t) * t * ctrl[0] + t * t * tipB[0]
        y = (1 - t) ** 2 * tipA[1] + 2 * (1 - t) * t * ctrl[1] + t * t * tipB[1]
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            col = woodl if (i % 7 < 4 and dx == 0 and dy == 0) else wood
            if (dx, dy) != (0, 0):
                col = shade(wood, -0.2)
            c.put(round(x) + dx - 0, round(y) + dy - 0, col)
    # gem at grip
    gx, gy = pts[20]
    c.put(round(gx) + 1, round(gy) + 1, pal['glow'])
    c.put(round(gx), round(gy), pal['accent'])
    # string
    sc = (230, 230, 220)
    mid = (7, 7)
    if pull:
        mid = (7 + 2.2 * pull, 7 + 2.2 * pull)
    c.line(tipA, mid, sc); c.line(mid, tipB, sc)
    if pull:
        # arrow pointing up-left from string centre
        ax, ay = mid
        c.line((ax, ay), (ax - 8.5, ay - 8.5), (150, 120, 90))
        c.put(round(ax - 8.5), round(ay - 8.5), (210, 215, 225)); c.put(round(ax - 7.5), round(ay - 8.5), (210, 215, 225)); c.put(round(ax - 8.5), round(ay - 7.5), (210, 215, 225))
        c.put(round(ax), round(ay) + 1, pal['main']); c.put(round(ax) + 1, round(ay), pal['light'])
    c.outline(OUTLINE)
    return c


def staff(pal, big=False, scepter=False):
    c = Canvas()
    rod_a, rod_b = (2.0, 14.2), (10.2, 6.0)
    c.line(rod_a, rod_b, WOOD['mid'], width=1.6, fn=lambda t, o: (WOOD['light'] if (isinstance(o, tuple) and o[0] + o[1] < 0) else WOOD['mid']) if int(t * 14) % 5 else pal['metal_l'])
    ox, oy = (11.2, 4.8)
    r = 3.2 if big else 2.6
    if scepter:
        # leafy crown
        for ang in range(0, 360, 60):
            x = ox + math.cos(math.radians(ang)) * (r + 0.6)
            y = oy + math.sin(math.radians(ang)) * (r + 0.6)
            c.disc(x, y, 0.9, pal['main'] if ang % 120 else pal['light'])
    else:
        # claws
        for ang in (200, 250, 290, 340):
            x = ox + math.cos(math.radians(ang)) * (r + 0.7)
            y = oy + math.sin(math.radians(ang)) * (r + 0.7)
            c.put(round(x), round(y), pal['metal_l'])
    c.disc(ox, oy, r, pal['main'], fn=lambda x, y: mix(pal['glow'], pal['main'], min(1, math.hypot(x - (ox - 0.8), y - (oy - 0.8)) / (r + 0.5))) if math.hypot(x - ox, y - oy) < r - 0.4 else pal['dark'])
    c.put(round(ox - 1), round(oy - 1), (255, 255, 255))
    c.outline(OUTLINE)
    # sparkles
    for (sx, sy) in ((14, 1), (15, 4), (8, 1)):
        if not c.filled(sx, sy):
            c.put(sx, sy, pal['glow'], 200)
    return c


def helmet(pal):
    c = Canvas()
    for y in range(2, 13):
        for x in range(3, 13):
            dx, dy = x - 7.5, y - 7.5
            if y < 5 and abs(dx) > 4.2 - (5 - y) * 0.9:
                continue
            if y >= 11 and (abs(dx) < 1.8):
                continue
            if 8 <= y <= 11 and abs(dx) < 2.6:
                continue  # face opening
            t = (x - 3) / 9.0
            col = pal['light'] if t < 0.25 else (pal['main'] if t < 0.7 else pal['dark'])
            if y == 2 or y == 3:
                col = shade(col, 0.25)
            c.put(x, y, col)
    # crest
    for y in range(0, 4):
        c.put(7, y, pal['accent']); c.put(8, y, pal['glow'] if y == 1 else pal['accent'])
    # visor shadow + eyes
    for x in range(5, 11):
        c.put(x, 7, pal['dark'])
    c.put(6, 8, pal['glow']); c.put(9, 8, pal['glow'])
    c.rect(5, 9, 5, 11, pal['dark']); c.rect(10, 9, 10, 11, pal['dark'])
    c.outline(OUTLINE)
    return c


def chestplate(pal):
    c = Canvas()
    for y in range(2, 15):
        for x in range(1, 15):
            ok = False
            if 4 <= x <= 11 and y >= 2:
                ok = True
            if y <= 6 and (x <= 3 or x >= 12):
                ok = True  # pauldrons
            if y <= 2 and (6 <= x <= 9):
                ok = False  # neck
            if y >= 12 and (x < 5 or x > 10):
                ok = False
            if (x in (1, 14)) and y in (2,):
                ok = False
            if not ok:
                continue
            t = (x - 1) / 13.0
            col = pal['light'] if t < 0.3 else (pal['main'] if t < 0.68 else pal['dark'])
            if y in (2, 3):
                col = shade(col, 0.2)
            c.put(x, y, col)
    # belt
    for x in range(4, 12):
        c.put(x, 11, pal['dark'])
        c.put(x, 12, shade(pal['metal'], -0.1))
    # emblem
    c.rect(7, 6, 8, 9, pal['accent']); c.put(7, 7, pal['glow']); c.put(8, 8, pal['glow'])
    c.rect(6, 7, 9, 8, pal['accent']); c.put(7, 7, pal['glow']); c.put(8, 8, pal['glow'])
    # rivets
    for p_ in ((5, 4), (10, 4), (2, 3), (13, 3)):
        c.put(*p_, STEEL['hi'])
    c.outline(OUTLINE)
    return c


def leggings(pal):
    c = Canvas()
    for y in range(2, 15):
        for x in range(3, 13):
            if y <= 4:
                ok = True
            else:
                ok = (x <= 7) or (x >= 8 and x <= 12)
                if 7 <= x <= 8 and y >= 6:
                    ok = False
            if y >= 13 and x in (3, 12):
                ok = False
            if not ok:
                continue
            t = ((x - 3) % 5) / 4.0
            col = pal['light'] if t < 0.25 else (pal['main'] if t < 0.7 else pal['dark'])
            if y <= 4:
                col = shade(pal['main'], 0.1 if x < 8 else -0.15)
            c.put(x, y, col)
    for x in range(3, 13):
        c.put(x, 3, pal['accent'] if x in (7, 8) else pal['dark'])
    c.put(7, 3, pal['glow']); c.put(8, 3, pal['glow'])
    for y in (9, 10):
        for x in (4, 5, 10, 11):
            c.put(x, y, shade(pal['metal_l'], 0.1))
    c.outline(OUTLINE)
    return c


def boots(pal):
    c = Canvas()
    for (x0, x1) in ((2, 6), (9, 13)):
        for y in range(5, 14):
            for x in range(x0, x1 + 1):
                if y <= 8 and (x == x0 and False):
                    continue
                if y >= 11 and x > x1 - 0 and False:
                    continue
                t = (x - x0) / float(x1 - x0)
                col = pal['light'] if t < 0.3 else (pal['main'] if t < 0.7 else pal['dark'])
                if y <= 6:
                    col = shade(pal['main'], 0.15 if x < x0 + 3 else -0.1)
                if y == 13:
                    col = pal['metal']
                c.put(x, y, col)
        # toe cap
        c.put(x0 - 1 if x0 < 8 else x0, 12, pal['main']); c.put(x0 - 1 if x0 < 8 else x0, 13, pal['metal'])
        for x in range(x0, x1 + 1):
            c.put(x, 5, pal['accent'])
        c.put(x0 + 1, 8, pal['glow'])
    c.outline(OUTLINE)
    return c


def gem(pal, kind='essence'):
    c = Canvas()
    # faceted diamond
    pts = [(8, 1), (12.6, 5), (11.6, 11), (8, 14.4), (4.4, 11), (3.4, 5)]
    for y in range(16):
        for x in range(16):
            # point-in-polygon
            inside = False
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]; xj, yj = pts[j]
                if ((yi > y + 0.5) != (yj > y + 0.5)) and (x + 0.5 < (xj - xi) * (y + 0.5 - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            if inside:
                u = (x - 3.4) / 9.2
                v = (y - 1) / 13.4
                col = pal['light'] if (u < 0.4 and v < 0.5) else (pal['main'] if u + v * 0.3 < 1.0 else pal['dark'])
                if v > 0.62:
                    col = pal['dark'] if u > 0.5 else pal['main']
                c.put(x, y, col)
    c.line((8, 2), (8, 13), pal['glow'], 1, fn=lambda t, o: pal['glow'] if 0.1 < t < 0.5 else None) if False else None
    for (x, y) in ((6, 4), (7, 3), (6, 5)):
        c.put(x, y, (255, 255, 255))
    c.line((4, 6), (12, 6), shade(pal['main'], 0.2))
    c.outline(OUTLINE)
    return c


def shard(pal):
    c = Canvas()
    def crystal(cx, base_y, h, w, tilt):
        for i in range(h):
            half = max(0.5, (w / 2.0) * (1 - (i / float(h)) ** 1.6) + 0.5)
            y = base_y - i
            x = cx + tilt * i
            for dx in range(-int(half) - 1, int(half) + 2):
                if abs(dx) <= half:
                    col = pal['light'] if dx < -half * 0.3 else (pal['main'] if dx < half * 0.4 else pal['dark'])
                    if i == h - 1:
                        col = pal['glow']
                    c.put(round(x) + dx, y, col)
    crystal(8, 14, 12, 4, 0.0)
    crystal(4, 14, 7, 3, -0.25)
    crystal(12, 14, 8, 3, 0.2)
    c.put(7, 5, (255, 255, 255)); c.put(7, 6, pal['glow'])
    c.outline(OUTLINE)
    return c


def sigil(pal):
    c = Canvas()
    c.disc(7.5, 7.5, 6.4, pal['metal'], fn=lambda x, y: GOLD['mid'] if math.hypot(x - 7.5, y - 7.5) > 5.0 else (pal['dark'] if math.hypot(x - 7.5, y - 7.5) > 4.0 else pal['metal']))
    for ang in range(0, 360, 45):
        x = 7.5 + math.cos(math.radians(ang)) * 5.6
        y = 7.5 + math.sin(math.radians(ang)) * 5.6
        c.put(round(x), round(y), GOLD['light'])
    # rune cross
    for k in range(-3, 4):
        c.put(7 + 0, 7 + k, pal['glow']); c.put(8, 7 + k, pal['glow'])
        c.put(7 + k, 7, pal['glow']); c.put(7 + k, 8, pal['glow'])
    c.rect(6, 6, 9, 9, pal['main'])
    c.put(7, 7, (255, 255, 255)); c.put(8, 8, pal['light'])
    c.outline(OUTLINE)
    return c


def dust(pal):
    c = Canvas()
    import random as R
    r = R.Random(7)
    for i in range(34):
        a = r.random() * math.tau
        d = (r.random() ** 0.7) * 5.2
        x, y = 8 + math.cos(a) * d, 10 + math.sin(a) * d * 0.55
        col = r.choice([pal['main'], pal['light'], pal['glow'], pal['dark']])
        c.put(round(x), round(y), col)
    for (x, y) in ((4, 4), (11, 3), (9, 6), (13, 7)):
        c.put(x, y, pal['glow'])
        c.put(x - 1, y, pal['light'], 150); c.put(x + 1, y, pal['light'], 150); c.put(x, y - 1, pal['light'], 150); c.put(x, y + 1, pal['light'], 150)
    return c


def rune(pal):
    c = Canvas()
    c.rect(3, 2, 12, 13, (86, 88, 98))
    c.rect(4, 3, 11, 12, (112, 116, 128))
    c.rect(4, 3, 5, 12, (140, 144, 156))
    c.rect(10, 3, 11, 12, (92, 96, 108))
    for (x, y) in ((8, 4), (8, 5), (8, 6), (7, 6), (9, 6), (8, 8), (7, 9), (9, 9), (6, 10), (10, 10), (8, 10)):
        c.put(x, y, pal['glow'])
    c.put(8, 7, (255, 255, 255))
    c.outline(OUTLINE)
    return c


def anchor(pal):
    c = Canvas()
    # stone with ring
    c.disc(8, 8.5, 6.0, (110, 114, 126), fn=lambda x, y: (80, 84, 96) if (x + y) % 5 == 0 else ((140, 144, 156) if x < 7 and y < 8 else (110, 114, 126)))
    c.disc(8, 8.5, 3.4, pal['dark'])
    c.disc(8, 8.5, 2.3, pal['main'], fn=lambda x, y: pal['glow'] if (x, y) in ((7, 7),) else (pal['light'] if x < 8 and y < 9 else pal['main']))
    for ang in range(0, 360, 90):
        x = 8 + math.cos(math.radians(ang)) * 5.2
        y = 8.5 + math.sin(math.radians(ang)) * 5.2
        c.put(round(x), round(y), pal['glow'])
    c.outline(OUTLINE)
    return c


def compass(pal):
    c = Canvas()
    c.disc(8, 8, 6.6, GOLD['mid'], fn=lambda x, y: GOLD['light'] if (x < 7 and y < 7 and math.hypot(x - 8, y - 8) > 5) else (GOLD['dark'] if math.hypot(x - 8, y - 8) > 5.4 else (200, 205, 215)))
    c.disc(8, 8, 4.2, (40, 48, 74))
    c.line((8, 8), (11.5, 4.5), (255, 90, 70), 1.4)
    c.line((8, 8), (4.5, 11.5), (236, 236, 244), 1.4)
    c.put(8, 8, GOLD['light'])
    for (x, y) in ((8, 3), (8, 12), (3, 8), (12, 8)):
        c.put(x, y, pal['glow'])
    c.put(8, 1, GOLD['mid']); c.put(8, 0, GOLD['light'])
    c.outline(OUTLINE)
    return c


def book(pal, cover, big=False):
    c = Canvas()
    c.rect(3, 2, 12, 14, cover)
    c.rect(3, 2, 4, 14, shade(cover, -0.35))
    c.rect(11, 2, 12, 14, shade(cover, -0.15))
    c.rect(5, 3, 10, 13, shade(cover, 0.08))
    for x in range(3, 13):
        c.put(x, 2, shade(cover, 0.3)); c.put(x, 14, shade(cover, -0.4))
    c.rect(11, 5, 12, 6, GOLD['mid'])
    # emblem
    c.rect(7, 6, 8, 9, pal['glow']); c.rect(6, 7, 9, 8, pal['glow'])
    c.put(7, 7, (255, 255, 255))
    if big:
        for x in range(4, 12):
            c.put(x, 12, GOLD['mid'])
        c.put(2, 3, pal['glow']); c.put(13, 12, pal['glow'])
    c.outline(OUTLINE)
    return c


def elixir(pal, liquid):
    c = Canvas()
    # bottle
    for y in range(6, 14):
        for x in range(4, 12):
            if (x - 7.5) ** 2 / 14.0 + (y - 10) ** 2 / 17.0 <= 1.0:
                u = (x - 4) / 8.0
                col = shade(liquid, 0.25) if u < 0.3 else (liquid if u < 0.75 else shade(liquid, -0.3))
                c.put(x, y, col)
    for y in range(3, 6):
        for x in (6, 7, 8, 9):
            c.put(x, y, (200, 220, 230) if x < 8 else (150, 170, 190))
    c.rect(6, 2, 9, 2, WOOD['mid'])
    c.put(6, 8, (255, 255, 255)); c.put(5, 9, shade(liquid, 0.6))
    c.put(10, 11, pal['glow']) if False else None
    c.outline(OUTLINE)
    return c


def dagger_placeholder(pal):
    return sword(pal)


# ---------------------------------------------------------------- registry
def draw(icon, element):
    pal = PALS.get(element, PALS['arcane'])
    if icon == 'sword':
        return sword(pal)
    if icon == 'greatsword':
        return sword(pal, big=True)
    if icon == 'bow':
        return bow(pal)
    if icon == 'bow_big':
        return bow(pal, big=True)
    if icon == 'staff':
        return staff(pal)
    if icon == 'staff_big':
        return staff(pal, big=True)
    if icon == 'scepter':
        return staff(pal, big=True, scepter=True)
    if icon == 'helmet':
        return helmet(pal)
    if icon == 'chestplate':
        return chestplate(pal)
    if icon == 'leggings':
        return leggings(pal)
    if icon == 'boots':
        return boots(pal)
    if icon == 'essence':
        return gem(pal)
    if icon == 'sigil':
        return sigil(pal)
    if icon == 'shard':
        return shard(PALS['void'] if False else P(main='#7a5cf0', light='#bfb0ff', dark='#32208a', glow='#7ff4ff'))
    if icon == 'dust':
        return dust(P(main='#8f6cf0', light='#c9b8ff', dark='#4a3498', glow='#8ff7ff'))
    if icon == 'rune':
        return rune(P(main='#ffd34a', light='#fff0a0', dark='#a26a10', glow='#ffd86a'))
    if icon == 'anchor':
        return anchor(P(main='#7a5cf0', light='#bfb0ff', dark='#32208a', glow='#7ff4ff'))
    if icon == 'compass':
        return compass(P(main='#7a5cf0', light='#bfb0ff', dark='#32208a', glow='#7ff4ff'))
    if icon == 'journal':
        return book(PALS['arcane'], (110, 56, 40))
    if icon == 'tome':
        return book(PALS['void'], (56, 34, 110), big=True)
    if icon == 'elixir_blue':
        return elixir(PALS['frost'], (70, 130, 255))
    if icon == 'elixir_red':
        return elixir(PALS['flame'], (235, 60, 80))
    raise ValueError(icon)


def bow_frames(element, big=False):
    pal = PALS[element]
    return [bow(pal, big, pull=0), bow(pal, big, pull=0.45), bow(pal, big, pull=0.75), bow(pal, big, pull=1.0)]
