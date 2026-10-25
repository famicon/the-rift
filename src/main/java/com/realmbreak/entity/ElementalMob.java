package com.realmbreak.entity;

import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.ModParticles;
import com.realmbreak.magic.Magic;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.util.EnumSet;

/** Every humanoid Rift/dungeon enemy: knights melee, mages/sprites/wraiths throw hitscan bolts. */
public class ElementalMob extends Monster {
    public final String mobId;
    public final String element;
    public final String style;

    public ElementalMob(EntityType<? extends Monster> type, Level level) {
        super(type, level);
        String key = BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath();
        this.mobId = key;
        JsonObject m = Content.MOBS.get(key);
        this.element = m == null ? "void" : Content.str(m, "element", "void");
        this.style = m == null ? "knight" : Content.str(m, "style", "knight");
        double hp, dmg, spd, armor;
        switch (style) {
            case "knight": hp = 44; dmg = 7; spd = 0.25; armor = 6; break;
            case "mage": hp = 26; dmg = 3; spd = 0.25; armor = 0; break;
            case "wraith": hp = 30; dmg = 5; spd = 0.28; armor = 0; break;
            case "sprite": hp = 20; dmg = 4; spd = 0.3; armor = 0; break;
            case "golem": hp = 70; dmg = 10; spd = 0.2; armor = 4; break;
            default: hp = 36; dmg = 7; spd = 0.32; armor = 2; break;
        }
        getAttribute(Attributes.MAX_HEALTH).setBaseValue(hp);
        getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(dmg);
        getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(spd);
        getAttribute(Attributes.ARMOR).setBaseValue(armor);
        setHealth((float) hp);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 30).add(Attributes.ATTACK_DAMAGE, 6).add(Attributes.MOVEMENT_SPEED, 0.27)
                .add(Attributes.FOLLOW_RANGE, 28).add(Attributes.ARMOR, 2);
    }

    public boolean ranged() {
        return style.equals("mage") || style.equals("sprite") || style.equals("wraith");
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        if (ranged()) this.goalSelector.addGoal(2, new BoltGoal(this));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.1, false));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.9));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 10.0f));
        this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        boolean r = super.doHurtTarget(target);
        if (r && target instanceof LivingEntity le) Magic.rider(element, le);
        return r;
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level() instanceof ServerLevel sl && tickCount % 6 == 0 && random.nextInt(2) == 0) {
            sl.sendParticles(ModParticles.byElement(element), getX(), getY() + getBbHeight() * 0.6, getZ(), 1, 0.3, 0.4, 0.3, 0.01);
        }
    }

    /** Hitscan bolt thrown at the target while in range and line of sight. */
    static final class BoltGoal extends Goal {
        private final ElementalMob mob;
        private int cooldown = 30;

        BoltGoal(ElementalMob mob) {
            this.mob = mob;
            setFlags(EnumSet.of(Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = mob.getTarget();
            return t != null && t.isAlive() && mob.distanceToSqr(t) < 15 * 15 && mob.distanceToSqr(t) > 3.5 * 3.5 && mob.hasLineOfSight(t);
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void tick() {
            LivingEntity t = mob.getTarget();
            if (t == null) return;
            mob.getLookControl().setLookAt(t, 30f, 30f);
            if (--cooldown <= 0) {
                cooldown = 45 + mob.random.nextInt(25);
                if (mob.level() instanceof ServerLevel sl) {
                    ParticleOptions pt = ModParticles.byElement(mob.element);
                    net.minecraft.world.phys.Vec3 from = mob.getEyePosition();
                    net.minecraft.world.phys.Vec3 to = t.position().add(0, t.getBbHeight() * 0.6, 0);
                    Magic.line(sl, pt, from, to);
                    float dmg = (float) mob.getAttributeValue(Attributes.ATTACK_DAMAGE) + 2.0f;
                    t.hurt(mob.damageSources().indirectMagic(mob, mob), dmg);
                    Magic.rider(mob.element, t);
                }
            }
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        return super.hurt(source, amount);
    }
}
