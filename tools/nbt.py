"""Minimal NBT writer (big-endian, gzip) for Minecraft structure templates."""
import gzip
import struct


class TByte(int): pass
class TShort(int): pass
class TInt(int): pass
class TLong(int): pass
class TFloat(float): pass
class TDouble(float): pass


def _tid(v):
    if isinstance(v, bool):
        return 1
    if isinstance(v, TByte): return 1
    if isinstance(v, TShort): return 2
    if isinstance(v, (TInt, int)) and not isinstance(v, (TLong,)): return 3
    if isinstance(v, TLong): return 4
    if isinstance(v, TFloat): return 5
    if isinstance(v, (TDouble, float)): return 6
    if isinstance(v, str): return 8
    if isinstance(v, list): return 9
    if isinstance(v, dict): return 10
    raise TypeError(type(v))


def _str(s):
    b = s.encode('utf-8')
    return struct.pack('>H', len(b)) + b


def _payload(v, tid):
    if tid == 1: return struct.pack('>b', int(v))
    if tid == 2: return struct.pack('>h', int(v))
    if tid == 3: return struct.pack('>i', int(v))
    if tid == 4: return struct.pack('>q', int(v))
    if tid == 5: return struct.pack('>f', float(v))
    if tid == 6: return struct.pack('>d', float(v))
    if tid == 8: return _str(v)
    if tid == 9:
        if not v:
            return struct.pack('>bi', 0, 0)
        et = _tid(v[0])
        out = [struct.pack('>bi', et, len(v))]
        for x in v:
            out.append(_payload(x, et))
        return b''.join(out)
    if tid == 10:
        out = []
        for k, x in v.items():
            t = _tid(x)
            out.append(struct.pack('>b', t) + _str(k) + _payload(x, t))
        out.append(b'\x00')
        return b''.join(out)
    raise TypeError(tid)


def dumps(root):
    return struct.pack('>b', 10) + _str('') + _payload(root, 10)


def write(path, root):
    with gzip.GzipFile(path, 'wb', mtime=0) as f:
        f.write(dumps(root))
