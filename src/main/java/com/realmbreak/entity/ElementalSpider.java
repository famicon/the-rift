package com.realmbreak.entity;

import com.realmbreak.Content;
import com.realmbreak.ModParticles;
import com.realmbreak.magic.Magic;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.level.Level;

/** Frost Crawler and Thorn Stalker: wall-climbing spiders with an elemental bite. */
public class ElementalSpider extends Spider {
    public final String element;

    public ElementalSpider(EntityType<? extends Spider> type, Level level) {
        super(type, level);
        String key = BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath();
        com.google.gson.JsonObject m = Content.MOBS.get(key);
        this.element = m == null ? "frost" : Content.str(m, "element", "frost");
        getAttribute(Attributes.MAX_HEALTH).setBaseValue(30);
        setHealth(30f);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Spider.createAttributes().add(Attributes.MAX_HEALTH, 30).add(Attributes.ATTACK_DAMAGE, 6).add(Attributes.MOVEMENT_SPEED, 0.34);
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
        if (level() instanceof ServerLevel sl && tickCount % 8 == 0) {
            sl.sendParticles(ModParticles.byElement(element), getX(), getY() + 0.4, getZ(), 1, 0.4, 0.2, 0.4, 0.01);
        }
    }
}
