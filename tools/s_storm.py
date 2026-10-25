"""Stormwatch Aerie - Storm dungeon: a copper-and-stone tower crowning a windswept mesa, reached by a grand stair."""
import math
from arch import *
import s_core

SITE_GATE = 7
BOSS = 2
G0 = 16            # natural ground
M = 18             # mesa height
START = (40, G0, 85)
ROD = 'minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]'


def trap(v, F2, th):
    y2 = F2 - 1
    for x in range(35, 55):
        for z in range(26, 55):
            if (x // 2 + z // 2) % 3 == 0 and 36 <= x <= 52 and 30 <= z <= 50 and (x, z) != (40, 40):
                v.set(x, y2, z, 'minecraft:blue_ice')
                if (x + z) % 5 == 0:
                    v.set(x, F2, z, 'minecraft:cobweb')
    for x in range(36, 55, 6):
        for z in range(34, 55, 6):
            if (x, z) != (40, 40) and x % 6 == 0:
                pillar(v, x, z, F2, F2 + 6, th['pal']['pillar'], th['pal']['cap'])
                v.set(x, F2 + 7, z, ROD)


def ring(vv, cx, cz, y, r):
    vv.ring(cx, y, cz, r - 5, 'minecraft:waxed_oxidized_cut_copper', 1.0)
    for i in range(8):
        a = i / 8 * math.tau
        x, z = round(cx + math.cos(a) * 8), round(cz + math.sin(a) * 8)
        vv.set(x, y + 1, z, 'minecraft:waxed_oxidized_copper')
        vv.set(x, y + 2, z, 'minecraft:waxed_oxidized_copper')
        vv.set(x, y + 3, z, ROD)


def crown(v, G, F3, th, R):
    top = F3 + 17
    for i in range(4):
        a = i / 4 * math.tau + math.pi / 4
        x, z = round(40 + math.cos(a) * 18), round(40 + math.sin(a) * 18)
        for y in range(top, top + 20):
            v.set(x, y, z, 'minecraft:waxed_oxidized_copper' if y % 5 else 'minecraft:waxed_exposed_copper')
        for k in range(3):
            v.set(x, top + 20 + k, z, ROD)
        # tapered base
        v.cone(x, z, top, 8, 3.0, 'minecraft:waxed_oxidized_cut_copper')
    # wind ring: floating glass hoops
    for k, yy in enumerate((top + 14, top + 22)):
        for i in range(48):
            a = i / 48 * math.tau
            v.set(round(40 + math.cos(a) * (22 - k * 3)), yy, round(40 + math.sin(a) * (22 - k * 3)), 'minecraft:light_blue_stained_glass' if i % 3 else 'minecraft:sea_lantern')


def build():
    v = Vox('stormwatch_aerie')
    rng = v.rng
    G = G0
    v.ground = G
    Gk = G + M
    BB = Mix(rng, ('minecraft:stone_bricks', 4), ('minecraft:polished_andesite', 2), ('minecraft:waxed_weathered_cut_copper', 2), ('minecraft:waxed_oxidized_cut_copper', 1))
    FL = Mix(rng, ('minecraft:polished_andesite', 3), ('minecraft:smooth_stone', 2), ('minecraft:stone_bricks', 2))
    ROCK = Mix(rng, ('minecraft:stone', 4), ('minecraft:andesite', 3), ('minecraft:tuff', 2), ('minecraft:cobblestone', 1))
    pal = dict(wall=BB, floor=FL, pillar='minecraft:purpur_pillar[axis=y]', cap='minecraft:waxed_oxidized_copper', base='minecraft:polished_andesite',
               trim='minecraft:waxed_exposed_cut_copper', accent='minecraft:waxed_oxidized_cut_copper', roof='minecraft:waxed_oxidized_cut_copper', lantern=lantern(True, True),
               pane='minecraft:cyan_stained_glass_pane', banner='cyan')
    th = dict(BB=BB, FL=FL, pal=pal, stair='minecraft:stone_brick_stairs', boss=BOSS, dname='stormwatch', mob1='realmbreak:gale_sentinel', mob2='realmbreak:storm_sprite',
              carpet='minecraft:cyan_carpet', dais='minecraft:waxed_oxidized_copper', throne='minecraft:waxed_oxidized_cut_copper', fuel='minecraft:soul_soil', fire='minecraft:soul_fire',
              channel='minecraft:waxed_oxidized_copper', glass='minecraft:cyan_stained_glass', trap=trap, ring=ring, crown=crown, spire=None)
    # ---- mesa (stacked discs, wider at the base, ragged edge)
    for y in range(2, Gk):
        r = 27 + (Gk - y) * 0.22
        for x in range(40 - 36, 40 + 37):
            for z in range(40 - 36, 40 + 37):
                d = math.hypot(x - 40, z - 40)
                jag = 1.6 * math.sin(math.atan2(z - 40, x - 40) * 5 + y * 0.35) + 1.2 * math.sin(math.atan2(z - 40, x - 40) * 11 - y * 0.2)
                if d <= r + jag:
                    v.set(x, y, z, ROCK())
    v.disc(40, Gk - 1, 40, 29, FL)
    v.ring(40, Gk - 1, 40, 29, pal['trim'], 1.0)
    # ---- grand stair (north-bound), parapets, lanterns
    sx0, sx1 = 37, 43
    n = M
    for i in range(n):
        z = 81 - i
        y = G + i
        for x in range(sx0 - 1, sx1 + 2):
            for yy in range(G - 3, y):
                v.set(x, yy, z, BB)
        for x in range(sx0, sx1 + 1):
            v.set(x, y, z, stair('minecraft:stone_brick_stairs', 'south'))
            for yy in range(y + 1, y + 5):
                v.air(x, yy, z)
        for x in (sx0 - 1, sx1 + 1):
            for yy in range(y, y + 2):
                v.set(x, yy, z, BB)
            v.set(x, y + 2, z, 'minecraft:stone_brick_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
            if i % 4 == 2:
                v.set(x, y + 3, z, lantern(False, True))
    for z in range(81 - n, 82 - n + 3):
        pass
    # approach path and plaza
    for z in range(82, 86):
        for x in range(sx0 - 1, sx1 + 2):
            for yy in range(G - 3, G):
                v.set(x, yy, z, BB)
            v.set(x, G - 1, z, FL)
    # air above the plaza between stair top and keep entrance
    for x in range(sx0, sx1 + 1):
        for z in range(60, 66):
            for yy in range(Gk, Gk + 6):
                v.air(x, yy, z)
    # ---- keep on the mesa
    info = s_core.keep(v, Gk, th, round_r=21, KH=34)
    # ---- mesa-edge storm masts and perimeter
    for i in range(12):
        a = i / 12 * math.tau
        x, z = round(40 + math.cos(a) * 28), round(40 + math.sin(a) * 28)
        if 34 <= x <= 46 and z > 40:
            continue
        for yy in range(Gk, Gk + 7):
            v.set(x, yy, z, pal['pillar'])
        v.set(x, Gk + 7, z, ROD)
        v.set(x, Gk + 6, z + (1 if z < 40 else -1), lantern(True, True))
    # hanging banners/pennants on the stair gate
    for dx in (-5, 5):
        pillar(v, 40 + dx, 63, Gk, Gk + 10, pal['pillar'], pal['cap'], pal['base'])
        v.set(40 + dx, Gk + 11, 63, ROD)
    v.landmark(40, G, 85, SITE_GATE)
    v.set(40, G - 1, 85, 'minecraft:chiseled_stone_bricks')
    for dx in (-2, 2):
        pillar(v, 40 + dx, 85, G, G + 4, pal['pillar'], pal['cap'])
        v.set(40 + dx, G + 5, 85, ROD)
    v.weather({'minecraft:stone_bricks': ['minecraft:cracked_stone_bricks', 'minecraft:mossy_stone_bricks']}, 0.05)
    v.info = info
    return v
