package com.realmbreak.net;

import com.realmbreak.Content;
import com.realmbreak.data.PData;
import com.realmbreak.magic.Magic;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;

public final class Net {
    private Net() {}

    public static void registerPayloads() {
        PayloadTypeRegistry.playS2C().register(DataPayload.TYPE, DataPayload.CODEC);
        PayloadTypeRegistry.playC2S().register(DataPayload.TYPE, DataPayload.CODEC);
    }

    public static void send(ServerPlayer p, String channel, CompoundTag tag) {
        ServerPlayNetworking.send(p, new DataPayload(channel, tag));
    }

    /** Full state sync used by the quest log, skill tree and HUD. */
    public static void sync(ServerPlayer p) {
        PData d = PData.of(p);
        CompoundTag t = new CompoundTag();
        t.putInt("mana", (int) d.mana());
        t.putInt("maxMana", (int) Magic.maxMana(d));
        t.putInt("points", d.points());
        t.putInt("sel", d.sel());
        t.put("skills", d.tag.getList("skills", Tag.TAG_STRING).copy());
        t.put("sites", d.tag.getList("sites", Tag.TAG_STRING).copy());
        t.put("quests", d.quests().copy());
        send(p, "sync", t);
    }
}
