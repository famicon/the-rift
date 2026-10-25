package com.realmbreak;

import com.realmbreak.data.PData;
import com.realmbreak.entity.RiftBoss;
import com.realmbreak.magic.Magic;
import com.realmbreak.net.DataPayload;
import com.realmbreak.net.Net;
import com.realmbreak.quest.Dialogues;
import com.realmbreak.quest.Quests;
import net.fabricmc.fabric.api.entity.event.v1.ServerEntityWorldChangeEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public final class Events {
    /** arrows fired by element bows: arrow uuid -> element (+ "!" suffix for the storm bow) */
    private static final Map<UUID, String> ARROWS = new HashMap<>();

    private Events() {}

    public static void register() {
        Net.registerPayloads();
        ServerPlayNetworking.registerGlobalReceiver(DataPayload.TYPE, (payload, context) -> {
            ServerPlayer p = context.player();
            context.server().execute(() -> handleC2S(p, payload));
        });

        ServerTickEvents.END_SERVER_TICK.register(server -> {
            Scheduler.tick();
            for (ServerPlayer p : server.getPlayerList().getPlayers()) {
                Magic.tickPlayer(p);
                if (p.tickCount % 20 == 0) Quests.recheck(p);
            }
        });

        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
            ServerPlayer p = handler.getPlayer();
            PData d = PData.of(p);
            if (!d.flag("kit")) {
                d.setFlag("kit", true);
                Quests.giveItem(p, item("quest_journal", 1));
                Quests.giveItem(p, item("seekers_compass", 1));
                p.sendSystemMessage(Component.literal("Welcome to Realmbreak. Use your Seeker's Compass to find Wayfarer's Camp and speak to Maera. Press J for your journal, K for skills, V to cycle staff spells.").withStyle(ChatFormatting.GOLD));
            }
            Net.sync(p);
            Quests.pointCompassQuiet(p);
        });
        ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> Magic.forget(handler.getPlayer().getUUID()));

        ServerLifecycleEvents.SERVER_STOPPING.register(server -> Scheduler.clear());

        ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
            if (entity instanceof RiftBoss boss && entity.level() instanceof ServerLevel sl) {
                Quests.notifyBossKill(sl, boss);
                return;
            }
            Entity killer = source.getEntity();
            if (killer instanceof ServerPlayer sp) Quests.onKill(sp, entity);
        });

        ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) -> {
            if (entity instanceof ServerPlayer sp && !(source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY))) {
                if (Magic.hasPassive(PData.of(sp), "evade") && sp.getRandom().nextFloat() < 0.12f) {
                    sp.displayClientMessage(Component.literal("You slip between the shadows.").withStyle(ChatFormatting.DARK_PURPLE), true);
                    return false;
                }
            }
            if (source.getDirectEntity() instanceof AbstractArrow arrow) {
                String tag = ARROWS.remove(arrow.getUUID());
                if (tag != null && entity.level() instanceof ServerLevel sl && source.getEntity() instanceof ServerPlayer owner) {
                    boolean storm = tag.endsWith("!");
                    String el = storm ? tag.substring(0, tag.length() - 1) : tag;
                    if (!el.isEmpty()) Magic.rider(el, entity);
                    if (storm) {
                        Vec3 c = entity.position();
                        Magic.lightning(sl, c);
                        for (LivingEntity e : Magic.around(sl, c, 3.5, x -> Magic.validTarget(x, owner) && x != entity)) {
                            e.hurt(owner.damageSources().indirectMagic(owner, owner), 6.0f);
                        }
                    }
                }
            }
            return true;
        });

        ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
            if (entity instanceof AbstractArrow arrow && arrow.getOwner() instanceof ServerPlayer sp) {
                ItemStack held = sp.getMainHandItem().getItem() instanceof ModItems.ElementBow ? sp.getMainHandItem() : sp.getOffhandItem();
                if (held.getItem() instanceof ModItems.ElementBow bow) {
                    arrow.setBaseDamage(arrow.getBaseDamage() + bow.bonus);
                    if (ARROWS.size() > 600) ARROWS.clear();
                    ARROWS.put(arrow.getUUID(), bow.element + (bow.stormcaller ? "!" : ""));
                    if (bow.element.equals("flame")) arrow.igniteForSeconds(100);
                }
            }
        });

        AttackEntityCallback.EVENT.register((player, world, hand, entity, hit) -> {
            if (!world.isClientSide && player instanceof ServerPlayer sp && entity instanceof LivingEntity le) {
                PData d = PData.of(sp);
                if (Magic.hasPassive(d, "ignite")) le.igniteForSeconds(3);
                if (Magic.hasPassive(d, "chill")) Magic.rider("frost", le);
            }
            return InteractionResult.PASS;
        });

        ServerEntityWorldChangeEvents.AFTER_PLAYER_CHANGE_WORLD.register((player, origin, destination) -> Quests.recheck(player));
    }

    private static com.google.gson.JsonObject item(String id, int n) {
        com.google.gson.JsonObject o = new com.google.gson.JsonObject();
        o.addProperty("id", id);
        o.addProperty("count", n);
        return o;
    }

    private static void handleC2S(ServerPlayer p, DataPayload payload) {
        CompoundTag t = payload.tag();
        switch (payload.channel()) {
            case "dialogue" -> Dialogues.handle(p, t);
            case "unlock" -> Magic.unlock(p, t.getString("id"));
            case "cycle" -> Magic.cycle(p);
            case "request_sync" -> Net.sync(p);
            default -> {
            }
        }
    }
}
