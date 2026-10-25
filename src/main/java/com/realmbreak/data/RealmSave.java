package com.realmbreak.data;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** World-level storage for every player's Realmbreak progress. */
public class RealmSave extends SavedData {
    public static final String ID = "realmbreak_players";
    public final Map<UUID, CompoundTag> players = new HashMap<>();

    public static RealmSave get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<RealmSave>(RealmSave::new, RealmSave::load, null), ID);
    }

    public static RealmSave load(CompoundTag tag, HolderLookup.Provider provider) {
        RealmSave save = new RealmSave();
        CompoundTag pl = tag.getCompound("players");
        for (String key : pl.getAllKeys()) {
            try {
                save.players.put(UUID.fromString(key), pl.getCompound(key));
            } catch (IllegalArgumentException ignored) {
            }
        }
        return save;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider provider) {
        CompoundTag pl = new CompoundTag();
        for (Map.Entry<UUID, CompoundTag> e : players.entrySet()) {
            pl.put(e.getKey().toString(), e.getValue());
        }
        tag.put("players", pl);
        return tag;
    }
}
