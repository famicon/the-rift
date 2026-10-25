package com.realmbreak;

import com.realmbreak.data.PData;
import com.realmbreak.net.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/** Teleporting between the overworld and the Rift, and building Rift Gates. */
public final class RiftTravel {
    public static final ResourceKey<Level> RIFT = ResourceKey.create(Registries.DIMENSION, Content.id("the_rift"));

    private RiftTravel() {}

    public static void usePortal(ServerPlayer p, BlockPos portalPos) {
        ServerLevel rift = p.getServer().getLevel(RIFT);
        if (rift == null) {
            p.sendSystemMessage(Component.literal("The Rift dimension is not loaded.").withStyle(ChatFormatting.RED));
            return;
        }
        if (p.level().dimension() == RIFT) leave(p);
        else enter(p, portalPos, rift);
    }

    public static void enter(ServerPlayer p, BlockPos from, ServerLevel rift) {
        PData d = PData.of(p);
        CompoundTag ret = new CompoundTag();
        ret.putDouble("x", p.getX());
        ret.putDouble("y", p.getY());
        ret.putDouble("z", p.getZ());
        ret.putString("dim", p.level().dimension().location().toString());
        d.tag.put("ret", ret);
        d.dirty();
        BlockPos land = findLanding(rift, from.getX(), from.getZ());
        // existing gate nearby?
        BlockPos gate = findGateNear(rift, land, 14);
        if (gate == null) {
            buildGate(rift, land.offset(0, 0, 4), Direction.Axis.X, true);
        }
        p.teleportTo(rift, land.getX() + 0.5, land.getY(), land.getZ() + 0.5, 0f, 0f);
        p.setPortalCooldown(120);
        p.fallDistance = 0;
        rift.playSound(null, land, SoundEvents.PORTAL_TRAVEL, SoundSource.PLAYERS, 0.6f, 1.4f);
        if (!d.flag("rift_seen")) {
            d.setFlag("rift_seen", true);
            Cutscenes.play(p, "rift_entry", p.position());
        }
        com.realmbreak.quest.Quests.recheck(p);
    }

    public static void leave(ServerPlayer p) {
        PData d = PData.of(p);
        CompoundTag ret = d.tag.getCompound("ret");
        net.minecraft.server.MinecraftServer server = p.getServer();
        ServerLevel target = server.overworld();
        double x, y, z;
        if (ret.contains("x")) {
            ResourceKey<Level> key = ResourceKey.create(Registries.DIMENSION, net.minecraft.resources.ResourceLocation.parse(ret.getString("dim").isEmpty() ? "minecraft:overworld" : ret.getString("dim")));
            ServerLevel t = server.getLevel(key);
            if (t != null) target = t;
            x = ret.getDouble("x");
            y = ret.getDouble("y");
            z = ret.getDouble("z");
        } else {
            BlockPos sp = target.getSharedSpawnPos();
            x = sp.getX() + 0.5;
            y = sp.getY();
            z = sp.getZ() + 0.5;
        }
        BlockPos safe = safeSpot(target, (int) Math.floor(x), (int) Math.floor(y), (int) Math.floor(z));
        p.teleportTo(target, safe.getX() + 0.5, safe.getY(), safe.getZ() + 0.5, p.getYRot(), 0f);
        p.setPortalCooldown(120);
        p.fallDistance = 0;
        target.playSound(null, safe, SoundEvents.PORTAL_TRAVEL, SoundSource.PLAYERS, 0.6f, 1.2f);
    }

    private static boolean free(ServerLevel l, BlockPos p) {
        BlockState s = l.getBlockState(p);
        return s.getCollisionShape(l, p).isEmpty() && s.getFluidState().isEmpty();
    }

    static BlockPos safeSpot(ServerLevel l, int x, int y, int z) {
        l.getChunk(x >> 4, z >> 4);
        for (int dy = 0; dy < 24; dy++) {
            for (int sgn = -1; sgn <= 1; sgn += 2) {
                BlockPos p = new BlockPos(x, y + dy * sgn, z);
                if (free(l, p) && free(l, p.above()) && !free(l, p.below())) return p;
            }
        }
        int top = l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        return new BlockPos(x, top, z);
    }

    /** Find solid ground in the Rift near x,z (islands float, so spiral outwards); build a platform if nothing exists. */
    static BlockPos findLanding(ServerLevel rift, int x, int z) {
        for (int r = 0; r <= 112; r += 8) {
            int n = r == 0 ? 1 : 8;
            for (int i = 0; i < n; i++) {
                double a = i * Math.PI * 2 / n;
                int px = x + (int) Math.round(Math.cos(a) * r);
                int pz = z + (int) Math.round(Math.sin(a) * r);
                rift.getChunk(px >> 4, pz >> 4);
                int top = rift.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, px, pz);
                if (top > rift.getMinBuildHeight() + 8) {
                    BlockPos p = new BlockPos(px, top, pz);
                    // need an open spot with room for a gate 4 blocks to the south (+z) and flat-ish ground
                    if (free(rift, p) && free(rift, p.above()) && !free(rift, p.below()) && rift.getFluidState(p.below()).isEmpty()) return p;
                }
            }
        }
        BlockPos base = new BlockPos(x, 110, z);
        for (int dx = -6; dx <= 6; dx++) {
            for (int dz = -6; dz <= 6; dz++) {
                if (dx * dx + dz * dz <= 38) {
                    rift.setBlock(base.offset(dx, -1, dz), ModBlocks.state("riftstone_bricks"), 3);
                    rift.setBlock(base.offset(dx, -2, dz), ModBlocks.state("riftstone"), 3);
                }
            }
        }
        return base;
    }

    static BlockPos findGateNear(ServerLevel l, BlockPos c, int r) {
        Block portal = ModBlocks.get("rift_portal");
        for (int dx = -r; dx <= r; dx++) {
            for (int dz = -r; dz <= r; dz++) {
                for (int dy = -4; dy <= 8; dy++) {
                    BlockPos p = c.offset(dx, dy, dz);
                    if (l.getBlockState(p).getBlock() == portal) return p;
                }
            }
        }
        return null;
    }

    private static boolean replaceable(ServerLevel l, BlockPos p) {
        BlockState s = l.getBlockState(p);
        return s.isAir() || s.canBeReplaced() || s.getCollisionShape(l, p).isEmpty();
    }

    /** 5 wide x 6 tall gate; base is the centre of the bottom row (standing level). */
    public static boolean buildGate(ServerLevel l, BlockPos base, Direction.Axis axis, boolean clearFirst) {
        BlockState frame = ModBlocks.state("riftstone_bricks");
        BlockState accent = ModBlocks.state("chiseled_riftstone");
        BlockState glow = ModBlocks.state("rift_crystal_block");
        BlockState portal = ModBlocks.state("rift_portal").setValue(ModBlocks.RiftPortalBlock.AXIS, axis);
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 6; j++) {
                BlockPos p = at(base, axis, i - 2, j);
                if (!clearFirst && !replaceable(l, p)) return false;
            }
        }
        // ground support under the frame
        for (int i = 0; i < 5; i++) {
            BlockPos below = at(base, axis, i - 2, -1);
            if (replaceable(l, below)) l.setBlock(below, frame, 3);
        }
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 6; j++) {
                BlockPos p = at(base, axis, i - 2, j);
                boolean edge = i == 0 || i == 4 || j == 0 || j == 5;
                BlockState st;
                if (edge) {
                    boolean corner = (i == 0 || i == 4) && (j == 0 || j == 5);
                    st = (corner || (j == 5 && i == 2)) ? accent : frame;
                    if ((i == 0 || i == 4) && j == 3) st = glow;
                } else {
                    st = portal;
                }
                l.setBlock(p, st, 3);
            }
        }
        return true;
    }

    private static BlockPos at(BlockPos base, Direction.Axis axis, int off, int up) {
        return axis == Direction.Axis.X ? base.offset(off, up, 0) : base.offset(0, up, off);
    }
}
