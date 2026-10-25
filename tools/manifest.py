"""Single source of truth for Realmbreak content.  Everything (Java content JSON, lang, models,
textures, recipes, loot tables) is generated from this file by gen_data.py."""

ELEMENTS = ['flame', 'frost', 'storm', 'verdant', 'void']
EL_NAME = {'flame': 'Flame', 'frost': 'Frost', 'storm': 'Storm', 'verdant': 'Verdant', 'void': 'Void'}
# gear set prefix per element
SET = {'flame': 'cinder', 'frost': 'rime', 'storm': 'gale', 'verdant': 'thorn', 'void': 'null'}
SET_NAME = {'flame': 'Cinderplate', 'frost': 'Rimeweave', 'storm': 'Galeguard', 'verdant': 'Thornbark', 'void': 'Nullveil'}
SWORD_NAME = {'flame': 'Cinderfang', 'frost': 'Rimebrand', 'storm': 'Thunderedge', 'verdant': 'Thornblade', 'void': 'Nullblade'}
BOW_NAME = {'flame': 'Emberstring Bow', 'frost': 'Hoarfrost Bow', 'storm': 'Stormcall Bow', 'verdant': 'Wildwood Bow', 'void': 'Voidstring Bow'}
STAFF_NAME = {'flame': 'Staff of Cinders', 'frost': 'Staff of Rime', 'storm': 'Staff of Gales', 'verdant': 'Staff of Thorns', 'void': 'Staff of the Void'}
ARMOR_SLOTS = [('helmet', 'Helm'), ('chestplate', 'Cuirass'), ('leggings', 'Greaves'), ('boots', 'Sabatons')]

LORE = {
    'flame': 'Forged where the Rift bleeds fire.',
    'frost': 'Cold enough to still a heartbeat.',
    'storm': 'It hums with a caged tempest.',
    'verdant': 'Wild life answers its wielder.',
    'void': 'It remembers the dark between stars.',
}

# ------------------------------------------------------------------ items
ITEMS = []


def item(**kw):
    kw.setdefault('element', '')
    kw.setdefault('lore', '')
    kw.setdefault('rarity', 'common')
    ITEMS.append(kw)


for e in ELEMENTS:
    p = SET[e]
    item(id=f'{p}_sword', name=SWORD_NAME[e], kind='sword', element=e, damage=8, speed=-2.4, durability=1800, rarity='rare', lore=LORE[e], icon='sword')
    item(id=f'{p}_bow', name=BOW_NAME[e], kind='bow', element=e, durability=900, rarity='rare', lore=LORE[e], icon='bow', bonus=2.5)
    item(id=f'{p}_staff', name=STAFF_NAME[e], kind='staff', element=e, power=8.0, mana=12, cooldown=14, durability=1200, rarity='rare', lore=LORE[e], icon='staff')
    for slot, sname in ARMOR_SLOTS:
        item(id=f'{p}_{slot}', name=f'{SET_NAME[e]} {sname}', kind='armor', element=e, slot=slot, rarity='rare', lore=LORE[e] + ' Wear all four for a set bonus.', icon=slot)
    item(id=f'{e}_essence', name=f'{EL_NAME[e]} Essence', kind='misc', element=e, icon='essence', rarity='uncommon', lore=f'Crystallised {EL_NAME[e].lower()} magic.')
    item(id=f'{e}_sigil', name=f'Sigil of {EL_NAME[e]}', kind='misc', element=e, icon='sigil', rarity='epic', stack=1, lore='Place it upon the Boss Altar of its dungeon.')

# legendary boss weapons
item(id='emberbrand', name='Emberbrand, Cinder Tyrant\'s Edge', kind='sword', element='flame', damage=11, speed=-2.6, durability=3200, rarity='epic', legendary=True, icon='greatsword',
     lore='Right-click: unleash a ring of cinders.')
item(id='heart_of_winter', name='Heart of Winter', kind='staff', element='frost', power=13.0, mana=18, cooldown=12, durability=3000, rarity='epic', legendary=True, icon='staff_big',
     lore='Its bolts pierce everything in their path.')
item(id='stormpiercer', name='Stormpiercer', kind='bow', element='storm', durability=2400, rarity='epic', legendary=True, bonus=5.0, icon='bow_big',
     lore='Arrows call down the sky.')
item(id='oakenheart_scepter', name='Oakenheart Scepter', kind='staff', element='verdant', power=9.0, mana=16, cooldown=12, durability=3000, rarity='epic', legendary=True, icon='scepter',
     lore='Every strike mends its wielder.')
item(id='voidreaver', name='Voidreaver', kind='sword', element='void', damage=11, speed=-2.4, durability=3200, rarity='epic', legendary=True, icon='greatsword',
     lore='Right-click: slip through the veil.')

# utility / misc
item(id='apprentice_staff', name='Apprentice Staff', kind='staff', element='arcane', power=5.0, mana=8, cooldown=16, durability=500, rarity='uncommon', icon='staff',
     lore='A humble focus for a would-be Riftwalker.')
item(id='rift_shard', name='Rift Shard', kind='misc', icon='shard', rarity='uncommon', lore='A splinter of the plane where magic and the world collide.')
item(id='rift_dust', name='Rift Dust', kind='misc', icon='dust', lore='Glittering residue of unstable magic.')
item(id='ancient_rune', name='Ancient Rune', kind='misc', icon='rune', rarity='rare', lore='Old Aldric\'s script, still warm.')
item(id='rift_anchor', name='Rift Anchor', kind='anchor', icon='anchor', rarity='rare', stack=16,
     lore='Right-click a block to tear open a stable Rift Gate.')
item(id='seekers_compass', name='Seeker\'s Compass', kind='compass', icon='compass', rarity='rare', stack=1,
     lore='Use: find your quest destination. Sneak + Use: choose a destination.')
item(id='quest_journal', name='Riftwalker\'s Journal', kind='journal', icon='journal', rarity='uncommon', stack=1,
     lore='Use: open your quest log. (Default key: J)')
item(id='mana_elixir', name='Mana Elixir', kind='elixir', icon='elixir_blue', stack=16, rarity='uncommon', lore='Restores a large amount of mana.', mana=80, heal=0)
item(id='vitality_elixir', name='Vitality Elixir', kind='elixir', icon='elixir_red', stack=16, rarity='uncommon', lore='Restores health and grants regeneration.', mana=0, heal=12)
item(id='tome_of_insight', name='Tome of Insight', kind='tome', icon='tome', rarity='epic', stack=16, lore='Use: gain one skill point.')

ITEM_BY_ID = {i['id']: i for i in ITEMS}

# ------------------------------------------------------------------ sites (landmark stone block property 'site')
SITES = [
    'altar_flame', 'altar_frost', 'altar_storm', 'altar_verdant', 'altar_void',              # 0-4
    'cinderhold_gate', 'frostspire_gate', 'stormwatch_gate', 'elderroot_gate', 'observatory_gate',  # 5-9
    'standing_stones', 'dragon_bones', 'watchtower', 'colossus', 'titans_arch', 'moonwell',   # 10-15
    'rift_scar', 'crystal_cathedral', 'fallen_keep', 'rift_monolith', 'sky_bridge',          # 16-20
    'ashen_bastion', 'frostwatch_hold', 'stormwatch_perch', 'grovekeepers_lodge', 'veiled_sanctum',  # 21-25
]
SITE_NAME = {
    'altar_flame': 'the Altar of Flame', 'altar_frost': 'the Altar of Frost', 'altar_storm': 'the Altar of Storm',
    'altar_verdant': 'the Altar of Verdant', 'altar_void': 'the Altar of Void',
    'cinderhold_gate': 'the Gates of Cinderhold', 'frostspire_gate': 'the Gates of Frostspire',
    'stormwatch_gate': 'the Gates of Stormwatch Aerie', 'elderroot_gate': 'the Gates of Elderroot',
    'observatory_gate': 'the Gates of the Hollow Observatory',
    'standing_stones': 'the Standing Stones', 'dragon_bones': 'the Dragon Bones', 'watchtower': 'the Ruined Watchtower',
    'colossus': 'the Sleeping Colossus', 'titans_arch': 'the Titan\'s Arch', 'moonwell': 'the Moonwell',
    'rift_scar': 'a Rift Scar', 'crystal_cathedral': 'the Crystal Cathedral', 'fallen_keep': 'the Fallen Keep',
    'rift_monolith': 'the Rift Monolith', 'sky_bridge': 'the Sky Bridge',
    'ashen_bastion': 'the Ashen Bastion', 'frostwatch_hold': 'Frostwatch Hold', 'stormwatch_perch': 'Stormwatch Perch',
    'grovekeepers_lodge': 'the Grovekeeper\'s Lodge', 'veiled_sanctum': 'the Veiled Sanctum',
}

# ------------------------------------------------------------------ blocks
# kind: cube | pillar | leaves | log | plant | portal | landmark | altar | ore | glow
BLOCKS = [
    dict(id='riftstone', name='Riftstone', kind='cube', strength=2.0, tool='pickaxe'),
    dict(id='riftstone_bricks', name='Riftstone Bricks', kind='cube', strength=2.0, tool='pickaxe'),
    dict(id='chiseled_riftstone', name='Chiseled Riftstone', kind='cube', strength=2.0, tool='pickaxe'),
    dict(id='riftstone_pillar', name='Riftstone Pillar', kind='pillar', strength=2.0, tool='pickaxe'),
    dict(id='rift_turf', name='Rift Turf', kind='turf', strength=0.8, tool='shovel'),
    dict(id='rift_crystal_block', name='Rift Crystal Block', kind='glow', strength=1.5, tool='pickaxe', light=12, drops='rift_shard'),
    dict(id='rift_shard_ore', name='Rift Shard Ore', kind='cube', strength=3.0, tool='pickaxe', drops='rift_shard', light=4),
    dict(id='glimmerwood_log', name='Glimmerwood Log', kind='log', strength=2.0, tool='axe'),
    dict(id='glimmerwood_planks', name='Glimmerwood Planks', kind='cube', strength=2.0, tool='axe'),
    dict(id='glimmerwood_leaves', name='Glimmerwood Leaves', kind='leaves', strength=0.2, tool='hoe', light=6),
    dict(id='glow_bloom', name='Glow Bloom', kind='plant', strength=0.0, tool='', light=9),
]
for e in ELEMENTS:
    p = SET[e]
    BLOCKS.append(dict(id=f'{p}_bricks', name=f'{SET_NAME[e]} Bricks', kind='cube', strength=2.5, tool='pickaxe', element=e))
    BLOCKS.append(dict(id=f'{p}_rune', name=f'{EL_NAME[e]} Rune Block', kind='glow', strength=2.5, tool='pickaxe', light=13, element=e))
BLOCKS += [
    dict(id='rift_portal', name='Rift Portal', kind='portal', strength=-1, tool='', light=11),
    dict(id='landmark_stone', name='Landmark Stone', kind='landmark', strength=-1, tool='', light=9),
    dict(id='boss_altar', name='Boss Altar', kind='altar', strength=-1, tool='', light=7),
]
BLOCK_BY_ID = {b['id']: b for b in BLOCKS}

# ------------------------------------------------------------------ entities
MOBS = [
    # id, name, style, element
    ('cinder_knight', 'Cinder Knight', 'knight', 'flame'),
    ('ember_mage', 'Ember Mage', 'mage', 'flame'),
    ('rime_wraith', 'Rime Wraith', 'wraith', 'frost'),
    ('frost_crawler', 'Frost Crawler', 'spider', 'frost'),
    ('gale_sentinel', 'Gale Sentinel', 'knight', 'storm'),
    ('storm_sprite', 'Storm Sprite', 'sprite', 'storm'),
    ('thorn_stalker', 'Thorn Stalker', 'spider', 'verdant'),
    ('bark_guardian', 'Bark Guardian', 'golem', 'verdant'),
    ('void_acolyte', 'Void Acolyte', 'mage', 'void'),
    ('rift_stalker', 'Rift Stalker', 'stalker', 'void'),
    ('rift_wraith', 'Rift Wraith', 'wraith', 'void'),
]
BOSSES = [
    ('ignarax', 'Ignarax, the Cinder Tyrant', 'flame'),
    ('hrimgar', 'Hrimgar, the Frozen Regent', 'frost'),
    ('zephyra', 'Zephyra, Tempest Queen', 'storm'),
    ('sylvara', 'Sylvara, the Thornmother', 'verdant'),
    ('nyxoth', 'Nyxoth, the Hollow Star', 'void'),
]
NPCS = {
    # id: (name, title, skin-style)
    'maera': ('Maera', 'Rift Sage', 'sage'),
    'brannoch': ('Brannoch Ironwick', 'Dwarven Smith', 'smith'),
    'quill': ('Quill Mossfoot', 'Wandering Merchant', 'merchant'),
    'kaelen': ('Lord Kaelen Emberhart', 'Warden of the Ashen Bastion', 'flame_lord'),
    'seraphine': ('Seraphine Frostwhisper', 'Keeper of Frostwatch', 'frost_lady'),
    'vaelor': ('Captain Vaelor', 'Stormwatch Skyreaver', 'storm_captain'),
    'elowen': ('Elowen Oakshade', 'Grove Druid', 'druid'),
    'ysmera': ('Ysmera the Veiled', 'Oracle of the Hollow Star', 'oracle'),
    'aldric_echo': ('Echo of Aldric', 'The Last King', 'ghost_king'),
}

PARTICLES = ['rift_mote', 'ember_spark', 'frost_flake', 'storm_spark', 'leaf_wisp', 'void_wisp']
