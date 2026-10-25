# Realmbreak — a fantasy questing mod (Fabric 1.21.1)

Five questlines, five bosses, five dungeons, custom armour / swords / bows / magic staffs,
quest NPCs with dialogue and trading, cutscenes, Skyrim-style giant structures, and
**the Rift** — a floating-island dimension where the magic plane collides with the Overworld.

**Requires:** Minecraft 1.21.1, Fabric Loader 0.16.14+, Fabric API 0.116.9+1.21.1, Java 21.

## Building with GitHub Actions
1. Create a new GitHub repository and push this folder to it (`git init`, `git add .`, `git commit`, `git push`).
2. Open the **Actions** tab. The *Build Realmbreak* workflow runs on every push (or press *Run workflow*).
3. When it finishes, open the run and download the **realmbreak-mod** artifact. Unzip it and drop
   `realmbreak-1.0.0.jar` into your `mods/` folder together with Fabric API.
4. Pushing a tag like `v1.0.0` also attaches the jar to a GitHub Release.

> This project was authored without being able to compile it in the authoring environment.
> If the build fails, copy the first error from the Actions log back to Claude and it will be fixed.

## Playing
- You start with a **Riftwalker's Journal** and a **Seeker's Compass** (point it at your current objective; hold it to see the distance).
- **J** quest log · **K** skill trees · **V** cycle staff spell (hold a staff, right-click to cast) · **Backspace** skips a cutscene.
- Find **Wayfarer's Camps** in the Overworld: Maera (Rift Sage), Brannoch (smith), Quill (merchant).
- Questline 1 quest 2 (*Through the Scar*) takes you through a **Rift Scar** gate into the Rift. Every later questline sends you through it again.
- Touch **Landmark Stones** at structures to attune (quest objectives). Each dungeon ends at a **Boss Altar**:
  place the matching **Sigil** on it (earned during the questline), watch the cutscene, and fight.
- A **Rift Anchor** opens a gate home (or back to the Rift) anywhere there's room.

### Questlines (6 quests each)
| # | Line | Giver | Dungeon | Boss |
|---|------|-------|---------|------|
| 1 | The Ember Crown | Maera → Kaelen | Cinderhold Citadel | Ignarax, the Cinder Tyrant |
| 2 | The Frozen Regent | Seraphine | Frostspire Vault | Hrimgar |
| 3 | The Tempest Queen | Vaelor | Stormwatch Aerie | Zephyra |
| 4 | The Thornmother | Elowen | Elderroot Sanctum | Sylvara |
| 5 | The Hollow Star | Ysmera | Hollow Observatory | Nyxoth |

Lines 2–5 unlock after *Through the Scar*. Quest ids are `l1q1` … `l5q6`.

### Magic
Five elements — Flame, Frost, Storm, Verdant, Void — each with a 6-node skill tree (spells, stats, passives).
Skill points come from quests and bosses. Elemental armour sets grant set bonuses.

## Commands (op)
`/realmbreak rift` · `kit` · `points <n>` · `quest <id>` · `boss <id>` · `cutscene <id>`

## Project layout
- `src/main/java`, `src/client/java` — mod code.
- `src/main/resources` — all generated assets, worldgen JSON, structures (NBT), textures, lang, plus
  `realmbreak_content.json` and `realmbreak_story.json` which drive items, mobs, quests, dialogue and cutscenes.
- `tools/` — the Python generators that produced the textures, structures and JSON
  (`manifest.py` and `story.py` are the sources of truth; run with `PYTHONPATH=tools`).
