"""Rift-dimension structures: five elemental altars, crystal cathedral, fallen keep, monolith, sky bridge. Each sits on its own floating island."""
import math
from arch import *

G = 30
RC = 'realmbreak:rift_crystal_block'
CACHE = 'realmbreak:chests/rift_cache'
EL = [('flame', 'cinder', 0), ('frost', 'rime', 1), ('storm', 'gale', 2), ('verdant', 'thorn', 3), ('void', 'null', 4)]


def island(v, cx, cz, r, depth, rock=None, top='realmbreak:rift_turf'):
    rng = v.rng
    rock = rock or Mix(rng, ('realmbreak:riftstone', 5), ('minecraft:deepslate', 2), ('minecraft:tuff', 1))
    n = int(r) + 3
    for y in range(G - depth, G):
        t = (y - (G - depth)) / float(depth)
        rr = max(1.5, r * (t ** 0.7))
        for x in range(cx - n, cx + n + 1):
            for z in range(cz - n, cz + n + 1):
                d = math.hypot(x - cx, z - cz)
                jag = 1.5 * math.sin(math.atan2(z - cz, x - cx) * 5 + y * 0.5) * (1 - t * 0.6)
                if d <= rr + jag:
                    v.set(x, y, z, rock())
    for x in range(cx - n, cx + n + 1):
        for z in range(cz - n, cz + n + 1):
            if math.hypot(x - cx, z - cz) <= r:
                v.set(x, G - 1, z, top)


def altar(name, e, p, idx):
    v = Vox(name); v.ground = G; rng = v.rng
    c = 20
    island(v, c, c, 17, 16)
    B, R = f'realmbreak:{p}_bricks', f'realmbreak:{p}_rune'
    v.disc(c, G - 1, c, 11, B)
    v.ring(c, G - 1, c, 11, R, 1.0)
    v.ring(c, G - 1, c, 6, R, 1.0)
    for i in range(4):
        a = i / 4 * math.tau + math.pi / 4
        x, z = round(c + math.cos(a) * 9), round(c + math.sin(a) * 9)
        for y in range(G, G + 10):
            v.set(x, y, z, B if y % 4 else R)
        v.set(x, G + 10, z, R)
    # dais with landmark
    v.disc(c, G, c, 3, B)
    v.landmark(c, G + 1, c, idx)
    # element flavour
    if e == 'flame':
        for i in range(8):
            a = i / 8 * math.tau
            x, z = round(c + math.cos(a) * 13.5), round(c + math.sin(a) * 13.5)
            brazier(v, x, G, z, 'minecraft:netherrack', 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]')
        for dx, dz in ((-4, 0), (4, 0)):
            v.set(c + dx, G - 1, c + dz, 'minecraft:lava[level=0]')
    elif e == 'frost':
        for i in range(9):
            a = i / 9 * math.tau
            x, z = round(c + math.cos(a) * 13.5), round(c + math.sin(a) * 13.5)
            v.cone(x, z, G, 6 + i % 3 * 3, 2.0, Mix(rng, ('minecraft:blue_ice', 2), ('minecraft:packed_ice', 2))())
    elif e == 'storm':
        for i in range(6):
            a = i / 6 * math.tau
            x, z = round(c + math.cos(a) * 13.5), round(c + math.sin(a) * 13.5)
            for y in range(G, G + 11):
                v.set(x, y, z, 'minecraft:waxed_oxidized_copper')
            v.set(x, G + 11, z, 'minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]')
    elif e == 'verdant':
        for (x, z) in ((c - 13, c - 3), (c + 13, c + 2)):
            for y in range(G, G + 10):
                v.set(x, y, z, 'realmbreak:glimmerwood_log[axis=y]')
            v.sphere(x, G + 11, z, 5, 4, 5, 'realmbreak:glimmerwood_leaves[distance=1,persistent=true,waterlogged=false]')
    else:
        for i in range(7):
            a = i / 7 * math.tau + 0.3
            x, z = round(c + math.cos(a) * 13.5), round(c + math.sin(a) * 13.5)
            v.sphere(x, G + 5 + i % 3 * 2, z, 1.5, 2.5, 1.5, 'minecraft:obsidian')
            v.set(x, G + 8 + i % 3 * 2, z, 'minecraft:end_rod[facing=up]')
    v.chest(c + 2, G, c + 5, 'north', CACHE)
    v.chest(c - 2, G, c - 5, 'south', CACHE)
    return v


def cathedral():
    v = Vox('crystal_cathedral'); v.ground = G; rng = v.rng
    W, L = 61, 81
    cx = 30
    island(v, cx, 40, 36, 24)
    BB = Mix(rng, ('realmbreak:riftstone_bricks', 6), ('minecraft:amethyst_block', 1), ('minecraft:calcite', 1))
    FL = Mix(rng, ('realmbreak:riftstone', 3), ('minecraft:polished_deepslate', 2), ('minecraft:quartz_bricks', 1))
    pal = dict(wall=BB, floor=FL, pillar='realmbreak:riftstone_pillar[axis=y]', cap='realmbreak:chiseled_riftstone', base='realmbreak:riftstone', trim='realmbreak:chiseled_riftstone',
               roof='realmbreak:riftstone_bricks', pane='minecraft:purple_stained_glass_pane')
    x0, x1, z0, z1 = 21, 39, 12, 68
    H = 20
    v.room(x0, G - 1, z0, x1, G + H, z1, BB, FL, BB)
    # transepts
    v.room(10, G - 1, 34, 50, G + 14, 46, BB, FL, BB)
    v.carve(x0 + 1, G, 35, x1 - 1, G + 13, 45)
    # nave flooring pattern + carpet
    for z in range(z0 + 1, z1):
        for x in (29, 30, 31):
            v.set(x, G - 1, z, 'minecraft:purple_carpet') if False else None
            v.set(x, G, z, 'minecraft:purple_carpet')
    # buttresses & tall pointed windows
    for z in range(z0 + 4, z1 - 2, 6):
        for xs in (x0, x1):
            for y in range(G, G + H):
                v.set(xs + (-1 if xs == x0 else 1), y, z, pal['pillar'])
            for y in range(G + 3, G + 14):
                hw = 1 if y < G + 11 else 0
                for k in range(-hw, hw + 1):
                    v.set(xs, y, z + k, 'minecraft:purple_stained_glass')
        pillar(v, 25, z, G, G + H - 3, pal['pillar'], pal['cap'], pal['base'])
        pillar(v, 35, z, G, G + H - 3, pal['pillar'], pal['cap'], pal['base'])
        v.set(25, G + H - 5, z, lantern(True, True)); v.set(35, G + H - 5, z, lantern(True, True))
    # pitched roof along z using stairs
    for i in range(10):
        for z in range(z0 - 1, z1 + 2):
            v.set(x0 - 1 + i, G + H + i, z, stair('realmbreak:riftstone_bricks' if False else 'minecraft:deepslate_brick_stairs', 'east'))
            v.set(x1 + 1 - i, G + H + i, z, stair('minecraft:deepslate_brick_stairs', 'west'))
    for z in range(z0 - 1, z1 + 2):
        for y in range(G + H, G + H + 9):
            for x in range(x0 + (y - G - H), x1 - (y - G - H) + 1):
                v.air(x, y, z) if False else None
    # entrance (south) and apse (north)
    for y in range(G, G + 8):
        for x in range(27, 34):
            hh = 8 - (abs(x - 30) ** 2) // 2
            if y - G < hh:
                for z in range(z1 - 1, z1 + 1):
                    v.air(x, y, z)
    v.arch('x', 27, 33, G + 3, z1 - 1, 2, pal['trim'], pointed=True, thick=1)
    for z in range(z1 + 1, z1 + 9):
        for x in range(25, 36):
            v.set(x, G - 1, z, FL)
    # altar + landmark
    for x in range(26, 35):
        for z in range(z0 + 1, z0 + 6):
            v.set(x, G, z, 'minecraft:amethyst_block') if False else v.set(x, G, z, FL)
    v.landmark(30, G + 1, z0 + 3, 17)
    v.chest(27, G + 1, z0 + 2, 'south', CACHE); v.chest(33, G + 1, z0 + 2, 'south', CACHE)
    for dx in (-3, 3):
        v.sphere(30 + dx, G + 3, z0 + 3, 1.5, 1.5, 1.5, RC)
    # crystal spires
    for (sx, sz, h) in ((18, 10, 30), (42, 10, 30), (18, 70, 26), (42, 70, 26), (30, 6, 44)):
        v.cone(sx, sz, G, h, 4.0, RC if rng.random() < 0.7 else 'minecraft:amethyst_block')
    # pews
    for z in range(z0 + 10, z1 - 8, 3):
        for x in (23, 24, 26, 27, 33, 34, 36, 37):
            v.set(x, G, z, stair('minecraft:purpur_stairs', 'north'))
    v.spawner(30, G, 52, 'realmbreak:rift_wraith'); v.spawner(30, G, 24, 'realmbreak:rift_wraith')
    v.landmark(30, G, z1 + 8, 17) if False else None
    return v


def fallen_keep():
    v = Vox('fallen_keep'); v.ground = G; rng = v.rng
    island(v, 24, 24, 24, 20)
    BB = Mix(rng, ('minecraft:stone_bricks', 4), ('minecraft:cracked_stone_bricks', 2), ('minecraft:mossy_stone_bricks', 2), ('realmbreak:riftstone_bricks', 2))
    FL = Mix(rng, ('minecraft:stone_bricks', 2), ('realmbreak:riftstone', 2), ('minecraft:polished_andesite', 1))
    pal = dict(floor=FL, trim='minecraft:chiseled_stone_bricks', roof='minecraft:stone_brick_slab', pane='minecraft:iron_bars')
    x0, x1, z0, z1 = 12, 36, 12, 36
    v.room(x0, G - 1, z0, x1, G + 12, z1, BB, FL, None)
    v.carve(x0 + 1, G + 1, z0 + 1, x1 - 1, G + 11, z1 - 1)
    for (tx, tz) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        tower(v, tx, tz, G, 4, 18, BB, pal, floors=(9,), roof='battlement', slits=True)
    # throne dais & echo
    for x in range(21, 28):
        for z in range(z0 + 1, z0 + 5):
            v.set(x, G, z, 'minecraft:polished_andesite')
    v.set(24, G + 1, z0 + 2, 'minecraft:stone_brick_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]')
    v.set(24, G + 2, z0 + 1, 'minecraft:stone_bricks')
    v.set(24, G + 1, z0 + 1, 'minecraft:stone_bricks')
    v.npc(24, G + 1, z0 + 4, 'aldric_echo')
    for x in range(23, 26):
        for z in range(z0 + 5, z1):
            v.set(x, G, z, 'minecraft:red_carpet')
    for z in range(z0 + 6, z1 - 3, 5):
        for x in (18, 30):
            pillar(v, x, z, G + 1, G + 10, 'minecraft:stone_brick_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]' if False else 'minecraft:chiseled_stone_bricks', 'minecraft:stone_brick_slab[type=top,waterlogged=false]')
    # gate gap south
    for y in range(G, G + 7):
        for x in range(22, 27):
            for z in range(z1, z1 + 1):
                v.air(x, y, z)
    for z in range(z1 + 1, z1 + 8):
        for x in range(22, 27):
            v.set(x, G - 1, z, FL)
    v.chest(14, G + 1, 14, 'east', CACHE); v.chest(34, G + 1, 34, 'west', CACHE)
    v.spawner(24, G + 1, 26, 'realmbreak:rift_stalker')
    v.landmark(24, G, z1 + 6, 18)
    # fallen masonry & crystals pushing through
    for i in range(40):
        x, z = rng.randint(6, 42), rng.randint(6, 42)
        if v.get(x, G, z) is None:
            v.set(x, G, z, BB())
    for i in range(6):
        v.cone(rng.randint(8, 40), rng.randint(8, 40), G, rng.randint(5, 10), 1.8, RC)
    v.ruin(0.22, ymin=G + 6, only_names={'minecraft:stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:mossy_stone_bricks', 'realmbreak:riftstone_bricks'})
    return v


def monolith():
    v = Vox('rift_monolith'); v.ground = G; rng = v.rng
    island(v, 14, 14, 13, 14)
    c = 14
    R = Mix(rng, ('realmbreak:riftstone_bricks', 5), ('realmbreak:riftstone', 2))
    for y in range(G, G + 30):
        w = 2 if y < G + 18 else 1
        for dx in range(-w, w + 1):
            for dz in range(-w, w + 1):
                v.set(c + dx, y, c + dz, R())
        if y % 4 == 2:
            for dx in range(-w, w + 1):
                v.set(c + dx, y, c - w - 1 + 0, 'minecraft:air') if False else None
            v.set(c, y, c + w, 'realmbreak:rift_crystal_block'); v.set(c, y, c - w, 'realmbreak:rift_crystal_block')
            v.set(c + w, y, c, 'realmbreak:rift_crystal_block'); v.set(c - w, y, c, 'realmbreak:rift_crystal_block')
    v.sphere(c, G + 33, c, 2, 3, 2, 'realmbreak:rift_crystal_block')
    for i in range(8):
        a = i / 8 * math.tau
        x, z = round(c + math.cos(a) * 9), round(c + math.sin(a) * 9)
        for y in range(G, G + 4 + i % 3 * 2):
            v.set(x, y, z, 'realmbreak:riftstone_pillar[axis=y]')
    v.disc(c, G - 1, c, 5, 'realmbreak:chiseled_riftstone')
    v.landmark(c, G, c + 5, 19)
    v.chest(c + 3, G, c + 4, 'north', CACHE)
    return v


def sky_bridge():
    v = Vox('sky_bridge'); v.ground = G; rng = v.rng
    L = 90
    island(v, 12, 12, 11, 12)
    island(v, L - 12, 12, 11, 12)
    BB = Mix(rng, ('realmbreak:riftstone_bricks', 5), ('minecraft:deepslate_bricks', 1))
    # bridge deck x 12..L-12 along x, centred at z=12, width 5, gentle arch
    for x in range(14, L - 13):
        t = (x - 14) / float(L - 27)
        dy = round(4 * math.sin(t * math.pi))
        for z in range(10, 15):
            v.set(x, G - 1 + dy, z, BB() if z in (10, 14) else 'realmbreak:riftstone')
            if z not in (10, 14) and x % 6 == 0:
                v.set(x, G - 1 + dy, z, 'realmbreak:chiseled_riftstone')
        for z in (9, 15):
            v.set(x, G + dy, z - (0 if z == 9 else 0) + (1 if z == 9 else -1) * 0, 'minecraft:air') if False else None
        for z in (10, 14):
            v.set(x, G + dy, z, 'realmbreak:riftstone_bricks')
            if x % 6 == 3:
                v.set(x, G + dy + 1, z, 'minecraft:soul_lantern[hanging=false]')
        # arch support beneath
        if x % 12 == 0:
            for y in range(G - 8 + dy, G - 1 + dy):
                for z in (11, 13):
                    v.set(x, y, z, 'realmbreak:riftstone_pillar[axis=y]')
            v.sphere(x, G - 9 + dy, 12, 2, 2, 2, 'realmbreak:rift_crystal_block')
    # gate towers
    for (tx) in (12, L - 12):
        tower(v, tx, 12, G, 4, 14, BB, dict(floor='realmbreak:riftstone', trim='realmbreak:chiseled_riftstone', roof='realmbreak:riftstone_bricks', pane='minecraft:purple_stained_glass_pane'),
              floors=(7,), roof='cone', roof_h=8, slits=True)
        # doorway toward the bridge
        for y in range(G, G + 4):
            for dx in range(-5, 6):
                if abs(dx) >= 3:
                    pass
        side = 1 if tx == 12 else -1
        for y in range(G, G + 3):
            for k in range(2, 6):
                v.air(tx + side * k, y, 12)
    v.landmark(12, G, 20, 20)
    v.set(12, G - 1, 20, 'realmbreak:chiseled_riftstone')
    v.chest(L - 12, G, 19, 'north', CACHE)
    v.spawner(L - 16, G, 12, 'realmbreak:rift_wraith') if False else None
    return v


def build():
    out = [altar(f'altar_of_{e}', e, p, i) for (e, p, i) in EL]
    out += [cathedral(), fallen_keep(), monolith(), sky_bridge()]
    return out
