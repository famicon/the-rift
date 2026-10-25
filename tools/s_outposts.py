"""Wayfarer's Camp and the five element outposts (NPC hubs).  40x40, ground level G=4, gate to the south, landmark stone in the courtyard."""
import math
from arch import *

G = 4
LOOT = 'realmbreak:chests/outpost'
FIRE = 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]'
CAMPFIRE = 'minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]'
WALL = 'minecraft:cobblestone_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]'


def base(v, ground, size=40):
    for y in range(1, G - 1):
        for x in range(size):
            for z in range(size):
                v.set(x, y, z, 'minecraft:dirt')
    for x in range(size):
        for z in range(size):
            v.set(x, G - 1, z, ground() if callable(ground) else ground)


def path(v, blk, x0, z0, x1, z1):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            v.set(x, G - 1, z, blk() if callable(blk) else blk)


def furnish_hall(v, x0, z0, x1, z1, P, npc_in=None):
    cx = (x0 + x1) // 2
    v.room(x0, G - 1, z0, x1, G + 6, z1, P['wall'], P['floor'], P['wall'])
    roof_gable(v, x0, z0, x1, z1, G + 7, P['stair'], P['slab'], 'x')
    # door south + windows
    for dx in (0, 1):
        for y in (G, G + 1, G + 2):
            v.air(cx + dx, y, z1)
    v.door(cx, G, z1, 'south', P.get('door', 'oak_door'))
    v.air(cx + 1, G, z1); v.air(cx + 1, G + 1, z1)
    for x in range(x0 + 3, x1 - 2, 5):
        for y in (G + 2, G + 3):
            v.set(x, y, z0, P['pane']); v.set(x, y, z1, P['pane'])
    # interior
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            if abs(x - cx) <= 1:
                v.set(x, G, z, P.get('carpet', 'minecraft:red_carpet'))
    for x in range(x0 + 4, x1 - 2, 6):
        v.set(x, G + 5, (z0 + z1) // 2, lantern(True, P.get('soul', False)))
    v.chest(x0 + 1, G, z0 + 1, 'south', LOOT)
    v.barrel(x0 + 2, G, z0 + 1, LOOT)
    v.set(x1 - 1, G, z0 + 1, 'minecraft:crafting_table')
    v.set(x1 - 2, G, z0 + 1, 'minecraft:anvil[facing=east]')
    v.set(x1 - 1, G, z0 + 2, 'minecraft:bookshelf'); v.set(x1 - 1, G + 1, z0 + 2, 'minecraft:bookshelf')
    for z in (z0 + 1, z1 - 1):
        brazier(v, x0 + 1, G, z, P.get('fuel', 'minecraft:cobblestone'), P.get('fire', FIRE)) if False else None


def outpost(name, P, site, npcs, extras=None):
    v = Vox(name)
    v.ground = G
    rng = v.rng
    base(v, P['ground'])
    path(v, P['path'], 17, 4, 22, 39)
    path(v, P['path'], 8, 26, 31, 29)
    # palisade ring with crenellations
    for i in range(3, 37):
        for (x, z) in ((i, 3), (i, 36), (3, i), (36, i)):
            for y in range(G, G + 5):
                v.set(x, y, z, P['log'])
            if (x + z) % 2 == 0:
                v.set(x, G + 5, z, P['wall']())
    # gate gap + arch
    for x in range(18, 22):
        for y in range(G, G + 6):
            v.air(x, y, 36)
    v.arch('x', 18, 21, G + 3, 36, 1, P['trim'], pointed=True, thick=1)
    for x in (17, 22):
        for y in range(G, G + 7):
            v.set(x, y, 36, P['pillar'])
        v.set(x, G + 7, 36, lantern(False, P.get('soul', False)))
    # corner towers
    for (tx, tz) in ((3, 3), (36, 3), (3, 36), (36, 36)):
        tower(v, tx, tz, G, 3.4, 12, P['wall'], P['tpal'], floors=(6,), roof='cone', roof_h=6, slits=True)
    # main hall
    furnish_hall(v, 9, 6, 30, 16, P)
    # courtyard: landmark + npcs + lamps
    if site is not None:
        v.landmark(20, G, 28, site)
        v.set(20, G - 1, 28, P['trim'])
        for dx in (-2, 2):
            v.set(20 + dx, G, 28, P['pillar']); v.set(20 + dx, G + 1, 28, P['pillar'])
            v.set(20 + dx, G + 2, 28, lantern(False, P.get('soul', False)))
    for i, n in enumerate(npcs):
        v.npc(14 + i * 6, G, 25, n)
    for x in (10, 30):
        for z in (22, 32):
            v.set(x, G, z, WALL); v.set(x, G + 1, z, lantern(False, P.get('soul', False)))
    # small well and market stall
    v.set(6, G, 20, 'minecraft:barrel[facing=up,open=false]')
    v.chest(33, G, 20, 'west', LOOT)
    if extras:
        extras(v, rng)
    v.weather({P['wall_name']: P.get('wear', [])}, 0.05) if P.get('wear') else None
    return v


def ashen(v, rng):
    for (x, z) in ((12, 22), (28, 22)):
        for y in range(G, G + 5):
            v.set(x, y, z, 'minecraft:polished_basalt[axis=y]')
        brazier(v, x, G + 5, z, 'minecraft:netherrack', FIRE)
    # forge
    for x in range(6, 10):
        for z in range(31, 34):
            v.set(x, G, z, 'minecraft:blackstone')
    v.set(7, G + 1, 32, 'minecraft:blast_furnace[facing=east,lit=true]'); v.set(8, G + 1, 32, 'minecraft:anvil[facing=north]')
    v.set(7, G + 2, 32, 'minecraft:blackstone_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
    for y in range(G + 3, G + 7):
        v.set(7, y, 32, 'minecraft:blackstone_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')


def frost(v, rng):
    for i in range(7):
        x, z = rng.randint(6, 33), rng.randint(20, 33)
        if 16 <= x <= 23 or abs(z - 28) < 2 and 16 <= x <= 24:
            continue
        v.cone(x, z, G, rng.randint(4, 8), 1.6, 'minecraft:packed_ice')
    for x in range(8, 32):
        for z in range(18, 34):
            if rng.random() < 0.25 and v.get(x, G, z) is None:
                v.set(x, G, z, 'minecraft:snow[layers=%d]' % rng.randint(1, 3))
    # hot spring
    for x in range(30, 34):
        for z in range(26, 30):
            v.set(x, G - 1, z, 'minecraft:water[level=0]')
            v.set(x, G - 2, z, 'minecraft:blue_ice')


def storm(v, rng):
    ROD = 'minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]'
    for (x, z) in ((12, 22), (28, 22), (12, 32), (28, 32)):
        for y in range(G, G + 9):
            v.set(x, y, z, 'minecraft:waxed_oxidized_copper')
        v.set(x, G + 9, z, ROD)
    # wind-flag mast
    for y in range(G, G + 16):
        v.set(20, y, 22, 'minecraft:stripped_birch_log[axis=y]')
    for x in range(21, 26):
        v.set(x, G + 14, 22, 'minecraft:cyan_wool'); v.set(x, G + 13, 22, 'minecraft:white_wool')


def grove(v, rng):
    LEAF = 'minecraft:oak_leaves[distance=1,persistent=true,waterlogged=false]'
    for (x, z) in ((7, 22), (32, 24), (8, 32), (32, 33)):
        for y in range(G, G + 9):
            v.set(x, y, z, 'minecraft:oak_log[axis=y]'); v.set(x + 1, y, z, 'minecraft:oak_log[axis=y]')
        v.sphere(x, G + 11, z, 5, 4, 5, LEAF)
    for i in range(14):
        x, z = rng.randint(5, 34), rng.randint(19, 34)
        if v.get(x, G, z) is None and not (17 <= x <= 22) and not 8 <= z <= 29 and False:
            pass
        if v.get(x, G, z) is None and not (17 <= x <= 22):
            v.set(x, G, z, rng.choice(['minecraft:fern', 'minecraft:poppy', 'minecraft:blue_orchid', 'minecraft:short_grass']))


def veiled(v, rng):
    for (x, z) in ((11, 22), (29, 22), (11, 32), (29, 32)):
        pillar(v, x, z, G, G + 9, 'minecraft:purpur_pillar[axis=y]', 'minecraft:chiseled_stone_bricks', 'minecraft:polished_andesite')
        v.set(x, G + 10, z, 'minecraft:amethyst_block')
        v.set(x, G + 11, z, 'minecraft:end_rod[facing=up]')
    for i in range(10):
        a = i / 10 * math.tau
        x, z = round(20 + math.cos(a) * 6), round(28 + math.sin(a) * 6)
        if v.get(x, G, z) is None:
            v.set(x, G - 1, z, 'minecraft:amethyst_block')


def camp():
    v = Vox('wayfarers_camp')
    v.ground = G
    rng = v.rng
    base(v, Mix(rng, ('minecraft:grass_block', 5), ('minecraft:coarse_dirt', 2), ('minecraft:podzol', 1)))
    wool = ['red', 'blue', 'orange']
    for k, (tx, tz) in enumerate(((8, 10), (28, 8), (28, 26))):
        c = wool[k]
        for z in range(tz, tz + 7):
            for i in range(4):
                v.set(tx + i, G + i, z, f'minecraft:{c}_wool'); v.set(tx + 7 - i, G + i, z, f'minecraft:{c}_wool')
            v.set(tx + 3, G + 3, z, f'minecraft:{c}_wool'); v.set(tx + 4, G + 3, z, f'minecraft:{c}_wool')
        for x in range(tx + 1, tx + 7):
            v.air(x, G, tz); v.air(x, G, tz + 6)
        for z in range(tz + 1, tz + 6):
            for x in range(tx + 1, tx + 7):
                for y in range(G, G + 3):
                    if v.get(x, y, z) is None:
                        v.air(x, y, z)
            v.set(tx + 3, G, z, 'minecraft:white_carpet')
        v.chest(tx + 1, G, tz + 1, 'east', LOOT)
        v.set(tx + 6, G, tz + 5, 'minecraft:lantern[hanging=false]')
    v.set(20, G - 1, 20, 'minecraft:stone'); v.set(20, G, 20, CAMPFIRE)
    for (dx, dz) in ((-2, 0), (2, 0), (0, 2), (0, -2)):
        v.set(20 + dx, G, 20 + dz, 'minecraft:hay_block[axis=y]')
    v.set(21, G, 24, 'minecraft:anvil[facing=east]'); v.set(22, G, 24, 'minecraft:smithing_table'); v.set(23, G, 24, 'minecraft:blast_furnace[facing=south,lit=false]')
    v.set(14, G, 22, 'minecraft:barrel[facing=up,open=false]')
    v.npc(18, G, 22, 'maera'); v.npc(23, G, 21, 'brannoch'); v.npc(16, G, 18, 'quill')
    # signpost + banner poles
    for y in range(G, G + 6):
        v.set(20, y, 33, 'minecraft:spruce_log[axis=y]')
    v.set(20, G + 6, 33, 'minecraft:lantern[hanging=false]')
    return v


def build():
    out = [camp()]
    mk = lambda **k: dict(slab=k.pop('slab'), **k)
    def tp(wall, floor, roof, trim, pane):
        return dict(wall=wall, floor=floor, roof=roof, trim=trim, pane=pane, pillar='minecraft:stripped_oak_log[axis=y]')
    rng = out[0].rng
    P = dict(wall=Mix(rng, ('minecraft:polished_blackstone_bricks', 5), ('minecraft:blackstone', 2), ('minecraft:cracked_polished_blackstone_bricks', 1)),
             floor='minecraft:polished_blackstone', stair='minecraft:nether_brick_stairs', slab='minecraft:nether_brick_slab', log='minecraft:dark_oak_log[axis=y]',
             trim='minecraft:chiseled_polished_blackstone', pillar='minecraft:polished_basalt[axis=y]', pane='minecraft:red_stained_glass_pane', carpet='minecraft:red_carpet',
             ground=Mix(rng, ('minecraft:coarse_dirt', 3), ('minecraft:blackstone', 2), ('minecraft:netherrack', 1), ('minecraft:basalt[axis=y]', 1)), path='minecraft:polished_blackstone_bricks',
             tpal=dict(floor='minecraft:polished_blackstone', roof='minecraft:nether_bricks', trim='minecraft:polished_blackstone', pane='minecraft:red_stained_glass_pane'), wall_name='x')
    out.append(outpost('ashen_bastion', P, 21, ['kaelen'], ashen))
    P = dict(wall=Mix(rng, ('minecraft:stone_bricks', 4), ('minecraft:snow_block', 2), ('minecraft:spruce_planks', 2)), floor='minecraft:spruce_planks', stair='minecraft:spruce_stairs', slab='minecraft:spruce_slab',
             log='minecraft:spruce_log[axis=y]', trim='minecraft:packed_ice', pillar='minecraft:stripped_spruce_log[axis=y]', pane='minecraft:light_blue_stained_glass_pane', carpet='minecraft:light_blue_carpet',
             ground=Mix(rng, ('minecraft:snow_block', 4), ('minecraft:packed_ice', 1), ('minecraft:stone', 1)), path='minecraft:spruce_planks', soul=True,
             tpal=dict(floor='minecraft:spruce_planks', roof='minecraft:packed_ice', trim='minecraft:packed_ice', pane='minecraft:light_blue_stained_glass_pane'), wall_name='x')
    out.append(outpost('frostwatch_hold', P, 22, ['seraphine'], frost))
    P = dict(wall=Mix(rng, ('minecraft:stone_bricks', 4), ('minecraft:polished_andesite', 2), ('minecraft:waxed_weathered_cut_copper', 1)), floor='minecraft:polished_andesite', stair='minecraft:stone_brick_stairs',
             slab='minecraft:stone_brick_slab', log='minecraft:stripped_birch_log[axis=y]', trim='minecraft:waxed_oxidized_cut_copper', pillar='minecraft:waxed_oxidized_copper', pane='minecraft:cyan_stained_glass_pane',
             carpet='minecraft:cyan_carpet', ground=Mix(rng, ('minecraft:stone', 3), ('minecraft:andesite', 2), ('minecraft:gravel', 1)), path='minecraft:stone_bricks',
             tpal=dict(floor='minecraft:polished_andesite', roof='minecraft:waxed_oxidized_cut_copper', trim='minecraft:waxed_oxidized_cut_copper', pane='minecraft:cyan_stained_glass_pane'), wall_name='x')
    out.append(outpost('stormwatch_perch', P, 23, ['vaelor'], storm))
    P = dict(wall=Mix(rng, ('minecraft:oak_planks', 3), ('minecraft:stripped_oak_log[axis=y]', 2), ('minecraft:mossy_cobblestone', 1)), floor='minecraft:spruce_planks', stair='minecraft:oak_stairs', slab='minecraft:oak_slab',
             log='minecraft:oak_log[axis=y]', trim='minecraft:stripped_oak_wood[axis=y]', pillar='minecraft:oak_log[axis=y]', pane='minecraft:lime_stained_glass_pane', carpet='minecraft:green_carpet',
             ground=Mix(rng, ('minecraft:grass_block', 5), ('minecraft:podzol', 2), ('minecraft:moss_block', 2)), path='minecraft:dirt_path',
             tpal=dict(floor='minecraft:spruce_planks', roof='minecraft:moss_block', trim='minecraft:stripped_oak_wood[axis=y]', pane='minecraft:lime_stained_glass_pane'), wall_name='x')
    out.append(outpost('grovekeepers_lodge', P, 24, ['elowen'], grove))
    P = dict(wall=Mix(rng, ('minecraft:stone_bricks', 3), ('minecraft:mossy_stone_bricks', 2), ('minecraft:purpur_block', 1), ('minecraft:amethyst_block', 1)), floor='minecraft:polished_deepslate', stair='minecraft:purpur_stairs',
             slab='minecraft:purpur_slab', log='minecraft:purpur_pillar[axis=y]', trim='minecraft:chiseled_stone_bricks', pillar='minecraft:purpur_pillar[axis=y]', pane='minecraft:purple_stained_glass_pane', carpet='minecraft:purple_carpet',
             ground=Mix(rng, ('minecraft:stone', 3), ('minecraft:deepslate', 2), ('minecraft:calcite', 1)), path='minecraft:polished_deepslate', soul=True,
             tpal=dict(floor='minecraft:polished_deepslate', roof='minecraft:purpur_block', trim='minecraft:chiseled_stone_bricks', pane='minecraft:purple_stained_glass_pane'), wall_name='x')
    out.append(outpost('veiled_sanctum', P, 25, ['ysmera'], veiled))
    return out
