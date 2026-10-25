"""Builds all structure NBT files + isometric previews + struct_meta.json."""
import importlib
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'src/main/resources/data/realmbreak/structure')
PREV = os.path.join(ROOT, 'tools/_preview/structs')

MODULES = ['s_cinder', 's_frost', 's_storm', 's_elderroot', 's_observatory', 's_outposts', 's_landmarks', 's_rift']


def main(only=None, preview=True):
    sys.path.insert(0, os.path.dirname(__file__))
    import vox
    meta_path = os.path.join(ROOT, 'tools/struct_meta.json')
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for m in MODULES:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), m + '.py')):
            continue
        if only and m not in only:
            continue
        mod = importlib.import_module(m)
        t = time.time()
        res = mod.build()
        vs = res if isinstance(res, list) else [res]
        for v in vs:
            info = v.export(OUT)
            meta[v.name] = info
            if preview:
                vox.render(v, os.path.join(PREV, v.name + '_0.png'), view=0)
                vox.render(v, os.path.join(PREV, v.name + '_2.png'), view=2)
            print(f'{v.name}: size={info["size"]} blocks={info["blocks"]} ground={info["ground"]} ({time.time() - t:.1f}s)')
    json.dump(meta, open(meta_path, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    main(only=args or None)
