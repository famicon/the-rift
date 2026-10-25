package com.realmbreak;

import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;

public final class ModParticles {
    public static SimpleParticleType RIFT_MOTE, EMBER_SPARK, FROST_FLAKE, STORM_SPARK, LEAF_WISP, VOID_WISP;

    private ModParticles() {}

    public static void register() {
        RIFT_MOTE = reg("rift_mote");
        EMBER_SPARK = reg("ember_spark");
        FROST_FLAKE = reg("frost_flake");
        STORM_SPARK = reg("storm_spark");
        LEAF_WISP = reg("leaf_wisp");
        VOID_WISP = reg("void_wisp");
    }

    private static SimpleParticleType reg(String id) {
        return Registry.register(BuiltInRegistries.PARTICLE_TYPE, Content.id(id), FabricParticleTypes.simple());
    }

    public static SimpleParticleType byElement(String element) {
        switch (element) {
            case "flame": return EMBER_SPARK;
            case "frost": return FROST_FLAKE;
            case "storm": return STORM_SPARK;
            case "verdant": return LEAF_WISP;
            case "void": return VOID_WISP;
            default: return RIFT_MOTE;
        }
    }
}
