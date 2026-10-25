package com.realmbreak;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.data.PData;
import com.realmbreak.magic.Magic;
import com.realmbreak.net.Net;
import com.realmbreak.quest.Quests;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.item.UseOnContext;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.core.Direction;
import net.minecraft.core.BlockPos;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

public final class ModItems {
    public static final Map<String, Item> ITEMS = new LinkedHashMap<>();
    private static final Map<Item, String> STAFF_ELEMENT = new HashMap<>();
    private static final Map<String, Holder<ArmorMaterial>> MATERIALS = new HashMap<>();

    private ModItems() {}

    public static Item get(String id) {
        ResourceLocationHolder h = new ResourceLocationHolder(id);
        return BuiltInRegistries.ITEM.getOptional(h.rl()).orElse(Items.AIR);
    }

    private record ResourceLocationHolder(String raw) {
        net.minecraft.resources.ResourceLocation rl() {
            return raw.contains(":") ? net.minecraft.resources.ResourceLocation.parse(raw) : Content.id(raw);
        }
    }

    public static String staffElement(Item item) {
        return STAFF_ELEMENT.get(item);
    }

    // ------------------------------------------------------------------ tier
    static final class RealmTier implements Tier {
        private final int uses;
        private final Supplier<Ingredient> repair;

        RealmTier(int uses, Supplier<Ingredient> repair) {
            this.uses = uses;
            this.repair = repair;
        }

        @Override public int getUses() { return uses; }
        @Override public float getSpeed() { return 8.0f; }
        @Override public float getAttackDamageBonus() { return 0.0f; }
        @Override public TagKey<Block> getIncorrectBlocksForDrops() { return BlockTags.INCORRECT_FOR_DIAMOND_TOOL; }
        @Override public int getEnchantmentValue() { return 18; }
        @Override public Ingredient getRepairIngredient() { return repair.get(); }
    }

    // ------------------------------------------------------------------ item classes
    public static class ElementSword extends SwordItem {
        final String element;

        public ElementSword(Tier tier, Properties props, String element) {
            super(tier, props);
            this.element = element;
        }

        @Override
        public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
            boolean r = super.hurtEnemy(stack, target, attacker);
            if (!element.isEmpty()) Magic.rider(element, target);
            if (element.equals("verdant")) attacker.heal(1.0f);
            return r;
        }
    }

    /** Emberbrand: right-click for a ring of cinders. */
    public static class Emberbrand extends ElementSword {
        public Emberbrand(Tier tier, Properties props) {
            super(tier, props, "flame");
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            PData d = PData.of(sp);
            if (d.mana() < 25) {
                sp.displayClientMessage(Component.literal("Not enough mana (25 needed)").withStyle(ChatFormatting.RED), true);
                return InteractionResultHolder.fail(stack);
            }
            d.setMana(d.mana() - 25);
            ServerLevel lv = sp.serverLevel();
            Vec3 c = sp.position();
            for (int r = 1; r <= 6; r++) {
                final int rr = r;
                Scheduler.after(r, () -> Magic.ring(lv, ModParticles.EMBER_SPARK, c, rr, 12 + rr * 6));
            }
            Magic.sound(lv, c, SoundEvents.FIRECHARGE_USE, 1f, 0.7f);
            for (LivingEntity e : Magic.around(lv, c, 6.5, x -> Magic.validTarget(x, sp))) {
                Magic.damage(sp, e, 9.0f);
                e.igniteForSeconds(5);
            }
            sp.getCooldowns().addCooldown(this, 160);
            Net.sync(sp);
            return InteractionResultHolder.consume(stack);
        }
    }

    /** Voidreaver: right-click to blink forward. */
    public static class Voidreaver extends ElementSword {
        public Voidreaver(Tier tier, Properties props) {
            super(tier, props, "void");
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            PData d = PData.of(sp);
            if (d.mana() < 20) {
                sp.displayClientMessage(Component.literal("Not enough mana (20 needed)").withStyle(ChatFormatting.RED), true);
                return InteractionResultHolder.fail(stack);
            }
            d.setMana(d.mana() - 20);
            Magic.cast(sp, "void", "blink", 0f);
            sp.getCooldowns().addCooldown(this, 80);
            Net.sync(sp);
            return InteractionResultHolder.consume(stack);
        }
    }

    public static class ElementBow extends BowItem {
        public final double bonus;
        public final String element;
        public final boolean stormcaller;

        public ElementBow(Properties props, double bonus, String element, boolean stormcaller) {
            super(props);
            this.bonus = bonus;
            this.element = element;
            this.stormcaller = stormcaller;
        }
    }

    public static class StaffItem extends Item {
        public final String element;
        public final double power;
        public final double mana;
        public final int cooldown;

        public StaffItem(Properties props, String element, double power, double mana, int cooldown) {
            super(props);
            this.element = element;
            this.power = power;
            this.mana = mana;
            this.cooldown = cooldown;
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            boolean ok = Magic.castFromStaff(sp, stack, this, element, power, mana);
            if (!ok) return InteractionResultHolder.fail(stack);
            sp.getCooldowns().addCooldown(this, cooldown);
            stack.hurtAndBreak(1, sp, hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
            return InteractionResultHolder.consume(stack);
        }

        @Override
        public UseAnim getUseAnimation(ItemStack stack) {
            return UseAnim.NONE;
        }
    }

    public static class AnchorItem extends Item {
        public AnchorItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResult useOn(UseOnContext ctx) {
            Level level = ctx.getLevel();
            if (level.isClientSide) return InteractionResult.SUCCESS;
            if (!(ctx.getPlayer() instanceof ServerPlayer sp)) return InteractionResult.PASS;
            BlockPos base = ctx.getClickedPos().relative(ctx.getClickedFace());
            Direction.Axis axis = ctx.getHorizontalDirection().getAxis() == Direction.Axis.X ? Direction.Axis.Z : Direction.Axis.X;
            if (RiftTravel.buildGate((ServerLevel) level, base, axis, false)) {
                ctx.getItemInHand().shrink(1);
                sp.displayClientMessage(Component.literal("A Rift Gate tears open.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
                return InteractionResult.CONSUME;
            }
            sp.displayClientMessage(Component.literal("There is not enough room for a gate here (5 wide, 6 tall).").withStyle(ChatFormatting.RED), true);
            return InteractionResult.FAIL;
        }
    }

    public static class CompassItem extends Item {
        public CompassItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            Quests.pointCompass(sp);
            sp.getCooldowns().addCooldown(this, 20);
            return InteractionResultHolder.consume(stack);
        }
    }

    public static class JournalItem extends Item {
        public JournalItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            Net.sync(sp);
            Net.send(sp, "open_log", new CompoundTag());
            return InteractionResultHolder.consume(stack);
        }
    }

    public static class ElixirItem extends Item {
        final int mana;
        final int heal;

        public ElixirItem(Properties props, int mana, int heal) {
            super(props);
            this.mana = mana;
            this.heal = heal;
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            PData d = PData.of(sp);
            if (mana > 0) d.setMana(Math.min(Magic.maxMana(d), d.mana() + mana));
            if (heal > 0) {
                sp.heal(heal);
                sp.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 1));
            }
            stack.shrink(1);
            sp.playNotifySound(SoundEvents.GENERIC_DRINK, SoundSource.PLAYERS, 1f, 1f);
            sp.getCooldowns().addCooldown(this, 40);
            Net.sync(sp);
            return InteractionResultHolder.consume(stack);
        }
    }

    public static class TomeItem extends Item {
        public TomeItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide || !(player instanceof ServerPlayer sp)) return InteractionResultHolder.success(stack);
            PData.of(sp).addPoints(1);
            stack.shrink(1);
            sp.sendSystemMessage(Component.literal("You gain a skill point. Press K to spend it.").withStyle(ChatFormatting.AQUA));
            sp.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1f, 1f);
            Net.sync(sp);
            return InteractionResultHolder.consume(stack);
        }
    }

    // ------------------------------------------------------------------ registration
    private static Holder<ArmorMaterial> material(String element, String prefix, int h, int c, int l, int b, float tough, float kb) {
        EnumMap<ArmorItem.Type, Integer> def = new EnumMap<>(ArmorItem.Type.class);
        def.put(ArmorItem.Type.HELMET, h);
        def.put(ArmorItem.Type.CHESTPLATE, c);
        def.put(ArmorItem.Type.LEGGINGS, l);
        def.put(ArmorItem.Type.BOOTS, b);
        def.put(ArmorItem.Type.BODY, c);
        ArmorMaterial m = new ArmorMaterial(def, 18, SoundEvents.ARMOR_EQUIP_NETHERITE, () -> Ingredient.of(get(element + "_essence")),
                List.of(new ArmorMaterial.Layer(Content.id(prefix))), tough, kb);
        return Registry.registerForHolder(BuiltInRegistries.ARMOR_MATERIAL, Content.id(prefix), m);
    }

    private static Rarity rarity(String s) {
        switch (s) {
            case "uncommon": return Rarity.UNCOMMON;
            case "rare": return Rarity.RARE;
            case "epic": return Rarity.EPIC;
            default: return Rarity.COMMON;
        }
    }

    private static ArmorItem.Type slot(String s) {
        switch (s) {
            case "helmet": return ArmorItem.Type.HELMET;
            case "chestplate": return ArmorItem.Type.CHESTPLATE;
            case "leggings": return ArmorItem.Type.LEGGINGS;
            default: return ArmorItem.Type.BOOTS;
        }
    }

    public static void register() {
        MATERIALS.put("flame", material("flame", "cinder", 3, 8, 6, 3, 2.5f, 0.05f));
        MATERIALS.put("frost", material("frost", "rime", 3, 7, 6, 3, 2.0f, 0.0f));
        MATERIALS.put("storm", material("storm", "gale", 3, 7, 5, 3, 2.0f, 0.05f));
        MATERIALS.put("verdant", material("verdant", "thorn", 3, 7, 6, 3, 2.0f, 0.1f));
        MATERIALS.put("void", material("void", "null", 3, 8, 6, 3, 3.0f, 0.0f));

        for (JsonElement el : Content.content.getAsJsonArray("items")) {
            JsonObject o = el.getAsJsonObject();
            String id = o.get("id").getAsString();
            String kind = o.get("kind").getAsString();
            String element = Content.str(o, "element", "");
            Item.Properties p = new Item.Properties().rarity(rarity(Content.str(o, "rarity", "common")));
            if (o.has("stack")) p.stacksTo(o.get("stack").getAsInt());
            String lore = Content.str(o, "lore", "");
            if (!lore.isEmpty()) p.component(DataComponents.LORE, new ItemLore(List.of(Component.literal(lore).withStyle(ChatFormatting.GRAY))));
            if (o.has("legendary")) p.fireResistant();
            Item item;
            switch (kind) {
                case "sword": {
                    final String el2 = element;
                    Tier tier = new RealmTier(Content.num(o, "durability", 1500), () -> Ingredient.of(get(el2 + "_essence")));
                    int dmg = (int) Math.round(Content.dbl(o, "damage", 8)) - 1;
                    float spd = (float) Content.dbl(o, "speed", -2.4);
                    p.attributes(SwordItem.createAttributes(tier, dmg, spd));
                    if (id.equals("emberbrand")) item = new Emberbrand(tier, p);
                    else if (id.equals("voidreaver")) item = new Voidreaver(tier, p);
                    else item = new ElementSword(tier, p, element);
                    break;
                }
                case "bow":
                    p.durability(Content.num(o, "durability", 800));
                    item = new ElementBow(p, Content.dbl(o, "bonus", 2.0), element, id.equals("stormpiercer"));
                    break;
                case "staff": {
                    p.durability(Content.num(o, "durability", 800)).stacksTo(1);
                    item = new StaffItem(p, element.isEmpty() ? "arcane" : element, Content.dbl(o, "power", 6), Content.dbl(o, "mana", 10), Content.num(o, "cooldown", 14));
                    STAFF_ELEMENT.put(item, element.isEmpty() ? "arcane" : element);
                    break;
                }
                case "armor": {
                    ArmorItem.Type t = slot(Content.str(o, "slot", "helmet"));
                    p.durability(t.getDurability(36));
                    item = new ArmorItem(MATERIALS.get(element), t, p);
                    break;
                }
                case "anchor": item = new AnchorItem(p); break;
                case "compass": item = new CompassItem(p); break;
                case "journal": item = new JournalItem(p); break;
                case "elixir": item = new ElixirItem(p, Content.num(o, "mana", 0), Content.num(o, "heal", 0)); break;
                case "tome": item = new TomeItem(p); break;
                default: item = new Item(p); break;
            }
            ITEMS.put(id, Registry.register(BuiltInRegistries.ITEM, Content.id(id), item));
        }
    }
}
