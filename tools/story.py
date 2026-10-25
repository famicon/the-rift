"""Story data: 5 questlines x 6 quests, NPC dialogue + trades, cutscenes, skill trees.  Written to realmbreak_story.json by gen_story.py."""
import math

# site indices (see manifest.SITES)
S = dict(altar_flame=0, altar_frost=1, altar_storm=2, altar_verdant=3, altar_void=4,
         cinderhold=5, frostspire=6, stormwatch=7, elderroot=8, observatory=9,
         standing_stones=10, dragon_bones=11, watchtower=12, colossus=13, titans_arch=14, moonwell=15,
         rift_scar=16, cathedral=17, fallen_keep=18, monolith=19, sky_bridge=20,
         ashen=21, frostwatch=22, perch=23, grove=24, veiled=25)

# which structure each site / npc / boss maps to (for the compass)
SITE_STRUCT = {0: 'altar_of_flame', 1: 'altar_of_frost', 2: 'altar_of_storm', 3: 'altar_of_verdant', 4: 'altar_of_void',
               5: 'cinderhold_citadel', 6: 'frostspire_vault', 7: 'stormwatch_aerie', 8: 'elderroot_sanctum', 9: 'hollow_observatory',
               10: 'standing_stone_ring', 11: 'dragon_bones', 12: 'ruined_watchtower', 13: 'sleeping_colossus', 14: 'titans_arch', 15: 'moonwell_shrine',
               16: 'rift_scar', 17: 'crystal_cathedral', 18: 'fallen_keep', 19: 'rift_monolith', 20: 'sky_bridge',
               21: 'ashen_bastion', 22: 'frostwatch_hold', 23: 'stormwatch_perch', 24: 'grovekeepers_lodge', 25: 'veiled_sanctum'}
NPC_HOME = {'maera': 'wayfarers_camp', 'brannoch': 'wayfarers_camp', 'quill': 'wayfarers_camp', 'kaelen': 'ashen_bastion', 'seraphine': 'frostwatch_hold',
            'vaelor': 'stormwatch_perch', 'elowen': 'grovekeepers_lodge', 'ysmera': 'veiled_sanctum', 'aldric_echo': 'fallen_keep'}
BOSS_STRUCT = {'ignarax': 'cinderhold_citadel', 'hrimgar': 'frostspire_vault', 'zephyra': 'stormwatch_aerie', 'sylvara': 'elderroot_sanctum', 'nyxoth': 'hollow_observatory'}

E = {  # element -> (set prefix, essence, sigil, boss)
    'flame': ('cinder', 'flame_essence', 'flame_sigil', 'ignarax'),
    'frost': ('rime', 'frost_essence', 'frost_sigil', 'hrimgar'),
    'storm': ('gale', 'storm_essence', 'storm_sigil', 'zephyra'),
    'verdant': ('thorn', 'verdant_essence', 'verdant_sigil', 'sylvara'),
    'void': ('null', 'void_essence', 'void_sigil', 'nyxoth'),
}


def kill(target, n, dim='', text=None):
    return dict(type='kill', target=target, count=n, dim=dim, text=text)


def collect(item, n, text=None):
    return dict(type='collect', target=item, count=n, text=text)


def attune(site, text=None, dim=''):
    return dict(type='attune', site=site, count=1, text=text, dim=dim)


def talk(npc, text=None):
    return dict(type='talk', target=npc, count=1, text=text)


def rift(text='Step into the Rift'):
    return dict(type='rift', count=1, text=text)


def boss(bid, text=None):
    return dict(type='boss', target=bid, count=1, text=text)


def gift(*items):
    return [dict(id=i, count=c) for (i, c) in items]


QUESTS = []


def q(line, idx, qid, title, giver, turnin, objs, offer, progress, done, rewards, points=1, xp=60, give=None, start_cs='', end_cs='', requires=None, summary=''):
    QUESTS.append(dict(id=qid, line=line, idx=idx, title=title, giver=giver, turnin=turnin, objectives=objs, offer=offer, progress=progress, done=done,
                       rewards=rewards, points=points, xp=xp, give=give or [], start_cs=start_cs, end_cs=end_cs,
                       requires=requires if requires is not None else ('' if idx == 1 and line == 1 else (f'l{line}q{idx - 1}' if idx > 1 else 'l1q2')), summary=summary))


LINES = [
    dict(id=1, element='flame', name='The Ember Crown', npc='kaelen', boss='ignarax', dungeon='Cinderhold Citadel', blurb='A fire lord, a dying fortress, and a tyrant who wears the Rift\'s heat like a crown.'),
    dict(id=2, element='frost', name='The Frozen Regent', npc='seraphine', boss='hrimgar', dungeon='Frostspire Vault', blurb='Winter has a throne now, and a king who will not let the snow melt.'),
    dict(id=3, element='storm', name='The Tempest Queen', npc='vaelor', boss='zephyra', dungeon='Stormwatch Aerie', blurb='Above the peaks a queen of thunder hoards the sky itself.'),
    dict(id=4, element='verdant', name='The Thornmother', npc='elowen', boss='sylvara', dungeon='Elderroot Sanctum', blurb='The Great Tree is hollow, and the thing within it is hungry.'),
    dict(id=5, element='void', name='The Hollow Star', npc='ysmera', boss='nyxoth', dungeon='Hollow Observatory', blurb='A star fell into the Rift and it is not shining anymore.'),
]

# ============================================================== LINE 1 - FLAME
q(1, 1, 'l1q1', 'A Spark in the Ashes', 'maera', 'maera',
  [kill('any_hostile', 5, text='Defeat hostile monsters'), collect('rift_dust', 3, 'Gather Rift Dust from fallen magical foes')],
  ['Ah, a traveller with steady hands. I am Maera. I watch the sky for tears, and lately it has been tearing.',
   'Take this staff and this journal. Prove you can fight, and bring me glimmering dust from the things that stalk the night.'],
  ['The dust only falls from creatures touched by the Rift. Hunt them after dark.'],
  ['Good. You have a Riftwalker\'s knack. The dust hums in your pack, can you feel it?', 'There is a scar in the land not far from here. I will tell you where. Come back when you have your courage.'],
  gift(('mana_elixir', 2), ('minecraft:bread', 8)), points=1, give=gift(('apprentice_staff', 1), ('quest_journal', 1), ('seekers_compass', 1)), start_cs='intro',
  summary='Meet Maera and prove yourself against the things that stalk the night.')
q(1, 2, 'l1q2', 'Through the Scar', 'maera', 'maera',
  [attune(S['rift_scar'], 'Find and touch the Landmark Stone at a Rift Scar'), rift('Step through the Rift Gate'), collect('rift_shard', 3, 'Mine or loot 3 Rift Shards inside the Rift')],
  ['A Rift Scar is where the magic plane bleeds into our world. Follow your Seeker\'s Compass to one and touch its stone.',
   'Then step through the gate. The Rift will be beautiful, and it will try to kill you. Bring back three shards.'],
  ['Three Rift Shards, and a safe return. The Scar will take you in; the gate on the other side will bring you home.'],
  ['You went... and came back. By the stars, the Rift sings to you.', 'There are five great powers fraying there: Flame, Frost, Storm, Verdant and Void. Five wardens, five lords. Choose where to begin. Kaelen of the Ashen Bastion waits in the burning lands.'],
  gift(('rift_anchor', 2), ('vitality_elixir', 2)), points=1, xp=100, end_cs='',
  summary='Find a Rift Scar, cross into the Rift, and return with Rift Shards.')
q(1, 3, 'l1q3', 'The Warden of Ash', 'maera', 'kaelen',
  [attune(S['ashen'], 'Reach the Ashen Bastion'), kill('ember_mage', 4, 'rift', 'Defeat Ember Mages in the Rift'), talk('kaelen', 'Speak with Lord Kaelen')],
  ['Lord Kaelen Emberhart holds the Ashen Bastion against the Cinder Tyrant. He will not trust you until you have bled for the cause.',
   'Find the Bastion, then burn out the Ember Mages in the Rift that feed the Tyrant\'s fire.'],
  ['The Ember Mages gather in the Rift\'s ash plains. Bring their ashes to Kaelen.'],
  ['You smell of smoke and victory. Good. I am Kaelen, last warden of the Cinderhold.', 'Take this armour. It was my father\'s. Wear it and the fire may hesitate.'],
  gift(('cinder_helmet', 1), ('cinder_boots', 1)), points=1, xp=120,
  summary='Reach the Ashen Bastion, weaken the Rift\'s Ember Mages and speak with Lord Kaelen.')
q(1, 4, 'l1q4', 'Where the Dragon Fell', 'kaelen', 'kaelen',
  [attune(S['dragon_bones'], 'Touch the stone among the Dragon Bones'), attune(S['altar_flame'], 'Attune to the Altar of Flame in the Rift', 'rift'), collect('flame_essence', 6, 'Gather Flame Essence')],
  ['A dragon died in these hills long ago. Its heart-fire seeped into the Rift and became the Altar of Flame.',
   'Attune yourself at both, and gather essence. Ignarax\'s crown can only be answered with flame of the same kind.'],
  ['Dragon Bones in the overworld, the Altar of Flame in the Rift. Six essences besides.'],
  ['The fire accepts you! I did not think it would, not after the Tyrant. Here, the rest of my armour.', 'Now we hold the key to the Cinderhold. The way in lies behind a gate that no mortal has opened in a century.'],
  gift(('cinder_chestplate', 1), ('cinder_leggings', 1)), points=1, xp=140,
  summary='Attune to the Dragon Bones and the Rift\'s Altar of Flame.')
q(1, 5, 'l1q5', 'The Cinderhold', 'kaelen', 'kaelen',
  [attune(S['cinderhold'], 'Reach the Gates of Cinderhold'), kill('cinder_knight', 6, text='Slay Cinder Knights'), kill('rift_wraith', 3, 'rift', 'Banish Rift Wraiths in the Rift'), collect('flame_sigil', 1, 'Take the Sigil of Flame from the vault')],
  ['Cinderhold Citadel, my family\'s home, now a black fortress ringed by lava. The Tyrant\'s knights guard every hall.',
   'Fight through to the vault beneath the keep and take the Sigil of Flame. And clear the Wraiths in the Rift, or they will reinforce the Citadel through the scars.'],
  ['The vault lies beneath the great hall. Mind the lava on the second floor.'],
  ['The Sigil... I thought I would never hold it again. Hold it well. It is the key to the throne.', 'Take this blade, Cinderfang, and this staff. You will need them.'],
  gift(('cinder_sword', 1), ('cinder_staff', 1)), points=1, xp=200,
  summary='Storm Cinderhold Citadel and take the Sigil of Flame.')
q(1, 6, 'l1q6', 'The Cinder Tyrant', 'kaelen', 'kaelen',
  [rift('Be in the Rift when the Tyrant is struck down'), boss('ignarax', 'Defeat Ignarax, the Cinder Tyrant'), talk('kaelen', 'Return to Lord Kaelen')],
  ['Climb to the Throne of Cinders and place the Sigil on the altar. Ignarax will rise.',
   'His fire is bound to the Rift. Strike him down and the Rift will feel it. Make sure you are near a gate when you do.'],
  ['The Tyrant waits at the top of the Citadel. Place the Sigil of Flame on the altar.'],
  ['It is quiet. The ash is... settling. You did it. The Ember Crown is no more.', 'The Rift calls to you. Choose another warden. The world needs a Riftwalker.'],
  gift(('cinder_bow', 1), ('flame_essence', 8), ('tome_of_insight', 1)), points=2, xp=400, end_cs='finale_flame',
  summary='Defeat Ignarax and end the Ember Crown.')

# ============================================================== LINE 2 - FROST
q(2, 1, 'l2q1', 'Frostbitten Whispers', 'seraphine', 'seraphine',
  [attune(S['frostwatch'], 'Reach Frostwatch Hold'), talk('seraphine', 'Speak with Seraphine Frostwhisper'), kill('any_hostile', 6, text='Defeat hostile monsters')],
  ['Cold finds everyone. Few wish to be found by it. I am Seraphine, keeper of Frostwatch.',
   'My watch is failing. Prove you can hold a line, and I will tell you why the snow never stops.'],
  ['Six monsters, then return. The hold is quieter when the wolves are dead.'],
  ['The hold holds, for now. Listen: a regent sits in the Frostspire and sings winter into the world. His song carries into the Rift.',
   'Follow the cold. You will find where it begins.'],
  gift(('vitality_elixir', 2), ('minecraft:cooked_beef', 8)), points=1, xp=80,
  summary='Reach Frostwatch Hold and earn Seraphine\'s trust.')
q(2, 2, 'l2q2', 'Winter Beyond the Veil', 'seraphine', 'seraphine',
  [rift('Enter the Rift'), kill('rime_wraith', 4, 'rift', 'Banish Rime Wraiths in the Rift'), collect('frost_essence', 4, 'Gather Frost Essence')],
  ['Hrimgar\'s court is not only in the Frostspire. The Rift has its own Frost Expanse where his wraiths drift unchecked.',
   'Go through a gate. Banish four Rime Wraiths. Their essence will tell us what he is.'],
  ['Rime Wraiths cling to frozen ground in the Rift. They bite like the wind.'],
  ['This essence... it is not natural. It is a heartbeat, slowed to a crawl.', 'Here, wear the cold as a cloak. It will not sting you now.'],
  gift(('rime_helmet', 1), ('rime_boots', 1)), points=1, xp=120,
  summary='Cross into the Rift and banish the Rime Wraiths.')
q(2, 3, 'l2q3', 'Altar of Frost', 'seraphine', 'seraphine',
  [attune(S['altar_frost'], 'Attune to the Altar of Frost in the Rift', 'rift'), attune(S['standing_stones'], 'Touch the Standing Stones in the overworld'), collect('rift_shard', 5, 'Gather Rift Shards')],
  ['There is an Altar of Frost in the Rift, and an older circle of standing stones here. Both remember the first winter.',
   'Touch both and bring me five Rift Shards. I will make a ward.'],
  ['The Altar floats on its own island somewhere in the Rift. The stones stand on the plains.'],
  ['The stones are warm?! Impossible. And yet, the Altar answered you as well.', 'Take the rest of the Rimeweave. Winter will not take you.'],
  gift(('rime_chestplate', 1), ('rime_leggings', 1)), points=1, xp=140,
  summary='Attune to the Altar of Frost and the Standing Stones.')
q(2, 4, 'l2q4', 'The Rimebound Archive', 'seraphine', 'seraphine',
  [kill('frost_crawler', 5, 'rift', 'Slay Frost Crawlers in the Rift'), collect('ancient_rune', 1, 'Find an Ancient Rune in a ruin or vault'), talk('seraphine', 'Bring the rune to Seraphine')],
  ['An archive lies sealed in ice below Frostwatch, and its key is an Ancient Rune. They turn up in ruins and vaults.',
   'And the crawlers in the Rift have been chewing the ice from below. Thin them out.'],
  ['Ancient Runes sit in dungeon chests. Frost Crawlers swarm in the Rift\'s ice.'],
  ['Aldric\'s script. The Last King wrote the sealing runes. The Regent was his friend, once.', 'It is a long story. Take it with you: the vault of Frostspire.'],
  gift(('rime_sword', 1), ('mana_elixir', 3)), points=1, xp=160,
  summary='Find an Ancient Rune and thin the Frost Crawlers in the Rift.')
q(2, 5, 'l2q5', 'The Frostspire Vault', 'seraphine', 'seraphine',
  [attune(S['frostspire'], 'Reach the Gates of Frostspire'), kill('rime_wraith', 6, text='Banish Rime Wraiths'), kill('frost_crawler', 4, 'rift', 'Crush Frost Crawlers in the Rift'), collect('frost_sigil', 1, 'Take the Sigil of Frost from the vault')],
  ['Frostspire Vault: a crystal tower ringed with frozen water. The vault is beneath it.',
   'Take the Sigil of Frost. And clear the crawlers in the Rift; they are digging through to the Vault from below.'],
  ['The vault is below the great hall, past a stair behind the tower.'],
  ['The Sigil of Frost. It is so cold it burns. Hrimgar will feel it from here.', 'Take Rimebrand and a staff. Do not enter his hall unprepared.'],
  gift(('rime_staff', 1), ('minecraft:golden_apple', 2)), points=1, xp=200,
  summary='Take the Sigil of Frost from Frostspire Vault.')
q(2, 6, 'l2q6', 'The Frozen Regent', 'seraphine', 'seraphine',
  [rift('Be in the Rift when winter breaks'), boss('hrimgar', 'Defeat Hrimgar, the Frozen Regent'), talk('seraphine', 'Return to Seraphine')],
  ['At the top of the Spire, place the Sigil on the altar. Hrimgar will wake. He was a good man once.',
   'Whatever he says, finish it. The Rift will thaw when he falls.'],
  ['The Regent waits in the crown of the spire. Dress warm.'],
  ['The snow... it is melting. Look. Look! Thank you, Riftwalker.', 'Take the Hoarfrost Bow, and Seraphine\'s blessing.'],
  gift(('rime_bow', 1), ('frost_essence', 8), ('tome_of_insight', 1)), points=2, xp=400, end_cs='finale_frost',
  summary='Defeat Hrimgar and thaw the north.')

# ============================================================== LINE 3 - STORM
q(3, 1, 'l3q1', 'Winds of War', 'vaelor', 'vaelor',
  [attune(S['perch'], 'Reach Stormwatch Perch'), talk('vaelor', 'Speak with Captain Vaelor'), kill('any_hostile', 6, text='Defeat hostile monsters')],
  ['Captain Vaelor, Skyreaver. You are standing on the last perch that still has a roof.',
   'Zephyra hoards the thunder. I need fighters who do not flinch at lightning. Six kills. Go.'],
  ['The monsters come at dusk. Watch the sky.'],
  ['You did not flinch. Mostly. Fine.', 'The Queen\'s storms leak into the Rift. Follow them and you will find where the sky is bleeding.'],
  gift(('mana_elixir', 2), ('minecraft:cooked_chicken', 8)), points=1, xp=80,
  summary='Reach Stormwatch Perch and prove yourself to Captain Vaelor.')
q(3, 2, 'l3q2', 'Skyfall into the Rift', 'vaelor', 'vaelor',
  [rift('Enter the Rift'), kill('storm_sprite', 5, 'rift', 'Disperse Storm Sprites in the Rift'), collect('storm_essence', 4, 'Gather Storm Essence')],
  ['Storm sprites riding the Rift\'s thunderclouds are the Queen\'s scouts.',
   'Through a gate. Kill five sprites. Bring me the essence they drop. I want to feel what we are up against.'],
  ['Sprites cluster on the Rift\'s highlands. They crackle.'],
  ['It sings under my fingers. Beautiful, horrible stuff.', 'Galeguard, light as a gust, strong as a gale.'],
  gift(('gale_helmet', 1), ('gale_boots', 1)), points=1, xp=120,
  summary='Cross the Rift and disperse the Queen\'s Storm Sprites.')
q(3, 3, 'l3q3', 'Altar of Storm', 'vaelor', 'vaelor',
  [attune(S['altar_storm'], 'Attune to the Altar of Storm in the Rift', 'rift'), attune(S['titans_arch'], 'Touch the stone beneath the Titan\'s Arch'), collect('rift_shard', 5, 'Gather Rift Shards')],
  ['The Titan\'s Arch is a gate no titan ever walked through. It points at the Altar of Storm in the Rift.',
   'Touch both and the lightning will recognise you.'],
  ['The Arch stands in the peaks. The Altar floats in the Rift\'s sky.'],
  ['The lightning does not strike you. That is... new.', 'Take the rest of the Galeguard.'],
  gift(('gale_chestplate', 1), ('gale_leggings', 1)), points=1, xp=140,
  summary='Attune to the Titan\'s Arch and the Altar of Storm.')
q(3, 4, 'l3q4', 'The Lightning Rods', 'vaelor', 'vaelor',
  [attune(S['watchtower'], 'Reach the Ruined Watchtower'), kill('gale_sentinel', 4, 'rift', 'Topple Gale Sentinels in the Rift'), talk('vaelor', 'Report to Vaelor')],
  ['An old watchtower on the plains has the only working lightning rods for a hundred miles. It will show us the shape of her storms.',
   'And the Gale Sentinels in the Rift keep hammering at our wards. Break a few.'],
  ['The Watchtower is ruined but intact where it matters.'],
  ['You read the storm like a Skyreaver. The pattern points straight at her aerie.', 'Take Thunderedge. It was my sister\'s.'],
  gift(('gale_sword', 1), ('vitality_elixir', 3)), points=1, xp=160,
  summary='Visit the Ruined Watchtower and break the Rift\'s Gale Sentinels.')
q(3, 5, 'l3q5', 'Stormwatch Aerie', 'vaelor', 'vaelor',
  [attune(S['stormwatch'], 'Reach the Gates of Stormwatch Aerie'), kill('gale_sentinel', 6, text='Topple Gale Sentinels'), kill('storm_sprite', 4, 'rift', 'Disperse Storm Sprites in the Rift'), collect('storm_sigil', 1, 'Take the Sigil of Storm from the vault')],
  ['The Aerie is built on a mesa that was carved by lightning. A grand stair leads up. The vault is under the tower.',
   'Bring me the Sigil of Storm. And thin the sprites, or they will carry it away on the wind.'],
  ['The vault is under the great hall. Watch for slippery ice on the second floor.'],
  ['The Sigil! Look at that. I can feel my hair standing.', 'Take this staff. Zephyra will want it back.'],
  gift(('gale_staff', 1), ('minecraft:golden_apple', 2)), points=1, xp=200,
  summary='Climb the Aerie and take the Sigil of Storm.')
q(3, 6, 'l3q6', 'The Tempest Queen', 'vaelor', 'vaelor',
  [rift('Be in the Rift when the storm breaks'), boss('zephyra', 'Defeat Zephyra, the Tempest Queen'), talk('vaelor', 'Return to Vaelor')],
  ['Place the Sigil at the crown of the Aerie. Zephyra will come down. Fight her in the lightning, not against it.',
   'May the wind be at your back, Riftwalker.'],
  ['The Queen is at the top of the Aerie. Hold your ground when she calls the thunder.'],
  ['The sky is clear. I forgot what that looked like.', 'The Stormcall Bow. Aim high.'],
  gift(('gale_bow', 1), ('storm_essence', 8), ('tome_of_insight', 1)), points=2, xp=400, end_cs='finale_storm',
  summary='Defeat Zephyra and calm the sky.')

# ============================================================== LINE 4 - VERDANT
q(4, 1, 'l4q1', 'The Withering Grove', 'elowen', 'elowen',
  [attune(S['grove'], 'Reach the Grovekeeper\'s Lodge'), talk('elowen', 'Speak with Elowen Oakshade'), kill('any_hostile', 6, text='Defeat hostile monsters')],
  ['I am Elowen. The grove has been withering for a season. Something is eating the roots from below.',
   'Clear the creatures that gnaw the saplings. Then we will talk about the Rift.'],
  ['Six kills in the grove. They like the dark.'],
  ['The saplings breathe again. Thank you, stranger.', 'Look for the glimmering trees that bloom in the Rift. They are the grove\'s cousins.'],
  gift(('vitality_elixir', 2), ('minecraft:apple', 8)), points=1, xp=80,
  summary='Reach the Grovekeeper\'s Lodge and clear the gnawing things.')
q(4, 2, 'l4q2', 'Glimmerwood', 'elowen', 'elowen',
  [rift('Enter the Rift'), collect('glimmerwood_log', 8, 'Chop Glimmerwood Logs in the Rift'), kill('thorn_stalker', 4, 'rift', 'Slay Thorn Stalkers in the Rift')],
  ['Glimmerwood grows only in the Rift, and it glows. The Thornmother is wrapping her roots around it.',
   'Bring me eight logs. Cut a few thorn stalkers down while you are there.'],
  ['The Verdant Canopy in the Rift has Glimmerwood, thick as walls.'],
  ['It sings, you can feel it. The grove\'s song, played backwards.', 'Wear thorn and bark. They will know you for a friend.'],
  gift(('thorn_helmet', 1), ('thorn_boots', 1)), points=1, xp=120,
  summary='Chop Glimmerwood in the Rift and slay the Thorn Stalkers.')
q(4, 3, 'l4q3', 'Altar of Verdant', 'elowen', 'elowen',
  [attune(S['altar_verdant'], 'Attune to the Altar of Verdant in the Rift', 'rift'), attune(S['moonwell'], 'Touch the stone at the Moonwell'), collect('rift_shard', 5, 'Gather Rift Shards')],
  ['The Moonwell and the Altar of Verdant are the grove\'s two hearts. One in your world, one in the Rift.',
   'Touch both. Bring shards for a ward.'],
  ['The Moonwell is hidden in the forest. The Altar floats in the Canopy.'],
  ['Both hearts beat for you. Rare.', 'The rest of the Thornbark.'],
  gift(('thorn_chestplate', 1), ('thorn_leggings', 1)), points=1, xp=140,
  summary='Attune to the Moonwell and the Altar of Verdant.')
q(4, 4, 'l4q4', 'The Sleeping Giant', 'elowen', 'elowen',
  [attune(S['colossus'], 'Climb the Sleeping Colossus and touch its stone'), kill('bark_guardian', 4, 'rift', 'Fell Bark Guardians in the Rift'), talk('elowen', 'Return to Elowen')],
  ['There is a giant of stone who has been sleeping since before the Rift opened. He is the Thornmother\'s oldest enemy.',
   'And the bark guardians... they were gentle once. See what troubles them.'],
  ['The Colossus lies in the plains. Enter through its mouth.'],
  ['He stirs. Maybe not today. Soon.', 'Thornblade. Take it. It will not rot.'],
  gift(('thorn_sword', 1), ('mana_elixir', 3)), points=1, xp=160,
  summary='Visit the Sleeping Colossus and calm the Rift\'s Bark Guardians.')
q(4, 5, 'l4q5', 'Elderroot Sanctum', 'elowen', 'elowen',
  [attune(S['elderroot'], 'Reach the Gates of Elderroot'), kill('thorn_stalker', 6, text='Slay Thorn Stalkers'), kill('bark_guardian', 4, text='Fell Bark Guardians'), collect('verdant_sigil', 1, 'Take the Sigil of Verdant from the vault')],
  ['Elderroot Sanctum is the Great Tree itself, hollowed out. The Thornmother lives at its crown. The vault is under the roots.',
   'Take the Sigil. You will need it to wake her.'],
  ['Mind the berry bushes on the second floor. They bite.'],
  ['The Sigil of Verdant. It is warm, and alive.', 'This staff is cut from a branch of the Great Tree.'],
  gift(('thorn_staff', 1), ('minecraft:golden_apple', 2)), points=1, xp=200,
  summary='Descend into the roots of Elderroot and take the Sigil of Verdant.')
q(4, 6, 'l4q6', 'The Thornmother', 'elowen', 'elowen',
  [rift('Be in the Rift when she falls'), boss('sylvara', 'Defeat Sylvara, the Thornmother'), talk('elowen', 'Return to Elowen')],
  ['Climb the Great Tree and place the Sigil at its heart. Sylvara will rise.',
   'Do not fear the thorns. Fear what she grows from your fear.'],
  ['The Thornmother waits in the heart of the tree. Strike the roots too.'],
  ['The grove is green again. Look, the saplings stand.', 'The Wildwood Bow, for the Riftwalker who saved the Great Tree.'],
  gift(('thorn_bow', 1), ('verdant_essence', 8), ('tome_of_insight', 1)), points=2, xp=400, end_cs='finale_verdant',
  summary='Defeat Sylvara and save the Great Tree.')

# ============================================================== LINE 5 - VOID
q(5, 1, 'l5q1', 'The Veiled Oracle', 'ysmera', 'ysmera',
  [attune(S['veiled'], 'Reach the Veiled Sanctum'), talk('ysmera', 'Speak with Ysmera the Veiled'), kill('any_hostile', 6, text='Defeat hostile monsters')],
  ['I have seen you before, Riftwalker, in a sky that has not happened yet. I am Ysmera.',
   'The Hollow Star is wakening. Prove yourself. Six of the things that creep in the night.'],
  ['Night is thick with them tonight.'],
  ['The dark knows your name. Do not answer it.', 'The star fell into the Rift long ago. Go and see what it has become.'],
  gift(('mana_elixir', 3), ('minecraft:golden_carrot', 8)), points=1, xp=80,
  summary='Reach the Veiled Sanctum and meet the Oracle.')
q(5, 2, 'l5q2', 'Hollow Star Rising', 'ysmera', 'ysmera',
  [rift('Enter the Rift'), kill('void_acolyte', 4, 'rift', 'Defeat Void Acolytes in the Rift'), collect('void_essence', 4, 'Gather Void Essence')],
  ['In the Void Expanse the acolytes kneel to a thing that is not there. Show them it is not there.',
   'Bring me their essence. I need to read the shape of the hole.'],
  ['The acolytes hum in the Void Expanse.'],
  ['The essence is a ledger of everything that was lost.', 'Nullveil. It will hide your footsteps from the dark.'],
  gift(('null_helmet', 1), ('null_boots', 1)), points=1, xp=120,
  summary='Cross the Rift and quiet the Void Acolytes.')
q(5, 3, 'l5q3', 'Altar of Void', 'ysmera', 'ysmera',
  [attune(S['altar_void'], 'Attune to the Altar of Void in the Rift', 'rift'), attune(S['cathedral'], 'Touch the stone in the Crystal Cathedral', 'rift'), collect('rift_shard', 6, 'Gather Rift Shards')],
  ['The Crystal Cathedral and the Altar of Void hold the star\'s echo. Both are in the Rift. Do not look at the sky there for too long.'],
  ['The Cathedral is a nave of crystal. The Altar floats in the dark.'],
  ['The echo stays with you. Do not be afraid of it.', 'The rest of the Nullveil.'],
  gift(('null_chestplate', 1), ('null_leggings', 1)), points=1, xp=140,
  summary='Attune to the Crystal Cathedral and the Altar of Void.')
q(5, 4, 'l5q4', 'Echo of the Last King', 'ysmera', 'ysmera',
  [attune(S['fallen_keep'], 'Reach the Fallen Keep', 'rift'), talk('aldric_echo', 'Speak with the Echo of Aldric'), attune(S['monolith'], 'Touch the Rift Monolith', 'rift')],
  ['Aldric was the last king of the plane before the Rift. His echo lingers in the Fallen Keep. Ask him what he sealed.',
   'And touch the Monolith he raised to hold the star.'],
  ['Aldric\'s echo does not speak to the afraid.'],
  ['He told you? All of it? Then you know the price.', 'Nullblade. It will cut the dark.'],
  gift(('null_sword', 1), ('vitality_elixir', 3)), points=1, xp=160,
  summary='Speak with the Echo of Aldric in the Rift.')
q(5, 5, 'l5q5', 'The Hollow Observatory', 'ysmera', 'ysmera',
  [attune(S['observatory'], 'Reach the Gates of the Hollow Observatory', 'rift'), kill('void_acolyte', 6, text='Defeat Void Acolytes'), kill('rift_stalker', 4, 'rift', 'Slay Rift Stalkers in the Rift'), collect('void_sigil', 1, 'Take the Sigil of Void from the vault')],
  ['The Hollow Observatory floats in the Rift, where the star was studied and lost. The vault is under the dome.',
   'Take the Sigil of Void. Make sure the stalkers do not follow you out.'],
  ['The Observatory\'s upper floors are slippery with soul sand.'],
  ['The Sigil. It weighs nothing, and everything.', 'This staff leaves no shadow.'],
  gift(('null_staff', 1), ('minecraft:golden_apple', 2)), points=1, xp=200,
  summary='Fly to the Hollow Observatory and take the Sigil of Void.')
q(5, 6, 'l5q6', 'The Hollow Star', 'ysmera', 'ysmera',
  [rift('Face the star in the Rift'), boss('nyxoth', 'Defeat Nyxoth, the Hollow Star'), talk('ysmera', 'Return to Ysmera')],
  ['At the top of the Observatory, place the Sigil. The Star will return. It has been waiting.',
   'Do not look into it. Look past it.'],
  ['The Star hangs in the dome. Strike when it blinks.'],
  ['The sky is... blue. When did it become so blue?', 'The Voidstring Bow. For the Riftwalker who finished what Aldric started.'],
  gift(('null_bow', 1), ('void_essence', 8), ('tome_of_insight', 2)), points=3, xp=600, end_cs='finale_void',
  summary='Defeat Nyxoth and close the wound in the sky.')

# ============================================================== NPCs
NPCS = {
    'maera': dict(lines=['The Rift is not a place, it is a conversation between two worlds. Be careful what you say to it.', 'Lost? Look at your compass, and read your journal.'],
                  trades=[dict(cost=[('rift_shard', 2)], result=('mana_elixir', 2)), dict(cost=[('rift_shard', 3)], result=('vitality_elixir', 2)), dict(cost=[('rift_dust', 8)], result=('rift_anchor', 1))]),
    'brannoch': dict(lines=['Hah! A Riftwalker. Mind the anvil, lass, she bites.', 'Bring me shards and iron, and I will get you something that does not break.'],
                     trades=[dict(cost=[('rift_shard', 4)], result=('minecraft:diamond', 1)), dict(cost=[('rift_dust', 6)], result=('minecraft:iron_ingot', 6)), dict(cost=[('rift_shard', 8)], result=('minecraft:netherite_scrap', 1)),
                             dict(cost=[('rift_shard', 6)], result=('minecraft:enchanted_golden_apple', 1))]),
    'quill': dict(lines=['Quill Mossfoot, at your service! Potions, anchors, compasses, whatever you need. I never ask where it came from.', 'Rift dust? Hmmm. I will give you a fair price. Fair for me.'],
                  trades=[dict(cost=[('minecraft:emerald', 4)], result=('seekers_compass', 1)), dict(cost=[('rift_dust', 10)], result=('mana_elixir', 3)), dict(cost=[('rift_shard', 2)], result=('rift_anchor', 1)),
                          dict(cost=[('rift_dust', 8)], result=('vitality_elixir', 2)), dict(cost=[('minecraft:emerald', 6)], result=('quest_journal', 1))]),
    'kaelen': dict(lines=['The Citadel was my home. It is Ignarax\'s throne now.', 'Embers keep, Riftwalker.'],
                   trades=[dict(cost=[('flame_essence', 4)], result=('cinder_bricks', 8)), dict(cost=[('flame_essence', 8)], result=('flame_sigil', 1))]),
    'seraphine': dict(lines=['The cold is patient. We have to be more patient than the cold.', 'Warm your hands, then go.'],
                      trades=[dict(cost=[('frost_essence', 4)], result=('rime_bricks', 8)), dict(cost=[('frost_essence', 8)], result=('frost_sigil', 1))]),
    'vaelor': dict(lines=['The wind favours the quick. Be quick.', 'We do not fear the storm. We fear the quiet before it.'],
                   trades=[dict(cost=[('storm_essence', 4)], result=('gale_bricks', 8)), dict(cost=[('storm_essence', 8)], result=('storm_sigil', 1))]),
    'elowen': dict(lines=['Roots remember. So should you.', 'Take only what you need. And give back more.'],
                   trades=[dict(cost=[('verdant_essence', 4)], result=('thorn_bricks', 8)), dict(cost=[('verdant_essence', 8)], result=('verdant_sigil', 1))]),
    'ysmera': dict(lines=['Everything I say has already happened. Pay attention anyway.', 'I see you, and you see me, and neither of us is quite there.'],
                   trades=[dict(cost=[('void_essence', 4)], result=('null_bricks', 8)), dict(cost=[('void_essence', 8)], result=('void_sigil', 1))]),
    'aldric_echo': dict(lines=['I was a king once. Now I am a draught in a hall. Ask, and I will answer what I can.', 'Seal the Rift. Or open it. I no longer remember which was the mistake.'],
                        trades=[]),
}
# Quest talk-lines (what an NPC says when a talk objective completes) are written inline in 'done' for the quest; extra:
TALK_LINES = {
    'l5q4': ['I am Aldric. I was the last king before the Rift. I sealed a star into a hollow, and the star did not wish to stay sealed.',
             'Take my regret to Ysmera. Tell her that the Monolith still stands, and that the star is hungry.'],
}

# ============================================================== cutscenes
def orbit(n, radius, h, a0, sweep, ly, dur, texts=None, rise=0.0):
    shots = []
    for i in range(n):
        a1 = a0 + sweep * i / n
        a2 = a0 + sweep * (i + 1) / n
        p1 = [round(math.cos(a1) * radius, 2), round(h + rise * i, 2), round(math.sin(a1) * radius, 2)]
        p2 = [round(math.cos(a2) * radius, 2), round(h + rise * (i + 1), 2), round(math.sin(a2) * radius, 2)]
        shots.append(dict(dur=dur, **{'from': p1, 'to': p2}, look=[0, ly, 0], text=(texts[i] if texts and i < len(texts) else '')))
    return shots


CUTSCENES = {
    'intro': dict(anchor='player', title='Wayfarer\'s Camp', shots=orbit(4, 9, 3.5, 0.5, 2.2, 1.2, 70, ['A camp at the edge of the unknown...', 'Maera has read the sky for tears.', 'Something is wrong with the world.', 'And you are the only one who can see it.'], 0.5)),
    'rift_entry': dict(anchor='player', title='The Rift', shots=orbit(5, 6, 2.2, 3.9, 3.0, 1.5, 60, ['The air tastes of lightning...', 'Islands drift in a violet sky.', 'This is where magic and world collide.', 'The Rift.', 'Everything here wants to be remembered.'], 0.8)),
    'boss_ignarax': dict(anchor='altar', title='Ignarax, the Cinder Tyrant', shots=orbit(4, 8, 5, 0.2, 2.5, 3, 55, ['The sigil blazes.', 'The throne cracks.', 'Fire climbs the walls.', 'IGNARAX RISES.'], 1.5)),
    'boss_hrimgar': dict(anchor='altar', title='Hrimgar, the Frozen Regent', shots=orbit(4, 8, 5, 1.0, 2.5, 3, 55, ['Frost spreads over the floor.', 'A crown of ice assembles.', 'The air stops moving.', 'HRIMGAR RISES.'], 1.5)),
    'boss_zephyra': dict(anchor='altar', title='Zephyra, Tempest Queen', shots=orbit(4, 8, 5, 2.0, 2.5, 3, 55, ['Thunder rolls through the dome.', 'The wind begins to scream.', 'Lightning gathers.', 'ZEPHYRA DESCENDS.'], 1.5)),
    'boss_sylvara': dict(anchor='altar', title='Sylvara, the Thornmother', shots=orbit(4, 8, 5, 3.0, 2.5, 3, 55, ['Roots tear up the floor.', 'The Great Tree groans.', 'Green fire glows in the bark.', 'SYLVARA AWAKENS.'], 1.5)),
    'boss_nyxoth': dict(anchor='altar', title='Nyxoth, the Hollow Star', shots=orbit(4, 8, 5, 4.0, 2.5, 3, 55, ['The dome goes dark.', 'A hole opens in the sky.', 'Something looks back.', 'NYXOTH BLINKS.'], 1.5)),
    'finale_flame': dict(anchor='player', title='The Ember Crown Falls', shots=orbit(3, 10, 4, 0.0, 2.0, 2, 70, ['The fires die. The ash settles.', 'The Cinderhold is silent.', 'A new dawn over the burnt hills.'], 1.0)),
    'finale_frost': dict(anchor='player', title='The Regent Is Gone', shots=orbit(3, 10, 4, 1.0, 2.0, 2, 70, ['The ice begins to crack.', 'Water runs under the snow.', 'Spring, at last.'], 1.0)),
    'finale_storm': dict(anchor='player', title='The Sky Is Clear', shots=orbit(3, 10, 4, 2.0, 2.0, 2, 70, ['The thunder fades.', 'Clouds part over the peaks.', 'A silence full of birdsong.'], 1.0)),
    'finale_verdant': dict(anchor='player', title='The Great Tree Heals', shots=orbit(3, 10, 4, 3.0, 2.0, 2, 70, ['The thorns wither.', 'Green shoots break the ash.', 'The grove breathes again.'], 1.0)),
    'finale_void': dict(anchor='player', title='The Star Goes Out', shots=orbit(3, 10, 4, 4.0, 2.0, 2, 70, ['The hole in the sky closes.', 'Stars, ordinary ones, come out.', 'The Rift is quiet, for now.'], 1.0)),
}

# ============================================================== skill trees
# node: id, name, desc, cost, requires[], effect {stat: value} or spell
SKILLS = {}
for el, nm in (('flame', 'Flame'), ('frost', 'Frost'), ('storm', 'Storm'), ('verdant', 'Verdant'), ('void', 'Void')):
    sp1 = dict(flame=('Fire Nova', 'nova'), frost=('Frost Nova', 'nova'), storm=('Chain Lightning', 'chain'), verdant=('Thorn Snare', 'snare'), void=('Blink', 'blink'))[el]
    sp2 = dict(flame=('Meteor', 'meteor'), frost=('Ice Lance', 'lance'), storm=('Tempest', 'tempest'), verdant=('Bloom', 'bloom'), void=('Rift Rend', 'rend'))[el]
    cap = dict(flame=('Cinder Soul', 'Your melee strikes ignite foes.', 'ignite'), frost=('Winter\'s Grasp', 'Your melee strikes chill foes.', 'chill'),
               storm=('Stormstride', 'Move faster, always.', 'swift'), verdant=('Heartwood', 'Slowly regenerate health.', 'regen'), void=('Veilstep', 'Unseen strikes: a chance to evade damage.', 'evade'))[el]
    SKILLS[el] = [
        dict(id=f'{el}_1', name=f'{nm} Attunement', desc='+10% spell power.', cost=1, requires=[], effect=dict(power=0.10), x=0, y=0),
        dict(id=f'{el}_2', name='Reservoir', desc='+25 maximum mana.', cost=1, requires=[f'{el}_1'], effect=dict(mana=25), x=0, y=1),
        dict(id=f'{el}_3', name=sp1[0], desc=f'Unlocks {sp1[0]}. Press V to cycle spells while holding a staff.', cost=2, requires=[f'{el}_1'], spell=sp1[1], x=-1, y=1),
        dict(id=f'{el}_4', name='Spellweaving', desc='+15% spell power, +1 mana/sec regeneration.', cost=2, requires=[f'{el}_2'], effect=dict(power=0.15, regen=1.0), x=1, y=2),
        dict(id=f'{el}_5', name=sp2[0], desc=f'Unlocks {sp2[0]}. Press V to cycle spells while holding a staff.', cost=3, requires=[f'{el}_3', f'{el}_4'], spell=sp2[1], x=0, y=3),
        dict(id=f'{el}_6', name=cap[0], desc=cap[1], cost=3, requires=[f'{el}_5'], passive=cap[2], x=0, y=4),
    ]


def build():
    return dict(lines=LINES, quests=QUESTS, npcs={k: dict(lines=v['lines'], trades=[dict(cost=[dict(id=i, count=c) for (i, c) in t['cost']], result=dict(id=t['result'][0], count=t['result'][1])) for t in v['trades']], home=NPC_HOME[k]) for k, v in NPCS.items()},
                site_struct={str(k): v for k, v in SITE_STRUCT.items()}, boss_struct=BOSS_STRUCT, talk_lines=TALK_LINES, cutscenes=CUTSCENES, skills=SKILLS)
