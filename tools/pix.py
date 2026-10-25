"""Tiny pixel-art toolkit used by the Realmbreak asset generators (numpy + Pillow)."""
import math
import random
import numpy as np
from PIL import Image


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def shade(c, f):
    """f>0 lighten towards white, f<0 darken towards black."""
    if f >= 0:
        return mix(c, (255, 255, 255), f)
    return mix(c, (0, 0, 0), -f)


def clampc(c):
    return tuple(max(0, min(255, int(v))) for v in c)


class Canvas:
    def __init__(self, w=16, h=16, fill=None):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
        if fill is not None:
            self.fill(fill)

    def fill(self, c):
        self.a[:, :, :3] = c
        self.a[:, :, 3] = 255

    def put(self, x, y, c, alpha=255):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = clampc(c)
            self.a[y, x, 3] = alpha

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return tuple(int(v) for v in self.a[y, x])
        return (0, 0, 0, 0)

    def filled(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3] > 0

    def rect(self, x0, y0, x1, y1, c, alpha=255):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c, alpha)

    def line(self, p0, p1, c, width=1, fn=None):
        (x0, y0), (x1, y1) = p0, p1
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            if width <= 1:
                col = fn(t, 0) if fn else c
                self.put(round(x), round(y), col)
            else:
                r = width / 2.0
                for dy in range(-int(r) - 1, int(r) + 2):
                    for dx in range(-int(r) - 1, int(r) + 2):
                        px, py = round(x) + dx, round(y) + dy
                        if math.hypot(px - x, py - y) <= r:
                            col = fn(t, (px - x, py - y)) if fn else c
                            self.put(px, py, col)

    def disc(self, cx, cy, r, c, fn=None):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if math.hypot(x - cx, y - cy) <= r:
                    self.put(x, y, fn(x, y) if fn else c)

    def outline(self, c, only_empty=True, diagonal=False):
        src = self.a[:, :, 3] > 0
        pts = []
        for y in range(self.h):
            for x in range(self.w):
                if src[y, x]:
                    continue
                nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                if diagonal:
                    nb += [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                for dx, dy in nb:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and src[yy, xx]:
                        pts.append((x, y))
                        break
        for x, y in pts:
            self.put(x, y, c)

    def paste(self, other, ox=0, oy=0):
        for y in range(other.h):
            for x in range(other.w):
                if other.a[y, x, 3] > 0:
                    self.put(x + ox, y + oy, tuple(other.a[y, x, :3]), int(other.a[y, x, 3]))

    def image(self):
        return Image.fromarray(self.a, 'RGBA')

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.image().save(path)


# ------------------------------------------------------------------ noise
def hash2(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 1442695040888963407) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 65535.0


def vnoise(x, y, seed=0, tile=None):
    """Smooth value noise; tile = period for seamless tiling."""
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)

    def h(ix, iy):
        if tile:
            ix %= tile
            iy %= tile
        return hash2(ix, iy, seed)

    a = h(x0, y0)
    b = h(x0 + 1, y0)
    c = h(x0, y0 + 1)
    d = h(x0 + 1, y0 + 1)
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def fbm(x, y, seed=0, octaves=3, tile=None):
    v, amp, tot = 0.0, 1.0, 0.0
    f = 1
    for o in range(octaves):
        t = tile * f if tile else None
        v += vnoise(x * f, y * f, seed + o * 17, t) * amp
        tot += amp
        amp *= 0.5
        f *= 2
    return v / tot


# ------------------------------------------------------------------ palettes
def P(**kw):
    return {k: rgb(v) if isinstance(v, str) else v for k, v in kw.items()}


ELEMENT_PAL = {
    'flame': P(main='#e2561c', light='#ff9a2e', dark='#6e2210', glow='#ffe07a', metal='#5a4a4c', metal_l='#8a7476', accent='#ffcf4a'),
    'frost': P(main='#5fb7e8', light='#d6f3ff', dark='#255a8a', glow='#b8f0ff', metal='#7d98b0', metal_l='#bcd4e6', accent='#ffffff'),
    'storm': P(main='#6a78f0', light='#cdd6ff', dark='#2b3274', glow='#fff06a', metal='#6e7488', metal_l='#aab0c8', accent='#ffe54a'),
    'verdant': P(main='#4cb84a', light='#b8f26a', dark='#1d5a26', glow='#d4ff7e', metal='#6b4e2c', metal_l='#9c7a46', accent='#ff9ad0'),
    'void': P(main='#8c48dc', light='#e2a8ff', dark='#26104a', glow='#e08cff', metal='#2e2440', metal_l='#5a4a80', accent='#ff5ad2'),
}

STEEL = P(dark='#59626e', mid='#98a3b0', light='#d4dce4', hi='#f4f8fc')
WOOD = P(dark='#4a2f18', mid='#7a5230', light='#a67a48')
GOLD = P(dark='#8a5a10', mid='#d9a521', light='#ffe066')
OUTLINE = (24, 20, 30)
