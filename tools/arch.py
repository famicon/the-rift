"""Reusable architecture kit built on vox.Vox."""
import math
import random
from vox import *


class Mix:
    """weighted random block chooser (callable)."""
    def __init__(self, rng, *choices):
        self.rng = rng
        self.items = []
        self.total = 0
        for c in choices:
            b, w = (c, 1) if isinstance(c, str) else c
            self.items.append((b, w))
            self.total += w

    def __call__(self):
        r = self.rng.random() * self.total
        for b, w in self.items:
            r -= w
            if r <= 0:
                return b
        return self.items[-1][0]


def foundation(v, x0, z0, x1, z1, y_top, depth, blk):
    v.fill(x0, y_top - depth, z0, x1, y_top, z1, None, fn=lambda x, y, z: blk() if callable(blk) else blk)


def foundation_disc(v, cx, cz, y_top, depth, r, blk):
    for y in range(y_top - depth, y_top + 1):
        rr = r - (y_top - y) * 0.0
        v.disc(cx, y, cz, rr, blk)


def crenellate_ring(v, cx, cz, y, r, blk):
    pts = []
    n = max(8, int(2 * math.pi * r))
    seen = set()
    for i in range(n):
        a = i / n * math.tau
        x, z = round(cx + math.cos(a) * r), round(cz + math.sin(a) * r)
        if (x, z) in seen:
            continue
        seen.add((x, z))
        if len(seen) % 2 == 0:
            v.set(x, y, z, blk() if callable(blk) else blk)


def crenellate_rect(v, x0, z0, x1, z1, y, blk):
    i = 0
    for x in range(x0, x1 + 1):
        for z in (z0, z1):
            if (x + z) % 2 == 0:
                v.set(x, y, z, blk() if callable(blk) else blk)
    for z in range(z0, z1 + 1):
        for x in (x0, x1):
            if (x + z) % 2 == 0:
                v.set(x, y, z, blk() if callable(blk) else blk)


def tower(v, cx, cz, y0, r, h, wall, pal, floors=(), roof='cone', roof_h=None, slits=True, glass=None, base_flare=True, trim=None, light=None):
    """round tower; floors = list of y offsets with solid floors."""
    trim = trim or pal.get('trim', wall)
    for y in range(y0, y0 + h):
        v.ring(cx, y, cz, r, wall, 1.6)
        v.disc(cx, y, cz, r - 1.6, 'air')
    if base_flare:
        v.ring(cx, y0, cz, r + 1, trim, 1.2)
        v.ring(cx, y0 + 1, cz, r + 0.6, trim, 1.0)
    for f in floors:
        v.disc(cx, y0 + f, cz, r - 1, pal['floor'])
    # trim bands
    for band in range(6, h, 7):
        v.ring(cx, y0 + band, cz, r + 0.8, trim, 1.0)
    if slits:
        for y in range(y0 + 4, y0 + h - 3, 7):
            for a in (0, 90, 180, 270):
                x = round(cx + math.cos(math.radians(a)) * r)
                z = round(cz + math.sin(math.radians(a)) * r)
                for dy in (0, 1, 2):
                    v.set(x, y + dy, z, glass or pal.get('pane', 'minecraft:iron_bars'))
    # top
    v.ring(cx, y0 + h, cz, r + 1.2, trim, 1.4)
    if roof == 'cone':
        rh = roof_h or int(r * 2.6)
        v.cone(cx, cz, y0 + h + 1, rh, r + 1.4, pal['roof'])
        v.set(cx, y0 + h + 1 + rh, cz, pal.get('spire', 'minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]'))
        if rh > 3:
            v.set(cx, y0 + h + rh, cz, pal.get('spire_base', pal['roof']))
    elif roof == 'battlement':
        v.disc(cx, y0 + h, cz, r + 1, pal['floor'])
        crenellate_ring(v, cx, cz, y0 + h + 1, r + 0.5, wall)
        if light:
            v.set(cx, y0 + h + 1, cz, light)
    elif roof == 'dome':
        v.sphere(cx, y0 + h, cz, r + 1.2, r + 1.2, r + 1.2, pal['roof'], hollow=True, upper=True, w=1.2)


def curtain_wall(v, x0, z0, x1, z1, y0, h, thick, wall, pal, crenel=True, walkway=True):
    """a straight wall between (x0,z0)-(x1,z1) axis aligned (one of them equal)."""
    if x0 == x1:
        xs = range(x0 - thick // 2, x0 - thick // 2 + thick)
        for x in xs:
            for z in range(min(z0, z1), max(z0, z1) + 1):
                for y in range(y0, y0 + h):
                    v.set(x, y, z, wall)
        if crenel:
            for z in range(min(z0, z1), max(z0, z1) + 1):
                for x in (xs[0], xs[-1]):
                    if z % 2 == 0:
                        v.set(x, y0 + h, z, wall)
                if walkway:
                    for x in xs[1:-1]:
                        v.set(x, y0 + h - 1, z, pal['floor'])
    else:
        zs = range(z0 - thick // 2, z0 - thick // 2 + thick)
        for z in zs:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for y in range(y0, y0 + h):
                    v.set(x, y, z, wall)
        if crenel:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for z in (zs[0], zs[-1]):
                    if x % 2 == 0:
                        v.set(x, y0 + h, z, wall)
                if walkway:
                    for z in zs[1:-1]:
                        v.set(x, y0 + h - 1, z, pal['floor'])


def pillar(v, x, z, y0, y1, shaft, cap=None, base=None):
    for y in range(y0, y1 + 1):
        v.set(x, y, z, shaft)
    if base:
        v.set(x, y0, z, base)
    if cap:
        v.set(x, y1, z, cap)


def chandelier(v, x, y_top, z, pal, drop=3, ring=True):
    for k in range(drop):
        v.set(x, y_top - k, z, 'minecraft:chain[axis=y,waterlogged=false]')
    y = y_top - drop
    v.set(x, y, z, pal.get('lantern', lantern()))
    if ring:
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v.set(x + dx, y + 1, z + dz, 'minecraft:iron_bars')
            v.set(x + dx, y, z + dz, pal.get('lantern', lantern()))


def brazier(v, x, y, z, fuel='minecraft:netherrack', fire='minecraft:fire[age=0,east=false,north=false,south=false,up=false,west=false]'):
    v.set(x, y, z, fuel)
    v.set(x, y + 1, z, fire)


def banner(v, x, y, z, facing, color='red'):
    v.set(x, y, z, f'minecraft:{color}_wall_banner[facing={facing}]')


def sconce(v, x, y, z, facing, torch=True):
    v.set(x, y, z, wall_torch(facing) if torch else lantern())


def hall(v, x0, z0, x1, z1, y0, h, pal, pillars=True, carpet=None, spacing=6, chand=True, banners=True):
    """interior hall: assumes shell exists; carves, lays floor, pillars, chandeliers."""
    v.carve(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y0 + h - 1, z1 - 1)
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            v.set(x, y0, z, pal['floor']() if callable(pal['floor']) else pal['floor'])
    if carpet:
        mid = (x0 + x1) // 2
        for z in range(z0 + 1, z1):
            for x in (mid - 1, mid, mid + 1):
                v.set(x, y0 + 1, z, carpet)
    if pillars:
        for x in range(x0 + spacing, x1 - 2, spacing):
            for z in (z0 + 3, z1 - 3):
                pillar(v, x, z, y0 + 1, y0 + h - 1, pal['pillar'], pal.get('cap'), pal.get('base'))
    if chand:
        for x in range(x0 + spacing // 2 + 1, x1 - 1, spacing):
            chandelier(v, x, y0 + h - 1, (z0 + z1) // 2, pal, drop=3)
    if banners:
        for x in range(x0 + 4, x1 - 3, spacing):
            banner(v, x, y0 + h - 4, z0 + 1, 'south', pal.get('banner', 'red'))
            banner(v, x, y0 + h - 4, z1 - 1, 'north', pal.get('banner', 'red'))


def corridor_x(v, x0, x1, z, y0, pal, w=3, h=4):
    """E-W corridor carved and lined; centred on z."""
    for x in range(x0, x1 + 1):
        for dz in range(-(w // 2) - 1, w // 2 + 2):
            for y in range(y0, y0 + h + 1):
                edge = abs(dz) == w // 2 + 1 or y in (y0, y0 + h)
                if edge:
                    v.set(x, y, z + dz, pal['wall']() if y != y0 else pal['floor']())
                else:
                    v.air(x, y, z + dz)
        if x % 5 == 0:
            v.set(x, y0 + h - 1, z - w // 2, pal.get('lantern', lantern(True)))


def corridor_z(v, z0, z1, x, y0, pal, w=3, h=4):
    for z in range(z0, z1 + 1):
        for dx in range(-(w // 2) - 1, w // 2 + 2):
            for y in range(y0, y0 + h + 1):
                edge = abs(dx) == w // 2 + 1 or y in (y0, y0 + h)
                if edge:
                    v.set(x + dx, y, z, pal['wall']() if y != y0 else pal['floor']())
                else:
                    v.air(x + dx, y, z)
        if z % 5 == 0:
            v.set(x - w // 2, y0 + h - 1, z, pal.get('lantern', lantern(True)))


def arena(v, cx, cz, y0, r, h, pal, boss_index, ring_fn=None, dome=True):
    """circular boss arena: floor disc, wall ring, dome, altar in centre with decorative rings."""
    for y in range(y0, y0 + h):
        v.ring(cx, y, cz, r, pal['wall'], 2.0)
        v.disc(cx, y, cz, r - 2, 'air')
    v.disc(cx, y0, cz, r, pal['floor'])
    # concentric floor rings
    for rr, blk in ((r - 3, pal['trim']), (int(r * 0.6), pal.get('accent', pal['trim'])), (4, pal['trim'])):
        v.ring(cx, y0, cz, rr, blk, 1.0)
    if ring_fn:
        ring_fn(v, cx, cz, y0, r)
    # columns around wall
    n = 12
    for i in range(n):
        a = i / n * math.tau
        x, z = round(cx + math.cos(a) * (r - 3)), round(cz + math.sin(a) * (r - 3))
        pillar(v, x, z, y0 + 1, y0 + h - 2, pal['pillar'], pal.get('cap'), pal.get('base'))
        v.set(x, y0 + h - 3, z, pal.get('lantern', lantern()))
    # roof
    if dome:
        v.sphere(cx, y0 + h - 1, cz, r + 1, int(r * 0.8), r + 1, pal['roof'], hollow=True, upper=True, w=2.0)
        # oculus
        for y in range(y0 + h, y0 + h + int(r * 0.8) + 2):
            v.disc(cx, y, cz, 3, 'air') if y > y0 + h + int(r * 0.8) - 3 else None
    v.altar(cx, y0 + 1, cz, boss_index)


def vault(v, x0, z0, x1, z1, y0, h, pal, loot, sigil_loot=None, facing='south'):
    v.room(x0, y0, z0, x1, y0 + h, z1, pal['wall'], pal['floor'], pal['wall'])
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    v.set(cx, y0 + 1, cz, pal['trim'])
    v.chest(cx, y0 + 2, cz, facing, sigil_loot or loot)
    for dx in (-2, 2):
        for dz in (-2, 2):
            v.chest(cx + dx, y0 + 1, cz + dz, facing, loot)
    for x in (x0 + 1, x1 - 1):
        for z in (z0 + 1, z1 - 1):
            pillar(v, x, z, y0 + 1, y0 + h - 1, pal['pillar'])
    v.set(cx, y0 + h - 1, cz, pal.get('lantern', lantern(True)))


def spawner_room(v, x0, z0, x1, z1, y0, h, pal, entity, loot=None, extra=None):
    v.room(x0, y0, z0, x1, y0 + h, z1, pal['wall'], pal['floor'], pal['wall'])
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    v.set(cx, y0 + 1, cz, pal['trim'])
    v.spawner(cx, y0 + 2, cz, entity)
    for dx, dz in ((-3, -3), (3, 3), (-3, 3), (3, -3)):
        if x0 < cx + dx < x1 and z0 < cz + dz < z1:
            pillar(v, cx + dx, cz + dz, y0 + 1, y0 + h - 1, pal['pillar'])
    if loot:
        v.chest(x0 + 1, y0 + 1, z0 + 1, 'south', loot)
    if extra:
        extra(v, x0, z0, x1, z1, y0, h)


def open_door(v, x, y, z, axis='x', w=2, h=3):
    """punch a doorway through a wall: axis = direction the wall runs along ('x' or 'z')."""
    for i in range(w):
        for j in range(h):
            if axis == 'x':
                v.air(x + i, y + j, z)
            else:
                v.air(x, y + j, z + i)


def gate_arch(v, plane, a0, a1, base, c, depth, blk, pointed=True):
    v.arch(plane, a0, a1, base, c, depth, blk, pointed=pointed, thick=2)


def buttress(v, x, z, facing, y0, h, blk, stair_blk, length=4):
    """flying buttress style stepped support leaning against a wall at (x,z) going outward along facing."""
    dx, dz = DIRS[facing]
    for i in range(1, length + 1):
        top = h - i * (h // (length + 1))
        for y in range(y0, y0 + max(1, top)):
            v.set(x + dx * i, y, z + dz * i, blk)
        v.set(x + dx * i, y0 + max(1, top), z + dz * i, stair(stair_blk, OPP[facing]))


def roof_gable(v, x0, z0, x1, z1, y, stair_blk, slab_blk, axis='x'):
    """simple gable roof over rectangle; ridge along `axis`."""
    if axis == 'x':
        w = z1 - z0 + 1
        half = w // 2
        for i in range(half + 1):
            for x in range(x0 - 1, x1 + 2):
                zN, zS = z0 + i - 1, z1 - i + 1
                if zN <= zS:
                    v.set(x, y + i, zN, stair(stair_blk, 'south'))
                    v.set(x, y + i, zS, stair(stair_blk, 'north'))
                    if zN == zS:
                        v.set(x, y + i, zN, slab(slab_blk, 'bottom'))
                    for z in range(zN + 1, zS):
                        v.air(x, y + i, z) if False else None
    else:
        w = x1 - x0 + 1
        half = w // 2
        for i in range(half + 1):
            for z in range(z0 - 1, z1 + 2):
                xW, xE = x0 + i - 1, x1 - i + 1
                if xW <= xE:
                    v.set(xW, y + i, z, stair(stair_blk, 'east'))
                    v.set(xE, y + i, z, stair(stair_blk, 'west'))
                    if xW == xE:
                        v.set(xW, y + i, z, slab(slab_blk, 'bottom'))


def window(v, plane, c, a, y, w, h, thick, glass, frame=None, pointed=True):
    """punch a tall window through a wall. plane='z': wall runs along x occupying z=c..c+thick-1, window centred on x=a.
    plane='x': wall runs along z occupying x=c..c+thick-1, centred on z=a."""
    half = w // 2
    for j in range(h):
        # narrow the top two rows for a pointed look
        hw = half
        if pointed and j >= h - 2:
            hw = max(0, half - (1 if j == h - 2 else 2))
        for i in range(-hw, hw + 1):
            for t in range(thick):
                x, z = (a + i, c + t) if plane == 'z' else (c + t, a + i)
                if t == thick // 2 and glass:
                    v.set(x, y + j, z, glass)
                else:
                    v.air(x, y + j, z)
        if frame:
            for i in (-hw - 1, hw + 1):
                for t in range(thick):
                    x, z = (a + i, c + t) if plane == 'z' else (c + t, a + i)
                    v.set(x, y + j, z, frame)
    if frame:
        for i in range(-half, half + 1):
            for t in range(thick):
                x, z = (a + i, c + t) if plane == 'z' else (c + t, a + i)
                v.set(x, y - 1, z, frame)


def keep_shell(v, x0, z0, x1, z1, y0, h, pal, wall_t=2, pilaster=8, trim_every=10):
    """solid walled box with pilasters and trim bands (interior carved)."""
    v.fill(x0, y0, z0, x1, y0 + h, z1, None, fn=lambda x, y, z: pal['wall']())
    v.carve(x0 + wall_t, y0 + 1, z0 + wall_t, x1 - wall_t, y0 + h - 1, z1 - wall_t)
    for y in range(y0 + trim_every, y0 + h, trim_every):
        for x in range(x0 - 1, x1 + 2):
            v.set(x, y, z0 - 1, pal['trim']); v.set(x, y, z1 + 1, pal['trim'])
        for z in range(z0 - 1, z1 + 2):
            v.set(x0 - 1, y, z, pal['trim']); v.set(x1 + 1, y, z, pal['trim'])
    if pilaster:
        for x in range(x0 + pilaster // 2, x1, pilaster):
            for y in range(y0, y0 + h):
                v.set(x, y, z0 - 1, pal['pillar']); v.set(x, y, z1 + 1, pal['pillar'])
        for z in range(z0 + pilaster // 2, z1, pilaster):
            for y in range(y0, y0 + h):
                v.set(x0 - 1, y, z, pal['pillar']); v.set(x1 + 1, y, z, pal['pillar'])


def floor_slab(v, x0, z0, x1, z1, y, pal):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            v.set(x, y, z, pal['floor']())


def switchback(v, x0, z0, y0, h, axis='z', dirn=1, width=3, blk='minecraft:stone_brick_stairs', landing=None, clear=3, rail=None):
    """Two-flight staircase climbing h blocks from standing level y0 to y0+h.
    Entry at the bottom of lane A (a=0), exit at the end of lane B (a=0 side) at standing level y0+h.
    axis 'z': run along z (dirn +1/-1), lanes side by side along +x. axis 'x': run along x, lanes along +z."""
    half = (h + 1) // 2
    other = h - half
    lan = landing or v.rng and 'minecraft:stone_bricks'

    def P(a, b):
        return (x0 + b, z0 + dirn * a) if axis == 'z' else (x0 + dirn * a, z0 + b)
    if axis == 'z':
        asc = 'south' if dirn == 1 else 'north'
    else:
        asc = 'east' if dirn == 1 else 'west'
    face_up = OPP[asc]
    face_down = asc   # returning flight ascends opposite direction
    total_a = half + width  # run length incl. landing
    # carve volume: per column, only as high as the stairs need (keeps the floor above intact elsewhere)
    for a in range(-1, total_a + 1):
        for b in range(0, 2 * width):
            if b >= width and 0 <= a <= half + width - 1:
                k = (half + width - 1) - a
                top = y0 + half + k + clear if k < other else y0 + clear
            elif b < width and half <= a < half + width:
                top = y0 + half + clear
            elif b < width and a < half:
                top = y0 + max(a, 0) + clear
            else:
                top = y0 + clear
            x, z = P(a, b)
            for y in range(y0, top + 1):
                v.air(x, y, z)
    # lane A
    for k in range(half):
        for b in range(width):
            x, z = P(k, b)
            for yy in range(y0 - 1, y0 + k):
                v.set(x, yy, z, lan)
            v.set(x, y0 + k, z, stair(blk, face_up))
    # landing
    for a in range(half, half + width):
        for b in range(0, 2 * width):
            x, z = P(a, b)
            for yy in range(y0 - 1, y0 + half):
                v.set(x, yy, z, lan)
    # lane B (ascends in the opposite direction)
    for k in range(other):
        a = half + width - 1 - k
        for b in range(width, 2 * width):
            x, z = P(a, b)
            for yy in range(y0 - 1, y0 + half + k):
                v.set(x, yy, z, lan)
            v.set(x, y0 + half + k, z, stair(blk, face_down))
    # clearance above lane B near the top handled by carve; ensure exit floor
    return P(0, width)
