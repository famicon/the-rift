"""Seven overworld landmarks: giant, readable silhouettes with a landmark stone and some loot."""
import math
from arch import *

G = 4
LOOT = 'realmbreak:chests/ruins'
FIRE = 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]'


def ground(v, size, blk, r=None):
    for y in range(1, G - 1):
        for x in range(size):
            for z in range(size):
                if r is None or math.hypot(x - size / 2, z - size / 2) <= r:
                    v.set(x, y, z, 'minecraft:dirt')
    for x in range(size):
        for z in range(size):
            if r is None or math.hypot(x - size / 2, z - size / 2) <= r:
                v.set(x, G - 1, z, blk() if callable(blk) else blk)


def standing_stones():
    v = Vox('standing_stone_ring'); v.ground = G; rng = v.rng
    S = 41
    M = Mix(rng, ('minecraft:stone_bricks', 3), ('minecraft:mossy_stone_bricks', 2), ('minecraft:andesite', 2), ('minecraft:cobblestone', 1))
    ground(v, S, Mix(rng, ('minecraft:grass_block', 6), ('minecraft:mossy_cobblestone', 1), ('minecraft:podzol', 1)), 20)
    c = 20
    n = 12
    for i in range(n):
        a = i / n * math.tau
        x, z = round(c + math.cos(a) * 14), round(c + math.sin(a) * 14)
        h = 7 + (i % 3) * 2
        for dx in (0, 1):
            for dz in (0, 1):
                for y in range(G, G + h - (dx + dz)):
                    v.set(x + dx, y, z + dz, M())
        v.set(x, G + h, z, 'minecraft:sea_lantern') if i % 3 == 0 else None
    # lintels on pairs
    for i in range(0, n, 2):
        a0, a1 = i / n * math.tau, (i + 1) / n * math.tau
        p0 = (round(c + math.cos(a0) * 14), round(c + math.sin(a0) * 14)); p1 = (round(c + math.cos(a1) * 14), round(c + math.sin(a1) * 14))
        h = 7 + (i % 3) * 2
        v.line((p0[0], G + 7, p0[1]), (p1[0], G + 7, p1[1]), 'minecraft:chiseled_stone_bricks', th=0) if i % 4 == 0 else None
    for r in (4, 8):
        v.ring(c, G - 1, c, r, 'minecraft:chiseled_stone_bricks', 1.0)
    v.disc(c, G - 1, c, 3, 'minecraft:polished_andesite')
    v.landmark(c, G, c, 10)
    for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3)):
        brazier(v, c + dx, G, c + dz, 'minecraft:mossy_cobblestone', FIRE)
    v.chest(c + 2, G, c + 2, 'north', LOOT)
    v.weather({'minecraft:stone_bricks': ['minecraft:cracked_stone_bricks']}, 0.1)
    return v


def dragon_bones():
    v = Vox('dragon_bones'); v.ground = G; rng = v.rng
    W, L = 31, 71
    B = Mix(rng, ('minecraft:bone_block[axis=y]', 6), ('minecraft:calcite', 1), ('minecraft:diorite', 1))
    for y in range(1, G - 1):
        for x in range(W):
            for z in range(L):
                v.set(x, y, z, 'minecraft:dirt')
    for x in range(W):
        for z in range(L):
            v.set(x, G - 1, z, Mix(rng, ('minecraft:coarse_dirt', 3), ('minecraft:sand', 2), ('minecraft:red_sand', 1), ('minecraft:terracotta', 1))())
    cx = 15
    # spine: arched vertebrae along z
    for z in range(8, 64):
        t = (z - 8) / 55.0
        y = G + 1 + round(3 * math.sin(t * math.pi))
        v.set(cx, y, z, B()); v.set(cx, y + 1, z, B()) if z % 3 == 0 else None
        # ribs
        if z % 3 == 0 and 14 < z < 52:
            rh = 7 - abs(z - 33) // 5
            for side in (-1, 1):
                for k in range(rh + 1):
                    ang = k / rh * math.pi * 0.85
                    x = cx + side * round(math.sin(ang) * (rh - 1))
                    yy = y - 1 + round(math.cos(ang) * 0) + round(k * 0.6) if False else y + round(math.cos(ang) * rh) - rh + 1 + rh
                    v.set(x, G + 1 + round((1 - math.cos(ang)) * 0 + math.sin(ang * 0.5) * 0), z, B()) if False else None
                    yy = G + 1 + round(math.sin(ang) * rh * 0.9)
                    xx = cx + side * round((1 - math.cos(ang)) * (rh * 0.9) + 1)
                    v.set(xx, yy, z, B())
    # tail taper
    for z in range(56, 70):
        y = G + 1 - (z - 56) // 6
        v.set(cx, max(G, y), z, B())
    # skull at z=0..9
    for x in range(cx - 4, cx + 5):
        for z in range(0, 9):
            for y in range(G, G + 6):
                shell = x in (cx - 4, cx + 4) or z in (0, 8) or y in (G + 5,) or (y == G)
                if y == G + 5 and (x - cx) ** 2 + (z - 4) ** 2 > 14 + 8:
                    continue
                if shell:
                    v.set(x, y, z, B())
                else:
                    v.air(x, y, z)
    for dx in (-2, 2):
        v.set(cx + dx, G + 3, 0, 'minecraft:black_concrete'); v.set(cx + dx, G + 3, 1, 'minecraft:black_concrete')
    for x in range(cx - 3, cx + 4, 2):
        v.set(x, G + 1, 0, 'minecraft:bone_block[axis=x]'); v.set(x, G + 2, 0, 'minecraft:bone_block[axis=x]') if False else None
    for dx in (-3, -1, 1, 3):
        v.air(cx + dx, G + 1, 0) if False else None
    # horns
    for side in (-1, 1):
        for k in range(8):
            v.set(cx + side * (4 + k // 2), G + 5 + k, 7 + k // 3, B())
    v.chest(cx, G + 1, 5, 'south', LOOT)
    v.chest(cx - 2, G + 1, 4, 'south', LOOT)
    v.landmark(cx, G, 11, 11)
    v.weather({'minecraft:bone_block[axis=y]': []}, 0)
    return v


def watchtower():
    v = Vox('ruined_watchtower'); v.ground = G; rng = v.rng
    S = 31
    ground(v, S, Mix(rng, ('minecraft:grass_block', 5), ('minecraft:cobblestone', 1), ('minecraft:gravel', 1)), 15)
    M = Mix(rng, ('minecraft:stone_bricks', 4), ('minecraft:mossy_stone_bricks', 2), ('minecraft:cracked_stone_bricks', 2), ('minecraft:cobblestone', 1))
    pal = dict(floor=Mix(rng, ('minecraft:stone_bricks', 1), ('minecraft:oak_planks', 1)), trim='minecraft:chiseled_stone_bricks', roof='minecraft:stone_brick_slab', pane='minecraft:iron_bars')
    c = 15
    tower(v, c, c, G, 6, 26, M, pal, floors=(8, 16), roof='battlement', slits=True)
    # entrance
    for y in range(G, G + 3):
        for x in (c - 1, c, c + 1):
            for z in range(c + 3, c + 8):
                v.air(x, y, z)
    # ladders inside
    for y in range(G, G + 25):
        v.set(c - 3, y, c, 'minecraft:ladder[facing=east,waterlogged=false]')
    for f in (8, 16, 24):
        v.air(c - 3, G + f, c) if f < 24 else None
    for f in (8, 16):
        v.air(c - 3, G + f, c)
        v.air(c - 3, G + f - 1, c) if False else None
        v.air(c - 2, G + f, c)
    v.chest(c + 2, G + 8 + 1, c, 'west', LOOT)
    v.chest(c + 2, G + 16 + 1, c + 1, 'west', LOOT)
    v.landmark(c, G, c + 10, 12)
    v.set(c, G - 1, c + 10, 'minecraft:chiseled_stone_bricks')
    v.spawner(c, G + 17, c - 2, 'minecraft:skeleton')
    v.ruin(0.05, ymin=G + 18, only_names={'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:cobblestone'})
    # fallen rubble
    for i in range(30):
        x, z = c + rng.randint(-11, 11), c + rng.randint(-11, 11)
        if math.hypot(x - c, z - c) > 8 and v.get(x, G, z) is None:
            v.set(x, G, z, M())
    return v


def colossus():
    v = Vox('sleeping_colossus'); v.ground = G; rng = v.rng
    W, L = 41, 81
    M = Mix(rng, ('minecraft:stone', 4), ('minecraft:mossy_cobblestone', 2), ('minecraft:andesite', 2), ('minecraft:moss_block', 1), ('minecraft:cobblestone', 1))
    for y in range(1, G - 1):
        for x in range(W):
            for z in range(L):
                v.set(x, y, z, 'minecraft:dirt')
    for x in range(W):
        for z in range(L):
            v.set(x, G - 1, z, Mix(rng, ('minecraft:grass_block', 6), ('minecraft:moss_block', 1))())
    cx = 20
    # torso (hollow, z 28..60), head (z 8..26), legs, arms
    v.sphere(cx, G + 2, 44, 13, 11, 18, M, hollow=True, upper=True, w=2.0)
    v.sphere(cx, G + 3, 17, 8, 9, 9, M, hollow=True, upper=True, w=2.0)
    for side in (-1, 1):
        v.sphere(cx + side * 17, G + 1, 38, 4, 5, 15, M, upper=True)    # arms
        v.sphere(cx + side * 6, G + 1, 70, 5, 5, 13, M, upper=True)     # legs
        v.sphere(cx + side * 17, G + 1, 24, 5, 5, 5, M, upper=True)     # fists
    # carved face
    for dx in (-3, 3):
        for y in (G + 7, G + 8):
            v.set(cx + dx, y, 9, 'minecraft:obsidian')
        v.set(cx + dx, G + 7, 8, 'minecraft:glowstone')
    for x in range(cx - 2, cx + 3):
        v.set(x, G + 3, 9, 'minecraft:air')
    # mouth entrance -> head chamber -> neck -> torso chamber
    for y in range(G, G + 4):
        for x in range(cx - 2, cx + 3):
            for z in range(7, 14):
                v.air(x, y, z)
    for y in range(G, G + 4):
        for x in range(cx - 2, cx + 3):
            for z in range(24, 32):
                v.air(x, y, z)
    v.disc(cx, G - 1, 44, 11, 'minecraft:stone_bricks')
    v.disc(cx, G - 1, 17, 6, 'minecraft:stone_bricks')
    for z in range(7, 34):
        for x in range(cx - 2, cx + 3):
            v.set(x, G - 1, z, 'minecraft:stone_bricks')
    for z in (14, 20, 36, 44, 52):
        for dx in (-1, 1):
            v.set(cx + dx * 3, G, z, 'minecraft:soul_lantern[hanging=false]') if False else v.set(cx + dx * 3, G, z, 'minecraft:lantern[hanging=false]')
    v.chest(cx, G, 50, 'north', LOOT); v.chest(cx + 3, G, 50, 'north', LOOT)
    v.spawner(cx, G, 40, 'minecraft:zombie')
    v.landmark(cx, G + 8, 40, 13) if False else None
    v.landmark(cx, G, 3, 13)
    v.set(cx, G - 1, 3, 'minecraft:chiseled_stone_bricks')
    # mossy runes on the chest
    for i in range(0, 360, 30):
        x = round(cx + math.cos(math.radians(i)) * 9); z = round(44 + math.sin(math.radians(i)) * 14)
        v.set(x, G + 12 - abs(round(math.sin(math.radians(i)) * 3)), z, 'minecraft:shroomlight') if False else None
    return v


def titans_arch():
    v = Vox('titans_arch'); v.ground = G; rng = v.rng
    W, D = 61, 25
    M = Mix(rng, ('minecraft:stone', 3), ('minecraft:andesite', 3), ('minecraft:tuff', 2), ('minecraft:cobblestone', 1))
    for y in range(1, G - 1):
        for x in range(W):
            for z in range(D):
                v.set(x, y, z, 'minecraft:stone')
    for x in range(W):
        for z in range(D):
            v.set(x, G - 1, z, Mix(rng, ('minecraft:stone', 3), ('minecraft:gravel', 1), ('minecraft:andesite', 1))())
    cx = 30
    for x in range(W):
        for y in range(G, G + 40):
            u = (x - cx) / 27.0
            for z in range(4, D - 4):
                zz = (z - 12) / 8.0
                outer = (u * u) + ((y - G) / 36.0) ** 2
                inner = (u * u) / (0.55 ** 2) + ((y - G) / 24.0) ** 2
                if outer <= 1.0 and inner >= 1.0 and abs(zz) <= 1 - 0.1 * ((y - G) / 36.0):
                    if abs(zz) < 0.9 or rng.random() < 0.7:
                        v.set(x, y, z, M())
    v.landmark(cx, G, 12, 14)
    v.set(cx, G - 1, 12, 'minecraft:chiseled_stone_bricks')
    for dx in (-2, 2):
        pillar(v, cx + dx, 12, G, G + 4, 'minecraft:stone_bricks', 'minecraft:chiseled_stone_bricks')
        v.set(cx + dx, G + 5, 12, 'minecraft:lantern[hanging=false]')
    v.chest(cx, G, 6, 'south', LOOT)
    # hanging sea lanterns under the span
    for i in range(-4, 5, 2):
        v.set(cx + i * 3, G + 21 - abs(i) * 0, 12, 'minecraft:air') if False else None
    return v


def moonwell():
    v = Vox('moonwell_shrine'); v.ground = G; rng = v.rng
    S = 33
    ground(v, S, Mix(rng, ('minecraft:grass_block', 5), ('minecraft:moss_block', 3), ('minecraft:podzol', 1)), 16)
    c = 16
    v.disc(c, G - 1, c, 11, 'minecraft:polished_diorite')
    v.ring(c, G - 1, c, 11, 'minecraft:quartz_bricks', 1.0)
    for y in (G - 1, G - 2):
        v.disc(c, y, c, 6, 'minecraft:water[level=0]') if y == G - 1 else v.disc(c, y, c, 6, 'minecraft:blue_ice')
    v.ring(c, G, c, 7, 'minecraft:quartz_slab[type=bottom,waterlogged=false]', 1.0)
    v.ring(c, G - 1, c, 7, 'minecraft:smooth_quartz', 1.0)
    v.set(c, G - 1, c, 'minecraft:sea_lantern')
    n = 8
    for i in range(n):
        a = i / n * math.tau
        x, z = round(c + math.cos(a) * 10), round(c + math.sin(a) * 10)
        pillar(v, x, z, G, G + 9, 'minecraft:quartz_pillar[axis=y]', 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz')
        v.set(x, G + 10, z, 'minecraft:end_rod[facing=up]')
    # ring beam
    for i in range(96):
        a = i / 96 * math.tau
        v.set(round(c + math.cos(a) * 10), G + 9, round(c + math.sin(a) * 10), 'minecraft:quartz_slab[type=top,waterlogged=false]')
    # blossom trees
    LEAF = 'minecraft:cherry_leaves[distance=1,persistent=true,waterlogged=false]'
    for (x, z) in ((3, 6), (29, 8), (4, 27), (28, 26)):
        for y in range(G, G + 7):
            v.set(x, y, z, 'minecraft:cherry_log[axis=y]')
        v.sphere(x, G + 8, z, 5, 4, 5, LEAF)
    v.landmark(c, G, 26, 15)
    v.set(c, G - 1, 26, 'minecraft:chiseled_quartz_block')
    v.chest(c + 2, G, 24, 'north', LOOT)
    path_ = [(x, z) for x in range(15, 18) for z in range(23, 28)]
    for (x, z) in path_:
        v.set(x, G - 1, z, 'minecraft:smooth_quartz')
    return v


def rift_scar():
    v = Vox('rift_scar'); v.ground = G; rng = v.rng
    S = 37
    ground(v, S, Mix(rng, ('minecraft:blackstone', 3), ('minecraft:deepslate', 2), ('minecraft:crying_obsidian', 1), ('minecraft:calcite', 1)), 18)
    c = 18
    # jagged crystal shards ringed around the gate
    for i in range(22):
        a = rng.random() * math.tau
        r = 7 + rng.random() * 9
        x, z = round(c + math.cos(a) * r), round(c + math.sin(a) * r)
        h = rng.randint(5, 16)
        v.cone(x, z, G, h, 2.0, 'realmbreak:rift_crystal_block' if rng.random() < 0.6 else 'minecraft:amethyst_block')
    # standing gate
    v.rift_gate(c - 2, G, c, 'x')
    # steps + dais
    for i in range(3):
        v.disc(c, G - 1 + 0, c + 0, 7 - i * 2, 'minecraft:polished_blackstone_bricks') if False else None
    v.disc(c, G - 1, c, 7, 'realmbreak:riftstone_bricks')
    v.ring(c, G - 1, c, 7, 'realmbreak:chiseled_riftstone', 1.0)
    v.rift_gate(c - 2, G, c, 'x')
    for dx in (-5, 5):
        for y in range(G, G + 6):
            v.set(c + dx, y, c + 3, 'realmbreak:riftstone_pillar[axis=y]')
        v.set(c + dx, G + 6, c + 3, 'realmbreak:rift_crystal_block')
    v.landmark(c, G, c + 9, 16)
    v.set(c, G - 1, c + 9, 'realmbreak:chiseled_riftstone')
    v.chest(c + 4, G, c + 5, 'north', 'realmbreak:chests/rift_cache')
    return v


def build():
    return [standing_stones(), dragon_bones(), watchtower(), colossus(), titans_arch(), moonwell(), rift_scar()]
