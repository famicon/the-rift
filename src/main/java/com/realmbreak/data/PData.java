package com.realmbreak.data;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;

/** Convenient view over one player's persistent Realmbreak data. */
public final class PData {
    public final CompoundTag tag;
    private final RealmSave save;

    private PData(RealmSave save, CompoundTag tag) {
        this.save = save;
        this.tag = tag;
    }

    public static PData of(ServerPlayer p) {
        RealmSave save = RealmSave.get(p.getServer());
        CompoundTag t = save.players.computeIfAbsent(p.getUUID(), k -> new CompoundTag());
        return new PData(save, t);
    }

    public void dirty() {
        save.setDirty();
    }

    // ---- mana
    public double mana() {
        return tag.contains("mana") ? tag.getDouble("mana") : 60.0;
    }

    public void setMana(double v) {
        tag.putDouble("mana", v);
    }

    // ---- skill points / skills
    public int points() {
        return tag.getInt("points");
    }

    public void addPoints(int n) {
        tag.putInt("points", Math.max(0, points() + n));
        dirty();
    }

    public boolean hasSkill(String id) {
        ListTag l = tag.getList("skills", Tag.TAG_STRING);
        for (int i = 0; i < l.size(); i++) if (l.getString(i).equals(id)) return true;
        return false;
    }

    public void addSkill(String id) {
        if (hasSkill(id)) return;
        ListTag l = tag.getList("skills", Tag.TAG_STRING);
        l.add(StringTag.valueOf(id));
        tag.put("skills", l);
        dirty();
    }

    // ---- selected spell index
    public int sel() {
        return tag.getInt("sel");
    }

    public void setSel(int v) {
        tag.putInt("sel", v);
    }

    // ---- sites
    public boolean hasSite(int site) {
        ListTag l = tag.getList("sites", Tag.TAG_STRING);
        String s = Integer.toString(site);
        for (int i = 0; i < l.size(); i++) if (l.getString(i).equals(s)) return true;
        return false;
    }

    public void addSite(int site) {
        if (hasSite(site)) return;
        ListTag l = tag.getList("sites", Tag.TAG_STRING);
        l.add(StringTag.valueOf(Integer.toString(site)));
        tag.put("sites", l);
        dirty();
    }

    // ---- quests: {qid: {st:int, p:int[]}}
    public CompoundTag quests() {
        if (!tag.contains("quests", Tag.TAG_COMPOUND)) tag.put("quests", new CompoundTag());
        return tag.getCompound("quests");
    }

    // ---- flags
    public boolean flag(String key) {
        return tag.getBoolean("f_" + key);
    }

    public void setFlag(String key, boolean v) {
        tag.putBoolean("f_" + key, v);
        dirty();
    }
}
