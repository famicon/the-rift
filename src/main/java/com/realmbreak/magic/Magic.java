package com.realmbreak.magic;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.ModItems;
import com.realmbreak.ModParticles;
import com.realmbreak.Scheduler;
import com.realmbreak.data.PData;
import com.realmbreak.entity.QuestNpcEntity;
import com.realmbreak.net.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Predicate;

/** Mana, skills, set bonuses and every player spell. */
public final class Magic {
    public static final String[] ELEMENTS = {"flame", "frost", "storm", "verdant", "void"};
    private static final Map<UUID, Integer> LAST_MANA = new HashMap<>();
    private static int tickCounter = 0;

    private Magic() {}

    // =============================================================== skills
    public static JsonArray tree(String element) {
        JsonObject skills = Content.story.getAsJsonObject("skills");
        return skills != null && skills.has(element) ? skills.getAsJsonArray(element) : new JsonArray();
    }

    public static JsonObject node(String id) {
        JsonObject skills = Content.story.getAsJsonObject("skills");
        for (String el : skills.keySet()) {
            for (JsonElement e : skills.getAsJsonArray(el)) {
                JsonObject n = e.getAsJsonObject();
                if (n.get("id").getAsString().equals(id)) return n;
            }
        }
        return null;
    }

    /** Sum of an effect stat across unlocked nodes; element == null means every tree. */
    public static double stat(PData d, String element, String key) {
        double sum = 0;
        for (String el : ELEMENTS) {
            if (element != null && !el.equals(element)) continue;
            for (JsonElement e : tree(el)) {
                JsonObject n = e.getAsJsonObject();
                if (!n.has("effect") || !d.hasSkill(n.get("id").getAsString())) continue;
                sum += Content.dbl(n.getAsJsonObject("effect"), key, 0);
            }
        }
        return sum;
    }

    public static boolean hasPassive(PData d, String passive) {
        for (String el : ELEMENTS) {
            for (JsonElement e : tree(el)) {
                JsonObject n = e.getAsJsonObject();
                if (n.has("passive") && n.get("passive").getAsString().equals(passive) && d.hasSkill(n.get("id").getAsString())) return true;
            }
        }
        return false;
    }

    public static double maxMana(PData d) {
        return 100 + stat(d, null, "mana");
    }

    public static double regenPerSecond(PData d) {
        return 2.0 + stat(d, null, "regen");
    }

    public static double power(PData d, String element) {
        if (element.equals("arcane")) return 1.0 + 0.4 * stat(d, null, "power");
        return 1.0 + stat(d, element, "power");
    }

    /** Spells available with a staff of this element: "bolt" first, then unlocked specials. */
    public static List<String> spells(PData d, String element) {
        List<String> out = new ArrayList<>();
        out.add("bolt");
        for (JsonElement e : tree(element)) {
            JsonObject n = e.getAsJsonObject();
            if (n.has("spell") && d.hasSkill(n.get("id").getAsString())) out.add(n.get("spell").getAsString());
        }
        return out;
    }

    public static String spellName(String element, String kind) {
        if (kind.equals("bolt")) return capitalize(element.equals("arcane") ? "arcane" : element) + " Bolt";
        for (JsonElement e : tree(element)) {
            JsonObject n = e.getAsJsonObject();
            if (n.has("spell") && n.get("spell").getAsString().equals(kind)) return n.get("name").getAsString();
        }
        return kind;
    }

    private static String capitalize(String s) {
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    public static boolean unlock(ServerPlayer p, String id) {
        PData d = PData.of(p);
        JsonObject n = node(id);
        if (n == null || d.hasSkill(id)) return false;
        int cost = n.get("cost").getAsInt();
        if (d.points() < cost) {
            p.displayClientMessage(Component.literal("Not enough skill points.").withStyle(ChatFormatting.RED), true);
            return false;
        }
        for (JsonElement r : n.getAsJsonArray("requires")) {
            if (!d.hasSkill(r.getAsString())) {
                p.displayClientMessage(Component.literal("Requires an earlier skill.").withStyle(ChatFormatting.RED), true);
                return false;
            }
        }
        d.addPoints(-cost);
        d.addSkill(id);
        p.sendSystemMessage(Component.literal("Skill unlocked: " + n.get("name").getAsString()).withStyle(ChatFormatting.AQUA));
        p.playNotifySound(SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.8f, 1.4f);
        Net.sync(p);
        return true;
    }

    // =============================================================== per-tick upkeep
    public static void tickPlayer(ServerPlayer p) {
        PData d = PData.of(p);
        double max = maxMana(d);
        double regen = regenPerSecond(d) + (fullSetElement(p) != null ? 1.5 : 0.0);
        double m = Math.min(max, d.mana() + regen / 20.0);
        d.setMana(m);
        tickCounter++;
        if ((p.tickCount + p.getId()) % 5 == 0) {
            int cur = (int) m;
            Integer last = LAST_MANA.get(p.getUUID());
            if (last == null || last != cur) {
                LAST_MANA.put(p.getUUID(), cur);
                CompoundTag t = new CompoundTag();
                t.putInt("mana", cur);
                t.putInt("max", (int) max);
                Net.send(p, "mana", t);
            }
        }
        if (p.tickCount % 40 == 0) {
            String set = fullSetElement(p);
            if (set != null) {
                switch (set) {
                    case "flame" -> p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 100, 0, true, false, true));
                    case "frost" -> p.setTicksFrozen(0);
                    case "storm" -> p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 100, 0, true, false, true));
                    case "verdant" -> p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0, true, false, true));
                    case "void" -> p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 100, 0, true, false, true));
                    default -> {
                    }
                }
            }
            if (hasPassive(d, "regen")) p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0, true, false, true));
            if (hasPassive(d, "swift")) p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 100, 0, true, false, true));
        }
        if (p.tickCount % 600 == 0) d.dirty();
    }

    public static void forget(UUID id) {
        LAST_MANA.remove(id);
    }

    public static String fullSetElement(ServerPlayer p) {
        JsonObject prefixes = Content.content.getAsJsonObject("set_prefix");
        for (String el : ELEMENTS) {
            String pre = prefixes.get(el).getAsString();
            if (isItem(p.getItemBySlot(EquipmentSlot.HEAD), pre + "_helmet") && isItem(p.getItemBySlot(EquipmentSlot.CHEST), pre + "_chestplate")
                    && isItem(p.getItemBySlot(EquipmentSlot.LEGS), pre + "_leggings") && isItem(p.getItemBySlot(EquipmentSlot.FEET), pre + "_boots")) {
                return el;
            }
        }
        return null;
    }

    private static boolean isItem(ItemStack s, String id) {
        return !s.isEmpty() && s.getItem() == ModItems.get(id);
    }

    // =============================================================== helpers
    public static boolean validTarget(Entity e, Entity caster) {
        return e instanceof LivingEntity && e != caster && e.isAlive() && !(e instanceof Player) && !(e instanceof QuestNpcEntity) && !(e instanceof ArmorStand);
    }

    public record Hit(Vec3 pos, LivingEntity entity) {}

    public static Hit ray(ServerPlayer p, double range) {
        Vec3 eye = p.getEyePosition();
        Vec3 look = p.getLookAngle();
        Vec3 end = eye.add(look.scale(range));
        ServerLevel lv = p.serverLevel();
        BlockHitResult bhr = lv.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
        if (bhr.getType() != HitResult.Type.MISS) end = bhr.getLocation();
        AABB box = new AABB(eye, end).inflate(1.5);
        LivingEntity best = null;
        Vec3 bestPos = null;
        double bestD = Double.MAX_VALUE;
        for (Entity e : lv.getEntities(p, box, x -> validTarget(x, p))) {
            java.util.Optional<Vec3> c = e.getBoundingBox().inflate(0.35).clip(eye, end);
            if (c.isPresent()) {
                double dd = eye.distanceToSqr(c.get());
                if (dd < bestD) {
                    bestD = dd;
                    best = (LivingEntity) e;
                    bestPos = c.get();
                }
            }
        }
        if (best != null) return new Hit(bestPos, best);
        return new Hit(end, null);
    }

    public static void damage(ServerPlayer p, LivingEntity target, float amount) {
        target.hurt(p.damageSources().indirectMagic(p, p), amount);
    }

    public static List<LivingEntity> around(ServerLevel lv, Vec3 c, double r, Predicate<LivingEntity> pred) {
        AABB box = new AABB(c.x - r, c.y - r, c.z - r, c.x + r, c.y + r, c.z + r);
        List<LivingEntity> out = new ArrayList<>();
        for (LivingEntity e : lv.getEntitiesOfClass(LivingEntity.class, box, pred)) {
            if (e.position().distanceTo(c) <= r + e.getBbWidth() * 0.5) out.add(e);
        }
        return out;
    }

    public static void particles(ServerLevel lv, ParticleOptions pt, Vec3 pos, int count, double spread, double speed) {
        lv.sendParticles(pt, pos.x, pos.y, pos.z, count, spread, spread, spread, speed);
    }

    public static void line(ServerLevel lv, ParticleOptions pt, Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        double len = d.length();
        if (len < 0.01) return;
        Vec3 step = d.scale(0.6 / len);
        Vec3 cur = from;
        int n = (int) (len / 0.6);
        for (int i = 0; i < n; i++) {
            lv.sendParticles(pt, cur.x, cur.y, cur.z, 1, 0.03, 0.03, 0.03, 0.0);
            cur = cur.add(step);
        }
    }

    public static void ring(ServerLevel lv, ParticleOptions pt, Vec3 c, double r, int points) {
        for (int i = 0; i < points; i++) {
            double a = i * Math.PI * 2 / points;
            lv.sendParticles(pt, c.x + Math.cos(a) * r, c.y + 0.15, c.z + Math.sin(a) * r, 1, 0.02, 0.02, 0.02, 0.0);
        }
    }

    public static void sound(ServerLevel lv, Vec3 pos, SoundEvent s, float vol, float pitch) {
        lv.playSound(null, pos.x, pos.y, pos.z, s, SoundSource.PLAYERS, vol, pitch);
    }

    public static void lightning(ServerLevel lv, Vec3 pos) {
        LightningBolt b = EntityType.LIGHTNING_BOLT.create(lv);
        if (b != null) {
            b.moveTo(pos.x, pos.y, pos.z);
            b.setVisualOnly(true);
            lv.addFreshEntity(b);
        }
    }

    /** Status effect carried by every hit of this element. */
    public static void rider(String element, LivingEntity target) {
        switch (element) {
            case "flame" -> target.igniteForSeconds(4);
            case "frost" -> {
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
                target.setTicksFrozen(Math.min(target.getTicksRequiredToFreeze() + 40, target.getTicksFrozen() + 60));
            }
            case "storm" -> {
                if (target.level() instanceof ServerLevel lv) {
                    lv.sendParticles(ParticleTypes.ELECTRIC_SPARK, target.getX(), target.getY() + 1, target.getZ(), 8, 0.3, 0.5, 0.3, 0.1);
                }
            }
            case "verdant" -> target.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0));
            case "void" -> target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0));
            default -> {
            }
        }
    }

    // =============================================================== casting
    private static double costMult(String kind) {
        switch (kind) {
            case "bolt": return 1.0;
            case "nova": case "chain": case "snare": case "bloom": case "blink": return 2.0;
            default: return 3.0;
        }
    }

    public static boolean castFromStaff(ServerPlayer p, ItemStack stack, Item staffItem, String element, double staffPower, double staffMana) {
        PData d = PData.of(p);
        List<String> list = spells(d, element);
        int sel = Math.floorMod(d.sel(), list.size());
        String kind = list.get(sel);
        double cost = staffMana * costMult(kind);
        if (d.mana() < cost) {
            p.displayClientMessage(Component.literal("Not enough mana (" + (int) cost + " needed)").withStyle(ChatFormatting.RED), true);
            return false;
        }
        double power = staffPower * power(d, element);
        boolean ok = cast(p, element, kind, (float) power);
        if (ok) {
            d.setMana(d.mana() - cost);
            Net.sync(p);
        }
        return ok;
    }

    public static void cycle(ServerPlayer p) {
        ItemStack s = p.getMainHandItem();
        String element = ModItems.staffElement(s.getItem());
        if (element == null) return;
        PData d = PData.of(p);
        List<String> list = spells(d, element);
        int sel = (Math.floorMod(d.sel(), list.size()) + 1) % list.size();
        d.setSel(sel);
        d.dirty();
        p.displayClientMessage(Component.literal("Spell: " + spellName(element, list.get(sel))).withStyle(ChatFormatting.AQUA), true);
        Net.sync(p);
    }

    public static boolean cast(ServerPlayer p, String element, String kind, float power) {
        ServerLevel lv = p.serverLevel();
        ParticleOptions pt = ModParticles.byElement(element);
        Vec3 eye = p.getEyePosition();
        switch (kind) {
            case "bolt": {
                Hit h = ray(p, 30);
                Vec3 from = eye.add(p.getLookAngle().scale(0.8)).add(0, -0.25, 0);
                line(lv, pt, from, h.pos());
                particles(lv, pt, h.pos(), 14, 0.35, 0.05);
                sound(lv, eye, SoundEvents.EVOKER_CAST_SPELL, 0.7f, 1.4f);
                if (h.entity() != null) {
                    damage(p, h.entity(), power);
                    rider(element, h.entity());
                    if (element.equals("storm")) chain(p, h.entity(), power * 0.5f, 2, 5.0);
                }
                return true;
            }
            case "nova": {
                Vec3 c = p.position();
                for (int r = 1; r <= 5; r++) {
                    final int rr = r;
                    Scheduler.after(r, () -> ring(lv, pt, c, rr, 10 + rr * 6));
                }
                sound(lv, c, element.equals("frost") ? SoundEvents.GLASS_BREAK : SoundEvents.FIRECHARGE_USE, 1f, 0.8f);
                for (LivingEntity e : around(lv, c, 5.5, x -> validTarget(x, p))) {
                    damage(p, e, power * 0.9f);
                    rider(element, e);
                }
                return true;
            }
            case "lance": {
                Hit h = ray(p, 32);
                Vec3 from = eye.add(p.getLookAngle().scale(0.8));
                line(lv, pt, from, h.pos());
                line(lv, ParticleTypes.SNOWFLAKE, from, h.pos());
                sound(lv, eye, SoundEvents.GLASS_BREAK, 0.8f, 1.6f);
                Vec3 look = p.getLookAngle();
                Vec3 end = h.pos();
                AABB box = new AABB(eye, end).inflate(1.0);
                for (Entity e : lv.getEntities(p, box, x -> validTarget(x, p))) {
                    if (e.getBoundingBox().inflate(0.4).clip(eye, end).isPresent()) {
                        damage(p, (LivingEntity) e, power * 1.2f);
                        rider("frost", (LivingEntity) e);
                    }
                }
                return true;
            }
            case "chain": {
                Hit h = ray(p, 26);
                line(lv, ParticleTypes.ELECTRIC_SPARK, eye.add(p.getLookAngle().scale(0.8)), h.pos());
                sound(lv, eye, SoundEvents.LIGHTNING_BOLT_THUNDER, 0.4f, 1.8f);
                if (h.entity() != null) {
                    damage(p, h.entity(), power);
                    chain(p, h.entity(), power * 0.7f, 3, 6.5);
                }
                return true;
            }
            case "tempest": {
                Hit h = ray(p, 36);
                Vec3 c = h.pos();
                for (int i = 0; i < 6; i++) {
                    final int k = i;
                    Scheduler.after(8 + i * 8, () -> {
                        Vec3 pos = c.add((lv.random.nextDouble() - 0.5) * 8, 0, (lv.random.nextDouble() - 0.5) * 8);
                        lightning(lv, pos);
                        for (LivingEntity e : around(lv, pos, 2.6, x -> validTarget(x, p))) {
                            damage(p, e, power * 1.1f);
                        }
                    });
                }
                return true;
            }
            case "snare": {
                Hit h = ray(p, 24);
                Vec3 c = h.pos();
                particles(lv, ParticleTypes.COMPOSTER, c, 40, 2.0, 0.1);
                particles(lv, pt, c, 24, 1.6, 0.05);
                sound(lv, c, SoundEvents.EVOKER_CAST_SPELL, 1f, 0.6f);
                for (LivingEntity e : around(lv, c, 4.0, x -> validTarget(x, p))) {
                    damage(p, e, power * 0.5f);
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 4));
                    e.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
                }
                return true;
            }
            case "bloom": {
                float heal = 4f + power * 0.6f;
                Vec3 c = p.position();
                for (LivingEntity e : around(lv, c, 6.0, x -> x instanceof Player)) {
                    e.heal(heal);
                    particles(lv, ParticleTypes.HAPPY_VILLAGER, e.position().add(0, 1, 0), 12, 0.5, 0.05);
                }
                ring(lv, pt, c, 4, 30);
                sound(lv, c, SoundEvents.AMETHYST_BLOCK_CHIME, 1f, 1.2f);
                return true;
            }
            case "blink": {
                Vec3 look = p.getLookAngle();
                Vec3 start = p.position();
                Vec3 best = start;
                for (double t = 0.5; t <= 12.0; t += 0.5) {
                    Vec3 test = start.add(look.x * t, look.y * t, look.z * t);
                    AABB bb = p.getBoundingBox().move(test.subtract(start));
                    if (lv.noCollision(p, bb)) best = test;
                    else break;
                }
                particles(lv, pt, start.add(0, 1, 0), 30, 0.4, 0.1);
                p.teleportTo(best.x, best.y, best.z);
                p.fallDistance = 0;
                particles(lv, pt, best.add(0, 1, 0), 30, 0.4, 0.1);
                sound(lv, best, SoundEvents.ENDERMAN_TELEPORT, 1f, 1.3f);
                return true;
            }
            case "rend": {
                Vec3 c = p.position();
                for (LivingEntity e : around(lv, c, 9.0, x -> validTarget(x, p))) {
                    Vec3 dir = c.subtract(e.position()).normalize().scale(1.1);
                    e.setDeltaMovement(dir.x, 0.3, dir.z);
                    e.hurtMarked = true;
                }
                ring(lv, pt, c, 8, 40);
                Scheduler.after(12, () -> {
                    ring(lv, pt, c, 3, 20);
                    particles(lv, ParticleTypes.PORTAL, c.add(0, 1, 0), 60, 1.5, 0.5);
                    for (LivingEntity e : around(lv, c, 4.0, x -> validTarget(x, p))) {
                        damage(p, e, power * 1.2f);
                        rider("void", e);
                    }
                });
                sound(lv, c, SoundEvents.ENDERMAN_TELEPORT, 1f, 0.5f);
                return true;
            }
            case "meteor": {
                Hit h = ray(p, 40);
                Vec3 c = h.pos();
                for (int i = 0; i < 5; i++) {
                    Scheduler.after(i * 5, () -> ring(lv, pt, c, 4, 28));
                }
                Scheduler.after(26, () -> {
                    particles(lv, ParticleTypes.EXPLOSION, c.add(0, 1, 0), 3, 1.5, 0.0);
                    particles(lv, ParticleTypes.LAVA, c.add(0, 1, 0), 40, 2.0, 0.2);
                    sound(lv, c, SoundEvents.FIRECHARGE_USE, 1.5f, 0.5f);
                    for (LivingEntity e : around(lv, c, 4.5, x -> validTarget(x, p))) {
                        damage(p, e, power * 2.0f);
                        e.igniteForSeconds(6);
                    }
                });
                return true;
            }
            default:
                return false;
        }
    }

    private static void chain(ServerPlayer p, LivingEntity first, float dmg, int jumps, double reach) {
        ServerLevel lv = p.serverLevel();
        LivingEntity cur = first;
        List<LivingEntity> hit = new ArrayList<>();
        hit.add(first);
        for (int i = 0; i < jumps; i++) {
            LivingEntity next = null;
            double bd = Double.MAX_VALUE;
            final LivingEntity from = cur;
            for (LivingEntity e : around(lv, cur.position(), reach, x -> validTarget(x, p))) {
                if (hit.contains(e)) continue;
                double dd = e.distanceToSqr(from);
                if (dd < bd) {
                    bd = dd;
                    next = e;
                }
            }
            if (next == null) break;
            line(lv, ParticleTypes.ELECTRIC_SPARK, cur.position().add(0, 1, 0), next.position().add(0, 1, 0));
            damage(p, next, dmg);
            hit.add(next);
            cur = next;
        }
    }
}
