import sys; sys.path.insert(0,'.')
import importlib, walk, s_core
name = sys.argv[1]
m = importlib.import_module(name)
v = m.build()
G = 16
res = s_core.check(v, G, v.info, getattr(m,'START',(40, G, 79)))
print(res)
import vox
vox.render(v, f'_preview/structs/{v.name}_0.png', view=0)
vox.render_slice(v, f'_preview/slice_{name}_z40.png', 'z', 40)
