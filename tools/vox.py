"""Voxel builder + structure NBT exporter + isometric previewer."""
import math
import os
import random
import nbt
from nbt import TByte, TShort, TInt, TDouble

DATA_VERSION = 3955  # Minecraft 1.21.1
DIRS = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}
OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
RIGHT = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}
LEFT = {v: k for k, v in RIGHT.items()}


def parse(b):
    if b is None:
        return None
    if '[' in b:
        name, props = b[:-1].split('[')
        pd = dict(p.split('=') for p in props.split(','))
    else:
        name, pd = b, {}
    if ':' not in name:
        name = 'minecraft:' + name
    return name, tuple(sorted(pd.items()))


def stair(block, facing, half='bottom', shape='straight'):
    return f'{block}[facing={facing},half={half},shape={shape},waterlogged=false]'


def slab(block, typ='bottom'):
    return f'{block}[type={typ},waterlogged=false]'


def axis(block, ax):
    return f'{block}[axis={ax}]'


def trapdoor(block, facing, half='top', open_=False):
    return f'{block}[facing={facing},half={half},open={"true" if open_ else "false"},powered=false,waterlogged=false]'


def wall_torch(facing):
    return f'minecraft:wall_torch[facing={facing}]'


def lantern(hanging=False, soul=False):
    return f'minecraft:{"soul_" if soul else ""}lantern[hanging={"true" if hanging else "false"},waterlogged=false]'


class Vox:
    def __init__(self, name):
        self.name = name
        self.b = {}          # (x,y,z) -> parsed state or 'air'
        self.be = {}         # (x,y,z) -> nbt dict
        self.entities = []   # (pos(float3), nbt)
        self.ground = 1
        self.rng = random.Random(sum(ord(c) for c in name) * 31 + 7)

    # ---------------- basic
    def set(self, x, y, z, blk):
        x, y, z = int(x), int(y), int(z)
        if callable(blk):
            blk = blk()
        if blk is None:
            return
        self.b[(x, y, z)] = 'air' if blk == 'air' else parse(blk)

    def air(self, x, y, z):
        self.b[(int(x), int(y), int(z))] = 'air'

    def get(self, x, y, z):
        return self.b.get((int(x), int(y), int(z)))

    def solid(self, x, y, z):
        v = self.b.get((int(x), int(y), int(z)))
        return v is not None and v != 'air'

    def fill(self, x0, y0, z0, x1, y1, z1, blk, fn=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, fn(x, y, z) if fn else blk)

    def carve(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, 'air')

    def shell(self, x0, y0, z0, x1, y1, z1, blk, top=True, bottom=True):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    edge = x in (x0, x1) or z in (z0, z1) or (top and y == y1) or (bottom and y == y0)
                    if edge:
                        self.set(x, y, z, blk() if callable(blk) else blk)

    def room(self, x0, y0, z0, x1, y1, z1, wall, floor=None, ceil=None):
        """hollow room: walls, floor at y0, ceiling at y1, air inside."""
        self.fill(x0, y0, z0, x1, y1, z1, None)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                for y in range(y0, y1 + 1):
                    if x in (x0, x1) or z in (z0, z1):
                        self.set(x, y, z, wall() if callable(wall) else wall)
                    elif y == y0:
                        self.set(x, y, z, (floor or wall)() if callable(floor or wall) else (floor or wall))
                    elif y == y1:
                        self.set(x, y, z, (ceil or wall)() if callable(ceil or wall) else (ceil or wall))
                    else:
                        self.air(x, y, z)

    def disc(self, cx, y, cz, r, blk, hollow_r=None):
        r2 = r * r
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                d2 = (x - cx) ** 2 + (z - cz) ** 2
                if d2 <= r2 + 0.25 and (hollow_r is None or d2 >= hollow_r * hollow_r):
                    self.set(x, y, z, blk() if callable(blk) else blk)

    def ring(self, cx, y, cz, r, blk, w=1.0):
        self.disc(cx, y, cz, r, blk, hollow_r=max(0, r - w))

    def cyl(self, cx, cz, y0, y1, r, blk, hollow=False, w=1.0):
        for y in range(y0, y1 + 1):
            if hollow:
                self.ring(cx, y, cz, r, blk, w)
            else:
                self.disc(cx, y, cz, r, blk)

    def cylair(self, cx, cz, y0, y1, r):
        for y in range(y0, y1 + 1):
            self.disc(cx, y, cz, r, 'air')

    def sphere(self, cx, cy, cz, rx, ry, rz, blk, hollow=False, upper=False, w=1.0, fn=None):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                if upper and y < cy:
                    continue
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                    if d <= 1.0:
                        if hollow:
                            dd = ((x - cx) / max(0.5, rx - w)) ** 2 + ((y - cy) / max(0.5, ry - w)) ** 2 + ((z - cz) / max(0.5, rz - w)) ** 2
                            if dd < 1.0:
                                continue
                        self.set(x, y, z, fn(x, y, z) if fn else (blk() if callable(blk) else blk))

    def cone(self, cx, cz, y0, h, r0, blk, hollow=False):
        for i in range(h):
            r = r0 * (1 - i / float(h))
            if r < 0.4:
                self.set(cx, y0 + i, cz, blk() if callable(blk) else blk)
                continue
            if hollow:
                self.ring(cx, y0 + i, cz, r, blk, 1.2)
            else:
                self.disc(cx, y0 + i, cz, r, blk)

    def line(self, p0, p1, blk, th=0):
        (x0, y0, z0), (x1, y1, z1) = p0, p1
        n = int(max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))) * 2 + 1
        for i in range(n + 1):
            t = i / n
            x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
            if th <= 0:
                self.set(round(x), round(y), round(z), blk() if callable(blk) else blk)
            else:
                self.sphere(x, y, z, th, th, th, blk)

    # ---------------- architecture helpers
    def arch(self, plane, a0, a1, base, c, depth, blk, pointed=False, thick=1):
        """vertical arch over the opening a0..a1 (inclusive). plane='x': arch spans along x at z=c..c+depth-1;
        plane='z': spans along z at x=c..c+depth-1.  Ring blocks start at y=base (the spring line)."""
        span = a1 - a0 + 1
        mid = (a0 + a1) / 2.0
        for a in range(a0 - thick, a1 + thick + 1):
            for y in range(base, base + span + thick + 2):
                dy = y - base + 0.5
                if pointed:
                    cx = a0 - 0.5 if a > mid else a1 + 0.5
                    dist = math.hypot(a - cx, dy)
                    r = span
                else:
                    dist = math.hypot(a - mid, dy)
                    r = span / 2.0
                if r <= dist < r + thick:
                    for d in range(depth):
                        if plane == 'x':
                            self.set(a, y, c + d, blk() if callable(blk) else blk)
                        else:
                            self.set(c + d, y, a, blk() if callable(blk) else blk)

    def square_spiral(self, x0, z0, s, y0, height, stair_blk, clear=3, lit=None):
        """walkable stair running around the perimeter of an s x s square, climbing `height` blocks."""
        path = []
        for x in range(x0, x0 + s - 1):
            path.append((x, z0, 'east'))
        for z in range(z0, z0 + s - 1):
            path.append((x0 + s - 1, z, 'south'))
        for x in range(x0 + s - 1, x0, -1):
            path.append((x, z0 + s - 1, 'west'))
        for z in range(z0 + s - 1, z0, -1):
            path.append((x0, z, 'north'))
        n = len(path)
        for i in range(height):
            x, z, mv = path[i % n]
            y = y0 + i
            self.set(x, y, z, stair(stair_blk, OPP[mv]))
            for k in range(1, clear + 1):
                self.air(x, y + k, z)
            # a support block below for robustness
            if i % n >= 0:
                pass
        return path

    def door(self, x, y, z, facing, blk='oak_door', hinge='left', open_=False):
        o = 'true' if open_ else 'false'
        self.set(x, y, z, f'minecraft:{blk}[facing={facing},half=lower,hinge={hinge},open={o},powered=false]')
        self.set(x, y + 1, z, f'minecraft:{blk}[facing={facing},half=upper,hinge={hinge},open={o},powered=false]')

    def chest(self, x, y, z, facing, loot):
        self.set(x, y, z, f'minecraft:chest[facing={facing},type=single,waterlogged=false]')
        self.be[(x, y, z)] = {'id': 'minecraft:chest', 'LootTable': loot}

    def barrel(self, x, y, z, loot):
        self.set(x, y, z, 'minecraft:barrel[facing=up,open=false]')
        self.be[(x, y, z)] = {'id': 'minecraft:barrel', 'LootTable': loot}

    def spawner(self, x, y, z, entity, count=3, rng_range=4, maxnear=6, rplayer=14):
        self.set(x, y, z, 'minecraft:spawner')
        self.be[(x, y, z)] = {'id': 'minecraft:mob_spawner',
                              'SpawnData': {'entity': {'id': entity}},
                              'SpawnPotentials': [{'weight': TInt(1), 'data': {'entity': {'id': entity}}}],
                              'RequiredPlayerRange': TShort(rplayer), 'MaxNearbyEntities': TShort(maxnear), 'SpawnCount': TShort(count),
                              'SpawnRange': TShort(rng_range), 'Delay': TShort(20), 'MinSpawnDelay': TShort(200), 'MaxSpawnDelay': TShort(500)}

    def npc(self, x, y, z, npc_id):
        self.entities.append(((x + 0.5, y, z + 0.5), (x, y, z), {'id': 'realmbreak:quest_npc', 'NpcId': npc_id, 'PersistenceRequired': TByte(1)}))

    def mob(self, x, y, z, entity):
        self.entities.append(((x + 0.5, y, z + 0.5), (x, y, z), {'id': entity, 'PersistenceRequired': TByte(1)}))

    def landmark(self, x, y, z, site_index):
        self.set(x, y, z, f'realmbreak:landmark_stone[site={site_index}]')

    def altar(self, x, y, z, boss_index):
        self.set(x, y, z, f'realmbreak:boss_altar[boss={boss_index}]')

    def rift_gate(self, x, y, z, ax='x', frame='realmbreak:riftstone_bricks', accent='realmbreak:chiseled_riftstone', glow='realmbreak:rift_crystal_block'):
        """5 wide x 6 tall gate; (x,y,z) = bottom-left frame corner; ax = axis along which gate is wide."""
        def P(i, j):
            return (x + i, y + j, z) if ax == 'x' else (x, y + j, z + i)
        for i in range(5):
            for j in range(6):
                edge = i in (0, 4) or j in (0, 5)
                if edge:
                    blk = accent if (i in (0, 4) and j in (0, 5)) or (j == 5 and i == 2) else frame
                    if (i in (0, 4) and j == 3):
                        blk = glow
                    self.set(*P(i, j), blk)
                else:
                    self.set(*P(i, j), f'realmbreak:rift_portal[axis={ax}]')

    # ---------------- ageing
    def weather(self, mapping, prob):
        """randomly swap blocks by name: mapping {'minecraft:stone_bricks': ['minecraft:mossy_stone_bricks', ...]}"""
        for k, v in list(self.b.items()):
            if v == 'air':
                continue
            alts = mapping.get(v[0])
            if alts and self.rng.random() < prob:
                self.b[k] = (self.rng.choice(alts), v[1])

    def ruin(self, prob, ymin=None, only_names=None):
        for k, v in list(self.b.items()):
            if v == 'air':
                continue
            if ymin is not None and k[1] < ymin:
                continue
            if only_names and v[0] not in only_names:
                continue
            if self.rng.random() < prob:
                del self.b[k]

    def bounds(self):
        xs = [k[0] for k in self.b]; ys = [k[1] for k in self.b]; zs = [k[2] for k in self.b]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    # ---------------- export
    def export(self, outdir):
        (mx, my, mz), (Mx, My, Mz) = self.bounds()
        palette, pidx = [], {}
        blocks = []
        for (x, y, z), st in sorted(self.b.items()):
            if st == 'air':
                key = ('minecraft:air', ())
            else:
                key = st
            if key not in pidx:
                pidx[key] = len(palette)
                e = {'Name': key[0]}
                if key[1]:
                    e['Properties'] = {k: v for k, v in key[1]}
                palette.append(e)
            ent = {'pos': [TInt(x - mx), TInt(y - my), TInt(z - mz)], 'state': TInt(pidx[key])}
            if (x, y, z) in self.be:
                ent['nbt'] = self.be[(x, y, z)]
            blocks.append(ent)
        ents = []
        for (px, py, pz), (bx, by, bz), tag in self.entities:
            ents.append({'pos': [TDouble(px - mx), TDouble(py - my), TDouble(pz - mz)], 'blockPos': [TInt(bx - mx), TInt(by - my), TInt(bz - mz)], 'nbt': tag})
        root = {'DataVersion': TInt(DATA_VERSION), 'size': [TInt(Mx - mx + 1), TInt(My - my + 1), TInt(Mz - mz + 1)], 'palette': palette, 'blocks': blocks, 'entities': ents}
        os.makedirs(outdir, exist_ok=True)
        nbt.write(os.path.join(outdir, self.name + '.nbt'), root)
        return {'size': [Mx - mx + 1, My - my + 1, Mz - mz + 1], 'ground': self.ground - my, 'blocks': len(blocks)}


# ====================================================================== preview
COLORS = [
    ('realmbreak:rift_portal', (150, 100, 255)), ('landmark', (255, 216, 106)), ('boss_altar', (200, 120, 255)), ('crystal', (140, 120, 255)),
    ('lava', (255, 120, 20)), ('magma', (220, 90, 20)), ('glowstone', (255, 220, 120)), ('lantern', (255, 210, 120)), ('torch', (255, 200, 90)), ('sea_lantern', (200, 245, 235)),
    ('shroomlight', (255, 170, 80)), ('amethyst', (170, 110, 230)), ('obsidian', (30, 20, 50)), ('purpur', (170, 120, 170)), ('end_stone', (225, 225, 170)),
    ('blackstone', (45, 40, 48)), ('basalt', (70, 70, 76)), ('nether_brick', (60, 30, 36)), ('deepslate', (60, 60, 66)), ('stone_brick', (125, 125, 125)), ('cobblestone', (110, 110, 110)),
    ('stone', (125, 125, 125)), ('andesite', (135, 135, 135)), ('granite', (150, 100, 85)), ('diorite', (190, 190, 190)), ('calcite', (225, 225, 220)), ('tuff', (110, 112, 100)),
    ('blue_ice', (110, 170, 240)), ('packed_ice', (140, 180, 235)), ('ice', (150, 200, 250)), ('snow', (245, 248, 250)), ('quartz', (235, 230, 222)),
    ('copper', (180, 110, 80)), ('oxidized', (80, 180, 160)), ('weathered', (100, 160, 130)), ('exposed', (160, 130, 100)),
    ('glass', (190, 225, 245)), ('dark_oak', (60, 40, 20)), ('spruce', (100, 70, 40)), ('oak', (160, 130, 80)), ('birch', (200, 190, 140)), ('jungle', (150, 105, 70)), ('mangrove', (120, 50, 50)), ('cherry', (230, 170, 190)),
    ('log', (95, 70, 40)), ('leaves', (50, 120, 40)), ('moss', (80, 120, 50)), ('vine', (60, 110, 40)), ('grass', (90, 150, 60)), ('dirt', (110, 80, 55)), ('mud', (70, 55, 50)),
    ('gold', (240, 200, 60)), ('iron', (190, 190, 195)), ('chain', (70, 70, 80)), ('bone', (230, 225, 200)), ('sand', (220, 205, 150)), ('terracotta', (150, 90, 70)),
    ('wool', (200, 60, 60)), ('carpet', (170, 40, 50)), ('banner', (190, 50, 50)), ('brick', (150, 80, 70)), ('water', (60, 100, 220)), ('prismarine', (90, 160, 150)),
    ('riftstone', (60, 58, 84)), ('rune', (230, 200, 90)), ('bricks', (110, 108, 120)),
]


def color_of(name):
    for k, c in COLORS:
        if k in name:
            return c
    h = abs(hash(name)) % 200
    return (60 + h // 2, 80 + h // 3, 90 + h // 4)


def render(v, path, scale=5, view=0, maxpx=2400):
    from PIL import Image, ImageDraw
    pts = [(k, color_of(s[0])) for k, s in v.b.items() if s != 'air' and 'barrier' not in s[0]]
    if not pts:
        return
    S = set(k for k, _ in pts)
    (mx, my, mz), (Mx, My, Mz) = v.bounds()
    W, D = Mx - mx + 1, Mz - mz + 1
    def tr(x, y, z):
        x -= mx; z -= mz
        if view == 1:
            x, z = D - 1 - z, x
        elif view == 2:
            x, z = W - 1 - x, D - 1 - z
        elif view == 3:
            x, z = z, W - 1 - x
        return x, y - my, z
    # choose scale to fit
    ext = (W + D) * 0.866 * scale
    if ext > maxpx:
        scale = max(2, int(scale * maxpx / ext))
    pw = int((W + D) * 0.866 * scale) + 20
    ph = int((W + D) * 0.5 * scale + (My - my + 2) * scale) + 20
    img = Image.new('RGB', (pw, ph), (22, 24, 36))
    dr = ImageDraw.Draw(img)
    items = []
    for (x, y, z), c in pts:
        tx, ty, tz = tr(x, y, z)
        items.append((tx + tz, ty, tx, tz, (x, y, z), c))
    items.sort()
    for _, ty, tx, tz, k, c in items:
        sx = (tx - tz) * 0.866 * scale + (D) * 0.866 * scale + 10
        sy = (tx + tz) * 0.5 * scale - ty * scale + (My - my + 1) * scale + 10
        s = scale
        top = [(sx, sy - s), (sx + 0.866 * s, sy - s + 0.5 * s), (sx, sy - s + s), (sx - 0.866 * s, sy - s + 0.5 * s)]
        left = [(sx - 0.866 * s, sy - s + 0.5 * s), (sx, sy), (sx, sy + s), (sx - 0.866 * s, sy + 0.5 * s)]
        right = [(sx, sy), (sx + 0.866 * s, sy - s + 0.5 * s + 0), (sx + 0.866 * s, sy + 0.5 * s), (sx, sy + s)]
        def sh(f):
            return tuple(max(0, min(255, int(ch * f))) for ch in c)
        dr.polygon(left, fill=sh(0.62))
        dr.polygon(right, fill=sh(0.8))
        dr.polygon(top, fill=sh(1.05))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def render_slice(v, path, axis, coord, scale=8):
    """vertical cross-section: axis='z' shows x-y plane at z=coord; axis='x' shows z-y at x=coord."""
    from PIL import Image
    (mx, my, mz), (Mx, My, Mz) = v.bounds()
    if axis == 'z':
        w = Mx - mx + 1
    else:
        w = Mz - mz + 1
    h = My - my + 1
    img = Image.new('RGB', (w * scale, h * scale), (22, 24, 36))
    px = img.load()
    for (x, y, z), st in v.b.items():
        if st == 'air':
            continue
        if (axis == 'z' and z != coord) or (axis == 'x' and x != coord):
            continue
        u = (x - mx) if axis == 'z' else (z - mz)
        c = color_of(st[0])
        for dx in range(scale):
            for dy in range(scale):
                edge = dx == 0 or dy == 0
                col = tuple(int(ch * (0.8 if edge else 1.0)) for ch in c)
                px[u * scale + dx, (h - 1 - (y - my)) * scale + dy] = col
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
