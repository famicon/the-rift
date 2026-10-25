package com.realmbreak;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.entity.RiftBoss;
import com.realmbreak.quest.Quests;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.LinkedHashMap;
import java.util.Map;

public final class ModBlocks {
    public static final Map<String, Block> BLOCKS = new LinkedHashMap<>();
    public static final Map<String, Item> BLOCK_ITEMS = new LinkedHashMap<>();

    private ModBlocks() {}

    public static Block get(String id) {
        return BLOCKS.get(id);
    }

    public static BlockState state(String id) {
        Block b = BLOCKS.get(id);
        return b == null ? net.minecraft.world.level.block.Blocks.STONE.defaultBlockState() : b.defaultBlockState();
    }

    // ------------------------------------------------------------------ blocks
    public static class RiftPortalBlock extends Block {
        public static final EnumProperty<Direction.Axis> AXIS = BlockStateProperties.HORIZONTAL_AXIS;
        private static final VoxelShape X_SHAPE = Block.box(0, 0, 6, 16, 16, 10);
        private static final VoxelShape Z_SHAPE = Block.box(6, 0, 0, 10, 16, 16);

        public RiftPortalBlock(Properties props) {
            super(props);
            registerDefaultState(stateDefinition.any().setValue(AXIS, Direction.Axis.X));
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
            b.add(AXIS);
        }

        @Override
        protected VoxelShape getShape(BlockState s, BlockGetter g, BlockPos p, CollisionContext c) {
            return s.getValue(AXIS) == Direction.Axis.X ? X_SHAPE : Z_SHAPE;
        }

        @Override
        protected VoxelShape getCollisionShape(BlockState s, BlockGetter g, BlockPos p, CollisionContext c) {
            return Shapes.empty();
        }

        @Override
        protected void entityInside(BlockState s, Level level, BlockPos pos, Entity e) {
            if (level.isClientSide) return;
            if (e instanceof ServerPlayer sp && !sp.isOnPortalCooldown()) {
                RiftTravel.usePortal(sp, pos);
            }
        }

        @Override
        public void animateTick(BlockState s, Level level, BlockPos pos, RandomSource r) {
            if (r.nextInt(3) == 0) {
                level.addParticle(ModParticles.RIFT_MOTE, pos.getX() + r.nextDouble(), pos.getY() + r.nextDouble(), pos.getZ() + r.nextDouble(),
                        (r.nextDouble() - 0.5) * 0.04, r.nextDouble() * 0.06, (r.nextDouble() - 0.5) * 0.04);
            }
        }
    }

    public static class LandmarkBlock extends Block {
        public static final IntegerProperty SITE = IntegerProperty.create("site", 0, 25);

        public LandmarkBlock(Properties props) {
            super(props);
            registerDefaultState(stateDefinition.any().setValue(SITE, 0));
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
            b.add(SITE);
        }

        @Override
        protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
            if (level.isClientSide) return InteractionResult.SUCCESS;
            if (player instanceof ServerPlayer sp) Quests.onAttune(sp, state.getValue(SITE), pos);
            return InteractionResult.CONSUME;
        }

        @Override
        public void animateTick(BlockState s, Level level, BlockPos pos, RandomSource r) {
            if (r.nextInt(4) == 0) {
                level.addParticle(ModParticles.RIFT_MOTE, pos.getX() + 0.5 + (r.nextDouble() - 0.5) * 0.8, pos.getY() + 1.0, pos.getZ() + 0.5 + (r.nextDouble() - 0.5) * 0.8,
                        0, 0.05, 0);
            }
        }
    }

    public static class BossAltarBlock extends Block {
        public static final IntegerProperty BOSS = IntegerProperty.create("boss", 0, 4);

        public BossAltarBlock(Properties props) {
            super(props);
            registerDefaultState(stateDefinition.any().setValue(BOSS, 0));
        }

        @Override
        protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
            b.add(BOSS);
        }

        private static JsonObject boss(int idx) {
            return Content.content.getAsJsonArray("bosses").get(Math.max(0, Math.min(4, idx))).getAsJsonObject();
        }

        @Override
        protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
            if (!level.isClientSide) {
                JsonObject b = boss(state.getValue(BOSS));
                player.displayClientMessage(Component.literal("Place the Sigil of " + capital(Content.str(b, "element", "")) + " here to summon " + Content.str(b, "name", "the guardian") + ".")
                        .withStyle(ChatFormatting.LIGHT_PURPLE), true);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        @Override
        protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
            JsonObject b = boss(state.getValue(BOSS));
            String element = Content.str(b, "element", "");
            if (stack.getItem() != ModItems.get(element + "_sigil")) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
            if (level.isClientSide) return ItemInteractionResult.SUCCESS;
            if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp)) return ItemInteractionResult.CONSUME;
            AABB zone = new AABB(pos).inflate(40);
            if (!sl.getEntitiesOfClass(RiftBoss.class, zone).isEmpty()) {
                sp.displayClientMessage(Component.literal("The guardian already stirs...").withStyle(ChatFormatting.RED), true);
                return ItemInteractionResult.CONSUME;
            }
            stack.shrink(1);
            final String bid = Content.str(b, "id", "ignarax");
            net.minecraft.world.phys.Vec3 anchor = net.minecraft.world.phys.Vec3.atCenterOf(pos);
            sl.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.HOSTILE, 2.0f, 0.5f);
            int ticks = Cutscenes.playNear(sl, anchor, 36, "boss_" + bid);
            final BlockPos spawnAt = pos.north(4);
            Scheduler.after(Math.max(10, ticks + 5), () -> {
                EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Content.id(bid));
                Entity e = type.create(sl);
                if (e instanceof RiftBoss boss) {
                    boss.moveTo(spawnAt.getX() + 0.5, spawnAt.getY(), spawnAt.getZ() + 0.5, 0f, 0f);
                    boss.finalizeSpawn(sl, sl.getCurrentDifficultyAt(spawnAt), MobSpawnType.EVENT, null);
                    sl.addFreshEntity(boss);
                }
            });
            return ItemInteractionResult.CONSUME;
        }
    }

    private static String capital(String s) {
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    /** Glowing plant that must stand on solid ground. */
    public static class GlowBloomBlock extends Block {
        private static final VoxelShape SHAPE = Block.box(3, 0, 3, 13, 12, 13);

        public GlowBloomBlock(Properties props) {
            super(props);
        }

        @Override
        protected VoxelShape getShape(BlockState s, BlockGetter g, BlockPos p, CollisionContext c) {
            return SHAPE;
        }

        @Override
        protected boolean canSurvive(BlockState s, LevelReader level, BlockPos pos) {
            return level.getBlockState(pos.below()).isFaceSturdy(level, pos.below(), Direction.UP);
        }

        @Override
        protected BlockState updateShape(BlockState s, Direction dir, BlockState nstate, LevelAccessor level, BlockPos pos, BlockPos npos) {
            return !s.canSurvive(level, pos) ? net.minecraft.world.level.block.Blocks.AIR.defaultBlockState() : super.updateShape(s, dir, nstate, level, pos, npos);
        }

        @Override
        public void animateTick(BlockState s, Level level, BlockPos pos, RandomSource r) {
            if (r.nextInt(8) == 0) {
                level.addParticle(ModParticles.RIFT_MOTE, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5, (r.nextDouble() - 0.5) * 0.02, 0.03, (r.nextDouble() - 0.5) * 0.02);
            }
        }
    }

    // ------------------------------------------------------------------ registration
    public static void register() {
        for (JsonElement el : Content.content.getAsJsonArray("blocks")) {
            JsonObject o = el.getAsJsonObject();
            String id = o.get("id").getAsString();
            String kind = o.get("kind").getAsString();
            double strength = Content.dbl(o, "strength", 2.0);
            String tool = Content.str(o, "tool", "");
            int light = Content.num(o, "light", 0);
            BlockBehaviour.Properties p = BlockBehaviour.Properties.of();
            if (strength < 0) p.strength(-1.0f, 3600000.0f);
            else p.strength((float) strength, (float) Math.max(strength, 3.0));
            if (!tool.isEmpty() && strength >= 0) p.requiresCorrectToolForDrops();
            if (light > 0) {
                final int lv = light;
                p.lightLevel(s -> lv);
            }
            Block block;
            switch (kind) {
                case "pillar":
                    p.sound(SoundType.STONE);
                    block = new RotatedPillarBlock(p);
                    break;
                case "log":
                    p.sound(SoundType.WOOD);
                    block = new RotatedPillarBlock(p);
                    break;
                case "turf":
                    p.sound(SoundType.GRASS);
                    block = new Block(p);
                    break;
                case "leaves":
                    p.sound(SoundType.GRASS).noOcclusion().isValidSpawn((s, g, pp, t) -> false).isSuffocating((s, g, pp) -> false).isViewBlocking((s, g, pp) -> false);
                    block = new LeavesBlock(p);
                    break;
                case "plant":
                    p.sound(SoundType.GRASS).noCollission().noOcclusion().instabreak().pushReaction(PushReaction.DESTROY);
                    block = new GlowBloomBlock(p);
                    break;
                case "portal":
                    p.noCollission().noOcclusion().pushReaction(PushReaction.BLOCK).sound(SoundType.GLASS);
                    block = new RiftPortalBlock(p);
                    break;
                case "landmark":
                    p.sound(SoundType.AMETHYST);
                    block = new LandmarkBlock(p);
                    break;
                case "altar":
                    p.sound(SoundType.AMETHYST);
                    block = new BossAltarBlock(p);
                    break;
                case "glow":
                    p.sound(SoundType.AMETHYST);
                    block = new Block(p);
                    break;
                default:
                    p.sound(SoundType.STONE);
                    block = new Block(p);
                    break;
            }
            BLOCKS.put(id, Registry.register(BuiltInRegistries.BLOCK, Content.id(id), block));
            if (!kind.equals("portal")) {
                Item.Properties ip = new Item.Properties();
                BLOCK_ITEMS.put(id, Registry.register(BuiltInRegistries.ITEM, Content.id(id), new BlockItem(block, ip)));
            }
        }
    }
}
