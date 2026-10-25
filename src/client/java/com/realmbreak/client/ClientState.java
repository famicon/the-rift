package com.realmbreak.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.util.ArrayList;
import java.util.List;

/** Client mirror of the server's per-player Realmbreak state. */
public final class ClientState {
    public static CompoundTag sync = new CompoundTag();
    public static int mana = 0, maxMana = 100;
    public static String compassTarget = "";
    public static String compassName = "";
    public static int compassX, compassZ;
    public static boolean compassValid = false;

    private ClientState() {}

    public static int points() {
        return sync.getInt("points");
    }

    public static boolean hasSkill(String id) {
        ListTag l = sync.getList("skills", Tag.TAG_STRING);
        for (int i = 0; i < l.size(); i++) if (l.getString(i).equals(id)) return true;
        return false;
    }

    public static int questState(String id) {
        CompoundTag q = sync.getCompound("quests");
        return q.contains(id, Tag.TAG_COMPOUND) ? q.getCompound(id).getInt("st") : -1;
    }

    public static int[] questProg(String id, int n) {
        CompoundTag q = sync.getCompound("quests");
        int[] p = q.contains(id, Tag.TAG_COMPOUND) ? q.getCompound(id).getIntArray("p") : new int[0];
        int[] out = new int[n];
        System.arraycopy(p, 0, out, 0, Math.min(n, p.length));
        return out;
    }

    public static List<JsonObject> quests() {
        List<JsonObject> out = new ArrayList<>();
        JsonArray a = Content.story.getAsJsonArray("quests");
        for (JsonElement e : a) out.add(e.getAsJsonObject());
        return out;
    }

    /** First active quest (for the tracker), or null. */
    public static JsonObject trackedQuest() {
        for (JsonObject q : quests()) {
            int st = questState(q.get("id").getAsString());
            if (st == 0 || st == 1) return q;
        }
        return null;
    }
}
