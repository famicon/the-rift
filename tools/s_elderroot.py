"""Elderroot Sanctum - Verdant dungeon: a colossal hollow tree with flared roots, a glowing canopy and a heart-chamber arena."""
import math
from arch import *
import s_core

SITE_GATE = 8
BOSS = 3
LEAF = 'minecraft:oak_leaves[distance=1,persistent=true,waterlogged=false]'
LEAF2 = 'minecraft:flowering_azalea_leaves[distance=1,persistent=true,waterlogged=false]'
LEAF3 = 'minecraft:azalea_leaves[distance=1,persistent=true,waterlogged=false]'
BUSH = 'minecraft:sweet_berry_bush[age=3]'
FIRE = 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]'


def trap(v, F2, th):
    y2 = F2 - 1
    for x in range(35, 55):
        for z in range(26, 55):
            if (x // 2 + z // 2) % 3 == 0 and 36 <= x <= 52 and 30 <= z <= 50 and (x, z) != (40, 40):
                v.set(x, y2, z, 'minecraft:moss_block')
                if (x + z) % 3 == 0:
                    v.set(x, F2, z, BUSH)
                elif (x + z) % 7 == 0:
                    v.set(x, F2, z, 'minecraft:cobweb')
    for x in range(36, 55, 6):
        for z in range(34, 55, 6):
            if (x, z) != (40, 40) and x % 6 == 0:
                pillar(v, x, z, F2, F2 + 6, th['pal']['pillar'], th['pal']['cap'])
                v.set(x, F2 + 5, z + 1, 'minecraft:shroomlight')


def ring(vv, cx, cz, y, r):
    vv.ring(cx, y, cz, r - 5, 'minecraft:moss_block', 1.0)
    for i in range(8):
        a = i / 8 * math.tau
        x, z = round(cx + math.cos(a) * 8), round(cz + math.sin(a) * 8)
        for k in range(1, 4):
            vv.set(x, y + k, z, 'minecraft:stripped_mangrove_log[axis=y]')
        vv.set(x, y + 4, z, 'minecraft:shroomlight')


def crown(v, G, F3, th, R):
    top = F3 + 17
    rng = v.rng

    def leaves(x, y, z):
        r = rng.random()
        return LEAF if r < 0.55 else (LEAF2 if r < 0.8 else (LEAF3 if r < 0.96 else 'minecraft:shroomlight'))
    v.sphere(40, top - 3, 40, 36, 20, 36, None, hollow=True, upper=True, w=3.0, fn=leaves)
    for i in range(6):
        a = i / 6 * math.tau + 0.4
        x, z = round(40 + math.cos(a) * 30), round(40 + math.sin(a) * 30)
        v.sphere(x, top - 8, z, 14, 10, 14, None, hollow=True, upper=True, w=2.5, fn=leaves)
    # great boughs: thick logs from the trunk rim up into the canopy
    for i in range(6):
        a = i / 6 * math.tau + 0.4
        p0 = (round(40 + math.cos(a) * 20), top - 2, round(40 + math.sin(a) * 20))
        p1 = (round(40 + math.cos(a) * 30), top + 6, round(40 + math.sin(a) * 30))
        v.line(p0, p1, 'minecraft:dark_oak_log[axis=y]', th=1)
    # clear the oculus again
    for y in range(top - 2, top + 20):
        v.disc(40, y, 40, 3, 'air')


def mushroom(v, x, z, y, h, r):
    for k in range(h):
        v.set(x, y + k, z, 'minecraft:mushroom_stem')
    v.sphere(x, y + h, z, r, max(2, r // 2 + 1), r, 'minecraft:red_mushroom_block', upper=True)
    for dx, dz in ((r - 1, 0), (-(r - 1), 0), (0, r - 1), (0, -(r - 1))):
        v.set(x + dx, y + h + 1, z + dz, 'minecraft:white_mushroom_block')


def build():
    v = Vox('elderroot_sanctum')
    rng = v.rng
    G = 16
    v.ground = G
    BB = Mix(rng, ('minecraft:dark_oak_log[axis=y]', 5), ('minecraft:mangrove_log[axis=y]', 2), ('minecraft:stripped_dark_oak_log[axis=y]', 1), ('minecraft:moss_block', 1), ('minecraft:spruce_log[axis=y]', 1))
    FL = Mix(rng, ('minecraft:dark_oak_planks', 3), ('minecraft:spruce_planks', 2), ('minecraft:moss_block', 1))
    pal = dict(wall=BB, floor=FL, pillar='minecraft:stripped_mangrove_log[axis=y]', cap='minecraft:mossy_stone_bricks', base='minecraft:mossy_stone_bricks',
               trim='minecraft:stripped_dark_oak_wood[axis=y]', accent='minecraft:moss_block', roof=lambda: LEAF2, lantern=lantern(True, False),
               pane='minecraft:lime_stained_glass_pane', banner='green')
    th = dict(BB=BB, FL=FL, pal=pal, stair='minecraft:dark_oak_stairs', boss=BOSS, dname='elderroot', mob1='realmbreak:thorn_stalker', mob2='realmbreak:bark_guardian',
              carpet='minecraft:green_carpet', dais='minecraft:moss_block', throne='minecraft:stripped_mangrove_log[axis=y]', fuel='minecraft:mossy_cobblestone', fire=FIRE,
              channel='minecraft:rooted_dirt', glass='minecraft:lime_stained_glass', trap=trap, ring=ring, crown=crown, spire=None, turrets=False)
    # ---- ground disc
    GR = Mix(rng, ('minecraft:grass_block', 5), ('minecraft:moss_block', 3), ('minecraft:podzol', 2), ('minecraft:coarse_dirt', 1))
    for y in range(3, G - 1):
        v.disc(40, y, 40, 37, 'minecraft:dirt')
    v.disc(40, G - 1, 40, 37, GR)
    for x in range(36, 45):
        for z in range(60, 81):
            for y in range(4, G - 1):
                v.set(x, y, z, 'minecraft:dirt')
    for x in range(37, 44):
        for z in range(58, 81):
            v.set(x, G - 1, z, 'minecraft:spruce_planks' if (x + z) % 3 else 'minecraft:stripped_spruce_log[axis=y]')
    # ---- tree keep
    info = s_core.keep(v, G, th, round_r=21, KH=36)
    # ---- flared roots
    for i in range(9):
        a = i / 9 * math.tau + 0.2
        for k in range(3):
            aa = a + (k - 1) * 0.12
            p0 = (round(40 + math.cos(aa) * 21), G + 12 - k * 2, round(40 + math.sin(aa) * 21))
            pm = (round(40 + math.cos(aa) * 28), G + 3, round(40 + math.sin(aa) * 28))
            p1 = (round(40 + math.cos(aa) * 35), G - 2, round(40 + math.sin(aa) * 35))
            v.line(p0, pm, 'minecraft:dark_oak_log[axis=y]', th=2 if k == 1 else 1)
            v.line(pm, p1, 'minecraft:dark_oak_log[axis=y]', th=1)
    # re-open the doorway the roots may have covered
    for y in range(G, G + 9):
        for x in range(35, 46):
            hh = 9 - (abs(x - 40) ** 2) // 3
            if y - G < hh:
                for z in range(56, 67):
                    v.air(x, y, z)
    # ---- giant mushrooms + lanterns around the glade
    for (x, z, h, r) in ((14, 56, 8, 5), (66, 52, 10, 6), (18, 22, 7, 4), (62, 20, 9, 5), (30, 70, 6, 4), (52, 72, 7, 4)):
        mushroom(v, x, z, G, h, r)
    for z in range(62, 80, 4):
        for x in (36, 44):
            v.set(x, G, z, 'minecraft:mossy_stone_brick_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
            v.set(x, G + 1, z, lantern(False, False))
    v.landmark(40, G, 79, SITE_GATE)
    v.set(40, G - 1, 79, 'minecraft:mossy_stone_bricks')
    for dx in (-2, 2):
        pillar(v, 40 + dx, 79, G, G + 5, pal['pillar'], pal['cap'])
        v.set(40 + dx, G + 6, 79, 'minecraft:shroomlight')
    v.info = info
    return v
