"""Shared dungeon keep: great hall -> F1 spawner chambers -> F2 trap hall -> F3 boss arena, plus a basement vault.
Same verified geometry as Cinderhold (interior x/z 26..54, three stacked switchbacks on the west strip).
th = theme dict.  round_r: if set, the shell is a cylinder (radius round_r) instead of a rectangle."""
import math
from arch import *


def keep(v, G, th, round_r=None, KH=34, arena_r=12):
    BB, FL, pal = th['BB'], th['FL'], th['pal']
    stair_blk = th['stair']
    boss = th['boss']
    kx0, kz0, kx1, kz1 = 24, 24, 56, 56
    cx = cz = 40
    F1, F2, F3 = G + 13, G + 23, G + 33
    R = round_r
    loot = f"realmbreak:chests/{th['dname']}_loot"
    vloot = f"realmbreak:chests/{th['dname']}_vault"
    # ---------------- shell
    if R:
        v.cyl(cx, cz, G, G + KH, R + 2, None, fn=None) if False else None
        for y in range(G, G + KH + 1):
            v.disc(cx, y, cz, R + 2, BB)
        for y in range(G + 1, G + KH):
            v.disc(cx, y, cz, R, 'air')
        for y in range(G + 11, G + KH, 11):
            v.ring(cx, y, cz, R + 3, pal['trim'], 1.0)
        n = 14
        for i in range(n):
            a = i / n * math.tau
            x, z = round(cx + math.cos(a) * (R + 3)), round(cz + math.sin(a) * (R + 3))
            for y in range(G, G + KH):
                v.set(x, y, z, pal['pillar'])
            v.set(x, G + KH, z, pal['cap'])
    else:
        keep_shell(v, kx0, kz0, kx1, kz1, G, KH + 1, pal, wall_t=2, pilaster=8, trim_every=11)
    # ---------------- floors
    def slab_floor(y):
        if R:
            v.disc(cx, y, cz, R, FL)
        else:
            floor_slab(v, kx0 + 2, kz0 + 2, kx1 - 2, kz1 - 2, y, pal)
    for fy in (F1, F2, F3):
        slab_floor(fy - 1)
    def carve(y0, y1):
        if R:
            v.cylair(cx, cz, y0, y1, R - 1)
        else:
            v.carve(kx0 + 2, y0, kz0 + 2, kx1 - 2, y1, kz1 - 2)
    carve(G, F1 - 2)
    slab_floor(G - 1)
    for z in range(kz0 + 2, kz1 - 1):
        for x in (39, 40, 41):
            v.set(x, G, z, th.get('carpet', 'minecraft:red_carpet'))
    for x in range(kx0 + 6, kx1 - 4, 6):
        for z in (kz0 + 6, kz1 - 6):
            pillar(v, x, z, G, F1 - 2, pal['pillar'], pal['cap'], pal['base'])
            v.set(x, F1 - 4, z + (1 if z < 40 else -1), pal['lantern'])
    for x in range(kx0 + 5, kx1 - 3, 6):
        chandelier(v, x, F1 - 2, 40, pal, drop=4)
    # throne / dais at the north end of the hall
    for x in range(35, 46):
        for z in range(kz0 + 2, kz0 + 8):
            v.set(x, G, z, pal['accent'])
    for x in range(37, 44):
        for z in range(kz0 + 2, kz0 + 6):
            v.set(x, G + 1, z, th['dais'])
    v.set(40, G + 2, kz0 + 3, stair(th['stair'], 'south'))
    v.set(40, G + 3, kz0 + 2, th['throne']); v.set(40, G + 4, kz0 + 2, th['throne'])
    for dx in (-3, 3):
        brazier(v, 40 + dx, G + 2, kz0 + 4, th['fuel'], th['fire'])
    # decorative hall channels
    for z in range(kz0 + 12, kz1 - 8):
        for x in (31, 49):
            v.set(x, G - 1, z, th['channel'])
    # entrance (south), carved straight through whatever the shell is
    ez0, ez1 = (cz + R - 1, cz + R + 4) if R else (kz1 - 2, kz1 + 2)
    for y in range(G, G + 9):
        for x in range(36, 45):
            hh = 8 - (abs(x - 40) ** 2) // 3
            if y - G < hh:
                for z in range(ez0, ez1 + 1):
                    v.air(x, y, z)
    v.arch('x', 36, 44, G + 4, ez0, ez1 - ez0 + 1, pal['trim'], pointed=True, thick=1)
    # windows
    if R:
        glass = th.get('glass', pal['pane'].replace('_pane', ''))
        for story_y in (G + 3, F1 + 2, F2 + 2):
            for i in range(20):
                a = (i + 0.5) / 20 * math.tau
                if story_y == G + 3 and math.sin(a) > 0.85:
                    continue
                for rr in (R, R + 1):
                    x, z = round(cx + math.cos(a) * rr), round(cz + math.sin(a) * rr)
                    for y in range(story_y, story_y + 5):
                        v.set(x, y, z, glass)
    else:
        for story_y in (G + 3, F1 + 2, F2 + 2):
            for a in range(kx0 + 6, kx1 - 4, 8):
                window(v, 'z', kz0, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                if not (story_y == G + 3 and 34 <= a <= 46):
                    window(v, 'z', kz1 - 1, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                window(v, 'x', kx0, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                window(v, 'x', kx1 - 1, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
        if th.get('turrets', True):
            for (tx, tz) in ((kx0 - 1, kz0 - 1), (kx1 + 1, kz0 - 1), (kx0 - 1, kz1 + 1), (kx1 + 1, kz1 + 1)):
                tower(v, tx, tz, G, 6, 44, BB, pal, floors=(10, 20, 30), roof='cone', roof_h=20, glass=pal['pane'], slits=True)
    # ---------------- upper floors
    sx = 27
    carve(F1, F1 + 8); carve(F2, F2 + 7); carve(F3, F3 + 17)
    def chamber(x0, z0, x1, z1, ent):
        spawner_room(v, x0, z0, x1, z1, F1 - 1, 8, pal, ent, loot)
    chamber(44, 28, 54, 38, th['mob1'])
    chamber(44, 42, 54, 52, th['mob2'])
    for y in range(F1, F1 + 3):
        for zz in (33, 34, 47, 48):
            v.air(44, y, zz)
    for x in range(34, 44, 4):
        chandelier(v, x, F1 + 7, 40, pal, drop=2)
    for x in range(34, 44):
        for z in range(34, 46):
            v.set(x, F1 - 1, z, FL)
    # F2 hazard hall
    th['trap'](v, F2, th)
    for x in range(kx0 + 12, kx1 - 5, 8):
        chandelier(v, x, F2 + 7, 40, pal, drop=3)
    for (x, z) in ((kx1 - 4, 46), (kx1 - 4, 34)):
        v.chest(x, F2, z, 'west', loot)
    v.spawner(38, F2, 46, th['mob2']); v.spawner(44, F2, 34, th['mob1'])
    # F3 arena
    arena(v, 40, 40, F3 - 1, arena_r, 18, pal, boss, ring_fn=th['ring'], dome=True)
    # stairs last
    switchback(v, sx, 27, G, 13, 'z', 1, 2, stair_blk, landing=BB)
    switchback(v, sx, 37, F1, 10, 'z', 1, 2, stair_blk, landing=BB)
    switchback(v, sx, 45, F2, 10, 'z', 1, 2, stair_blk, landing=BB)
    for x in range(sx + 3, 36):
        for z in range(47, 50):
            v.set(x, F3 - 1, z, pal['floor'])
            for y in range(F3, F3 + 4):
                v.air(x, y, z)
    # roof
    if R:
        for x in range(cx - R - 2, cx + R + 3):
            for z in range(cz - R - 2, cz + R + 3):
                d = math.hypot(x - cx, z - cz)
                if arena_r + 1 < d <= R + 2:
                    v.set(x, F3 + 17, z, BB)
    else:
        for x in range(kx0, kx1 + 1):
            for z in range(kz0, kz1 + 1):
                if v.get(x, F3 + 19, z) is None and math.hypot(x - 40, z - 40) > 16:
                    v.set(x, F3 + 17, z, BB)
        crenellate_rect(v, kx0, kz0, kx1, kz1, F3 + 18, BB)
    th['crown'](v, G, F3, th, R)
    # ---------------- basement vault
    VY = G - 15
    foundation(v, 30, VY - 1, 30, 50, VY - 1, 0, BB)
    vault(v, 33, 33, 47, 47, VY, 8, pal, loot, vloot, facing='south')
    v.fill(48, VY, 28, 56, VY, 52, None, fn=lambda x, y, z: BB())
    v.carve(49, VY + 1, 33, 54, G - 2, 45)
    switchback(v, 49, 33, VY + 1, G - VY - 1, 'z', 1, 3, stair_blk, landing=BB)
    for y in range(VY + 1, VY + 4):
        for z in range(33, 36):
            v.air(47, y, z); v.air(48, y, z)
    for y in range(VY + 1, VY + 4):
        v.set(47, y, 34, 'minecraft:iron_bars')
    return dict(G=G, F1=F1, F2=F2, F3=F3, VY=VY)


def check(v, G, info, start):
    import walk
    G = info['G']
    F1, F2, F3, VY = info['F1'], info['F2'], info['F3'], info['VY']
    res, n = walk.check(v, start, {'altar': (40, F3, 40), 'vault_chest': (40, VY + 2, 40), 'hall': (40, G, 40), 'f1': (40, F1, 40),
                                    'f2': (40, F2, 36), 'sp1': (44, F1, 33), 'sp2': (36, F2, 46)})
    return res
