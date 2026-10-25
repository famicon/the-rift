package com.realmbreak.entity;

import com.realmbreak.Content;
import com.realmbreak.ModParticles;
import com.realmbreak.Scheduler;
import com.realmbreak.magic.Magic;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/** The five elemental guardians. Abilities are telegraphed (ring particles) and scale across three phases. */
public class RiftBoss extends Monster {
    public final String bossId;
    public final String element;
    private final ServerBossEvent bar;
    private int abilityCd = 100;
    private int phase = 1;

    public RiftBoss(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        this.bossId = BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath();
        com.google.gson.JsonObject m = Content.MOBS.get(bossId);
        this.element = m == null ? "void" : Content.str(m, "element", "void");
        BossEvent.BossBarColor color;
        switch (element) {
            case "flame": color = BossEvent.BossBarColor.RED; break;
            case "frost": color = BossEvent.BossBarColor.BLUE; break;
            case "storm": color = BossEvent.BossBarColor.YELLOW; break;
            case "verdant": color = BossEvent.BossBarColor.GREEN; break;
            default: color = BossEvent.BossBarColor.PURPLE; break;
        }
        this.bar = new ServerBossEvent(Component.literal(m == null ? bossId : Content.str(m, "name", bossId)), color, BossEvent.BossBarOverlay.NOTCHED_10);
        this.xpReward = 120;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 450).add(Attributes.ATTACK_DAMAGE, 11).add(Attributes.MOVEMENT_SPEED, 0.3)
                .add(Attributes.FOLLOW_RANGE, 48).add(Attributes.KNOCKBACK_RESISTANCE, 0.85).add(Attributes.ARMOR, 8).add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public boolean removeWhenFarAway(double d) {
        return false;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return true;
    }

    @Override
    public void startSeenByPlayer(ServerPlayer p) {
        super.startSeenByPlayer(p);
        bar.addPlayer(p);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer p) {
        super.stopSeenByPlayer(p);
        bar.removePlayer(p);
    }

    @Override
    public void setCustomName(Component name) {
        super.setCustomName(name);
        bar.setName(getDisplayName());
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Phase", phase);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        phase = Math.max(1, tag.getInt("Phase"));
        if (hasCustomName()) bar.setName(getDisplayName());
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        // the guardian ignores fall/void-free chip damage from suffocation
        if (source.is(net.minecraft.tags.DamageTypeTags.IS_FALL)) return false;
        return super.hurt(source, amount);
    }

    // ------------------------------------------------------------------ AI
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        bar.setProgress(getHealth() / getMaxHealth());
        float frac = getHealth() / getMaxHealth();
        int newPhase = frac > 0.66f ? 1 : (frac > 0.33f ? 2 : 3);
        if (newPhase != phase) {
            phase = newPhase;
            if (level() instanceof ServerLevel sl) {
                Magic.ring(sl, ModParticles.byElement(element), position(), 6, 40);
                sl.playSound(null, getX(), getY(), getZ(), SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 1.5f, 1.2f);
                for (ServerPlayer p : players(40)) p.sendSystemMessage(Component.literal(getDisplayName().getString() + " grows furious! (Phase " + phase + ")").withStyle(net.minecraft.ChatFormatting.DARK_PURPLE));
            }
            abilityCd = Math.min(abilityCd, 30);
        }
        if (getTarget() == null || !(level() instanceof ServerLevel)) return;
        if (--abilityCd <= 0) {
            abilityCd = Math.max(45, 105 - phase * 20) + random.nextInt(30);
            useAbility((ServerLevel) level());
        }
    }

    private List<ServerPlayer> players(double r) {
        List<ServerPlayer> out = new ArrayList<>();
        if (level() instanceof ServerLevel sl) {
            for (ServerPlayer p : sl.players()) {
                if (p.isAlive() && !p.isSpectator() && !p.isCreative() && p.distanceTo(this) <= r) out.add(p);
            }
        }
        return out;
    }

    private int minions(ServerLevel sl) {
        return sl.getEntitiesOfClass(ElementalMob.class, getBoundingBox().inflate(32)).size() + sl.getEntitiesOfClass(ElementalSpider.class, getBoundingBox().inflate(32)).size();
    }

    private ParticleOptions pt() {
        return ModParticles.byElement(element);
    }

    /** Telegraph a ring at c, then run boom after the delay. */
    private void telegraph(ServerLevel sl, Vec3 c, double r, int delay, Runnable boom) {
        for (int t = 0; t < delay; t += 5) {
            final int tt = t;
            Scheduler.after(Math.max(1, t), () -> {
                if (isAlive()) Magic.ring(sl, pt(), c, r * (0.4 + 0.6 * tt / (double) delay), 24);
            });
        }
        Scheduler.after(delay, () -> {
            if (isAlive()) boom.run();
        });
    }

    private void hitPlayers(ServerLevel sl, Vec3 c, double r, float dmg, java.util.function.Consumer<LivingEntity> extra) {
        for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(r), x -> x instanceof Player pl && !pl.isCreative() && !pl.isSpectator())) {
            if (e.position().distanceTo(c) <= r + 0.5) {
                e.hurt(damageSources().indirectMagic(this, this), dmg);
                if (extra != null) extra.accept(e);
            }
        }
    }

    private void summon(ServerLevel sl, String mobId, int count) {
        if (minions(sl) >= 5) return;
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(Content.id(mobId));
        for (int i = 0; i < count; i++) {
            Entity e = type.create(sl);
            if (e instanceof net.minecraft.world.entity.Mob mob) {
                double a = random.nextDouble() * Math.PI * 2;
                mob.moveTo(getX() + Math.cos(a) * 4, getY(), getZ() + Math.sin(a) * 4, random.nextFloat() * 360f, 0f);
                mob.finalizeSpawn(sl, sl.getCurrentDifficultyAt(blockPosition()), MobSpawnType.MOB_SUMMONED, null);
                if (getTarget() != null) mob.setTarget(getTarget());
                sl.addFreshEntity(mob);
                Magic.particles(sl, ParticleTypes.POOF, mob.position().add(0, 1, 0), 12, 0.4, 0.05);
            }
        }
    }

    private void knock(LivingEntity e, Vec3 from, double power) {
        Vec3 dir = e.position().subtract(from).multiply(1, 0, 1);
        if (dir.lengthSqr() < 0.01) dir = new Vec3(1, 0, 0);
        dir = dir.normalize().scale(power);
        e.setDeltaMovement(dir.x, 0.45, dir.z);
        e.hurtMarked = true;
    }

    private void useAbility(ServerLevel sl) {
        int pick = random.nextInt(phase >= 3 ? 4 : (phase == 2 ? 3 : 2));
        List<ServerPlayer> targets = players(34);
        if (targets.isEmpty()) return;
        switch (bossId) {
            case "ignarax": ignarax(sl, pick, targets); break;
            case "hrimgar": hrimgar(sl, pick, targets); break;
            case "zephyra": zephyra(sl, pick, targets); break;
            case "sylvara": sylvara(sl, pick, targets); break;
            default: nyxoth(sl, pick, targets); break;
        }
    }

    private void strikeAt(ServerLevel sl, ServerPlayer p, double r, int delay, float dmg, java.util.function.Consumer<LivingEntity> extra, boolean bolt) {
        final Vec3 c = p.position();
        telegraph(sl, c, r, delay, () -> {
            if (bolt) Magic.lightning(sl, c);
            Magic.particles(sl, pt(), c.add(0, 0.5, 0), 30, r * 0.4, 0.1);
            hitPlayers(sl, c, r, dmg, extra);
        });
    }

    // ---- Ignarax (flame)
    private void ignarax(ServerLevel sl, int pick, List<ServerPlayer> t) {
        switch (pick) {
            case 0: {
                Vec3 c = position();
                telegraph(sl, c, 8, 30, () -> {
                    Magic.particles(sl, ParticleTypes.LAVA, c.add(0, 1, 0), 40, 3.0, 0.2);
                    sl.playSound(null, c.x, c.y, c.z, SoundEvents.FIRECHARGE_USE, SoundSource.HOSTILE, 2f, 0.5f);
                    hitPlayers(sl, c, 8, 10f, e -> { e.igniteForSeconds(5); knock(e, c, 1.1); });
                });
                break;
            }
            case 1:
                for (int i = 0; i < Math.min(3, t.size()); i++) {
                    final ServerPlayer p = t.get(i);
                    for (int k = 0; k < 3; k++) Scheduler.after(k * 15, () -> { if (p.isAlive()) strikeAt(sl, p, 3.0, 28, 9f, e -> e.igniteForSeconds(4), false); });
                }
                break;
            case 2:
                summon(sl, "cinder_knight", 2);
                break;
            default: {
                LivingEntity target = getTarget();
                if (target != null) {
                    Vec3 dir = target.position().subtract(position()).normalize();
                    setDeltaMovement(dir.x * 1.3, 0.7, dir.z * 1.3);
                    hurtMarked = true;
                    Scheduler.after(16, () -> {
                        if (!isAlive()) return;
                        Vec3 c = position();
                        Magic.particles(sl, ParticleTypes.EXPLOSION, c.add(0, 1, 0), 3, 1.5, 0);
                        hitPlayers(sl, c, 5, 12f, e -> { e.igniteForSeconds(4); knock(e, c, 1.2); });
                    });
                }
                break;
            }
        }
    }

    // ---- Hrimgar (frost)
    private void hrimgar(ServerLevel sl, int pick, List<ServerPlayer> t) {
        switch (pick) {
            case 0: {
                Vec3 c = position();
                telegraph(sl, c, 9, 30, () -> {
                    Magic.particles(sl, ParticleTypes.SNOWFLAKE, c.add(0, 1, 0), 60, 3.5, 0.2);
                    sl.playSound(null, c.x, c.y, c.z, SoundEvents.GLASS_BREAK, SoundSource.HOSTILE, 2f, 0.6f);
                    hitPlayers(sl, c, 9, 8f, e -> { Magic.rider("frost", e); e.setTicksFrozen(220); knock(e, c, 0.9); });
                });
                break;
            }
            case 1:
                for (int i = 0; i < Math.min(4, t.size()); i++) {
                    final ServerPlayer p = t.get(i);
                    for (int k = 0; k < 3; k++) Scheduler.after(k * 12, () -> { if (p.isAlive()) strikeAt(sl, p, 2.2, 24, 8f, e -> Magic.rider("frost", e), false); });
                }
                break;
            case 2:
                summon(sl, "rime_wraith", 2);
                break;
            default:
                for (int k = 0; k < 6; k++) {
                    Scheduler.after(k * 14, () -> {
                        if (!isAlive()) return;
                        Magic.particles(sl, ParticleTypes.SNOWFLAKE, position().add(0, 2, 0), 50, 6.0, 0.1);
                        hitPlayers(sl, position(), 13, 3f, e -> e.setTicksFrozen(Math.min(e.getTicksRequiredToFreeze() + 40, e.getTicksFrozen() + 50)));
                    });
                }
                break;
        }
    }

    // ---- Zephyra (storm)
    private void zephyra(ServerLevel sl, int pick, List<ServerPlayer> t) {
        switch (pick) {
            case 0:
                for (ServerPlayer p : t) strikeAt(sl, p, 2.6, 30, 10f, e -> Magic.rider("storm", e), true);
                break;
            case 1: {
                Vec3 c = position();
                telegraph(sl, c, 10, 24, () -> {
                    Magic.particles(sl, ParticleTypes.CLOUD, c.add(0, 1, 0), 60, 4.0, 0.3);
                    sl.playSound(null, c.x, c.y, c.z, SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.HOSTILE, 1.5f, 1.5f);
                    hitPlayers(sl, c, 10, 5f, e -> knock(e, c, 1.6));
                });
                break;
            }
            case 2:
                summon(sl, "storm_sprite", 3);
                break;
            default:
                for (int k = 0; k < 8; k++) {
                    Scheduler.after(k * 10, () -> {
                        if (!isAlive()) return;
                        Vec3 c = position().add((random.nextDouble() - 0.5) * 20, 0, (random.nextDouble() - 0.5) * 20);
                        telegraph(sl, c, 2.5, 20, () -> {
                            Magic.lightning(sl, c);
                            hitPlayers(sl, c, 2.5, 9f, e -> Magic.rider("storm", e));
                        });
                    });
                }
                break;
        }
    }

    // ---- Sylvara (verdant)
    private void sylvara(ServerLevel sl, int pick, List<ServerPlayer> t) {
        switch (pick) {
            case 0:
                for (ServerPlayer p : t) strikeAt(sl, p, 2.8, 26, 6f, e -> {
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 70, 5));
                    e.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
                }, false);
                break;
            case 1: {
                Vec3 c = position();
                telegraph(sl, c, 8, 28, () -> {
                    Magic.particles(sl, ParticleTypes.COMPOSTER, c.add(0, 1, 0), 60, 3.5, 0.2);
                    hitPlayers(sl, c, 8, 9f, e -> { e.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0)); knock(e, c, 1.0); });
                });
                break;
            }
            case 2:
                summon(sl, "thorn_stalker", 2);
                summon(sl, "bark_guardian", 1);
                break;
            default:
                heal(getMaxHealth() * 0.03f);
                Magic.particles(sl, ParticleTypes.HAPPY_VILLAGER, position().add(0, 2, 0), 30, 1.5, 0.1);
                Vec3 c = position();
                telegraph(sl, c, 6, 30, () -> hitPlayers(sl, c, 6, 7f, e -> e.addEffect(new MobEffectInstance(MobEffects.POISON, 120, 1))));
                break;
        }
    }

    // ---- Nyxoth (void)
    private void nyxoth(ServerLevel sl, int pick, List<ServerPlayer> t) {
        switch (pick) {
            case 0: {
                ServerPlayer p = t.get(random.nextInt(t.size()));
                Vec3 behind = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(-3));
                Magic.particles(sl, ParticleTypes.PORTAL, position().add(0, 2, 0), 40, 1.0, 0.5);
                teleportTo(behind.x, p.getY(), behind.z);
                Magic.particles(sl, ParticleTypes.PORTAL, position().add(0, 2, 0), 40, 1.0, 0.5);
                sl.playSound(null, getX(), getY(), getZ(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.HOSTILE, 1.5f, 0.6f);
                Vec3 c = position();
                telegraph(sl, c, 4.5, 14, () -> hitPlayers(sl, c, 4.5, 8f, e -> { Magic.rider("void", e); knock(e, c, 0.9); }));
                break;
            }
            case 1: {
                Vec3 c = position();
                for (int k = 0; k < 6; k++) {
                    Scheduler.after(k * 8, () -> {
                        if (!isAlive()) return;
                        Magic.ring(sl, pt(), c, 12 - k2(c), 36);
                        for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, new AABB(c, c).inflate(15), x -> x instanceof Player pl && !pl.isCreative() && !pl.isSpectator())) {
                            Vec3 dir = c.subtract(e.position()).multiply(1, 0, 1);
                            if (dir.lengthSqr() > 1) {
                                dir = dir.normalize().scale(0.55);
                                e.setDeltaMovement(e.getDeltaMovement().add(dir.x, 0.05, dir.z));
                                e.hurtMarked = true;
                            }
                        }
                    });
                }
                Scheduler.after(52, () -> {
                    if (!isAlive()) return;
                    Magic.particles(sl, ParticleTypes.REVERSE_PORTAL, c.add(0, 1, 0), 80, 2.5, 0.3);
                    hitPlayers(sl, c, 4.5, 13f, e -> Magic.rider("void", e));
                });
                break;
            }
            case 2:
                summon(sl, "rift_wraith", 2);
                break;
            default: {
                Vec3 c = position();
                telegraph(sl, c, 11, 45, () -> {
                    Magic.particles(sl, ParticleTypes.REVERSE_PORTAL, c.add(0, 1.5, 0), 120, 4.0, 0.4);
                    sl.playSound(null, c.x, c.y, c.z, SoundEvents.WITHER_BREAK_BLOCK, SoundSource.HOSTILE, 2f, 0.6f);
                    hitPlayers(sl, c, 11, 16f, e -> { Magic.rider("void", e); e.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 30, 1)); });
                });
                break;
            }
        }
    }

    private static double k2(Vec3 c) {
        return 0;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (level() instanceof ServerLevel sl) {
            Magic.particles(sl, ParticleTypes.EXPLOSION_EMITTER, position().add(0, 2, 0), 2, 0.5, 0);
            for (ServerPlayer p : players(60)) {
                p.sendSystemMessage(Component.literal(getDisplayName().getString() + " has fallen!").withStyle(net.minecraft.ChatFormatting.GOLD));
            }
        }
        bar.setProgress(0f);
        bar.removeAllPlayers();
    }
}
