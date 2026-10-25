"""Cinderhold Citadel - Flame dungeon: lava-moated black fortress with a spired keep and a Throne of Cinders arena."""
import math
from arch import *

SITE_GATE = 5   # cinderhold_gate
BOSS = 0        # ignarax


def build():
    v = Vox('cinderhold_citadel')
    rng = v.rng
    G = 16
    v.ground = G
    BB = Mix(rng, ('minecraft:polished_blackstone_bricks', 7), ('minecraft:cracked_polished_blackstone_bricks', 2), ('minecraft:blackstone', 1), ('minecraft:polished_blackstone', 1))
    FL = Mix(rng, ('minecraft:polished_blackstone', 3), ('minecraft:polished_blackstone_bricks', 2), ('minecraft:smooth_basalt', 1))
    pal = dict(wall=BB, floor=FL, pillar='minecraft:polished_basalt[axis=y]', cap='minecraft:chiseled_polished_blackstone', base='minecraft:polished_blackstone',
               trim='minecraft:chiseled_polished_blackstone', accent='minecraft:crimson_nylium' if False else 'minecraft:nether_bricks', roof='minecraft:nether_bricks',
               lantern=lantern(True, True), pane='minecraft:red_stained_glass_pane', banner='red', spire='minecraft:end_rod[facing=up]', spire_base='minecraft:gilded_blackstone')
    roof_st = 'minecraft:nether_brick_stairs'
    cx = cz = 40

    # ---------------- foundation + moat
    foundation(v, 0, 0, 80, 80, G - 1, G - 2, BB)
    for x in range(0, 81):
        for z in range(0, 81):
            ring_d = max(abs(x - 40), abs(z - 40))
            if 31 <= ring_d <= 37:      # moat band
                for y in range(G - 5, G):
                    v.air(x, y, z)
                for y in range(G - 6, G - 2):
                    pass
            if 31 <= ring_d <= 37:
                v.set(x, G - 6, z, 'minecraft:blackstone')
                v.set(x, G - 5, z, 'minecraft:lava[level=0]')
                v.set(x, G - 4, z, 'minecraft:lava[level=0]')
                v.set(x, G - 3, z, 'minecraft:lava[level=0]')
            elif ring_d in (30, 38):
                v.set(x, G - 1, z, pal['trim'])
    # outer apron
    for x in range(0, 81):
        for z in range(0, 81):
            if max(abs(x - 40), abs(z - 40)) >= 39:
                v.set(x, G - 1, z, FL)
    # bridge (south)
    for z in range(70, 79):
        for x in range(36, 45):
            v.set(x, G - 1, z, FL)
            for y in range(G - 5, G - 1):
                if x in (36, 44):
                    v.set(x, y, z, BB)
        for x in (36, 44):
            v.set(x, G, z, 'minecraft:polished_blackstone_brick_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
            if z % 3 == 0:
                v.set(x, G + 1, z, lantern(False, True))

    # ---------------- courtyard floor
    for x in range(10, 71):
        for z in range(10, 71):
            v.set(x, G - 1, z, FL)
            if (x + z) % 9 == 0 and rng.random() < 0.5:
                v.set(x, G - 1, z, 'minecraft:magma_block')
    for z in range(40, 72):   # path to keep
        for x in range(37, 44):
            v.set(x, G - 1, z, 'minecraft:nether_bricks' if (x + z) % 2 else 'minecraft:red_nether_bricks')

    # ---------------- curtain wall (square ring at +-30)
    L, R = 10, 70
    H = 15
    for (x0, z0, x1, z1) in ((L, L, R, L), (L, R, R, R), (L, L, L, R), (R, L, R, R)):
        curtain_wall(v, x0, z0, x1, z1, G, H, 4, BB, pal)
    # inner walkway ledge + banners
    for i in range(14, 67, 8):
        banner(v, i, G + 8, L + 4, 'south', 'red') if False else None
    # corner towers
    for (tx, tz) in ((L, L), (R, L), (L, R), (R, R)):
        tower(v, tx, tz, G, 8, 30, BB, pal, floors=(8, 16, 24), roof='cone', roof_h=16, glass='minecraft:red_stained_glass_pane')
    for (tx, tz) in ((40, L), (L, 40), (R, 40)):
        tower(v, tx, tz, G, 5, 22, BB, pal, floors=(7, 14), roof='cone', roof_h=11, glass='minecraft:red_stained_glass_pane')
    # gatehouse (south, z=R)
    gx0, gx1 = 31, 49
    v.fill(gx0, G, R - 4, gx1, G + 22, R + 4, None, fn=lambda x, y, z: BB())
    v.carve(gx0 + 3, G + 1, R - 3, gx1 - 3, G + 20, R + 3)
    for x in range(gx0 + 3, gx1 - 2):
        for z in range(R - 3, R + 4):
            v.set(x, G + 12, z, FL)
    # gate passage and arch
    for y in range(G, G + 10):
        for x in range(37, 44):
            hh = 9 - (abs(x - 40) ** 2) // 3
            if y - G < hh:
                for z in range(R - 5, R + 6):
                    v.air(x, y, z)
    v.arch('x', 37, 43, G + 5, R - 5, 11, pal['trim'], pointed=True, thick=1)
    for x in range(38, 43):
        for y in range(G + 4, G + 9):
            if y - G < 9 - (abs(x - 40) ** 2) // 3:
                v.set(x, y, R + 3, 'minecraft:iron_bars')
    for tx in (gx0 - 2, gx1 + 2):
        tower(v, tx, R + 4, G, 6, 26, BB, pal, floors=(8, 16), roof='cone', roof_h=14, glass='minecraft:red_stained_glass_pane')
    # gate crenellations & banners
    crenellate_rect(v, gx0, R - 4, gx1, R + 4, G + 23, BB)
    for bx in (34, 46):
        for by in (G + 14,):
            banner(v, bx, by, R + 5, 'south', 'red')

    # ---------------- the keep
    kx0, kz0, kx1, kz1 = 24, 24, 56, 56
    KH = 34
    keep_shell(v, kx0, kz0, kx1, kz1, G, KH + 1, pal, wall_t=2, pilaster=8, trim_every=11)
    # plinth steps
    for i, off in enumerate((1, 2)):
        for x in range(kx0 - off - 1, kx1 + off + 2):
            for z in (kz0 - off - 1, kz1 + off + 1):
                v.set(x, G - 1 + (1 - i) * 0, z, FL)
    # floors
    F1, F2, F3 = G + 13, G + 23, G + 33
    for fy in (F1, F2, F3):
        floor_slab(v, kx0 + 2, kz0 + 2, kx1 - 2, kz1 - 2, fy - 1, pal)
        floor_slab(v, kx0 + 2, kz0 + 2, kx1 - 2, kz1 - 2, fy - 1, pal)
    # ground-floor great hall carve & decor
    v.carve(kx0 + 2, G, kz0 + 2, kx1 - 2, F1 - 2, kz1 - 2)
    for x in range(kx0 + 2, kx1 - 1):
        for z in range(kz0 + 2, kz1 - 1):
            v.set(x, G - 1, z, FL)
    for z in range(kz0 + 2, kz1 - 1):
        for x in (39, 40, 41):
            v.set(x, G, z, 'minecraft:red_carpet')
    for x in range(kx0 + 6, kx1 - 4, 6):
        for z in (kz0 + 6, kz1 - 6):
            pillar(v, x, z, G, F1 - 2, pal['pillar'], pal['cap'], pal['base'])
            v.set(x, F1 - 4, z + (1 if z < 40 else -1), lantern(True, True))
    for x in range(kx0 + 5, kx1 - 3, 6):
        chandelier(v, x, F1 - 2, 40, pal, drop=4)
    # throne dais at north end
    for i in range(4):
        for x in range(36 + i, 45 - i):
            v.set(x, G + i, kz0 + 3 + 3 - i, stair('minecraft:nether_brick_stairs', 'south')) if False else None
    for x in range(35, 46):
        for z in range(kz0 + 2, kz0 + 8):
            v.set(x, G, z, 'minecraft:nether_bricks')
    for x in range(37, 44):
        for z in range(kz0 + 2, kz0 + 6):
            v.set(x, G + 1, z, 'minecraft:red_nether_bricks')
    v.set(40, G + 2, kz0 + 3, stair('minecraft:blackstone_stairs', 'south'))
    v.set(40, G + 3, kz0 + 2, 'minecraft:blackstone')
    v.set(40, G + 4, kz0 + 2, 'minecraft:blackstone')
    v.set(39, G + 2, kz0 + 2, 'minecraft:blackstone_slab[type=top,waterlogged=false]'); v.set(41, G + 2, kz0 + 2, 'minecraft:blackstone_slab[type=top,waterlogged=false]')
    for dx in (-3, 3):
        brazier(v, 40 + dx, G + 2, kz0 + 4)
    # lava channels in hall (decorative, safe-edged)
    for z in range(kz0 + 12, kz1 - 8):
        for x in (31, 49):
            v.set(x, G - 1, z, 'minecraft:magma_block')
    # keep entrance (south) pointed arch
    for y in range(G, G + 9):
        for x in range(36, 45):
            hh = 8 - (abs(x - 40) ** 2) // 3
            if y - G < hh:
                for z in range(kz1 - 2, kz1 + 3):
                    v.air(x, y, z)
    v.arch('x', 36, 44, G + 4, kz1 - 2, 5, pal['trim'], pointed=True, thick=1)
    # tall windows on all faces (hall + upper floors)
    for story_y in (G + 3, F1 + 2, F2 + 2):
        for a in range(kx0 + 6, kx1 - 4, 8):
            if not (story_y == G + 3 and a in (36, 44, 40) and False):
                window(v, 'z', kz0, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                if not (story_y == G + 3 and 34 <= a <= 46):
                    window(v, 'z', kz1 - 1, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                window(v, 'x', kx0, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
                window(v, 'x', kx1 - 1, a, story_y, 3, 6, 2, pal['pane'], frame=pal['trim'])
    # corner turrets
    for (tx, tz) in ((kx0 - 1, kz0 - 1), (kx1 + 1, kz0 - 1), (kx0 - 1, kz1 + 1), (kx1 + 1, kz1 + 1)):
        tower(v, tx, tz, G, 6, 44, BB, pal, floors=(10, 20, 30), roof='cone', roof_h=20, glass='minecraft:red_stained_glass_pane', slits=True)
    # ---------------- floors (carve first, then three stacked 2-wide switchbacks along the west strip)
    sx, sz = 27, 27
    stair_blk = 'minecraft:blackstone_stairs'
    v.carve(kx0 + 2, F1, kz0 + 2, kx1 - 2, F1 + 8, kz1 - 2)
    v.carve(kx0 + 2, F2, kz0 + 2, kx1 - 2, F2 + 7, kz1 - 2)
    v.carve(kx0 + 2, F3, kz0 + 2, kx1 - 2, F3 + 17, kz1 - 2)
    # floor 1: barracks chambers
    def chamber(x0, z0, x1, z1, ent, loot):
        spawner_room(v, x0, z0, x1, z1, F1 - 1, 8, pal, ent, loot)
    chamber(44, 28, 54, 38, 'realmbreak:ember_mage', 'realmbreak:chests/cinderhold_loot')
    chamber(44, 42, 54, 52, 'realmbreak:cinder_knight', 'realmbreak:chests/cinderhold_loot')
    for y in range(F1, F1 + 3):
        for zz in (33, 34, 47, 48):
            v.air(44, y, zz)
    for x in range(34, 44, 4):
        chandelier(v, x, F1 + 7, 40, pal, drop=2)
    for x in range(34, 44):
        for z in range(34, 46):
            v.set(x, F1 - 1, z, FL)
    # floor 2: lava trap hall
    y2 = F2 - 1
    for x in range(35, kx1 - 1):
        for z in range(kz0 + 2, kz1 - 1):
            if (x // 2 + z // 2) % 3 == 0 and 36 <= x <= 52 and 30 <= z <= 50 and (x, z) != (40, 40):
                v.set(x, y2, z, 'minecraft:magma_block')
    for x in range(kx0 + 12, kx1 - 9, 6):
        for z in range(kz0 + 10, kz1 - 9, 6):
            if x > 34 and (x, z) != (40, 40) and (x % 6 == 0):
                pillar(v, x, z, F2, F2 + 6, pal['pillar'], pal['cap'])
    for x in range(kx0 + 12, kx1 - 5, 8):
        chandelier(v, x, F2 + 7, 40, pal, drop=3)
    for (x, z) in ((kx1 - 4, 46), (kx1 - 4, 34)):
        v.chest(x, F2, z, 'west', 'realmbreak:chests/cinderhold_loot')
    v.spawner(38, F2, 46, 'realmbreak:cinder_knight'); v.spawner(44, F2, 34, 'realmbreak:ember_mage')
    # floor 3: Throne of Cinders arena
    def lava_ring(vv, cx_, cz_, y, r):
        vv.ring(cx_, y, cz_, r - 5, 'minecraft:magma_block', 1.0)
        for i in range(8):
            a = i / 8 * math.tau
            vv.set(round(cx_ + math.cos(a) * 8), y + 1, round(cz_ + math.sin(a) * 8), 'minecraft:netherrack')
            vv.set(round(cx_ + math.cos(a) * 8), y + 2, round(cz_ + math.sin(a) * 8), 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]')
    arena(v, 40, 40, F3 - 1, 12, 18, pal, BOSS, ring_fn=lava_ring, dome=True)
    # stairs last so nothing overwrites them
    switchback(v, sx, 27, G, 13, 'z', 1, 2, stair_blk, landing=BB)
    switchback(v, sx, 37, F1, 10, 'z', 1, 2, stair_blk, landing=BB)
    switchback(v, sx, 45, F2, 10, 'z', 1, 2, stair_blk, landing=BB)
    # arena door: corridor from the top landing into the arena
    for x in range(sx + 3, 36):
        for z in range(47, 50):
            v.set(x, F3 - 1, z, pal['floor'])
            for y in range(F3, F3 + 4):
                v.air(x, y, z)
    for x in range(sx, sx + 4):
        for z in range(45, 53):
            if v.get(x, F3 - 1, z) is None or v.get(x, F3 - 1, z) == 'air':
                pass
    # keep roof over the arena corners: flat battlement
    for x in range(kx0, kx1 + 1):
        for z in range(kz0, kz1 + 1):
            if v.get(x, F3 + 19, z) is None and math.hypot(x - 40, z - 40) > 16:
                v.set(x, F3 + 17, z, BB)
    crenellate_rect(v, kx0, kz0, kx1, kz1, F3 + 18, BB)
    # horns: basalt spikes on the keep corners
    for (hx, hz, sx_, sz_) in ((kx0, kz0, -1, -1), (kx1, kz0, 1, -1), (kx0, kz1, -1, 1), (kx1, kz1, 1, 1)):
        for i in range(14):
            v.set(hx + sx_ * int(i * 0.5), F3 + 18 + i, hz + sz_ * int(i * 0.5), 'minecraft:polished_basalt[axis=y]' if i < 10 else 'minecraft:gilded_blackstone')
    # ---------------- basement vault under hall (switchback from the NE of the hall)
    VY = G - 15
    foundation(v, 30, VY - 1, 30, 50, VY - 1, 0, BB)
    v.fill(30, VY - 1, 30, 60, VY, 60, None, fn=lambda x, y, z: BB()) if False else None
    vault(v, 33, 33, 47, 47, VY, 8, pal, 'realmbreak:chests/cinderhold_loot', 'realmbreak:chests/cinderhold_vault', facing='south')
    v.fill(48, VY, 28, 56, VY, 52, None, fn=lambda x, y, z: BB())
    v.carve(49, VY + 1, 33, 54, G - 2, 45)
    switchback(v, 49, 33, VY + 1, G - VY - 1, 'z', 1, 3, 'minecraft:blackstone_stairs', landing=BB)
    for y in range(VY + 1, VY + 4):
        for z in range(33, 36):
            v.air(47, y, z); v.air(48, y, z)
    for y in range(VY + 1, VY + 4):
        v.set(47, y, 34, 'minecraft:iron_bars')
    for z in range(34, 40):
        v.set(48, VY, z, 'minecraft:magma_block') if z in (36, 38) else None
    # ---------------- exterior dressing
    # approach braziers + landmark plaza south of the bridge
    for z in (74, 70):
        for x in (35, 45):
            pass
    pz = 79
    v.landmark(40, G, pz, SITE_GATE)
    v.set(40, G - 1, pz, 'minecraft:chiseled_polished_blackstone')
    for dx in (-2, 2):
        pillar(v, 40 + dx, pz, G, G + 4, pal['pillar'], pal['cap'])
        v.set(40 + dx, G + 5, pz, 'minecraft:netherrack')
        v.set(40 + dx, G + 6, pz, 'minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]')
    # lava falls from tower bases into moat (decor): magma accents
    for (tx, tz) in ((L, L), (R, L), (L, R), (R, R)):
        for a in range(0, 360, 45):
            x = round(tx + math.cos(math.radians(a)) * 9); z = round(tz + math.sin(math.radians(a)) * 9)
            v.set(x, G, z, 'minecraft:blackstone_wall[east=none,north=none,south=none,up=true,west=none,waterlogged=false]')
    # ageing
    v.weather({'minecraft:polished_blackstone_bricks': ['minecraft:cracked_polished_blackstone_bricks']}, 0.04)
    v.ruin(0.012, ymin=G + 30, only_names={'minecraft:nether_bricks', 'minecraft:polished_blackstone_bricks'})
    return v
