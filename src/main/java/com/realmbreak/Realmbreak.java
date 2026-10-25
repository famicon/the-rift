package com.realmbreak;

import com.realmbreak.world.ModFeatures;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Realmbreak implements ModInitializer {
    public static final String MOD_ID = "realmbreak";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
    public static CreativeModeTab TAB;

    @Override
    public void onInitialize() {
        Content.load();
        ModBlocks.register();
        ModItems.register();
        ModParticles.register();
        ModEntities.register();
        ModFeatures.register();

        TAB = Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, Content.id("main"),
                FabricItemGroup.builder()
                        .title(Component.translatable("itemGroup.realmbreak"))
                        .icon(() -> new ItemStack(ModItems.get("rift_shard")))
                        .displayItems((params, out) -> {
                            for (Item i : ModItems.ITEMS.values()) out.accept(i);
                            for (Item i : ModBlocks.BLOCK_ITEMS.values()) out.accept(i);
                        })
                        .build());

        Events.register();
        RealmCommands.register();

        for (String f : new String[]{"overworld_obelisk", "overworld_rock_spire", "overworld_islet"}) {
            if (Realmbreak.class.getResource("/data/" + MOD_ID + "/worldgen/placed_feature/" + f + ".json") == null) {
                LOGGER.warn("Realmbreak: placed feature '{}' is missing from the mod jar (incomplete upload?); skipping it.", f);
                continue;
            }
            BiomeModifications.addFeature(BiomeSelectors.foundInOverworld(), GenerationStep.Decoration.SURFACE_STRUCTURES,
                    ResourceKey.create(Registries.PLACED_FEATURE, Content.id(f)));
        }
        LOGGER.info("Realmbreak loaded: {} items, {} blocks", ModItems.ITEMS.size(), ModBlocks.BLOCKS.size());
    }
}
