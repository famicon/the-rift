"""Generates textures, models, blockstates, lang, recipes, loot tables and tags from manifest.py."""
import json
import os
from PIL import Image
from pix import *
import manifest as M
import tex_items as TI
import tex_blocks as TB
import tex_entities as TE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'src/main/resources')
ASSETS = os.path.join(RES, 'assets/realmbreak')
DATA = os.path.join(RES, 'data/realmbreak')
MCDATA = os.path.join(RES, 'data/minecraft')
NS = 'realmbreak'


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def tex(kind, name, cv):
    cv.save(os.path.join(ASSETS, 'textures', kind, name + '.png'))


lang = {}

# ====================================================================== ITEMS
def gen_items():
    for it in M.ITEMS:
        i = it['id']
        lang[f'item.{NS}.{i}'] = it['name']
        if it['kind'] == 'bow':
            big = it.get('legendary', False)
            pal = TI.PALS[it['element']]
            frames = [TI.bow(pal, big, 0), TI.bow(pal, big, 0.45), TI.bow(pal, big, 0.75), TI.bow(pal, big, 1.0)]
            tex('item', i, frames[0])
            for k in range(3):
                tex('item', f'{i}_pulling_{k}', frames[k + 1])
            wj(os.path.join(ASSETS, 'models/item', i + '.json'), {
                'parent': 'minecraft:item/bow',
                'textures': {'layer0': f'{NS}:item/{i}'},
                'overrides': [
                    {'predicate': {'pulling': 1}, 'model': f'{NS}:item/{i}_pulling_0'},
                    {'predicate': {'pulling': 1, 'pull': 0.65}, 'model': f'{NS}:item/{i}_pulling_1'},
                    {'predicate': {'pulling': 1, 'pull': 0.9}, 'model': f'{NS}:item/{i}_pulling_2'},
                ]})
            for k in range(3):
                wj(os.path.join(ASSETS, 'models/item', f'{i}_pulling_{k}.json'), {
                    'parent': f'minecraft:item/bow_pulling_{k}', 'textures': {'layer0': f'{NS}:item/{i}_pulling_{k}'}})
        else:
            tex('item', i, TI.draw(it['icon'], it['element']))
            parent = 'minecraft:item/handheld' if it['kind'] in ('sword', 'staff') else 'minecraft:item/generated'
            wj(os.path.join(ASSETS, 'models/item', i + '.json'), {'parent': parent, 'textures': {'layer0': f'{NS}:item/{i}'}})


# ====================================================================== BLOCKS
def block_textures():
    T = {}
    T['riftstone'] = [('riftstone', TB.riftstone(1))]
    T['riftstone_bricks'] = [('riftstone_bricks', TB.bricks([rgb('#3b3a54'), rgb('#47466a')], rgb('#1c1b2c'), 2, glow=rgb('#7ff4ff'), glow_n=2))]
    T['chiseled_riftstone'] = [('chiseled_riftstone', TB.chiseled())]
    T['riftstone_pillar'] = [('riftstone_pillar', TB.pillar_side()), ('riftstone_pillar_top', TB.pillar_top())]
    T['rift_turf'] = [('rift_turf_top', TB.turf_top()), ('rift_turf_side', TB.turf_side()), ('rift_turf_bottom', TB.soil())]
    T['rift_crystal_block'] = [('rift_crystal_block', TB.crystal_block())]
    T['rift_shard_ore'] = [('rift_shard_ore', TB.ore())]
    T['glimmerwood_log'] = [('glimmerwood_log', TB.log_side()), ('glimmerwood_log_top', TB.log_top())]
    T['glimmerwood_planks'] = [('glimmerwood_planks', TB.planks())]
    T['glimmerwood_leaves'] = [('glimmerwood_leaves', TB.leaves())]
    T['glow_bloom'] = [('glow_bloom', TB.bloom())]
    for k, e in enumerate(M.ELEMENTS):
        p = M.SET[e]
        T[f'{p}_bricks'] = [(f'{p}_bricks', TB.element_bricks(e))]
        T[f'{p}_rune'] = [(f'{p}_rune', TB.rune_block(e, 20 + k))]
    T['landmark_stone'] = [('landmark_stone_side', TB.landmark_side()), ('landmark_stone_top', TB.landmark_top())]
    T['boss_altar'] = [('boss_altar_top', TB.altar_top()), ('boss_altar_side', TB.altar_side())]
    return T


def gen_blocks():
    texs = block_textures()
    for bid, lst in texs.items():
        for name, cv in lst:
            tex('block', name, cv)
    # animated portal
    portal = TB.portal_frames(16)
    tex('block', 'rift_portal', portal)
    wj(os.path.join(ASSETS, 'textures/block/rift_portal.png.mcmeta'), {'animation': {'frametime': 2, 'interpolate': True}})

    def B(path, obj):
        wj(os.path.join(ASSETS, 'models/block', path + '.json'), obj)

    def S(bid, obj):
        wj(os.path.join(ASSETS, 'blockstates', bid + '.json'), obj)

    def I(bid, obj=None):
        wj(os.path.join(ASSETS, 'models/item', bid + '.json'), obj or {'parent': f'{NS}:block/{bid}'})

    for b in M.BLOCKS:
        bid, kind = b['id'], b['kind']
        lang[f'block.{NS}.{bid}'] = b['name']
        if kind in ('cube', 'glow', 'leaves'):
            B(bid, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/{bid}'}})
            S(bid, {'variants': {'': {'model': f'{NS}:block/{bid}'}}})
            I(bid)
        elif kind in ('pillar', 'log'):
            side = f'{NS}:block/{bid}'
            top = f'{NS}:block/{bid}_top'
            B(bid, {'parent': 'minecraft:block/cube_column', 'textures': {'end': top, 'side': side}})
            m = f'{NS}:block/{bid}'
            S(bid, {'variants': {'axis=y': {'model': m}, 'axis=x': {'model': m, 'x': 90, 'y': 90}, 'axis=z': {'model': m, 'x': 90}}})
            I(bid)
        elif kind == 'turf':
            B(bid, {'parent': 'minecraft:block/cube_bottom_top', 'textures': {'top': f'{NS}:block/rift_turf_top', 'side': f'{NS}:block/rift_turf_side', 'bottom': f'{NS}:block/rift_turf_bottom'}})
            S(bid, {'variants': {'': {'model': f'{NS}:block/{bid}'}}})
            I(bid)
        elif kind == 'plant':
            B(bid, {'parent': 'minecraft:block/cross', 'textures': {'cross': f'{NS}:block/{bid}'}})
            S(bid, {'variants': {'': {'model': f'{NS}:block/{bid}'}}})
            I(bid, {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:block/{bid}'}})
        elif kind == 'portal':
            for ax, (f, t) in (('x', ([0, 0, 6], [16, 16, 10])), ('z', ([6, 0, 0], [10, 16, 16]))):
                faces = {'north': {'uv': [0, 0, 16, 16], 'texture': '#t'}, 'south': {'uv': [0, 0, 16, 16], 'texture': '#t'}} if ax == 'x' else \
                    {'east': {'uv': [0, 0, 16, 16], 'texture': '#t'}, 'west': {'uv': [0, 0, 16, 16], 'texture': '#t'}}
                B(f'rift_portal_{ax}', {'textures': {'t': f'{NS}:block/rift_portal', 'particle': f'{NS}:block/rift_portal'},
                                        'elements': [{'from': f, 'to': t, 'faces': faces}]})
            S(bid, {'variants': {'axis=x': {'model': f'{NS}:block/rift_portal_x'}, 'axis=z': {'model': f'{NS}:block/rift_portal_z'}}})
        elif kind == 'landmark':
            B(bid, {'parent': 'minecraft:block/cube_bottom_top', 'textures': {'top': f'{NS}:block/landmark_stone_top', 'side': f'{NS}:block/landmark_stone_side', 'bottom': f'{NS}:block/riftstone'}})
            S(bid, {'variants': {'': {'model': f'{NS}:block/{bid}'}}})
            I(bid)
        elif kind == 'altar':
            B(bid, {'textures': {'top': f'{NS}:block/boss_altar_top', 'side': f'{NS}:block/boss_altar_side', 'particle': f'{NS}:block/boss_altar_side'},
                    'elements': [
                        {'from': [0, 0, 0], 'to': [16, 4, 16], 'faces': {d: {'uv': [0, 0, 16, 4], 'texture': '#side'} for d in ('north', 'south', 'east', 'west')} | {'up': {'uv': [0, 0, 16, 16], 'texture': '#top'}, 'down': {'uv': [0, 0, 16, 16], 'texture': '#side'}}},
                        {'from': [3, 4, 3], 'to': [13, 9, 13], 'faces': {d: {'uv': [3, 0, 13, 5], 'texture': '#side'} for d in ('north', 'south', 'east', 'west')}},
                        {'from': [0, 9, 0], 'to': [16, 12, 16], 'faces': {d: {'uv': [0, 0, 16, 3], 'texture': '#side'} for d in ('north', 'south', 'east', 'west')} | {'up': {'uv': [0, 0, 16, 16], 'texture': '#top'}, 'down': {'uv': [0, 0, 16, 16], 'texture': '#side'}}}]})
            S(bid, {'variants': {'': {'model': f'{NS}:block/{bid}'}}})
            I(bid)


# ====================================================================== ENTITIES / PARTICLES / MISC TEXTURES
def gen_entities():
    seed = 3
    for nid, (name, title, style) in M.NPCS.items():
        lang[f'npc.{NS}.{nid}'] = name
        cv = TE.humanoid(TE.spec_for(style), seed=seed)
        seed += 1
        tex('entity/npc', nid, cv)
    lang[f'entity.{NS}.quest_npc'] = 'Villager of the Realm'
    for (mid, name, style, el) in M.MOBS:
        lang[f'entity.{NS}.{mid}'] = name
        if style == 'spider':
            tex('entity', mid, TE.spider(el))
        else:
            tex('entity', mid, TE.humanoid(TE.spec_for(style, el), seed=seed))
            seed += 1
    for (bid, name, el) in M.BOSSES:
        lang[f'entity.{NS}.{bid}'] = name
        tex('entity', bid, TE.humanoid(TE.spec_for('boss_' + el, el), seed=seed))
        seed += 1
    for e in M.ELEMENTS:
        l1, l2 = TE.armor_layers(e)
        p = M.SET[e]
        tex('models/armor', f'{p}_layer_1', l1)
        tex('models/armor', f'{p}_layer_2', l2)


def gen_particles():
    cols = {'rift_mote': ((176, 140, 255), (200, 255, 255)), 'ember_spark': ((255, 120, 30), (255, 240, 160)), 'frost_flake': ((150, 220, 255), (255, 255, 255)),
            'storm_spark': ((255, 230, 80), (255, 255, 255)), 'leaf_wisp': ((120, 230, 90), (230, 255, 160)), 'void_wisp': ((190, 70, 255), (255, 200, 255))}
    for pid in M.PARTICLES:
        c, core = cols[pid]
        tex('particle', pid, TE.particle(c, core, 'star' if pid in ('storm_spark', 'frost_flake') else 'orb'))
        wj(os.path.join(ASSETS, 'particles', pid + '.json'), {'textures': [f'{NS}:{pid}']})


def gen_icon():
    cv = Canvas(128, 128, fill=(14, 8, 30))
    import math
    for y in range(128):
        for x in range(128):
            dx, dy = (x - 64) / 64.0, (y - 64) / 64.0
            r = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            v = 0.5 + 0.5 * math.sin(a * 3 + r * 9)
            t = max(0, 1 - r)
            col = mix((20, 10, 50), (127, 244, 255), t * v)
            col = mix(col, (224, 96, 255), max(0, (v - 0.6) * t))
            cv.put(x, y, col)
    sw = TI.draw('greatsword', 'flame').image().resize((96, 96), Image.NEAREST)
    base = cv.image()
    base.paste(sw, (16, 16), sw)
    os.makedirs(ASSETS, exist_ok=True)
    base.save(os.path.join(ASSETS, 'icon.png'))


# ====================================================================== LANG extras
def lang_extras():
    lang['itemGroup.realmbreak'] = 'Realmbreak'
    lang['key.categories.realmbreak'] = 'Realmbreak'
    lang['key.realmbreak.quest_log'] = 'Open Quest Log'
    lang['key.realmbreak.skill_tree'] = 'Open Skill Tree'
    lang['key.realmbreak.cast'] = 'Cast Selected Spell'
    lang['key.realmbreak.cycle'] = 'Cycle Spell'
    lang['key.realmbreak.skip'] = 'Skip Cutscene'
    lang['death.attack.realmbreak.rift'] = '%1$s was unmade by rift magic'


# ====================================================================== RECIPES
def item_id(i):
    return i if ':' in i else f'{NS}:{i}'


def shaped(name, pattern, key, result, count=1, cat='equipment'):
    wj(os.path.join(DATA, 'recipe', name + '.json'), {
        'type': 'minecraft:crafting_shaped', 'category': cat, 'pattern': pattern,
        'key': {k: {'item': item_id(v)} for k, v in key.items()},
        'result': {'count': count, 'id': item_id(result)}})


def shapeless(name, ings, result, count=1, cat='misc'):
    wj(os.path.join(DATA, 'recipe', name + '.json'), {
        'type': 'minecraft:crafting_shapeless', 'category': cat,
        'ingredients': [{'item': item_id(i)} for i in ings],
        'result': {'count': count, 'id': item_id(result)}})


def gen_recipes():
    for e in M.ELEMENTS:
        p = M.SET[e]
        E = f'{e}_essence'
        shaped(f'{p}_sword', [' E ', 'ERE', ' S '], {'E': E, 'R': 'rift_shard', 'S': 'minecraft:stick'}, f'{p}_sword')
        shaped(f'{p}_bow', [' ES', 'R S', ' ES'], {'E': E, 'R': 'rift_shard', 'S': 'minecraft:string'}, f'{p}_bow')
        shaped(f'{p}_staff', [' RE', ' SR', 'S  '], {'E': E, 'R': 'rift_shard', 'S': 'minecraft:stick'}, f'{p}_staff')
        shaped(f'{p}_helmet', ['EEE', 'E E'], {'E': E}, f'{p}_helmet')
        shaped(f'{p}_chestplate', ['E E', 'EEE', 'EEE'], {'E': E}, f'{p}_chestplate')
        shaped(f'{p}_leggings', ['EEE', 'E E', 'E E'], {'E': E}, f'{p}_leggings')
        shaped(f'{p}_boots', ['E E', 'E E'], {'E': E}, f'{p}_boots')
        shaped(f'{e}_sigil', ['EDE', 'DRD', 'EDE'], {'E': E, 'D': 'rift_dust', 'R': 'rift_shard'}, f'{e}_sigil', cat='misc')
    shaped('rift_anchor', ['RDR', 'DOD', 'RDR'], {'R': 'rift_shard', 'D': 'rift_dust', 'O': 'minecraft:obsidian'}, 'rift_anchor', cat='misc')
    shaped('apprentice_staff', [' R', 'S ', 'S '][::1] if False else ['  R', ' S ', 'S  '], {'R': 'rift_shard', 'S': 'minecraft:stick'}, 'apprentice_staff')
    shapeless('seekers_compass', ['minecraft:compass', 'rift_shard', 'rift_shard'], 'seekers_compass')
    shapeless('quest_journal', ['minecraft:book', 'rift_dust'], 'quest_journal')
    shapeless('mana_elixir', ['minecraft:glass_bottle', 'rift_dust', 'rift_dust', 'minecraft:lapis_lazuli'], 'mana_elixir')
    shapeless('vitality_elixir', ['minecraft:glass_bottle', 'rift_dust', 'minecraft:glistering_melon_slice'], 'vitality_elixir')
    shaped('riftstone_bricks', ['SS', 'SS'], {'S': 'riftstone'}, 'riftstone_bricks', 4, 'building')
    shaped('riftstone_pillar', ['S', 'S'], {'S': 'riftstone'}, 'riftstone_pillar', 2, 'building')
    shapeless('glimmerwood_planks', ['glimmerwood_log'], 'glimmerwood_planks', 4, 'building')
    shaped('chiseled_riftstone', ['S', 'S'], {'S': 'riftstone_bricks'}, 'chiseled_riftstone', 1, 'building')


# ====================================================================== LOOT
def block_loot(name, item, count=None, fortune=False, chance=None, extra=None):
    entry = {'type': 'minecraft:item', 'name': item_id(item)}
    funcs = []
    if count:
        funcs.append({'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': count[0], 'max': count[1]}})
    if fortune:
        funcs.append({'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'})
    if funcs:
        entry['functions'] = funcs
    pool = {'rolls': 1.0, 'bonus_rolls': 0.0, 'entries': [entry], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}
    if chance:
        entry['conditions'] = [{'condition': 'minecraft:random_chance', 'chance': chance}]
    wj(os.path.join(DATA, 'loot_table/blocks', name + '.json'), {'type': 'minecraft:block', 'pools': [pool], 'random_sequence': f'{NS}:blocks/{name}'})


def gen_block_loot():
    for b in M.BLOCKS:
        bid, kind = b['id'], b['kind']
        if b['strength'] < 0:
            continue
        if kind == 'leaves':
            wj(os.path.join(DATA, 'loot_table/blocks', bid + '.json'), {'type': 'minecraft:block', 'random_sequence': f'{NS}:blocks/{bid}', 'pools': [
                {'rolls': 1.0, 'bonus_rolls': 0.0, 'entries': [{'type': 'minecraft:item', 'name': 'minecraft:stick', 'conditions': [{'condition': 'minecraft:random_chance', 'chance': 0.15}]}]},
                {'rolls': 1.0, 'bonus_rolls': 0.0, 'entries': [{'type': 'minecraft:item', 'name': f'{NS}:rift_dust', 'conditions': [{'condition': 'minecraft:random_chance', 'chance': 0.06}]}]}]})
        elif b.get('drops'):
            if bid == 'rift_shard_ore':
                block_loot(bid, b['drops'], (1, 3), fortune=True)
            else:
                block_loot(bid, b['drops'], (2, 4))
        else:
            block_loot(bid, bid)


def chest(name, pools):
    wj(os.path.join(DATA, 'loot_table/chests', name + '.json'), {'type': 'minecraft:chest', 'random_sequence': f'{NS}:chests/{name}', 'pools': pools})


def entry(item, weight=1, count=None, enchant=None):
    e = {'type': 'minecraft:item', 'name': item_id(item), 'weight': weight}
    f = []
    if count:
        f.append({'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': count[0], 'max': count[1]}})
    if enchant:
        f.append({'function': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': enchant[0], 'max': enchant[1]}, 'options': '#minecraft:on_random_loot'})
    if f:
        e['functions'] = f
    return e


def pool(entries, rolls=(1, 1), bonus=0.0):
    r = rolls[0] if rolls[0] == rolls[1] else {'type': 'minecraft:uniform', 'min': rolls[0], 'max': rolls[1]}
    return {'rolls': float(r) if not isinstance(r, dict) else r, 'bonus_rolls': bonus, 'entries': entries}


DUNGEONS = {'cinderhold': 'flame', 'frostspire': 'frost', 'stormwatch': 'storm', 'elderroot': 'verdant', 'observatory': 'void'}


def gen_chests():
    for d, e in DUNGEONS.items():
        p = M.SET[e]
        chest(f'{d}_vault', [
            pool([entry(f'{e}_sigil')], (1, 1)),
            pool([entry('rift_shard', 6, (3, 7)), entry(f'{e}_essence', 5, (2, 5)), entry('ancient_rune', 3, (1, 2)), entry('vitality_elixir', 4, (1, 3)), entry('mana_elixir', 4, (1, 3)),
                  entry('tome_of_insight', 2), entry('minecraft:diamond', 3, (1, 4)), entry('minecraft:golden_apple', 2, (1, 2)),
                  entry(f'{p}_sword', 1, None, (20, 30)), entry(f'{p}_helmet', 1), entry(f'{p}_boots', 1)], (3, 5))])
        chest(f'{d}_loot', [
            pool([entry('rift_shard', 5, (1, 3)), entry(f'{e}_essence', 4, (1, 2)), entry('rift_dust', 8, (2, 5)), entry('minecraft:iron_ingot', 6, (2, 6)),
                  entry('minecraft:gold_ingot', 4, (1, 4)), entry('vitality_elixir', 3), entry('mana_elixir', 3), entry('minecraft:arrow', 6, (8, 24)),
                  entry('minecraft:book', 2, None, (10, 25)), entry('ancient_rune', 1)], (2, 4))])
    chest('outpost', [pool([entry('minecraft:bread', 8, (3, 8)), entry('minecraft:iron_ingot', 5, (1, 4)), entry('rift_dust', 4, (1, 3)), entry('vitality_elixir', 3),
                            entry('minecraft:arrow', 5, (6, 16)), entry('minecraft:coal', 6, (3, 8)), entry('minecraft:cooked_beef', 6, (2, 5))], (2, 4))])
    chest('ruins', [pool([entry('minecraft:iron_ingot', 6, (2, 5)), entry('minecraft:gold_ingot', 4, (1, 3)), entry('rift_dust', 5, (1, 4)), entry('ancient_rune', 2),
                          entry('minecraft:diamond', 2, (1, 2)), entry('minecraft:book', 3, None, (15, 30)), entry('mana_elixir', 3), entry('vitality_elixir', 3),
                          entry('rift_shard', 3, (1, 2))], (2, 4))])
    chest('rift_cache', [pool([entry('rift_shard', 8, (2, 5)), entry('rift_dust', 8, (3, 7))] + [entry(f'{e}_essence', 3, (1, 2)) for e in M.ELEMENTS] +
                               [entry('ancient_rune', 3), entry('tome_of_insight', 2), entry('mana_elixir', 4), entry('vitality_elixir', 4), entry('minecraft:ender_pearl', 3, (1, 3)),
                                entry('minecraft:diamond', 3, (1, 3))], (3, 5))])


def entity_loot(name, pools):
    wj(os.path.join(DATA, 'loot_table/entities', name + '.json'), {'type': 'minecraft:entity', 'random_sequence': f'{NS}:entities/{name}', 'pools': pools})


def chance_entry(item, chance, count=(1, 1)):
    e = {'type': 'minecraft:item', 'name': item_id(item), 'conditions': [{'condition': 'minecraft:random_chance', 'chance': chance}]}
    if count != (1, 1):
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': count[0], 'max': count[1]}}]
    return e


def gen_entity_loot():
    for (mid, name, style, el) in M.MOBS:
        pools = [pool([chance_entry(f'{el}_essence', 0.45)]), pool([chance_entry('rift_dust', 0.7, (1, 2))]), pool([chance_entry('rift_shard', 0.12)])]
        entity_loot(mid, pools)
    legend = {'flame': 'emberbrand', 'frost': 'heart_of_winter', 'storm': 'stormpiercer', 'verdant': 'oakenheart_scepter', 'void': 'voidreaver'}
    for (bid, name, el) in M.BOSSES:
        entity_loot(bid, [
            pool([entry(f'{el}_essence', 1, (4, 7))]),
            pool([entry('rift_shard', 1, (5, 9))]),
            pool([entry('tome_of_insight', 1)]),
            pool([entry(legend[el], 1)]),
            pool([entry('ancient_rune', 1, (1, 3))])])


# ====================================================================== TAGS
def gen_tags():
    tools = {'pickaxe': [], 'axe': [], 'shovel': [], 'hoe': []}
    for b in M.BLOCKS:
        if b['strength'] >= 0 and b.get('tool'):
            tools[b['tool']].append(f"{NS}:{b['id']}")
    for t, vals in tools.items():
        wj(os.path.join(MCDATA, f'tags/block/mineable/{t}.json'), {'replace': False, 'values': vals})
    wj(os.path.join(MCDATA, 'tags/block/leaves.json'), {'replace': False, 'values': [f'{NS}:glimmerwood_leaves']})
    wj(os.path.join(MCDATA, 'tags/block/logs.json'), {'replace': False, 'values': [f'{NS}:glimmerwood_log']})
    wj(os.path.join(MCDATA, 'tags/item/logs.json'), {'replace': False, 'values': [f'{NS}:glimmerwood_log']})
    wj(os.path.join(MCDATA, 'tags/block/needs_iron_tool.json'), {'replace': False, 'values': [f'{NS}:rift_shard_ore']})


def main():
    gen_items()
    gen_blocks()
    gen_entities()
    gen_particles()
    gen_icon()
    lang_extras()
    gen_recipes()
    gen_block_loot()
    gen_chests()
    gen_entity_loot()
    gen_tags()
    # content manifest consumed by Java at startup
    content = {'items': M.ITEMS, 'blocks': M.BLOCKS, 'sites': M.SITES,
               'site_names': [M.SITE_NAME[x] for x in M.SITES],
               'mobs': [dict(id=a, name=b, style=c, element=d) for (a, b, c, d) in M.MOBS],
               'bosses': [dict(id=a, name=b, element=c) for (a, b, c) in M.BOSSES],
               'npcs': [dict(id=k, name=v[0], title=v[1], style=v[2]) for k, v in M.NPCS.items()],
               'particles': M.PARTICLES, 'elements': M.ELEMENTS, 'set_prefix': M.SET}
    with open(os.path.join(RES, 'realmbreak_content.json'), 'w') as f:
        json.dump(content, f, indent=1)
    import gen_text
    lang.update(gen_text.lang_entries())
    wj(os.path.join(ASSETS, 'lang/en_us.json'), dict(sorted(lang.items())))
    print('data generated: ', len(lang), 'lang keys')


if __name__ == '__main__':
    main()
