package com.realmbreak.quest;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.ModItems;
import com.realmbreak.data.PData;
import com.realmbreak.entity.QuestNpcEntity;
import com.realmbreak.net.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/** Server-driven NPC conversations. The client only renders what it is sent and returns button ids. */
public final class Dialogues {
    private Dialogues() {}

    private static void send(ServerPlayer p, String npc, List<String> lines, List<String[]> buttons) {
        CompoundTag t = new CompoundTag();
        t.putString("npc", npc);
        JsonObject n = Content.NPCS.get(npc);
        t.putString("name", n == null ? npc : Content.str(n, "name", npc));
        t.putString("title", n == null ? "" : Content.str(n, "title", ""));
        ListTag ll = new ListTag();
        for (String s : lines) ll.add(StringTag.valueOf(s));
        t.put("lines", ll);
        ListTag bl = new ListTag();
        for (String[] b : buttons) {
            CompoundTag bt = new CompoundTag();
            bt.putString("id", b[0]);
            bt.putString("label", b[1]);
            bl.add(bt);
        }
        t.put("buttons", bl);
        Net.send(p, "dialogue", t);
    }

    private static List<String> strs(JsonArray a) {
        List<String> out = new ArrayList<>();
        for (JsonElement e : a) out.add(e.getAsString());
        return out;
    }

    private static boolean hasTrades(String npc) {
        JsonObject n = Content.story.getAsJsonObject("npcs").getAsJsonObject(npc);
        return n != null && n.getAsJsonArray("trades").size() > 0;
    }

    private static List<String[]> closeAndTrade(String npc) {
        List<String[]> b = new ArrayList<>();
        if (hasTrades(npc)) b.add(new String[]{"trade", "Trade"});
        b.add(new String[]{"close", "Farewell"});
        return b;
    }

    public static void open(ServerPlayer p, String npc) {
        PData d = PData.of(p);
        // talk objectives first (they may complete a quest, which we then offer to turn in immediately)
        List<String> talkLines = Quests.onTalk(p, npc);
        // 1. ready quests to turn in here
        for (JsonObject q : Quests.all()) {
            String id = q.get("id").getAsString();
            if (Quests.state(d, id) == 1 && Content.str(q, "turnin", "").equals(npc)) {
                List<String> lines = new ArrayList<>(strs(q.getAsJsonArray("done")));
                List<String[]> b = new ArrayList<>();
                b.add(new String[]{"complete:" + id, "Complete: " + Content.str(q, "title", id)});
                send(p, npc, lines, b);
                return;
            }
        }
        if (!talkLines.isEmpty()) {
            send(p, npc, talkLines, closeAndTrade(npc));
            return;
        }
        // 2. offers
        List<JsonObject> offers = Quests.offersFor(d, npc);
        if (!offers.isEmpty()) {
            JsonObject q = offers.get(0);
            String id = q.get("id").getAsString();
            List<String[]> b = new ArrayList<>();
            b.add(new String[]{"accept:" + id, "Accept: " + Content.str(q, "title", id)});
            b.add(new String[]{"close", "Not now"});
            send(p, npc, strs(q.getAsJsonArray("offer")), b);
            return;
        }
        // 3. active quest hints involving this npc
        for (JsonObject q : Quests.all()) {
            String id = q.get("id").getAsString();
            if (Quests.state(d, id) == 0 && (Content.str(q, "giver", "").equals(npc) || Content.str(q, "turnin", "").equals(npc))) {
                send(p, npc, strs(q.getAsJsonArray("progress")), closeAndTrade(npc));
                return;
            }
        }
        // 4. idle chatter
        JsonObject n = Content.story.getAsJsonObject("npcs").getAsJsonObject(npc);
        List<String> lines = n == null ? List.of("...") : strs(n.getAsJsonArray("lines"));
        send(p, npc, lines, closeAndTrade(npc));
    }

    private static boolean npcNearby(ServerPlayer p, String npc) {
        return !p.serverLevel().getEntitiesOfClass(QuestNpcEntity.class, p.getBoundingBox().inflate(10), n -> n.npcId().equals(npc)).isEmpty();
    }

    public static void handle(ServerPlayer p, CompoundTag tag) {
        String npc = tag.getString("npc");
        String act = tag.getString("act");
        if (!npcNearby(p, npc)) return;
        if (act.equals("close")) return;
        if (act.startsWith("accept:")) {
            JsonObject q = Quests.quest(act.substring(7));
            PData d = PData.of(p);
            if (q != null && Quests.state(d, q.get("id").getAsString()) == -1 && Quests.requirementMet(d, q) && Content.str(q, "giver", "").equals(npc)) {
                Quests.start(p, q);
                send(p, npc, strs(q.getAsJsonArray("progress")), closeAndTrade(npc));
            }
            return;
        }
        if (act.startsWith("complete:")) {
            if (Quests.complete(p, act.substring(9))) {
                // any follow-up from the same npc?
                open(p, npc);
            }
            return;
        }
        if (act.equals("trade")) {
            sendTrades(p, npc);
            return;
        }
        if (act.startsWith("buy:")) {
            int idx;
            try {
                idx = Integer.parseInt(act.substring(4));
            } catch (NumberFormatException e) {
                return;
            }
            buy(p, npc, idx);
            sendTrades(p, npc);
        }
    }

    private static String describe(JsonObject stack) {
        ItemStack s = new ItemStack(ModItems.get(stack.get("id").getAsString()), stack.get("count").getAsInt());
        return stack.get("count").getAsInt() + "x " + s.getHoverName().getString();
    }

    private static void sendTrades(ServerPlayer p, String npc) {
        JsonObject n = Content.story.getAsJsonObject("npcs").getAsJsonObject(npc);
        List<String[]> buttons = new ArrayList<>();
        JsonArray trades = n.getAsJsonArray("trades");
        for (int i = 0; i < trades.size(); i++) {
            JsonObject t = trades.get(i).getAsJsonObject();
            StringBuilder cost = new StringBuilder();
            for (JsonElement c : t.getAsJsonArray("cost")) {
                if (cost.length() > 0) cost.append(" + ");
                cost.append(describe(c.getAsJsonObject()));
            }
            buttons.add(new String[]{"buy:" + i, cost + "  ->  " + describe(t.getAsJsonObject("result"))});
        }
        buttons.add(new String[]{"close", "Done"});
        send(p, npc, List.of("What are you buying?"), buttons);
    }

    private static void buy(ServerPlayer p, String npc, int idx) {
        JsonObject n = Content.story.getAsJsonObject("npcs").getAsJsonObject(npc);
        JsonArray trades = n.getAsJsonArray("trades");
        if (idx < 0 || idx >= trades.size()) return;
        JsonObject t = trades.get(idx).getAsJsonObject();
        for (JsonElement c : t.getAsJsonArray("cost")) {
            JsonObject co = c.getAsJsonObject();
            if (Quests.countItem(p, co.get("id").getAsString()) < co.get("count").getAsInt()) {
                p.displayClientMessage(Component.literal("You cannot afford that.").withStyle(ChatFormatting.RED), true);
                return;
            }
        }
        for (JsonElement c : t.getAsJsonArray("cost")) {
            JsonObject co = c.getAsJsonObject();
            int left = co.get("count").getAsInt();
            var item = ModItems.get(co.get("id").getAsString());
            for (ItemStack s : p.getInventory().items) {
                if (left <= 0) break;
                if (s.getItem() == item) {
                    int take = Math.min(left, s.getCount());
                    s.shrink(take);
                    left -= take;
                }
            }
        }
        Quests.giveItem(p, t.getAsJsonObject("result"));
        p.displayClientMessage(Component.literal("Trade complete.").withStyle(ChatFormatting.GREEN), true);
        Quests.recheck(p);
    }
}
