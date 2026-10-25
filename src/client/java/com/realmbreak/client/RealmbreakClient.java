package com.realmbreak.client;

import com.realmbreak.ModBlocks;
import com.realmbreak.ModItems;
import com.realmbreak.ModParticles;
import com.realmbreak.net.DataPayload;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
import net.fabricmc.fabric.api.blockrenderlayer.v1.BlockRenderLayerMap;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.Minecraft;
import net.minecraft.client.particle.EndRodParticle;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public class RealmbreakClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientKeys.register();
        Renderers.register();

        ParticleFactoryRegistry pf = ParticleFactoryRegistry.getInstance();
        pf.register(ModParticles.RIFT_MOTE, EndRodParticle.Provider::new);
        pf.register(ModParticles.EMBER_SPARK, EndRodParticle.Provider::new);
        pf.register(ModParticles.FROST_FLAKE, EndRodParticle.Provider::new);
        pf.register(ModParticles.STORM_SPARK, EndRodParticle.Provider::new);
        pf.register(ModParticles.LEAF_WISP, EndRodParticle.Provider::new);
        pf.register(ModParticles.VOID_WISP, EndRodParticle.Provider::new);

        BlockRenderLayerMap.INSTANCE.putBlock(ModBlocks.state("glow_bloom").getBlock(), RenderType.cutout());
        BlockRenderLayerMap.INSTANCE.putBlock(ModBlocks.state("glimmerwood_leaves").getBlock(), RenderType.cutoutMipped());
        BlockRenderLayerMap.INSTANCE.putBlock(ModBlocks.state("rift_portal").getBlock(), RenderType.translucent());

        for (Item item : ModItems.ITEMS.values()) {
            if (item instanceof ModItems.ElementBow) {
                ItemProperties.register(item, ResourceLocation.withDefaultNamespace("pull"), (stack, level, entity, seed) -> {
                    if (entity == null || entity.getUseItem() != stack) return 0.0F;
                    return (stack.getUseDuration(entity) - entity.getUseItemRemainingTicks()) / 20.0F;
                });
                ItemProperties.register(item, ResourceLocation.withDefaultNamespace("pulling"),
                        (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack ? 1.0F : 0.0F);
            }
        }

        ClientPlayNetworking.registerGlobalReceiver(DataPayload.TYPE, (payload, ctx) -> {
            Minecraft mc = ctx.client();
            CompoundTag t = payload.tag();
            mc.execute(() -> handle(mc, payload.channel(), t));
        });

        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            CutscenePlayer.tick();
            if (mc.player == null) return;
            while (ClientKeys.QUEST_LOG.consumeClick()) if (mc.screen == null) mc.setScreen(new QuestLogScreen());
            while (ClientKeys.SKILLS.consumeClick()) if (mc.screen == null) mc.setScreen(new SkillScreen());
            while (ClientKeys.CYCLE.consumeClick()) ClientPlayNetworking.send(new DataPayload("cycle", new CompoundTag()));
        });
        ClientPlayConnectionEvents.JOIN.register((h, s, mc) -> {
            ClientState.sync = new CompoundTag();
            ClientState.compassValid = false;
            ClientPlayNetworking.send(new DataPayload("request_sync", new CompoundTag()));
        });
        ClientPlayConnectionEvents.DISCONNECT.register((h, mc) -> CutscenePlayer.stop());
        HudRenderCallback.EVENT.register(Hud::render);
    }

    private static void handle(Minecraft mc, String ch, CompoundTag t) {
        switch (ch) {
            case "sync" -> {
                ClientState.sync = t;
                ClientState.mana = t.getInt("mana");
                ClientState.maxMana = Math.max(1, t.getInt("maxMana"));
            }
            case "mana" -> {
                ClientState.mana = t.getInt("mana");
                ClientState.maxMana = Math.max(1, t.getInt("max"));
            }
            case "compass_target" -> {
                ClientState.compassTarget = t.getString("target");
                ClientState.compassValid = false;
            }
            case "compass" -> {
                ClientState.compassName = t.getString("name");
                ClientState.compassX = t.getInt("x");
                ClientState.compassZ = t.getInt("z");
                ClientState.compassValid = true;
            }
            case "dialogue" -> mc.setScreen(new DialogueScreen(t));
            case "cutscene" -> CutscenePlayer.start(t);
            case "open_log" -> mc.setScreen(new QuestLogScreen());
            default -> {
            }
        }
    }
}
