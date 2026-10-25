"""Frostspire Vault - Frost dungeon: round crystal-clad tower ringed by a frozen moat and six rim spires."""
import math
from arch import *
import s_core

SITE_GATE = 6
BOSS = 1
SNOW = 'minecraft:powder_snow'


def trap(v, F2, th):
    y2 = F2 - 1
    for x in range(35, 55):
        for z in range(26, 55):
            if (x // 2 + z // 2) % 3 == 0 and 36 <= x <= 52 and 30 <= z <= 50 and (x, z) != (40, 40):
                v.set(x, y2, z, 'minecraft:blue_ice')
                if (x + z) % 4 == 0:
                    v.set(x, F2, z, SNOW)
    for x in range(36, 55, 6):
        for z in range(34, 55, 6):
            if (x, z) != (40, 40) and x % 6 == 0:
                pillar(v, x, z, F2, F2 + 6, th['pal']['pillar'], th['pal']['cap'])


def ring(vv, cx, cz, y, r):
    vv.ring(cx, y, cz, r - 5, 'minecraft:blue_ice', 1.0)
    for i in range(8):
        a = i / 8 * math.tau
        x, z = round(cx + math.cos(a) * 8), round(cz + math.sin(a) * 8)
        for k in range(1, 4):
            vv.set(x, y + k, z, 'minecraft:packed_ice')
        vv.set(x, y + 4, z, 'minecraft:end_rod[facing=up]')


def crown(v, G, F3, th, R):
    top = F3 + 17
    for i in range(6):
        a = i / 6 * math.tau + 0.3
        x, z = round(40 + math.cos(a) * 17), round(40 + math.sin(a) * 17)
        h = 24 + (i % 3) * 8
        v.cone(x, z, top, h, 4.5, th['spire'])
        v.set(x, top + h, z, 'minecraft:sea_lantern')


def build():
    v = Vox('frostspire_vault')
    rng = v.rng
    G = 16
    v.ground = G
    BB = Mix(rng, ('minecraft:calcite', 3), ('minecraft:stone_bricks', 4), ('minecraft:snow_block', 1), ('minecraft:packed_ice', 2))
    FL = Mix(rng, ('minecraft:polished_diorite', 3), ('minecraft:packed_ice', 2), ('minecraft:stone_bricks', 2))
    SP = Mix(rng, ('minecraft:blue_ice', 3), ('minecraft:packed_ice', 3), ('minecraft:calcite', 1))
    pal = dict(wall=BB, floor=FL, pillar='minecraft:quartz_pillar[axis=y]', cap='minecraft:chiseled_quartz_block', base='minecraft:smooth_quartz',
               trim='minecraft:blue_ice', accent='minecraft:packed_ice', roof='minecraft:packed_ice', lantern=lantern(True, True),
               pane='minecraft:light_blue_stained_glass_pane', banner='light_blue')
    th = dict(BB=BB, FL=FL, pal=pal, stair='minecraft:stone_brick_stairs', boss=BOSS, dname='frostspire', mob1='realmbreak:rime_wraith', mob2='realmbreak:frost_crawler',
              carpet='minecraft:light_blue_carpet', dais='minecraft:blue_ice', throne='minecraft:packed_ice', fuel='minecraft:soul_soil', fire='minecraft:soul_fire',
              channel='minecraft:blue_ice', glass='minecraft:light_blue_stained_glass', trap=trap, ring=ring, crown=crown, spire=SP)
    # ---- platform
    SNOWM = Mix(rng, ('minecraft:snow_block', 5), ('minecraft:packed_ice', 2), ('minecraft:polished_diorite', 1))
    for y in range(2, G):
        v.disc(40, y, 40, 38, BB)
    for x in range(36, 45):
        for z in range(60, 81):
            for y in range(4, G):
                v.set(x, y, z, BB)
    v.disc(40, G - 1, 40, 38, SNOWM)
    for x in range(37, 44):
        for z in range(58, 81):
            v.set(x, G - 1, z, 'minecraft:polished_diorite' if (x + z) % 2 else 'minecraft:smooth_quartz')
    # frozen moat band
    for x in range(0, 81):
        for z in range(0, 81):
            d = math.hypot(x - 40, z - 40)
            if 28 <= d <= 33.5 and not (37 <= x <= 43 and z > 40):
                v.set(x, G - 1, z, 'minecraft:blue_ice' if (x * 7 + z * 3) % 5 == 0 else 'minecraft:packed_ice')
            elif 27 <= d < 28 or 33.5 < d <= 34.5:
                v.set(x, G - 1, z, 'minecraft:stone_bricks')
    v.set(40, G - 1, 40, BB)
    # ---- keep
    info = s_core.keep(v, G, th, round_r=21, KH=36)
    # ---- ice obelisks and crystals on the plaza
    for i in range(10):
        a = i / 10 * math.tau + 0.15
        x, z = round(40 + math.cos(a) * 30.5), round(40 + math.sin(a) * 30.5)
        if 36 <= x <= 44 and z > 40:
            continue
        h = 9 + (i % 4) * 4
        v.cone(x, z, G, h, 2.6, SP)
        v.set(x, G + h, z, 'minecraft:sea_lantern')
    for i in range(5):
        x, z = 40 + (i - 2) * 6, 66
        pillar(v, x, z, G, G + 6, pal['pillar'], pal['cap'], pal['base'])
        v.set(x, G + 7, z, 'minecraft:soul_lantern[hanging=false]')
    # outer gate arch
    for dx in (-3, 3):
        pillar(v, 40 + dx, 74, G, G + 9, pal['pillar'], pal['cap'], pal['base'])
    for x in range(36, 45):
        v.set(x, G + 10, 74, 'minecraft:blue_ice')
        v.set(x, G + 11, 74, BB)
    # landmark
    v.landmark(40, G, 79, SITE_GATE)
    v.set(40, G - 1, 79, 'minecraft:chiseled_quartz_block')
    for dx in (-2, 2):
        pillar(v, 40 + dx, 79, G, G + 4, pal['pillar'], pal['cap'])
        v.set(40 + dx, G + 5, 79, 'minecraft:soul_lantern[hanging=false]')
    v.weather({'minecraft:stone_bricks': ['minecraft:cracked_stone_bricks', 'minecraft:mossy_stone_bricks']}, 0.05)
    v.ruin(0.012, ymin=G + 30, only_names={'minecraft:packed_ice', 'minecraft:stone_bricks'})
    v.info = info
    return v
