"""Procedural humanoid skins (vanilla 64x32 box-UV layout), spider textures and armour layers."""
import math
import random
from pix import *

PARTS = {
    'head': dict(top=(8, 0, 8, 8), bottom=(16, 0, 8, 8), right=(0, 8, 8, 8), front=(8, 8, 8, 8), left=(16, 8, 8, 8), back=(24, 8, 8, 8)),
    'hat': dict(top=(40, 0, 8, 8), bottom=(48, 0, 8, 8), right=(32, 8, 8, 8), front=(40, 8, 8, 8), left=(48, 8, 8, 8), back=(56, 8, 8, 8)),
    'body': dict(top=(20, 16, 8, 4), bottom=(28, 16, 8, 4), right=(16, 20, 4, 12), front=(20, 20, 8, 12), left=(28, 20, 4, 12), back=(32, 20, 8, 12)),
    'arm': dict(top=(44, 16, 4, 4), bottom=(48, 16, 4, 4), right=(40, 20, 4, 12), front=(44, 20, 4, 12), left=(48, 20, 4, 12), back=(52, 20, 4, 12)),
    'leg': dict(top=(4, 16, 4, 4), bottom=(8, 16, 4, 4), right=(0, 20, 4, 12), front=(4, 20, 4, 12), left=(8, 20, 4, 12), back=(12, 20, 4, 12)),
}


def paint(cv, part, face, fn):
    x0, y0, w, h = PARTS[part][face]
    for v in range(h):
        for u in range(w):
            col = fn(u, v, w, h)
            if col is None:
                continue
            if len(col) == 4:
                cv.put(x0 + u, y0 + v, col[:3], col[3])
            else:
                cv.put(x0 + u, y0 + v, col)


def lit(c, face, u, v, w, h, rnd, jitter=0.05):
    f = {'top': 0.12, 'bottom': -0.25, 'right': -0.1, 'left': 0.0, 'front': 0.0, 'back': -0.12}[face]
    f += (0.07 * (1 - v / max(1, h - 1))) if face in ('front', 'back', 'left', 'right') else 0
    f += (rnd.random() - 0.5) * 2 * jitter
    return shade(c, f)


def fill(cv, part, c, rnd, jitter=0.05, faces=None):
    for face in (faces or PARTS[part].keys()):
        paint(cv, part, face, lambda u, v, w, h, face=face: lit(c, face, u, v, w, h, rnd, jitter))


class Spec(dict):
    def __getattr__(self, k):
        return self.get(k)


def humanoid(spec, seed=1):
    s = Spec(spec)
    rnd = random.Random(seed)
    cv = Canvas(64, 64)
    skin = s.skin or (222, 176, 140)
    hair = s.hair or (80, 56, 36)
    cloth = s.cloth or (70, 90, 160)
    cloth2 = s.cloth2 or (230, 200, 90)
    pants = s.pants or shade(cloth, -0.25)
    boots = s.boots or (60, 42, 30)
    glow = s.glow or (255, 255, 255)
    metal = s.metal
    alpha = s.alpha

    # ---- base fills
    fill(cv, 'head', skin if not s.mask else s.mask, rnd, 0.04)
    if metal:
        fill(cv, 'body', metal, rnd, 0.06)
        fill(cv, 'arm', metal, rnd, 0.06)
        fill(cv, 'leg', metal, rnd, 0.06)
    else:
        fill(cv, 'body', cloth, rnd, 0.05)
        fill(cv, 'arm', cloth if s.long_sleeves is not False else skin, rnd, 0.05)
        fill(cv, 'leg', cloth if s.robe else pants, rnd, 0.05)
    # hands (arm bottoms) and boots
    if not metal or s.bare_hands:
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'arm', face, lambda u, v, w, h: lit(skin, face, u, v, w, h, rnd) if v >= h - 3 else None)
    if not s.robe:
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'leg', face, lambda u, v, w, h, face=face: lit(boots if not metal else shade(metal, -0.3), face, u, v, w, h, rnd) if v >= h - 4 else None)
    else:
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'leg', face, lambda u, v, w, h, face=face: lit(cloth2, face, u, v, w, h, rnd) if v >= h - 1 else None)
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'body', face, lambda u, v, w, h, face=face: lit(cloth2, face, u, v, w, h, rnd) if v >= h - 1 else None)

    # ---- body details
    if s.belt:
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'body', face, lambda u, v, w, h: s.belt if v == h - 4 else None)
        paint(cv, 'body', 'front', lambda u, v, w, h: cloth2 if (v == h - 4 and u in (3, 4)) else None)
    if s.trim:
        # vertical trim down the front
        paint(cv, 'body', 'front', lambda u, v, w, h: shade(s.trim, -0.1 + rnd.random() * 0.1) if u in (3, 4) and v < h - 4 else None)
        for face in ('right', 'left'):
            paint(cv, 'arm', face, lambda u, v, w, h: s.trim if v == 3 else None)
    if s.apron:
        paint(cv, 'body', 'front', lambda u, v, w, h: lit(s.apron, 'front', u, v, w, h, rnd, 0.08) if 1 <= u <= 6 and v >= 3 else None)
    if s.pack:
        paint(cv, 'body', 'back', lambda u, v, w, h: lit(s.pack, 'back', u, v, w, h, rnd, 0.1) if 1 <= u <= 6 and 1 <= v <= 9 else None)
        paint(cv, 'body', 'back', lambda u, v, w, h: shade(s.pack, -0.4) if (u in (1, 6) or v == 1 or v == 9 or v == 5) and 1 <= u <= 6 and 1 <= v <= 9 else None)
    if s.cape:
        paint(cv, 'body', 'back', lambda u, v, w, h: lit(s.cape, 'back', u, v, w, h, rnd, 0.06))
        paint(cv, 'body', 'back', lambda u, v, w, h: shade(s.cape, 0.2) if v == 0 or u in (0, 7) else None)
    if s.emblem:
        paint(cv, 'body', 'front', lambda u, v, w, h: s.emblem if ((u in (3, 4) and v in (2, 3, 4, 5)) or (u in (2, 5) and v in (3, 4))) else None)
        paint(cv, 'body', 'front', lambda u, v, w, h: (255, 255, 255) if (u, v) == (3, 3) else None)
    if s.stars:
        for _ in range(26):
            part = rnd.choice(['body', 'arm', 'leg'])
            face = rnd.choice(['front', 'back', 'left', 'right'])
            x0, y0, w, h = PARTS[part][face]
            cv.put(x0 + rnd.randrange(w), y0 + rnd.randrange(h), rnd.choice([s.stars, (255, 255, 255)]))
    if s.cracks:
        for _ in range(int(s.crack_n or 18)):
            part = rnd.choice(['body', 'arm', 'leg', 'head'])
            face = rnd.choice(['front', 'back', 'left', 'right'])
            x0, y0, w, h = PARTS[part][face]
            x, y = rnd.randrange(w), rnd.randrange(h)
            for _k in range(rnd.randrange(2, 5)):
                cv.put(x0 + x, y0 + y, s.cracks)
                x = max(0, min(w - 1, x + rnd.choice([-1, 0, 1])))
                y = max(0, min(h - 1, y + rnd.choice([0, 1])))
    if s.moss:
        for _ in range(60):
            part = rnd.choice(['body', 'arm', 'leg', 'head'])
            face = rnd.choice(['front', 'back', 'left', 'right', 'top'])
            x0, y0, w, h = PARTS[part][face]
            cv.put(x0 + rnd.randrange(w), y0 + rnd.randrange(h), shade(s.moss, rnd.random() * 0.3 - 0.15))
    if s.tatter:
        # transparent ragged hem
        for part in ('body', 'leg'):
            for face in ('front', 'back', 'left', 'right'):
                x0, y0, w, h = PARTS[part][face]
                for u in range(w):
                    cut = rnd.randrange(0, 4)
                    for v in range(h - cut, h):
                        cv.a[y0 + v, x0 + u, 3] = 0
    if s.pauldrons:
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'arm', face, lambda u, v, w, h, face=face: lit(s.pauldrons, face, u, v, w, h, rnd, 0.06) if v < 3 else None)
        paint(cv, 'arm', 'top', lambda u, v, w, h: shade(s.pauldrons, 0.2))

    # ---- face
    eye = s.eye or (40, 30, 30)
    eyew = s.eyew or (240, 240, 240)
    if s.face != 'none':
        def face_fn(u, v, w, h):
            if s.visor:
                if v in (3, 4):
                    return glow if 1 <= u <= 6 and (v == 3 or u in (1, 2, 5, 6)) else shade(s.visor, 0.0)
                return None
            if v == 2 and u in (1, 2, 5, 6) and not s.noeyebrow:
                return shade(hair, -0.1)
            if v == 3 and u in (1, 2, 5, 6):
                return eyew if not s.glow_eyes else glow
            if v == 3 and u in (2, 5) and not s.glow_eyes:
                return eye
            if v == 5 and u in (3, 4):
                return shade(skin, -0.12)
            if v == 6 and u in (3, 4):
                return shade(skin, -0.28) if not s.mouth else s.mouth
            return None
        paint(cv, 'head', 'front', face_fn)
        if s.glow_eyes and not s.visor:
            paint(cv, 'head', 'front', lambda u, v, w, h: glow if (v == 3 and u in (1, 2, 5, 6)) or (v == 4 and u in (1, 6) and s.big_glow) else None)

    # ---- hair
    if s.hair_style in ('short', 'long', 'wild'):
        for face in ('top', 'back', 'left', 'right'):
            def hf(u, v, w, h, face=face):
                if face == 'top':
                    return lit(hair, 'top', u, v, w, h, rnd, 0.08)
                if s.hair_style == 'short':
                    return lit(hair, face, u, v, w, h, rnd, 0.08) if v < 3 or (face == 'back' and v < 6) else None
                return lit(hair, face, u, v, w, h, rnd, 0.08)
            paint(cv, 'head', face, hf)
        paint(cv, 'head', 'front', lambda u, v, w, h: lit(hair, 'front', u, v, w, h, rnd, 0.08) if v < 2 or (v < 3 and u in (0, 7)) or (s.hair_style != 'short' and u in (0, 7) and v < 8) else None)
        if s.hair_style == 'long':
            paint(cv, 'body', 'back', lambda u, v, w, h: lit(hair, 'back', u, v, w, h, rnd, 0.08) if 2 <= u <= 5 and v < 5 else None)
    if s.bald_top:
        pass

    # ---- beard
    if s.beard:
        bc = s.beard
        paint(cv, 'head', 'front', lambda u, v, w, h: lit(bc, 'front', u, v, w, h, rnd, 0.08) if (v >= 5 and (u <= 1 or u >= 6 or v >= 6) and not (v == 5 and 2 <= u <= 5 and not s.beard_full)) else None)
        for face in ('left', 'right'):
            paint(cv, 'head', face, lambda u, v, w, h, face=face: lit(bc, face, u, v, w, h, rnd, 0.08) if v >= 5 and u >= 3 else None)
        if s.beard_long:
            paint(cv, 'body', 'front', lambda u, v, w, h: lit(bc, 'front', u, v, w, h, rnd, 0.08) if 2 <= u <= 5 and v < s.beard_long else None)

    # ---- veil
    if s.veil:
        paint(cv, 'head', 'front', lambda u, v, w, h: lit(s.veil, 'front', u, v, w, h, rnd, 0.03) if v >= 5 else None)

    # ---- hood / hat layer (outer layer is inflated)
    if s.hood:
        hc = s.hood
        paint(cv, 'hat', 'top', lambda u, v, w, h: lit(hc, 'top', u, v, w, h, rnd))
        paint(cv, 'hat', 'back', lambda u, v, w, h: lit(hc, 'back', u, v, w, h, rnd))
        for face in ('left', 'right'):
            paint(cv, 'hat', face, lambda u, v, w, h, face=face: lit(hc, face, u, v, w, h, rnd) if u >= 2 or v < 2 else None)
        paint(cv, 'hat', 'front', lambda u, v, w, h: lit(hc, 'front', u, v, w, h, rnd) if (v < 2 or u in (0, 7) or (v == 2 and u in (1, 6))) else None)
        paint(cv, 'hat', 'bottom', lambda u, v, w, h: shade(hc, -0.2))
    if s.helm:
        hm = s.helm
        for face in ('top', 'back', 'left', 'right'):
            paint(cv, 'hat', face, lambda u, v, w, h, face=face: lit(hm, face, u, v, w, h, rnd, 0.06))
        paint(cv, 'hat', 'front', lambda u, v, w, h: lit(hm, 'front', u, v, w, h, rnd, 0.06) if (v < 2 or u in (0, 7) or (v >= 5 and (u <= 1 or u >= 6)) or (u in (3, 4) and v in (4, 5, 6))) else None)
        if s.helm_trim:
            paint(cv, 'hat', 'front', lambda u, v, w, h: s.helm_trim if v == 2 and 0 < u < 7 else None)
            paint(cv, 'hat', 'top', lambda u, v, w, h: s.helm_trim if u in (3, 4) else None)
    if s.horns:
        hc = s.horns
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'hat', face, lambda u, v, w, h, face=face: lit(hc, face, u, v, w, h, rnd) if (u in (0, 7) and v < 3) else None)
    if s.crown:
        cc = s.crown
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'hat', face, lambda u, v, w, h: shade(cc, 0.1 if (u % 2) else -0.1) if v == 0 else None)
        paint(cv, 'hat', 'front', lambda u, v, w, h: (255, 255, 255) if (v == 0 and u == 3) else None)
        paint(cv, 'hat', 'front', lambda u, v, w, h: s.crown_gem if (v == 0 and u in (3, 4)) and s.crown_gem else None)
        paint(cv, 'hat', 'top', lambda u, v, w, h: shade(cc, 0.05) if (u in (0, 7) or v in (0, 7)) else None)
    if s.antlers:
        ac = s.antlers
        paint(cv, 'hat', 'top', lambda u, v, w, h: ac if u in (1, 6) else None)
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'hat', face, lambda u, v, w, h: shade(ac, -0.1) if (u in (1, 6) and v == 0) else None)
    if s.hat_wide:
        hc = s.hat_wide
        for face in ('front', 'back', 'left', 'right', 'top'):
            paint(cv, 'hat', face, lambda u, v, w, h, face=face: lit(hc, face, u, v, w, h, rnd, 0.07) if (face == 'top' or v < 2) else None)
    if s.glow_lines:
        for _ in range(int(s.glow_n or 10)):
            part = rnd.choice(['body', 'arm', 'leg'])
            x0, y0, w, h = PARTS[part][rnd.choice(['front', 'back', 'left', 'right'])]
            x, y = rnd.randrange(w), rnd.randrange(h)
            for _k in range(rnd.randrange(2, 6)):
                cv.put(x0 + x, y0 + y, s.glow_lines)
                if rnd.random() < 0.5:
                    x = max(0, min(w - 1, x + rnd.choice([-1, 1])))
                else:
                    y = max(0, min(h - 1, y + 1))
    if alpha is not None:
        cv.a[:, :, 3] = np.where(cv.a[:, :, 3] > 0, np.minimum(cv.a[:, :, 3], alpha), 0)
    return cv


def front_preview(cv, scale=8):
    out = Canvas(16, 32)
    bg = Canvas(16, 32)

    def blit(part, face, dx, dy, mirror=False):
        x0, y0, w, h = PARTS[part][face]
        for v in range(h):
            for u in range(w):
                uu = (w - 1 - u) if mirror else u
                if cv.a[y0 + v, x0 + uu, 3] > 0:
                    out.put(dx + u, dy + v, tuple(cv.a[y0 + v, x0 + uu, :3]), int(cv.a[y0 + v, x0 + uu, 3]))
    blit('leg', 'front', 4, 20); blit('leg', 'front', 8, 20, True)
    blit('body', 'front', 4, 8)
    blit('arm', 'front', 0, 8); blit('arm', 'front', 12, 8, True)
    blit('head', 'front', 4, 0)
    blit('hat', 'front', 4, 0)
    return out


# ------------------------------------------------------------------ style catalogue
def pal(e):
    return ELEMENT_PAL[e]


def spec_for(style, element='flame'):
    p = ELEMENT_PAL.get(element, ELEMENT_PAL['void'])
    d = dict(skin=(222, 176, 140))
    if style == 'sage':
        d.update(cloth=(36, 120, 130), cloth2=(224, 198, 110), hood=(30, 104, 116), hair=(230, 230, 240), hair_style='long', glow_eyes=True, glow=(130, 255, 240),
                 trim=(224, 198, 110), belt=(120, 80, 40), robe=True, emblem=(130, 255, 240), beard=(235, 235, 245), beard_long=6, beard_full=True)
    elif style == 'smith':
        d.update(skin=(205, 150, 120), cloth=(110, 84, 62), pants=(70, 56, 44), apron=(60, 48, 40), hair=(190, 90, 40), hair_style='short', beard=(190, 90, 40), beard_long=7, beard_full=True,
                 helm=(120, 124, 136), helm_trim=(220, 170, 70), belt=(40, 30, 24), boots=(40, 32, 28))
    elif style == 'merchant':
        d.update(cloth=(70, 130, 70), cloth2=(230, 200, 90), pants=(110, 80, 50), hair=(150, 100, 60), hair_style='short', hat_wide=(70, 110, 60), pack=(150, 100, 60), beard=(150, 100, 60), belt=(60, 40, 30), trim=(230, 200, 90))
    elif style == 'flame_lord':
        d.update(metal=(52, 42, 46), pauldrons=(150, 40, 20), cape=(140, 30, 20), hair=(240, 120, 30), hair_style='short', beard=(200, 90, 30), glow=(255, 200, 80), crown=(230, 170, 50), crown_gem=(255, 90, 40),
                 trim=(235, 120, 40), belt=(235, 120, 40), cracks=(255, 150, 50), crack_n=10, bare_hands=False)
    elif style == 'frost_lady':
        d.update(skin=(236, 220, 226), cloth=(120, 170, 220), cloth2=(235, 248, 255), hair=(240, 248, 255), hair_style='long', robe=True, crown=(190, 235, 255), crown_gem=(120, 200, 255),
                 trim=(235, 248, 255), belt=(70, 110, 170), glow=(150, 230, 255), glow_eyes=True, cape=(100, 150, 205))
    elif style == 'storm_captain':
        d.update(cloth=(36, 50, 96), cloth2=(235, 200, 70), pants=(30, 36, 64), boots=(30, 26, 30), hair=(70, 70, 86), hair_style='short', hat_wide=(30, 40, 80), beard=(90, 90, 100), emblem=(235, 200, 70),
                 trim=(235, 200, 70), belt=(70, 50, 30), cape=(60, 80, 140), glow=(255, 240, 120))
    elif style == 'druid':
        d.update(skin=(190, 150, 110), cloth=(70, 110, 54), cloth2=(150, 190, 80), hair=(110, 76, 44), hair_style='long', robe=True, antlers=(190, 160, 110), hood=None, moss=(100, 180, 70),
                 trim=(150, 190, 80), belt=(90, 60, 36), glow_eyes=True, glow=(190, 255, 110), cape=(60, 96, 48))
    elif style == 'oracle':
        d.update(skin=(220, 200, 230), cloth=(36, 20, 64), cloth2=(150, 90, 230), hood=(28, 14, 52), robe=True, veil=(60, 30, 100), glow_eyes=True, glow=(255, 240, 255), stars=(220, 170, 255), belt=(150, 90, 230), emblem=(210, 150, 255), big_glow=True)
    elif style == 'ghost_king':
        d.update(metal=(170, 190, 230), pauldrons=(210, 225, 255), cape=(120, 150, 220), crown=(230, 240, 255), crown_gem=(140, 190, 255), beard=(220, 230, 250), beard_long=6, beard_full=True, hair=(220, 230, 250), hair_style='long',
                 glow_eyes=True, glow=(160, 220, 255), alpha=175, trim=(230, 240, 255), skin=(190, 205, 235))
    # ---- mobs
    elif style == 'knight':
        steel = shade(p['metal'], 0.0)
        d.update(metal=steel if element != 'storm' else (150, 160, 180), pauldrons=p['dark'] if element != 'storm' else (70, 90, 150), helm=shade(steel, -0.1) if element != 'storm' else (160, 170, 190), helm_trim=p['accent'], visor=(14, 10, 12),
                 glow=p['glow'], cape=shade(p['dark'], -0.1), trim=p['main'], belt=p['accent'], cracks=p['light'] if element == 'flame' else None, crack_n=14, glow_lines=p['glow'] if element in ('flame', 'storm') else None, glow_n=8, horns=p['light'] if element == 'flame' else None)
    elif style == 'mage':
        d.update(cloth=p['dark'], cloth2=p['main'], hood=shade(p['dark'], -0.1), robe=True, glow_eyes=True, glow=p['glow'], trim=p['light'], belt=p['accent'], emblem=p['glow'], skin=(190, 175, 190), long_sleeves=True)
    elif style == 'wraith':
        d.update(cloth=p['main'], cloth2=p['dark'], hood=shade(p['dark'], -0.05), robe=True, tatter=True, glow_eyes=True, big_glow=True, glow=p['glow'], alpha=190, skin=shade(p['main'], 0.3), glow_lines=p['glow'], glow_n=14, mask=shade(p['dark'], -0.2))
    elif style == 'sprite':
        d.update(skin=p['light'], cloth=p['main'], cloth2=p['glow'], hair=p['glow'], hair_style='wild', glow_eyes=True, glow=(255, 255, 255), trim=p['glow'], glow_lines=p['glow'], glow_n=14, pants=p['dark'], boots=p['accent'])
    elif style == 'golem':
        d.update(skin=(98, 70, 44), cloth=(98, 70, 44), pants=(84, 60, 38), long_sleeves=True, moss=(80, 150, 60), glow_eyes=True, glow=(190, 255, 100), big_glow=True, hair=(60, 110, 44), hair_style='wild', cracks=(190, 255, 100), crack_n=14, boots=(70, 50, 32), belt=(80, 150, 60), antlers=(130, 96, 60))
    elif style == 'stalker':
        d.update(skin=(60, 40, 90), cloth=(26, 18, 40), pants=(20, 14, 32), boots=(16, 10, 24), hood=(20, 12, 34), glow_eyes=True, glow=(255, 120, 240), big_glow=True, glow_lines=(190, 90, 255), glow_n=22, long_sleeves=True, belt=(190, 90, 255))
    # ---- bosses
    elif style == 'boss_flame':
        d.update(metal=(34, 28, 32), pauldrons=(90, 24, 16), helm=(40, 32, 36), helm_trim=(255, 160, 40), visor=(10, 6, 8), glow=(255, 170, 50), cape=(120, 24, 12), horns=(220, 90, 30), cracks=(255, 140, 30), crack_n=60,
                 glow_lines=(255, 190, 70), glow_n=24, trim=(255, 120, 30), belt=(255, 170, 50), emblem=(255, 190, 70), crown=(255, 150, 40))
    elif style == 'boss_frost':
        d.update(skin=(205, 225, 245), cloth=(30, 60, 110), cloth2=(190, 235, 255), robe=True, hood=(24, 50, 96), glow_eyes=True, big_glow=True, glow=(170, 245, 255), crown=(190, 235, 255), crown_gem=(255, 255, 255), cracks=(200, 245, 255), crack_n=24,
                 trim=(190, 235, 255), belt=(120, 180, 240), emblem=(190, 245, 255), cape=(40, 80, 140), mask=(210, 230, 245), glow_lines=(190, 245, 255), glow_n=14, beard=(235, 248, 255), beard_long=7)
    elif style == 'boss_storm':
        d.update(skin=(215, 220, 240), cloth=(70, 80, 130), cloth2=(255, 235, 100), robe=True, hair=(235, 240, 255), hair_style='long', crown=(255, 230, 90), crown_gem=(120, 200, 255), glow_eyes=True, big_glow=True, glow=(255, 245, 140),
                 glow_lines=(255, 240, 120), glow_n=26, trim=(255, 235, 100), belt=(255, 235, 100), cape=(50, 60, 110), emblem=(255, 235, 100))
    elif style == 'boss_verdant':
        d.update(skin=(110, 160, 90), cloth=(60, 96, 44), cloth2=(240, 150, 190), robe=True, hair=(70, 140, 56), hair_style='long', antlers=(150, 110, 70), moss=(120, 200, 80), glow_eyes=True, big_glow=True, glow=(220, 255, 120),
                 belt=(120, 80, 44), cape=(44, 80, 36), trim=(240, 150, 190), glow_lines=(240, 150, 190), glow_n=10, crown=(240, 150, 190), cracks=(40, 70, 30), crack_n=20)
    elif style == 'boss_void':
        d.update(skin=(20, 12, 34), cloth=(14, 8, 26), cloth2=(160, 90, 255), robe=True, hood=(10, 6, 20), glow_eyes=True, big_glow=True, glow=(255, 255, 255), stars=(200, 140, 255), glow_lines=(190, 110, 255), glow_n=40,
                 trim=(160, 90, 255), belt=(160, 90, 255), emblem=(255, 220, 255), cape=(24, 10, 44), crown=(190, 110, 255), crown_gem=(255, 255, 255), mask=(18, 10, 30), tatter=True)
    else:
        raise ValueError(style)
    return {k: v for k, v in d.items() if v is not None}


# ------------------------------------------------------------------ armour layers (64x32 usage)
def armor_layers(element):
    p = ELEMENT_PAL[element]
    main, light, dark, glow, accent = p['main'], p['light'], p['dark'], p['glow'], p['accent']
    metal = p['metal']
    rnd = random.Random(sum(ord(ch) for ch in element))
    layers = []
    for idx in (1, 2):
        cv = Canvas(64, 32)

        def plate(part, face, extra=None):
            def fn(u, v, w, h):
                t = (u / max(1, w - 1))
                base = main if (u + v) % 7 else shade(main, -0.12)
                col = lit(shade(base, 0.12 if t < 0.34 else (-0.12 if t > 0.75 else 0)), face, u, v, w, h, rnd, 0.04)
                if extra:
                    r = extra(u, v, w, h)
                    if r:
                        return r
                return col
            paint(cv, part, face, fn)
        # helmet / head
        for face in PARTS['head']:
            plate('head', face, (lambda u, v, w, h: accent if v == 0 or (v == 7 and False) else (dark if (v in (3, 4)) and face == 'front' and 1 <= u <= 6 else None)) if face in ('front',) else (lambda u, v, w, h: accent if v == 0 else None))
        paint(cv, 'head', 'front', lambda u, v, w, h: glow if v == 3 and u in (2, 5) else None)
        for face in ('top',):
            paint(cv, 'head', face, lambda u, v, w, h: accent if u in (3, 4) else None)
        # hat layer = crest
        paint(cv, 'hat', 'top', lambda u, v, w, h: light if u in (3, 4) else None)
        paint(cv, 'hat', 'back', lambda u, v, w, h: light if u in (3, 4) and v < 5 else None)
        paint(cv, 'hat', 'left', lambda u, v, w, h: light if v == 0 and u > 1 else None)
        paint(cv, 'hat', 'right', lambda u, v, w, h: light if v == 0 and u > 1 else None)
        # body
        for face in PARTS['body']:
            plate('body', face, (lambda u, v, w, h: glow if (u in (3, 4) and v in (2, 3, 4)) else (accent if v == h - 4 and False else None)) if face == 'front' else None)
        paint(cv, 'body', 'front', lambda u, v, w, h: dark if v == 7 else None)
        for face in ('front', 'back', 'left', 'right'):
            paint(cv, 'body', face, lambda u, v, w, h: accent if v == h - 3 else None)
        # arms
        for face in PARTS['arm']:
            plate('arm', face, lambda u, v, w, h: accent if v == 4 else (shade(metal, 0.1) if v >= h - 3 else None))
        # legs
        for face in PARTS['leg']:
            plate('leg', face, lambda u, v, w, h: dark if (v == 1 and idx == 2) else (accent if v == h - 4 and idx == 1 else (shade(metal, -0.1) if v >= h - 3 and idx == 1 else None)))
        layers.append(cv)
    return layers


# ------------------------------------------------------------------ spider (64x32): head(32,4,8x8x8) body0(0,0,6x6x6) body1(0,12,10x8x12) leg(18,0,16x2x2)
def box_uv(w, h, d):
    """faces of a box at texOffs (0,0): returns dict face-> (x,y,w,h) relative."""
    return dict(top=(d, 0, w, d), bottom=(d + w, 0, w, d), right=(0, d, d, h), front=(d, d, w, h), left=(d + w, d, d, h), back=(d + w + d, d, w, h))


def paint_box(cv, tx, ty, w, h, d, fn):
    for face, (x0, y0, fw, fh) in box_uv(w, h, d).items():
        for v in range(fh):
            for u in range(fw):
                c = fn(face, u, v, fw, fh)
                if c is not None:
                    cv.put(tx + x0 + u, ty + y0 + v, c)


def spider(element):
    p = ELEMENT_PAL[element]
    cv = Canvas(64, 32)
    rnd = random.Random(5 + len(element))
    if element == 'frost':
        body, spot, eye = (70, 110, 150), (200, 240, 255), (150, 240, 255)
    else:
        body, spot, eye = (56, 90, 40), (190, 230, 90), (255, 150, 220)

    def base(face, u, v, w, h, c=body):
        col = lit(c, face, u, v, w, h, rnd, 0.07)
        if rnd.random() < 0.08:
            col = shade(spot, -0.2)
        return col
    paint_box(cv, 32, 4, 8, 8, 8, lambda f, u, v, w, h: eye if (f == 'front' and v in (2, 3) and u in (1, 2, 5, 6)) else base(f, u, v, w, h, shade(body, 0.05)))
    paint_box(cv, 0, 0, 6, 6, 6, lambda f, u, v, w, h: base(f, u, v, w, h))
    paint_box(cv, 0, 12, 10, 8, 12, lambda f, u, v, w, h: (spot if (f in ('top',) and (u + v) % 4 == 0) else base(f, u, v, w, h)))
    paint_box(cv, 18, 0, 16, 2, 2, lambda f, u, v, w, h: lit(shade(body, -0.1), f, u, v, w, h, rnd, 0.05) if (u % 5) else shade(spot, -0.25))
    return cv


# ------------------------------------------------------------------ particles (8x8 glow orbs)
def particle(color, core=(255, 255, 255), shape='orb'):
    cv = Canvas(8, 8)
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5)
            if shape == 'star':
                d = min(abs(x - 3.5) + abs(y - 3.5) * 1.8, abs(y - 3.5) + abs(x - 3.5) * 1.8)
            if d < 3.9:
                t = d / 3.9
                a = int(255 * (1 - t) ** 1.2)
                col = mix(core, color, min(1, t * 1.6))
                cv.put(x, y, col, max(0, min(255, a)))
    return cv
