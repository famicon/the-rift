package com.realmbreak.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.realmbreak.Content;
import com.realmbreak.ModEntities;
import com.realmbreak.entity.ElementalSpider;
import com.realmbreak.entity.QuestNpcEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.SpiderModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

import java.util.Map;

/** Player-skin style humanoid renderer used for NPCs, mobs and (scaled up) bosses. */
public final class Renderers {
    private Renderers() {}

    public static class Humanoid<T extends Mob> extends MobRenderer<T, PlayerModel<T>> {
        private final float scale;
        private final java.util.function.Function<T, ResourceLocation> tex;

        public Humanoid(EntityRendererProvider.Context ctx, float scale, java.util.function.Function<T, ResourceLocation> tex) {
            super(ctx, new PlayerModel<>(ctx.bakeLayer(ModelLayers.PLAYER), false), 0.5f * scale);
            this.scale = scale;
            this.tex = tex;
            this.addLayer(new ItemInHandLayer<>(this, ctx.getItemInHandRenderer()));
        }

        @Override
        public ResourceLocation getTextureLocation(T entity) {
            return tex.apply(entity);
        }

        @Override
        protected void scale(T entity, PoseStack pose, float partial) {
            pose.scale(scale, scale, scale);
        }
    }

    public static class Spider extends MobRenderer<ElementalSpider, SpiderModel<ElementalSpider>> {
        private final ResourceLocation texture;

        public Spider(EntityRendererProvider.Context ctx, ResourceLocation texture) {
            super(ctx, new SpiderModel<>(ctx.bakeLayer(ModelLayers.SPIDER)), 0.8f);
            this.texture = texture;
        }

        @Override
        public ResourceLocation getTextureLocation(ElementalSpider entity) {
            return texture;
        }
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    public static void register() {
        EntityRendererRegistry.register(ModEntities.QUEST_NPC, ctx -> new Humanoid<QuestNpcEntity>(ctx, 1.0f,
                e -> Content.id("textures/entity/npc/" + e.npcId() + ".png")));
        for (Map.Entry<String, EntityType<?>> en : ModEntities.TYPES.entrySet()) {
            String id = en.getKey();
            if (id.equals("quest_npc")) continue;
            EntityType type = en.getValue();
            ResourceLocation tex = Content.id("textures/entity/" + id + ".png");
            boolean boss = false;
            for (var b : Content.content.getAsJsonArray("bosses")) if (b.getAsJsonObject().get("id").getAsString().equals(id)) boss = true;
            boolean spider = Content.MOBS.containsKey(id) && "spider".equals(Content.str(Content.MOBS.get(id), "style", ""));
            if (spider) {
                EntityRendererRegistry.register(type, ctx -> new Spider(ctx, tex));
            } else {
                final float sc = boss ? 1.8f : 1.0f;
                EntityRendererRegistry.register(type, ctx -> new Humanoid<Mob>(ctx, sc, e -> tex));
            }
        }
    }
}
