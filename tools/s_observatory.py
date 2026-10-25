"""Hollow Observatory - Void dungeon (Rift): an amethyst-domed star-gazing tower on a floating island."""
import math
from arch import *
import s_core

SITE_GATE = 9
BOSS = 4
START = (40, 40, 79)
RC = 'realmbreak:rift_crystal_block'


def trap(v, F2, th):
    y2 = F2 - 1
    for x in range(35, 55):
        for z in range(26, 55):
            if (x // 2 + z // 2) % 3 == 0 and 36 <= x <= 52 and 30 <= z <= 50 and (x, z) != (40, 40):
                v.set(x, y2, z, 'minecraft:soul_sand')
                if (x + z) % 4 == 0:
                    v.set(x, F2, z, 'minecraft:amethyst_cluster[facing=up,waterlogged=false]')
    for x in range(36, 55, 6):
        for z in range(34, 55, 6):
            if (x, z) != (40, 40) and x % 6 == 0:
                pillar(v, x, z, F2, F2 + 6, th['pal']['pillar'], th['pal']['cap'])
                v.set(x, F2 + 5, z + 1, RC)


def ring(vv, cx, cz, y, r):
    vv.ring(cx, y, cz, r - 5, RC, 1.0)
    for i in range(8):
        a = i / 8 * math.tau
        x, z = round(cx + math.cos(a) * 8), round(cz + math.sin(a) * 8)
        for k in range(1, 4):
            vv.set(x, y + k, z, 'minecraft:amethyst_block')
        vv.set(x, y + 4, z, 'minecraft:end_rod[facing=up]')


def crown(v, G, F3, th, R):
    top = F3 + 17
    # orrery rings of floating crystals
    for k, (rr, yy) in enumerate(((28, top + 10), (22, top + 18), (16, top + 26))):
        n = 6 + k * 2
        for i in range(n):
            a = i / n * math.tau + k
            x, z = round(40 + math.cos(a) * rr), round(40 + math.sin(a) * rr)
            v.sphere(x, yy, z, 2, 2, 2, RC)
            v.set(x, yy + 3, z, 'minecraft:end_rod[facing=up]')
        for i in range(72):
            a = i / 72 * math.tau
            v.set(round(40 + math.cos(a) * rr), yy, round(40 + math.sin(a) * rr), 'minecraft:purple_stained_glass')
    # great telescope: copper tube on a pier
    for y in range(top, top + 6):
        v.set(22, y, 58, 'realmbreak:riftstone_pillar[axis=y]')
    v.line((22, top + 6, 58), (8, top + 24, 76), 'minecraft:copper_block', th=1)
    v.set(8, top + 24, 76, 'minecraft:end_rod[facing=up]')


def build():
    v = Vox('hollow_observatory')
    rng = v.rng
    G = 40
    v.ground = G
    BB = Mix(rng, ('realmbreak:riftstone_bricks', 5), ('minecraft:deepslate_bricks', 2), ('minecraft:amethyst_block', 1), ('minecraft:purpur_block', 1))
    FL = Mix(rng, ('realmbreak:riftstone', 3), ('minecraft:polished_deepslate', 2), ('minecraft:purpur_block', 1))
    pal = dict(wall=BB, floor=FL, pillar='realmbreak:riftstone_pillar[axis=y]', cap='realmbreak:chiseled_riftstone', base='realmbreak:riftstone',
               trim='realmbreak:chiseled_riftstone', accent='realmbreak:null_bricks', roof='minecraft:purple_stained_glass', lantern=lantern(True, True),
               pane='minecraft:purple_stained_glass_pane', banner='purple')
    th = dict(BB=BB, FL=FL, pal=pal, stair='minecraft:stone_brick_stairs', boss=BOSS, dname='observatory', mob1='realmbreak:void_acolyte', mob2='realmbreak:rift_stalker',
              carpet='minecraft:purple_carpet', dais='realmbreak:null_rune', throne='realmbreak:chiseled_riftstone', fuel='minecraft:soul_soil', fire='minecraft:soul_fire',
              channel=RC, glass='minecraft:purple_stained_glass', trap=trap, ring=ring, crown=crown, spire=None, turrets=False)
    # ---- floating island: inverted cone of riftstone under a turfed plateau
    ROCK = Mix(rng, ('realmbreak:riftstone', 5), ('minecraft:deepslate', 2), ('minecraft:tuff', 1), ('minecraft:calcite', 1))
    for y in range(G - 34, G):
        t = (y - (G - 34)) / 34.0
        r = 6 + (44 - 6) * (t ** 0.65)
        for x in range(40 - 45, 40 + 46):
            for z in range(40 - 45, 40 + 46):
                d = math.hypot(x - 40, z - 40)
                jag = 2.0 * math.sin(math.atan2(z - 40, x - 40) * 6 + y * 0.4) * (1 - t * 0.5)
                if d <= r + jag:
                    v.set(x, y, z, ROCK())
    v.disc(40, G - 1, 40, 42, 'realmbreak:rift_turf')
    for x in range(36, 45):
        for z in range(60, 81):
            v.set(x, G - 2, z, 'realmbreak:riftstone')
    for x in range(37, 44):
        for z in range(58, 82):
            v.set(x, G - 1, z, 'realmbreak:riftstone_bricks' if (x + z) % 2 else 'realmbreak:chiseled_riftstone')
    # tapering stalactite crystals under the island
    for i in range(7):
        a = i / 7 * math.tau
        x, z = round(40 + math.cos(a) * 9), round(40 + math.sin(a) * 9)
        v.cone(x, z, G - 52, 20, 2.4, RC) if False else None
    info = s_core.keep(v, G, th, round_r=21, KH=34)
    # ---- plaza dressing: crystal pylons and glow blooms
    for i in range(8):
        a = i / 8 * math.tau + 0.2
        x, z = round(40 + math.cos(a) * 33), round(40 + math.sin(a) * 33)
        if 34 <= x <= 46 and z > 40:
            continue
        for y in range(G, G + 8):
            v.set(x, y, z, 'realmbreak:riftstone_pillar[axis=y]')
        v.sphere(x, G + 9, z, 2, 2, 2, RC)
    for z in range(62, 80, 4):
        for x in (36, 44):
            v.set(x, G, z, 'minecraft:deepslate_brick_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
            v.set(x, G + 1, z, lantern(False, True))
    v.landmark(40, G, 79, SITE_GATE)
    for dx in (-2, 2):
        pillar(v, 40 + dx, 79, G, G + 5, pal['pillar'], pal['cap'])
        v.set(40 + dx, G + 6, 79, RC)
    v.info = info
    return v
