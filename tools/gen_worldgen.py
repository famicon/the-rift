"""Generates worldgen JSON: the Rift dimension, biomes, features, structure sets/pools and tags."""
import json
import math
import os
import manifest as M

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(ROOT, 'src/main/resources/data/realmbreak')
NS = 'realmbreak'


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def W(rel, obj):
    wj(os.path.join(DATA, rel + '.json'), obj)


# ------------------------------------------------------------------ density function builders
def add(a, b): return {'type': 'minecraft:add', 'argument1': a, 'argument2': b}
def mul(a, b): return {'type': 'minecraft:mul', 'argument1': a, 'argument2': b}
def mn(a, b): return {'type': 'minecraft:min', 'argument1': a, 'argument2': b}
def mx(a, b): return {'type': 'minecraft:max', 'argument1': a, 'argument2': b}
def noise(n, xz=1.0, y=1.0): return {'type': 'minecraft:noise', 'noise': f'{NS}:{n}', 'xz_scale': xz, 'y_scale': y}
YGRAD = {'type': 'minecraft:y_clamped_gradient', 'from_y': -64, 'to_y': 320, 'from_value': -64.0, 'to_value': 320.0}


def tier(name, c, hamp, K, slope, mask, gain, thr, detail_amt=0.10):
    """flat-topped, cone-bottomed floating landmass layer. positive = solid"""
    h = noise('rift_height', 1.0, 0.0)
    b = noise('rift_bump', 1.0, 0.0)
    center = add(c, add(mul(hamp, h), mul(4.0, b)))
    d = add(YGRAD, mul(-1.0, center))               # y - centre ; <0 below the top plane
    top = mul(-1.0, d)                              # >0 below plane
    m = add(mul(gain, noise(mask, 1.0, 0.0)), -thr)
    body = add(add(mul(K, m), mul(slope, d)), mul(detail_amt, noise('rift_detail', 1.0, 1.2)))
    return mn(top, body)


TIERS = [
    ('t0', 62.0, 22.0, 1.0, 0.012, 'rift_mask_main', 1.6, -0.10),
    ('t1', 120.0, 18.0, 1.0, 0.045, 'rift_mask_a', 2.0, 0.30),
    ('t2', 178.0, 20.0, 1.0, 0.045, 'rift_mask_b', 2.0, 0.40),
    ('t3', 238.0, 14.0, 1.0, 0.050, 'rift_mask_c', 2.0, 0.50),
]


def final_density():
    parts = [tier(*t) for t in TIERS]
    return {'type': 'minecraft:interpolated', 'argument': mx(mx(parts[0], parts[1]), mx(parts[2], parts[3]))}


def gen_noises():
    for n, first, amps in (('rift_mask_main', -9, [1, 1, 0.5]), ('rift_mask_a', -8, [1, 1, 0.5]), ('rift_mask_b', -8, [1, 1, 0.5]), ('rift_mask_c', -7, [1, 1, 0.5]),
                           ('rift_height', -7, [1, 0.5]), ('rift_bump', -5, [1, 1]), ('rift_detail', -3, [1, 1, 1])):
        W(f'worldgen/noise/{n}', {'firstOctave': first, 'amplitudes': amps})


# ------------------------------------------------------------------ biomes
RIFT_BIOMES = {
    # id: (T, H, offset, sky, fog, particle, top, sub, element)
    'rift_meadow': (0.0, 0.0, 0.15, 0x9B7BFF, 0xE9B8FF, 'rift_mote', 'realmbreak:rift_turf', 'minecraft:dirt', 'meadow'),
    'ember_wastes': (0.5, 0.0, 0.0, 0xD2523A, 0xFF9A5A, 'ember_spark', 'minecraft:blackstone', 'minecraft:blackstone', 'flame'),
    'verdant_canopy': (0.25, 0.43, 0.0, 0x58C89A, 0xB8FFD0, 'leaf_wisp', 'minecraft:moss_block', 'minecraft:rooted_dirt', 'verdant'),
    'crystal_barrens': (-0.25, 0.43, 0.0, 0x7A8CFF, 0xC8D4FF, 'rift_mote', 'minecraft:amethyst_block', 'minecraft:calcite', 'crystal'),
    'frost_expanse': (-0.5, 0.0, 0.0, 0x7FB8FF, 0xD8F2FF, 'frost_flake', 'minecraft:snow_block', 'minecraft:packed_ice', 'frost'),
    'storm_highlands': (-0.25, -0.43, 0.0, 0x5A64C8, 0xA6B2FF, 'storm_spark', 'minecraft:calcite', 'minecraft:tuff', 'storm'),
    'void_expanse': (0.25, -0.43, 0.0, 0x3A1A6A, 0x8A4AD0, 'void_wisp', 'minecraft:end_stone', 'minecraft:deepslate', 'void'),
}

SPAWNS = {
    'rift_meadow': [('rift_wraith', 8, 1, 2), ('storm_sprite', 5, 1, 3), ('rift_stalker', 5, 1, 2), ('cinder_knight', 2, 1, 1), ('rime_wraith', 2, 1, 1), ('thorn_stalker', 2, 1, 2), ('void_acolyte', 2, 1, 1), ('ember_mage', 2, 1, 1), ('gale_sentinel', 2, 1, 1), ('bark_guardian', 2, 1, 1), ('frost_crawler', 2, 1, 2)],
    'ember_wastes': [('cinder_knight', 10, 1, 3), ('ember_mage', 10, 1, 2), ('rift_wraith', 3, 1, 1)],
    'verdant_canopy': [('thorn_stalker', 10, 1, 3), ('bark_guardian', 7, 1, 1), ('rift_stalker', 3, 1, 2)],
    'crystal_barrens': [('rift_wraith', 8, 1, 2), ('rift_stalker', 6, 1, 2), ('storm_sprite', 4, 1, 2), ('ember_mage', 2, 1, 1), ('frost_crawler', 2, 1, 2), ('void_acolyte', 2, 1, 1), ('cinder_knight', 2, 1, 1), ('bark_guardian', 2, 1, 1), ('gale_sentinel', 2, 1, 1)],
    'frost_expanse': [('rime_wraith', 10, 1, 2), ('frost_crawler', 10, 1, 3), ('rift_wraith', 3, 1, 1)],
    'storm_highlands': [('gale_sentinel', 10, 1, 2), ('storm_sprite', 10, 2, 4), ('rift_wraith', 3, 1, 1)],
    'void_expanse': [('void_acolyte', 10, 1, 2), ('rift_stalker', 10, 1, 3), ('rift_wraith', 6, 1, 2)],
}

# placed feature ids used per biome (vegetal step 9, ore step 6)
BIOME_FEATURES = {
    'rift_meadow': ['glimmer_tree_sparse', 'glow_bloom_patch', 'rift_spire_few'],
    'ember_wastes': ['spire_flame', 'magma_clusters'],
    'verdant_canopy': ['glimmer_tree_dense', 'glow_bloom_patch', 'spire_verdant'],
    'crystal_barrens': ['spire_crystal', 'spire_crystal_big'],
    'frost_expanse': ['spire_frost', 'ice_clusters'],
    'storm_highlands': ['spire_storm'],
    'void_expanse': ['spire_void', 'obsidian_clusters'],
}


def gen_biomes():
    for bid, (T, H, off, sky, fog, part, top, sub, el) in RIFT_BIOMES.items():
        feats = [[] for _ in range(11)]
        feats[6] = ['realmbreak:ore_rift_shard']
        feats[9] = [f'realmbreak:{f}' for f in BIOME_FEATURES[bid]]
        spawners = {k: [] for k in ('ambient', 'axolotls', 'creature', 'misc', 'monster', 'underground_water_creature', 'water_ambient', 'water_creature')}
        spawners['monster'] = [{'type': f'{NS}:{m}', 'weight': w, 'minCount': a, 'maxCount': b} for (m, w, a, b) in SPAWNS[bid]]
        W(f'worldgen/biome/{bid}', {
            'temperature': 0.5, 'downfall': 0.0, 'has_precipitation': False,
            'effects': {'sky_color': sky, 'fog_color': fog, 'water_color': 0x7A5CF0, 'water_fog_color': 0x2A1A6A,
                        'particle': {'options': {'type': f'{NS}:{part}'}, 'probability': 0.03},
                        'mood_sound': {'block_search_extent': 8, 'offset': 2.0, 'sound': 'minecraft:ambient.crimson_forest.mood', 'tick_delay': 6000}},
            'spawners': spawners, 'spawn_costs': {}, 'carvers': {}, 'features': feats})


def surface_rules():
    seq = []
    for bid, (T, H, off, sky, fog, part, top, sub, el) in RIFT_BIOMES.items():
        def depth(add_surface):
            return {'type': 'minecraft:stone_depth', 'offset': 0, 'surface_type': 'floor', 'add_surface_depth': add_surface, 'secondary_depth_range': 0}
        seq.append({'type': 'minecraft:condition', 'if_true': {'type': 'minecraft:biome', 'biome_is': [f'{NS}:{bid}']},
                    'then_run': {'type': 'minecraft:sequence', 'sequence': [
                        {'type': 'minecraft:condition', 'if_true': depth(False), 'then_run': {'type': 'minecraft:block', 'result_state': {'Name': top}}},
                        {'type': 'minecraft:condition', 'if_true': depth(True), 'then_run': {'type': 'minecraft:block', 'result_state': {'Name': sub}}}]}})
    seq.append({'type': 'minecraft:block', 'result_state': {'Name': f'{NS}:riftstone'}})
    return {'type': 'minecraft:sequence', 'sequence': seq}


def gen_dimension():
    W('dimension_type/the_rift', {
        'ultrawarm': False, 'natural': True, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False, 'ambient_light': 0.18,
        'fixed_time': 11800, 'monster_spawn_light_level': {'type': 'minecraft:uniform', 'min_inclusive': 0, 'max_inclusive': 15}, 'monster_spawn_block_light_limit': 15,
        'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False, 'logical_height': 384, 'min_y': -64, 'height': 384,
        'infiniburn': '#minecraft:infiniburn_overworld', 'effects': 'minecraft:overworld'})
    biomes = []
    for bid, (T, H, off, *_rest) in RIFT_BIOMES.items():
        biomes.append({'biome': f'{NS}:{bid}', 'parameters': {'temperature': T, 'humidity': H, 'continentalness': 0.0, 'erosion': 0.0, 'weirdness': 0.0, 'depth': 0.0, 'offset': off}})
    W('dimension/the_rift', {'type': f'{NS}:the_rift', 'generator': {'type': 'minecraft:noise', 'settings': f'{NS}:the_rift', 'biome_source': {'type': 'minecraft:multi_noise', 'biomes': biomes}}})
    shifted = lambda n: {'type': 'minecraft:shifted_noise', 'noise': f'minecraft:{n}', 'shift_x': 'minecraft:shift_x', 'shift_y': 0.0, 'shift_z': 'minecraft:shift_z', 'xz_scale': 0.25, 'y_scale': 0.0}
    W('worldgen/noise_settings/the_rift', {
        'sea_level': 0, 'disable_mob_generation': False, 'aquifers_enabled': False, 'ore_veins_enabled': False, 'legacy_random_source': False,
        'default_block': {'Name': f'{NS}:riftstone'}, 'default_fluid': {'Name': 'minecraft:air'}, 'spawn_target': [],
        'noise': {'min_y': -64, 'height': 384, 'size_horizontal': 1, 'size_vertical': 1},
        'noise_router': {'barrier': 0.0, 'fluid_level_floodedness': 0.0, 'fluid_level_spread': 0.0, 'lava': 0.0, 'temperature': shifted('temperature'),
                         'vegetation': shifted('vegetation'), 'continents': 0.0, 'erosion': 0.0, 'depth': 0.0, 'ridges': 0.0,
                         'initial_density_without_jaggedness': 0.0, 'final_density': final_density(), 'vein_toggle': 0.0, 'vein_ridged': 0.0, 'vein_gap': 0.0},
        'surface_rule': surface_rules()})


# ------------------------------------------------------------------ features
def placed(name, feature, placement):
    W(f'worldgen/placed_feature/{name}', {'feature': f'{NS}:{feature}' if ':' not in feature else feature, 'placement': placement})


def cfg(name, ftype, config):
    W(f'worldgen/configured_feature/{name}', {'type': ftype, 'config': config})


def gen_features():
    HM = {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'}
    SQ = {'type': 'minecraft:in_square'}
    BI = {'type': 'minecraft:biome'}

    def cnt(n): return {'type': 'minecraft:count', 'count': n}

    def rar(n): return {'type': 'minecraft:rarity_filter', 'chance': n}
    cfg('ore_rift_shard', 'minecraft:ore', {'discard_chance_on_air_exposure': 0.0, 'size': 6, 'targets': [
        {'state': {'Name': f'{NS}:rift_shard_ore'}, 'target': {'predicate_type': 'minecraft:block_match', 'block': f'{NS}:riftstone'}}]})
    placed('ore_rift_shard', 'ore_rift_shard', [cnt(34), SQ, {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': -60}, 'max_inclusive': {'absolute': 300}}}, BI])
    for name, kind, block in (('magma_clusters', 'ore', 'minecraft:magma_block'), ('ice_clusters', 'ore', 'minecraft:blue_ice'), ('obsidian_clusters', 'ore', 'minecraft:crying_obsidian')):
        cfg(name, 'minecraft:ore', {'discard_chance_on_air_exposure': 0.0, 'size': 9, 'targets': [{'state': {'Name': block}, 'target': {'predicate_type': 'minecraft:block_match', 'block': f'{NS}:riftstone'}}]})
        placed(name, name, [cnt(22), SQ, {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': -60}, 'max_inclusive': {'absolute': 300}}}, BI])
    # custom java features (config: {"element": "..."})
    for name, ftype, element in (
            ('glimmer_tree', 'glimmer_tree', 'rift'), ('spire_flame', 'spire', 'flame'), ('spire_frost', 'spire', 'frost'), ('spire_storm', 'spire', 'storm'),
            ('spire_verdant', 'spire', 'verdant'), ('spire_void', 'spire', 'void'), ('spire_crystal', 'spire', 'crystal'), ('spire_crystal_big', 'spire', 'crystal_big'),
            ('rift_spire', 'spire', 'crystal'), ('overworld_obelisk', 'obelisk', 'rune'), ('overworld_rock_spire', 'rock_spire', 'stone'), ('overworld_islet', 'islet', 'islet')):
        cfg(name, f'{NS}:{ftype}', {'element': element})
    placed('glimmer_tree_sparse', 'glimmer_tree', [cnt(1), rar(2), SQ, HM, BI])
    placed('glimmer_tree_dense', 'glimmer_tree', [cnt(3), SQ, HM, BI])
    for e in ('flame', 'frost', 'storm', 'verdant', 'void', 'crystal'):
        placed(f'spire_{e}', f'spire_{e}', [cnt(2), rar(2), SQ, HM, BI])
    placed('spire_crystal_big', 'spire_crystal_big', [cnt(1), rar(3), SQ, HM, BI])
    placed('rift_spire_few', 'rift_spire', [cnt(1), rar(3), SQ, HM, BI])
    # flowers
    cfg('glow_bloom_patch', 'minecraft:random_patch', {'tries': 28, 'xz_spread': 6, 'y_spread': 2, 'feature': {
        'feature': {'type': 'minecraft:simple_block', 'config': {'to_place': {'type': 'minecraft:simple_state_provider', 'state': {'Name': f'{NS}:glow_bloom'}}}},
        'placement': [{'type': 'minecraft:block_predicate_filter', 'predicate': {'type': 'minecraft:all_of', 'predicates': [
            {'type': 'minecraft:matching_blocks', 'blocks': 'minecraft:air'},
            {'type': 'minecraft:matching_blocks', 'offset': [0, -1, 0], 'blocks': [f'{NS}:rift_turf', 'minecraft:moss_block']}]}}]}})
    placed('glow_bloom_patch', 'glow_bloom_patch', [cnt(2), rar(2), SQ, HM, BI])
    # overworld additions
    placed('overworld_obelisk', 'overworld_obelisk', [rar(22), SQ, HM, BI])
    placed('overworld_rock_spire', 'overworld_rock_spire', [rar(14), SQ, HM, BI])
    placed('overworld_islet', 'overworld_islet', [rar(30), SQ, {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'}, BI])


# ------------------------------------------------------------------ structures
# id: (biome_tag, spacing, separation, dimension, kind)
STRUCT = {
    'wayfarers_camp': ('has_land', 40, 16, 'o'),
    'ashen_bastion': ('has_hot', 26, 10, 'o'), 'frostwatch_hold': ('has_cold', 26, 10, 'o'), 'stormwatch_perch': ('has_peaks', 26, 10, 'o'),
    'grovekeepers_lodge': ('has_forest', 26, 10, 'o'), 'veiled_sanctum': ('has_peaks', 30, 12, 'o'),
    'cinderhold_citadel': ('has_hot', 24, 9, 'o'), 'frostspire_vault': ('has_cold', 24, 9, 'o'), 'stormwatch_aerie': ('has_peaks', 24, 9, 'o'), 'elderroot_sanctum': ('has_forest', 24, 9, 'o'),
    'standing_stone_ring': ('has_land', 18, 7, 'o'), 'dragon_bones': ('has_land', 22, 9, 'o'), 'ruined_watchtower': ('has_land', 20, 8, 'o'),
    'sleeping_colossus': ('has_land', 28, 11, 'o'), 'titans_arch': ('has_peaks', 22, 9, 'o'), 'moonwell_shrine': ('has_forest', 22, 9, 'o'), 'rift_scar': ('has_land', 16, 6, 'o'),
    'hollow_observatory': ('rift_biomes', 20, 8, 'r'),
    'altar_of_flame': ('rift_biomes', 14, 6, 'r'), 'altar_of_frost': ('rift_biomes', 14, 6, 'r'), 'altar_of_storm': ('rift_biomes', 14, 6, 'r'),
    'altar_of_verdant': ('rift_biomes', 14, 6, 'r'), 'altar_of_void': ('rift_biomes', 14, 6, 'r'),
    'crystal_cathedral': ('rift_biomes', 22, 9, 'r'), 'fallen_keep': ('rift_biomes', 16, 7, 'r'), 'rift_monolith': ('rift_biomes', 11, 5, 'r'), 'sky_bridge': ('rift_biomes', 14, 6, 'r'),
}


def load_meta():
    p = os.path.join(ROOT, 'tools/struct_meta.json')
    if os.path.exists(p):
        return json.load(open(p))
    return {}


def gen_structures():
    meta = load_meta()
    salt = 1337
    for sid, (btag, sp, sep, dim) in STRUCT.items():
        salt += 7919
        m = meta.get(sid, {'ground': 1})
        g = m.get('ground', 1)
        st = {'type': 'minecraft:jigsaw', 'biomes': f'#{NS}:{btag}', 'step': 'surface_structures', 'spawn_overrides': {},
              'start_pool': f'{NS}:{sid}', 'size': 1, 'max_distance_from_center': 116, 'use_expansion_hack': False}
        if dim == 'o':
            st['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
            st['start_height'] = {'absolute': 1 - g}
            st['terrain_adaptation'] = 'beard_thin' if sid not in ('titans_arch',) else 'none'
        else:
            st['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': 70}, 'max_inclusive': {'absolute': 190}}
            st['terrain_adaptation'] = 'none'
        W(f'worldgen/structure/{sid}', st)
        W(f'worldgen/template_pool/{sid}', {'fallback': 'minecraft:empty', 'elements': [{'weight': 1, 'element': {
            'element_type': 'minecraft:single_pool_element', 'location': f'{NS}:{sid}', 'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
        W(f'worldgen/structure_set/{sid}', {'structures': [{'structure': f'{NS}:{sid}', 'weight': 1}],
                                           'placement': {'type': 'minecraft:random_spread', 'spacing': sp, 'separation': sep, 'salt': salt}})
        W(f'tags/worldgen/structure/{sid}', {'replace': False, 'values': [f'{NS}:{sid}']})


def gen_biome_tags():
    W('tags/worldgen/biome/rift_biomes', {'replace': False, 'values': [f'{NS}:{b}' for b in RIFT_BIOMES]})
    land = ['#minecraft:is_forest', '#minecraft:is_taiga', '#minecraft:is_hill', '#minecraft:is_mountain', '#minecraft:is_badlands', '#minecraft:is_savanna', '#minecraft:is_jungle',
            'minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:snowy_plains', 'minecraft:desert', 'minecraft:swamp', 'minecraft:cherry_grove', 'minecraft:grove']
    W('tags/worldgen/biome/has_land', {'replace': False, 'values': land})
    W('tags/worldgen/biome/has_hot', {'replace': False, 'values': ['#minecraft:is_badlands', '#minecraft:is_savanna', 'minecraft:desert', '#minecraft:is_hill', 'minecraft:plains', 'minecraft:sunflower_plains']})
    W('tags/worldgen/biome/has_cold', {'replace': False, 'values': ['#minecraft:is_taiga', 'minecraft:snowy_plains', 'minecraft:ice_spikes', 'minecraft:snowy_slopes', 'minecraft:grove', 'minecraft:frozen_peaks', 'minecraft:jagged_peaks', 'minecraft:stony_peaks', 'minecraft:meadow']})
    W('tags/worldgen/biome/has_peaks', {'replace': False, 'values': ['#minecraft:is_mountain', '#minecraft:is_hill', 'minecraft:meadow', 'minecraft:savanna_plateau', 'minecraft:windswept_savanna']})
    W('tags/worldgen/biome/has_forest', {'replace': False, 'values': ['#minecraft:is_forest', '#minecraft:is_jungle', '#minecraft:is_taiga', 'minecraft:swamp', 'minecraft:cherry_grove', 'minecraft:dark_forest']})


def main():
    gen_noises()
    gen_biomes()
    gen_dimension()
    gen_features()
    gen_structures()
    gen_biome_tags()
    print('worldgen generated')


if __name__ == '__main__':
    main()
