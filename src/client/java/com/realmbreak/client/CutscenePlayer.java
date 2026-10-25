package com.realmbreak.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.phys.Vec3;

/** Moves a detached camera entity along the shots defined in realmbreak_story.json. */
public final class CutscenePlayer {
    private static JsonArray shots;
    private static int shot, tick;
    private static double ax, ay, az;
    private static ArmorStand cam;
    private static boolean active;
    private static String text = "";
    private static int fade = 0;

    private CutscenePlayer() {}

    public static boolean active() {
        return active;
    }

    public static void start(CompoundTag t) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return;
        JsonObject cs = Content.story.getAsJsonObject("cutscenes").getAsJsonObject(t.getString("id"));
        if (cs == null) return;
        shots = cs.getAsJsonArray("shots");
        if (shots.size() == 0) return;
        ax = t.getDouble("ax");
        ay = t.getDouble("ay");
        az = t.getDouble("az");
        shot = 0;
        tick = 0;
        fade = 0;
        cam = new ArmorStand(EntityType.ARMOR_STAND, mc.level);
        cam.setInvisible(true);
        cam.setNoGravity(true);
        place(0f, true);
        mc.setCameraEntity(cam);
        active = true;
    }

    public static void stop() {
        Minecraft mc = Minecraft.getInstance();
        active = false;
        text = "";
        if (mc.player != null) mc.setCameraEntity(mc.player);
        cam = null;
    }

    private static double lerp(double a, double b, double f) {
        return a + (b - a) * f;
    }

    private static void place(float f, boolean snap) {
        JsonObject s = shots.get(shot).getAsJsonObject();
        JsonArray a = s.getAsJsonArray("from"), b = s.getAsJsonArray("to"), l = s.getAsJsonArray("look");
        double x = ax + lerp(a.get(0).getAsDouble(), b.get(0).getAsDouble(), f);
        double y = ay + lerp(a.get(1).getAsDouble(), b.get(1).getAsDouble(), f);
        double z = az + lerp(a.get(2).getAsDouble(), b.get(2).getAsDouble(), f);
        Vec3 look = new Vec3(ax + l.get(0).getAsDouble(), ay + l.get(1).getAsDouble(), az + l.get(2).getAsDouble());
        double dx = look.x - x, dy = look.y - y, dz = look.z - z;
        float yaw = (float) (Math.toDegrees(Math.atan2(dz, dx)) - 90.0);
        float pitch = (float) -Math.toDegrees(Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)));
        // the armor stand's eye height is ~1.65; position its feet so the eyes land on the target
        double fy = y - cam.getEyeHeight();
        if (snap) {
            cam.setPos(x, fy, z);
            cam.xo = cam.xOld = x;
            cam.yo = cam.yOld = fy;
            cam.zo = cam.zOld = z;
            cam.yRotO = yaw;
            cam.xRotO = pitch;
        } else {
            cam.xo = cam.xOld = cam.getX();
            cam.yo = cam.yOld = cam.getY();
            cam.zo = cam.zOld = cam.getZ();
            cam.yRotO = cam.getYRot();
            cam.xRotO = cam.getXRot();
            cam.setPos(x, fy, z);
        }
        cam.setYRot(yaw);
        cam.setXRot(pitch);
        cam.yHeadRot = yaw;
        cam.yHeadRotO = yaw;
        text = Content.str(s, "text", "");
    }

    public static void tick() {
        if (!active) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || cam == null) {
            stop();
            return;
        }
        if (ClientKeys.SKIP.consumeClick()) {
            stop();
            return;
        }
        int dur = Math.max(1, shots.get(shot).getAsJsonObject().get("dur").getAsInt());
        tick++;
        if (tick >= dur) {
            shot++;
            tick = 0;
            if (shot >= shots.size()) {
                stop();
                return;
            }
            place(0f, true);
            return;
        }
        place(tick / (float) dur, false);
    }

    public static void render(GuiGraphics g, int w, int h) {
        if (!active) return;
        Minecraft mc = Minecraft.getInstance();
        int bar = h / 8;
        g.fill(0, 0, w, bar, 0xFF000000);
        g.fill(0, h - bar, w, h, 0xFF000000);
        if (!text.isEmpty()) {
            var lines = mc.font.split(net.minecraft.network.chat.Component.literal(text), Math.min(w - 40, 360));
            int y = h - bar + 6;
            for (var l : lines) {
                g.drawString(mc.font, l, (w - mc.font.width(l)) / 2, y, 0xFFFFFFFF, true);
                y += 11;
            }
        }
        g.drawString(mc.font, "Backspace: skip", w - 90, 4, 0xFF777777, false);
    }
}
