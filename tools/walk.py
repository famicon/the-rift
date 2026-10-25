"""Rough walkability BFS over a Vox to verify key spots are reachable on foot."""
from collections import deque
def is_solid(v, x, y, z):
    s = v.b.get((x, y, z))
    if s is None:
        return y < v.ground      # natural terrain below ground level
    if s == 'air':
        return False
    n = s[0]
    if any(k in n for k in ('iron_bars', 'glass_pane', '_pane', 'fire', 'torch', 'lantern', 'carpet', 'banner', 'chain', 'end_rod', 'rail', 'button', 'pressure_plate', 'lightning_rod', 'vine', 'bloom', 'portal')):
        return False
    if 'door' in n or 'trapdoor' in n or 'fence_gate' in n:
        return False
    if 'slab' in n:
        return True
    return True
def passable(v, x, y, z):
    s = v.b.get((x, y, z))
    if s is None or s == 'air':
        return True
    n = s[0]
    if 'lava' in n or 'water' in n:
        return False
    return not is_solid(v, x, y, z)
def reach(v, start, maxn=3_000_000):
    (bx0,by0,bz0),(bx1,by1,bz1)=v.bounds()
    seen = {start}
    q = deque([start])
    while q:
        x, y, z = q.popleft()
        for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, nz = x+dx, z+dz
            if not (bx0-2<=nx<=bx1+2 and bz0-2<=nz<=bz1+2): continue
            # try same level, step up 1, step down up to 4
            for dy in (0, 1, -1, -2, -3, -4):
                ny = y+dy
                if not (is_solid(v, nx, ny-1, nz) and passable(v, nx, ny, nz) and passable(v, nx, ny+1, nz)):
                    continue
                if dy == 1 and not passable(v, x, y+2, z):
                    continue
                if dy < 0:
                    # need clearance to fall: cells above landing along drop
                    if not all(passable(v, nx, yy, nz) for yy in range(ny, y+2)):
                        continue
                if (nx, ny, nz) not in seen:
                    seen.add((nx, ny, nz)); q.append((nx, ny, nz))
                break
        if len(seen) > maxn: break
    return seen
def check(v, start, targets):
    seen = reach(v, start)
    out = {}
    for name, (tx, ty, tz) in targets.items():
        ok = any((tx+dx, ty+dy, tz+dz) in seen for dx in (-1,0,1) for dz in (-1,0,1) for dy in (-1,0,1))
        out[name] = ok
    return out, len(seen)
