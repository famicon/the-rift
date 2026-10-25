package com.realmbreak;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.net.Net;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.phys.Vec3;

/** Server side of cutscenes: tells the client to play one and keeps the player safe meanwhile. */
public final class Cutscenes {
    private Cutscenes() {}

    public static int duration(String id) {
        JsonObject cs = Content.story.getAsJsonObject("cutscenes").getAsJsonObject(id);
        if (cs == null) return 0;
        int total = 0;
        for (JsonElement s : cs.getAsJsonArray("shots")) total += s.getAsJsonObject().get("dur").getAsInt();
        return total;
    }

    public static int play(ServerPlayer p, String id, Vec3 anchor) {
        if (id == null || id.isEmpty()) return 0;
        int total = duration(id);
        if (total <= 0) return 0;
        CompoundTag t = new CompoundTag();
        t.putString("id", id);
        t.putDouble("ax", anchor.x);
        t.putDouble("ay", anchor.y);
        t.putDouble("az", anchor.z);
        Net.send(p, "cutscene", t);
        p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, total + 30, 4, false, false));
        p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, total + 10, 6, false, false));
        return total;
    }

    public static int playNear(ServerLevel level, Vec3 anchor, double radius, String id) {
        int total = 0;
        for (ServerPlayer p : level.players()) {
            if (p.position().distanceTo(anchor) <= radius) total = Math.max(total, play(p, id, anchor));
        }
        return total;
    }
}
