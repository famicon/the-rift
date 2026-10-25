package com.realmbreak.quest;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.Cutscenes;
import com.realmbreak.ModItems;
import com.realmbreak.RiftTravel;
import com.realmbreak.data.PData;
import com.realmbreak.entity.RiftBoss;
import com.realmbreak.net.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Quest state machine. State per quest: 0 = active, 1 = ready to turn in, 2 = done. */
public final class Quests {
    public static final Set<String> RIFT_STRUCTS = new HashSet<>(List.of("altar_of_flame", "altar_of_frost", "altar_of_storm", "altar_of_verdant", "altar_of_void",
            "crystal_cathedral", "fallen_keep", "rift_monolith", "sky_bridge", "hollow_observatory"));

    private Quests() {}

    public static JsonObject quest(String id) {
        return Content.QUESTS.get(id);
    }

    public static List<JsonObject> all() {
        List<JsonObject> out = new ArrayList<>();
        for (JsonElement e : Content.story.getAsJsonArray("quests")) out.add(e.getAsJsonObject());
        return out;
    }

    public static int state(PData d, String qid) {
        CompoundTag q = d.quests();
        return q.contains(qid, 10) ? q.getCompound(qid).getInt("st") : -1;
    }

    public static int[] prog(PData d, String qid, int n) {
        CompoundTag q = d.quests();
        int[] p = q.contains(qid, 10) ? q.getCompound(qid).getIntArray("p") : new int[0];
        if (p.length != n) {
            int[] np = new int[n];
            System.arraycopy(p, 0, np, 0, Math.min(p.length, n));
            return np;
        }
        return p;
    }

    private static void store(PData d, String qid, int st, int[] p) {
        CompoundTag e = new CompoundTag();
        e.putInt("st", st);
        e.putIntArray("p", p);
        d.quests().put(qid, e);
        d.dirty();
    }

    public static boolean requirementMet(PData d, JsonObject q) {
        String req = Content.str(q, "requires", "");
        return req.isEmpty() || state(d, req) == 2;
    }

    public static List<JsonObject> offersFor(PData d, String npc) {
        List<JsonObject> out = new ArrayList<>();
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) == -1 && Content.str(q, "giver", "").equals(npc) && requirementMet(d, q)) out.add(q);
        }
        return out;
    }

    // ------------------------------------------------------------------ lifecycle
    public static void start(ServerPlayer p, JsonObject q) {
        PData d = PData.of(p);
        String id = q.get("id").getAsString();
        JsonArray objs = q.getAsJsonArray("objectives");
        store(d, id, 0, new int[objs.size()]);
        for (JsonElement g : Content.array(q, "give")) giveItem(p, g.getAsJsonObject());
        p.sendSystemMessage(Component.literal("Quest started: ").withStyle(ChatFormatting.GOLD).append(Component.literal(Content.str(q, "title", id)).withStyle(ChatFormatting.YELLOW)));
        p.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 0.8f);
        Cutscenes.play(p, Content.str(q, "start_cs", ""), p.position());
        recheck(p);
        Net.sync(p);
        pointCompassQuiet(p);
    }

    public static void giveItem(ServerPlayer p, JsonObject g) {
        Item it = ModItems.get(g.get("id").getAsString());
        int n = g.get("count").getAsInt();
        ItemStack st = new ItemStack(it, n);
        if (!p.getInventory().add(st)) p.drop(st, false);
    }

    public static int countItem(ServerPlayer p, String id) {
        Item it = ModItems.get(id);
        int n = 0;
        for (ItemStack s : p.getInventory().items) if (s.getItem() == it) n += s.getCount();
        for (ItemStack s : p.getInventory().offhand) if (s.getItem() == it) n += s.getCount();
        return n;
    }

    private static void removeItem(ServerPlayer p, String id, int count) {
        Item it = ModItems.get(id);
        int left = count;
        for (ItemStack s : p.getInventory().items) {
            if (left <= 0) break;
            if (s.getItem() == it) {
                int take = Math.min(left, s.getCount());
                s.shrink(take);
                left -= take;
            }
        }
    }

    public static boolean inRift(ServerPlayer p) {
        return p.level().dimension() == RiftTravel.RIFT;
    }

    /** Recompute derived objectives (collect / rift) and detect completion. Called often; cheap when nothing is active. */
    public static void recheck(ServerPlayer p) {
        PData d = PData.of(p);
        boolean changed = false;
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) != 0) continue;
            JsonArray objs = q.getAsJsonArray("objectives");
            int[] pr = prog(d, id, objs.size());
            boolean all = true;
            for (int i = 0; i < objs.size(); i++) {
                JsonObject o = objs.get(i).getAsJsonObject();
                String type = o.get("type").getAsString();
                int need = Content.num(o, "count", 1);
                int before = pr[i];
                if (type.equals("collect")) {
                    pr[i] = Math.min(need, countItem(p, o.get("target").getAsString()));
                } else if (type.equals("rift")) {
                    if (inRift(p)) pr[i] = 1;
                }
                if (pr[i] != before) changed = true;
                if (pr[i] < need) all = false;
            }
            if (all) {
                store(d, id, 1, pr);
                changed = true;
                p.sendSystemMessage(Component.literal("Quest objectives complete: ").withStyle(ChatFormatting.GREEN)
                        .append(Component.literal(Content.str(q, "title", id)).withStyle(ChatFormatting.YELLOW))
                        .append(Component.literal(" - return to " + Content.npcName(Content.str(q, "turnin", ""))).withStyle(ChatFormatting.GRAY)));
                p.playNotifySound(SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 1f, 0.8f);
            } else if (changed) {
                store(d, id, 0, pr);
            }
        }
        if (changed) {
            Net.sync(p);
            pointCompassQuiet(p);
        }
    }

    private static boolean dimOk(ServerPlayer p, JsonObject o) {
        String dim = Content.str(o, "dim", "");
        if (dim.equals("rift")) return inRift(p);
        return true;
    }

    private static boolean matchesKill(JsonObject o, Entity victim) {
        String t = o.get("target").getAsString();
        if (t.equals("any_hostile")) return victim instanceof Enemy;
        return BuiltInRegistries.ENTITY_TYPE.getKey(victim.getType()).getPath().equals(t);
    }

    public static void onKill(ServerPlayer p, Entity victim) {
        PData d = PData.of(p);
        boolean changed = false;
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) != 0) continue;
            JsonArray objs = q.getAsJsonArray("objectives");
            int[] pr = prog(d, id, objs.size());
            boolean touched = false;
            for (int i = 0; i < objs.size(); i++) {
                JsonObject o = objs.get(i).getAsJsonObject();
                String type = o.get("type").getAsString();
                if (!(type.equals("kill") || type.equals("boss"))) continue;
                int need = Content.num(o, "count", 1);
                if (pr[i] >= need || !dimOk(p, o) || !matchesKill(o, victim)) continue;
                pr[i]++;
                touched = true;
                p.displayClientMessage(Component.literal(Content.str(q, "title", id) + ": " + Content.str(o, "text", "Defeat foes") + " (" + pr[i] + "/" + need + ")").withStyle(ChatFormatting.YELLOW), true);
            }
            if (touched) {
                store(d, id, 0, pr);
                changed = true;
            }
        }
        if (changed) recheck(p);
        if (changed) Net.sync(p);
    }

    public static void onAttune(ServerPlayer p, int site, BlockPos pos) {
        PData d = PData.of(p);
        JsonArray names = Content.content.getAsJsonArray("site_names");
        String name = site >= 0 && site < names.size() ? names.get(site).getAsString() : "a landmark";
        boolean first = !d.hasSite(site);
        d.addSite(site);
        ServerLevel lv = p.serverLevel();
        lv.sendParticles(com.realmbreak.ModParticles.RIFT_MOTE, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 30, 0.5, 0.6, 0.5, 0.05);
        lv.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.5f, 1.0f);
        boolean advanced = false;
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) != 0) continue;
            JsonArray objs = q.getAsJsonArray("objectives");
            int[] pr = prog(d, id, objs.size());
            boolean touched = false;
            for (int i = 0; i < objs.size(); i++) {
                JsonObject o = objs.get(i).getAsJsonObject();
                if (o.get("type").getAsString().equals("attune") && Content.num(o, "site", -1) == site && pr[i] < 1) {
                    pr[i] = 1;
                    touched = true;
                }
            }
            if (touched) {
                store(d, id, 0, pr);
                advanced = true;
            }
        }
        p.sendSystemMessage(Component.literal(first ? "You discover " + name + "." : "You attune to " + name + ".").withStyle(ChatFormatting.LIGHT_PURPLE));
        if (first) p.giveExperiencePoints(25);
        if (advanced) p.sendSystemMessage(Component.literal("The stone hums. Your quest advances.").withStyle(ChatFormatting.GREEN));
        recheck(p);
        Net.sync(p);
    }

    /** A talk objective can complete when the player speaks to the target NPC. Returns true if any advanced. */
    public static List<String> onTalk(ServerPlayer p, String npc) {
        PData d = PData.of(p);
        List<String> talkLines = new ArrayList<>();
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) != 0) continue;
            JsonArray objs = q.getAsJsonArray("objectives");
            int[] pr = prog(d, id, objs.size());
            boolean touched = false;
            for (int i = 0; i < objs.size(); i++) {
                JsonObject o = objs.get(i).getAsJsonObject();
                if (o.get("type").getAsString().equals("talk") && o.get("target").getAsString().equals(npc) && pr[i] < 1) {
                    pr[i] = 1;
                    touched = true;
                }
            }
            if (touched) {
                store(d, id, 0, pr);
                JsonObject tl = Content.story.getAsJsonObject("talk_lines");
                if (tl != null && tl.has(id)) for (JsonElement l : tl.getAsJsonArray(id)) talkLines.add(l.getAsString());
            }
        }
        if (!talkLines.isEmpty() || true) recheck(p);
        Net.sync(p);
        return talkLines;
    }

    /** Debug helper: jump a quest straight to ready and complete it. */
    public static void forceComplete(ServerPlayer p, String qid) {
        JsonObject q = quest(qid);
        if (q == null) return;
        PData d = PData.of(p);
        int n = q.getAsJsonArray("objectives").size();
        int[] pr = new int[n];
        for (int i = 0; i < n; i++) pr[i] = Content.num(q.getAsJsonArray("objectives").get(i).getAsJsonObject(), "count", 1);
        store(d, qid, 2, pr);
        for (JsonElement g : Content.array(q, "give")) giveItem(p, g.getAsJsonObject());
        for (JsonElement g : Content.array(q, "rewards")) giveItem(p, g.getAsJsonObject());
        d.addPoints(Content.num(q, "points", 1));
        recheck(p);
        Net.sync(p);
    }

    public static boolean complete(ServerPlayer p, String qid) {
        PData d = PData.of(p);
        JsonObject q = quest(qid);
        if (q == null || state(d, qid) != 1) return false;
        for (JsonElement e : q.getAsJsonArray("objectives")) {
            JsonObject o = e.getAsJsonObject();
            if (o.get("type").getAsString().equals("collect") && countItem(p, o.get("target").getAsString()) < Content.num(o, "count", 1)) {
                p.sendSystemMessage(Component.literal("You no longer carry everything required.").withStyle(ChatFormatting.RED));
                recheck(p);
                return false;
            }
        }
        for (JsonElement e : q.getAsJsonArray("objectives")) {
            JsonObject o = e.getAsJsonObject();
            if (o.get("type").getAsString().equals("collect")) {
                String item = o.get("target").getAsString();
                if (!item.endsWith("_sigil")) removeItem(p, item, Content.num(o, "count", 1));
            }
        }
        store(d, qid, 2, prog(d, qid, q.getAsJsonArray("objectives").size()));
        for (JsonElement g : Content.array(q, "rewards")) giveItem(p, g.getAsJsonObject());
        int pts = Content.num(q, "points", 1);
        d.addPoints(pts);
        p.giveExperiencePoints(Content.num(q, "xp", 50));
        p.sendSystemMessage(Component.literal("Quest complete: ").withStyle(ChatFormatting.GOLD).append(Component.literal(Content.str(q, "title", qid)).withStyle(ChatFormatting.YELLOW)));
        p.sendSystemMessage(Component.literal("+" + pts + " skill point" + (pts == 1 ? "" : "s") + " (press K)").withStyle(ChatFormatting.AQUA));
        p.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
        String endCs = Content.str(q, "end_cs", "");
        if (!endCs.isEmpty()) Cutscenes.play(p, endCs, p.position());
        // announce newly available lines
        if (qid.equals("l1q2")) {
            p.sendSystemMessage(Component.literal("Four more questlines are now open: find Seraphine, Vaelor, Elowen and Ysmera, or finish Kaelen's.").withStyle(ChatFormatting.LIGHT_PURPLE));
        }
        recheck(p);
        Net.sync(p);
        pointCompassQuiet(p);
        return true;
    }

    // ------------------------------------------------------------------ compass
    /** Structure id the compass should point to, or null. */
    public static String targetStructure(PData d) {
        JsonObject siteStruct = Content.story.getAsJsonObject("site_struct");
        JsonObject bossStruct = Content.story.getAsJsonObject("boss_struct");
        JsonObject npcs = Content.story.getAsJsonObject("npcs");
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            int st = state(d, id);
            if (st == 1) {
                String npc = Content.str(q, "turnin", "");
                if (npcs.has(npc)) return npcs.getAsJsonObject(npc).get("home").getAsString();
            }
            if (st != 0) continue;
            JsonArray objs = q.getAsJsonArray("objectives");
            int[] pr = prog(d, id, objs.size());
            for (int i = 0; i < objs.size(); i++) {
                JsonObject o = objs.get(i).getAsJsonObject();
                if (pr[i] >= Content.num(o, "count", 1)) continue;
                String type = o.get("type").getAsString();
                if (type.equals("attune")) return siteStruct.get(String.valueOf(Content.num(o, "site", 0))).getAsString();
                if (type.equals("talk") && npcs.has(o.get("target").getAsString())) return npcs.getAsJsonObject(o.get("target").getAsString()).get("home").getAsString();
                if (type.equals("boss")) return bossStruct.get(o.get("target").getAsString()).getAsString();
            }
        }
        for (JsonObject q : all()) {
            String id = q.get("id").getAsString();
            if (state(d, id) == -1 && requirementMet(d, q)) {
                String giver = Content.str(q, "giver", "maera");
                if (npcs.has(giver)) return npcs.getAsJsonObject(giver).get("home").getAsString();
            }
        }
        return "wayfarers_camp";
    }

    private static String pretty(String sid) {
        StringBuilder sb = new StringBuilder();
        for (String w : sid.split("_")) {
            if (sb.length() > 0) sb.append(' ');
            sb.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));
        }
        return sb.toString();
    }

    public static void pointCompassQuiet(ServerPlayer p) {
        // lightweight: only tell the client which structure is the current target (no search)
        CompoundTag t = new CompoundTag();
        t.putString("target", pretty(targetStructure(PData.of(p))));
        Net.send(p, "compass_target", t);
    }

    public static void pointCompass(ServerPlayer p) {
        PData d = PData.of(p);
        String sid = targetStructure(d);
        boolean riftTarget = RIFT_STRUCTS.contains(sid);
        if (riftTarget && !inRift(p)) {
            p.displayClientMessage(Component.literal(pretty(sid) + " lies within the Rift. Find a Rift Scar and step through the gate.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
            return;
        }
        if (!riftTarget && inRift(p)) {
            p.displayClientMessage(Component.literal(pretty(sid) + " lies in the overworld. Return through a Rift Gate.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
            return;
        }
        ServerLevel lv = p.serverLevel();
        BlockPos found = lv.findNearestMapStructure(TagKey.create(Registries.STRUCTURE, Content.id(sid)), p.blockPosition(), 64, false);
        if (found == null) {
            p.displayClientMessage(Component.literal("The compass spins: " + pretty(sid) + " is not close. Explore further.").withStyle(ChatFormatting.GRAY), true);
            return;
        }
        CompoundTag t = new CompoundTag();
        t.putString("name", pretty(sid));
        t.putInt("x", found.getX());
        t.putInt("z", found.getZ());
        Net.send(p, "compass", t);
        int dist = (int) Math.sqrt(p.blockPosition().distSqr(new BlockPos(found.getX(), p.getBlockY(), found.getZ())));
        p.displayClientMessage(Component.literal(pretty(sid) + ": " + dist + " blocks away (" + found.getX() + ", " + found.getZ() + ")").withStyle(ChatFormatting.AQUA), true);
    }

    public static void notifyBossKill(ServerLevel level, RiftBoss boss) {
        for (ServerPlayer p : level.players()) {
            if (p.distanceTo(boss) <= 64) onKill(p, boss);
        }
    }

    public static Vec3 anchor(ServerPlayer p) {
        return p.position();
    }
}
