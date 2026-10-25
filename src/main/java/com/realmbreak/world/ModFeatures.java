package com.realmbreak.world;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.realmbreak.Content;
import com.realmbreak.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

/** Custom worldgen features driven by an {"element": "..."} config. */
public final class ModFeatures {
    public record ElementConfig(String element) implements FeatureConfiguration {
        public static final Codec<ElementConfig> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.STRING.fieldOf("element").forGetter(ElementConfig::element)).apply(i, ElementConfig::new));
    }

    private ModFeatures() {}

    public static void register() {
        Registry.register(BuiltInRegistries.FEATURE, Content.id("spire"), new SpireFeature());
        Registry.register(BuiltInRegistries.FEATURE, Content.id("glimmer_tree"), new GlimmerTreeFeature());
        Registry.register(BuiltInRegistries.FEATURE, Content.id("obelisk"), new ObeliskFeature());
        Registry.register(BuiltInRegistries.FEATURE, Content.id("rock_spire"), new RockSpireFeature());
        Registry.register(BuiltInRegistries.FEATURE, Content.id("islet"), new IsletFeature());
    }

    // ------------------------------------------------------------------ helpers
    private static boolean solidBelow(WorldGenLevel level, BlockPos pos) {
        BlockState s = level.getBlockState(pos.below());
        return !s.isAir() && s.getFluidState().isEmpty() && !s.canBeReplaced();
    }

    private static void put(WorldGenLevel level, BlockPos p, BlockState s) {
        level.setBlock(p, s, 2);
    }

    private static BlockState persistentLeaves(BlockState s) {
        return s.hasProperty(LeavesBlock.PERSISTENT) ? s.setValue(LeavesBlock.PERSISTENT, true) : s;
    }

    // ------------------------------------------------------------------ elemental / crystal spires
    static final class SpireFeature extends Feature<ElementConfig> {
        SpireFeature() {
            super(ElementConfig.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<ElementConfig> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos o = ctx.origin();
            RandomSource r = ctx.random();
            if (!solidBelow(level, o)) return false;
            String el = ctx.config().element();
            BlockState a, b, tip;
            boolean big = false;
            switch (el) {
                case "flame": a = Blocks.BLACKSTONE.defaultBlockState(); b = Blocks.MAGMA_BLOCK.defaultBlockState(); tip = Blocks.SHROOMLIGHT.defaultBlockState(); break;
                case "frost": a = Blocks.PACKED_ICE.defaultBlockState(); b = Blocks.BLUE_ICE.defaultBlockState(); tip = Blocks.SEA_LANTERN.defaultBlockState(); break;
                case "storm": a = Blocks.WAXED_OXIDIZED_COPPER.defaultBlockState(); b = Blocks.WAXED_WEATHERED_CUT_COPPER.defaultBlockState(); tip = Blocks.GLOWSTONE.defaultBlockState(); break;
                case "verdant": a = Blocks.DARK_OAK_LOG.defaultBlockState(); b = Blocks.MOSS_BLOCK.defaultBlockState(); tip = Blocks.SHROOMLIGHT.defaultBlockState(); break;
                case "void": a = Blocks.OBSIDIAN.defaultBlockState(); b = Blocks.CRYING_OBSIDIAN.defaultBlockState(); tip = Blocks.AMETHYST_BLOCK.defaultBlockState(); break;
                case "crystal_big":
                    a = ModBlocks.state("rift_crystal_block"); b = Blocks.AMETHYST_BLOCK.defaultBlockState(); tip = ModBlocks.state("rift_crystal_block"); big = true; break;
                default:
                    a = ModBlocks.state("rift_crystal_block"); b = Blocks.AMETHYST_BLOCK.defaultBlockState(); tip = ModBlocks.state("rift_crystal_block"); break;
            }
            int h = big ? 18 + r.nextInt(20) : 7 + r.nextInt(12);
            double base = big ? 3.6 : 2.4 + r.nextDouble();
            double leanX = (r.nextDouble() - 0.5) * 5.0;
            double leanZ = (r.nextDouble() - 0.5) * 5.0;
            for (int y = 0; y < h; y++) {
                double t = y / (double) h;
                double rad = Math.max(0.4, base * (1.0 - t));
                int cx = (int) Math.round(leanX * t);
                int cz = (int) Math.round(leanZ * t);
                int ir = (int) Math.ceil(rad);
                for (int dx = -ir; dx <= ir; dx++) {
                    for (int dz = -ir; dz <= ir; dz++) {
                        if (dx * dx + dz * dz <= rad * rad + 0.3) {
                            put(level, o.offset(cx + dx, y, cz + dz), r.nextInt(4) == 0 ? b : a);
                        }
                    }
                }
            }
            put(level, o.offset((int) Math.round(leanX), h, (int) Math.round(leanZ)), tip);
            return true;
        }
    }

    // ------------------------------------------------------------------ glimmerwood tree
    static final class GlimmerTreeFeature extends Feature<ElementConfig> {
        GlimmerTreeFeature() {
            super(ElementConfig.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<ElementConfig> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos o = ctx.origin();
            RandomSource r = ctx.random();
            if (!solidBelow(level, o)) return false;
            BlockState log = ModBlocks.state("glimmerwood_log");
            BlockState leaves = persistentLeaves(ModBlocks.state("glimmerwood_leaves"));
            int h = 7 + r.nextInt(7);
            int bx = 0, bz = 0;
            for (int y = 0; y < h; y++) {
                if (y > 3 && r.nextInt(3) == 0) {
                    bx += r.nextInt(3) - 1;
                    bz += r.nextInt(3) - 1;
                }
                put(level, o.offset(bx, y, bz), log);
                if (y < 3) {
                    put(level, o.offset(bx + 1, y, bz), log);
                }
            }
            BlockPos top = o.offset(bx, h, bz);
            int rad = 3 + r.nextInt(2);
            for (int dx = -rad; dx <= rad; dx++) {
                for (int dy = -2; dy <= 3; dy++) {
                    for (int dz = -rad; dz <= rad; dz++) {
                        double d = dx * dx + dy * dy * 1.6 + dz * dz;
                        if (d <= rad * rad + 0.5 && r.nextInt(8) != 0) {
                            BlockPos p = top.offset(dx, dy, dz);
                            if (level.getBlockState(p).isAir() || level.getBlockState(p).canBeReplaced()) put(level, p, leaves);
                        }
                    }
                }
            }
            put(level, top.below(), log);
            return true;
        }
    }

    // ------------------------------------------------------------------ overworld obelisk
    static final class ObeliskFeature extends Feature<ElementConfig> {
        ObeliskFeature() {
            super(ElementConfig.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<ElementConfig> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos o = ctx.origin();
            RandomSource r = ctx.random();
            if (!solidBelow(level, o)) return false;
            BlockState brick = ModBlocks.state("riftstone_bricks");
            BlockState pillar = ModBlocks.state("riftstone_pillar");
            BlockState chiseled = ModBlocks.state("chiseled_riftstone");
            BlockState glow = ModBlocks.state("rift_crystal_block");
            int h = 12 + r.nextInt(8);
            for (int dx = -2; dx <= 2; dx++) for (int dz = -2; dz <= 2; dz++) {
                put(level, o.offset(dx, 0, dz), chiseled);
                put(level, o.offset(dx, -1, dz), brick);
            }
            for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) put(level, o.offset(dx, 1, dz), brick);
            for (int y = 2; y < h; y++) {
                int w = y < h - 4 ? 1 : 0;
                for (int dx = -w; dx <= w; dx++) for (int dz = -w; dz <= w; dz++) {
                    put(level, o.offset(dx, y, dz), pillar);
                }
                if (y % 4 == 3 && w == 1) {
                    put(level, o.offset(2, y, 0), glow); put(level, o.offset(-2, y, 0), glow);
                    put(level, o.offset(0, y, 2), glow); put(level, o.offset(0, y, -2), glow);
                }
            }
            put(level, o.offset(0, h, 0), chiseled);
            put(level, o.offset(0, h + 1, 0), glow);
            return true;
        }
    }

    // ------------------------------------------------------------------ tall rock spires
    static final class RockSpireFeature extends Feature<ElementConfig> {
        RockSpireFeature() {
            super(ElementConfig.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<ElementConfig> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos o = ctx.origin();
            RandomSource r = ctx.random();
            if (!solidBelow(level, o)) return false;
            BlockState[] rock = {Blocks.STONE.defaultBlockState(), Blocks.ANDESITE.defaultBlockState(), Blocks.TUFF.defaultBlockState(), Blocks.COBBLESTONE.defaultBlockState()};
            int h = 16 + r.nextInt(26);
            double base = 3.0 + r.nextDouble() * 2.5;
            double lx = (r.nextDouble() - 0.5) * 6, lz = (r.nextDouble() - 0.5) * 6;
            for (int y = -3; y < h; y++) {
                double t = Math.max(0, y) / (double) h;
                double rad = Math.max(0.5, base * (1.0 - t * 0.92) + (y < 4 ? 1.0 : 0.0));
                int cx = (int) Math.round(lx * t), cz = (int) Math.round(lz * t);
                int ir = (int) Math.ceil(rad);
                for (int dx = -ir; dx <= ir; dx++) for (int dz = -ir; dz <= ir; dz++) {
                    if (dx * dx + dz * dz <= rad * rad + 0.4) put(level, o.offset(cx + dx, y, cz + dz), rock[r.nextInt(rock.length)]);
                }
            }
            // a few moss patches at the foot
            for (int i = 0; i < 6; i++) {
                put(level, o.offset(r.nextInt(7) - 3, 0, r.nextInt(7) - 3), Blocks.MOSS_BLOCK.defaultBlockState());
            }
            return true;
        }
    }

    // ------------------------------------------------------------------ floating islets in the overworld sky
    static final class IsletFeature extends Feature<ElementConfig> {
        IsletFeature() {
            super(ElementConfig.CODEC);
        }

        @Override
        public boolean place(FeaturePlaceContext<ElementConfig> ctx) {
            WorldGenLevel level = ctx.level();
            BlockPos o = ctx.origin().above(30 + ctx.random().nextInt(26));
            RandomSource r = ctx.random();
            int rad = 5 + r.nextInt(4);
            int depth = 7 + r.nextInt(5);
            BlockState[] rock = {Blocks.STONE.defaultBlockState(), Blocks.ANDESITE.defaultBlockState(), Blocks.TUFF.defaultBlockState(), Blocks.DEEPSLATE.defaultBlockState()};
            for (int y = 0; y < depth; y++) {
                double t = y / (double) depth;
                double rr = Math.max(1.0, rad * (1.0 - t * 0.85));
                int ir = (int) Math.ceil(rr);
                for (int dx = -ir; dx <= ir; dx++) for (int dz = -ir; dz <= ir; dz++) {
                    if (dx * dx + dz * dz <= rr * rr + 0.4) put(level, o.offset(dx, -y, dz), y == 0 ? Blocks.GRASS_BLOCK.defaultBlockState() : (y < 3 ? Blocks.DIRT.defaultBlockState() : rock[r.nextInt(rock.length)]));
                }
            }
            // a lone tree or a crystal cluster
            if (r.nextBoolean()) {
                for (int y = 1; y <= 5; y++) put(level, o.offset(0, y, 0), Blocks.OAK_LOG.defaultBlockState());
                BlockState lv = persistentLeaves(Blocks.OAK_LEAVES.defaultBlockState());
                for (int dx = -2; dx <= 2; dx++) for (int dy = 4; dy <= 7; dy++) for (int dz = -2; dz <= 2; dz++) {
                    if (dx * dx + (dy - 5) * (dy - 5) + dz * dz <= 5 && !(dx == 0 && dz == 0 && dy < 6)) put(level, o.offset(dx, dy, dz), lv);
                }
            } else {
                for (int i = 0; i < 4; i++) {
                    int px = r.nextInt(5) - 2, pz = r.nextInt(5) - 2;
                    int h = 2 + r.nextInt(4);
                    for (int y = 1; y <= h; y++) put(level, o.offset(px, y, pz), y == h ? ModBlocks.state("rift_crystal_block") : Blocks.AMETHYST_BLOCK.defaultBlockState());
                }
            }
            return true;
        }
    }
}
