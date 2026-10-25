package com.realmbreak;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.entity.ElementalMob;
import com.realmbreak.entity.ElementalSpider;
import com.realmbreak.entity.QuestNpcEntity;
import com.realmbreak.entity.RiftBoss;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.LinkedHashMap;
import java.util.Map;

public final class ModEntities {
    public static EntityType<QuestNpcEntity> QUEST_NPC;
    public static final Map<String, EntityType<?>> TYPES = new LinkedHashMap<>();

    private ModEntities() {}

    @SuppressWarnings("unchecked")
    public static void register() {
        QUEST_NPC = Registry.register(BuiltInRegistries.ENTITY_TYPE, Content.id("quest_npc"),
                EntityType.Builder.<QuestNpcEntity>of(QuestNpcEntity::new, MobCategory.MISC).sized(0.6f, 1.95f).clientTrackingRange(10).build("quest_npc"));
        FabricDefaultAttributeRegistry.register(QUEST_NPC, QuestNpcEntity.createAttributes());
        TYPES.put("quest_npc", QUEST_NPC);

        for (JsonElement el : Content.content.getAsJsonArray("mobs")) {
            JsonObject m = el.getAsJsonObject();
            String id = m.get("id").getAsString();
            String style = Content.str(m, "style", "knight");
            if (style.equals("spider")) {
                EntityType<ElementalSpider> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, Content.id(id),
                        EntityType.Builder.<ElementalSpider>of(ElementalSpider::new, MobCategory.MONSTER).sized(1.2f, 0.8f).clientTrackingRange(8).build(id));
                FabricDefaultAttributeRegistry.register(t, ElementalSpider.createAttributes());
                SpawnPlacements.register(t, SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                        (type, level, spawnType, pos, random) -> Mob.checkMobSpawnRules(type, level, spawnType, pos, random));
                TYPES.put(id, t);
            } else {
                EntityType<ElementalMob> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, Content.id(id),
                        EntityType.Builder.<ElementalMob>of(ElementalMob::new, MobCategory.MONSTER).sized(0.6f, 1.95f).clientTrackingRange(8).build(id));
                FabricDefaultAttributeRegistry.register(t, ElementalMob.createAttributes());
                SpawnPlacements.register(t, SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                        (type, level, spawnType, pos, random) -> Mob.checkMobSpawnRules(type, level, spawnType, pos, random));
                TYPES.put(id, t);
            }
        }
        for (JsonElement el : Content.content.getAsJsonArray("bosses")) {
            JsonObject b = el.getAsJsonObject();
            String id = b.get("id").getAsString();
            EntityType<RiftBoss> t = Registry.register(BuiltInRegistries.ENTITY_TYPE, Content.id(id),
                    EntityType.Builder.<RiftBoss>of(RiftBoss::new, MobCategory.MONSTER).sized(1.2f, 3.6f).clientTrackingRange(16).fireImmune().build(id));
            FabricDefaultAttributeRegistry.register(t, RiftBoss.createAttributes());
            TYPES.put(id, t);
        }
    }
}
