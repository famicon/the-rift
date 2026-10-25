package com.realmbreak.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.ModItems;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.item.ItemStack;

public final class Hud {
    private Hud() {}

    public static void render(GuiGraphics g, DeltaTracker dt) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.options.hideGui && !CutscenePlayer.active()) return;
        int w = g.guiWidth(), h = g.guiHeight();
        if (CutscenePlayer.active()) {
            CutscenePlayer.render(g, w, h);
            return;
        }
        ItemStack main = mc.player.getMainHandItem();
        boolean staff = main.getItem() instanceof ModItems.StaffItem;
        if (staff || ClientState.mana < ClientState.maxMana) {
            int bw = 81, x = w / 2 - 91, y = h - 52;
            g.fill(x - 1, y - 1, x + bw + 1, y + 5, 0xFF000000);
            int fill = ClientState.maxMana <= 0 ? 0 : bw * ClientState.mana / ClientState.maxMana;
            g.fill(x, y, x + fill, y + 4, 0xFF4A7BFF);
            g.fill(x, y, x + fill, y + 1, 0xFF9FC0FF);
            if (staff) g.drawString(mc.font, ClientState.mana + "/" + ClientState.maxMana, x + bw + 4, y - 2, 0xFF9FC0FF, true);
        }
        // quest tracker
        JsonObject q = ClientState.trackedQuest();
        if (q != null && mc.screen == null) {
            String id = q.get("id").getAsString();
            int st = ClientState.questState(id);
            int x = w - 6, y = 6;
            String title = q.get("title").getAsString();
            g.drawString(mc.font, title, x - mc.font.width(title), y, 0xFFE9C46A, true);
            y += 11;
            if (st == 1) {
                String s = "Return to " + Content.npcName(Content.str(q, "turnin", ""));
                g.drawString(mc.font, s, x - mc.font.width(s), y, 0xFFFFD166, true);
            } else {
                JsonArray objs = q.getAsJsonArray("objectives");
                int[] pr = ClientState.questProg(id, objs.size());
                for (int i = 0; i < objs.size(); i++) {
                    JsonObject o = objs.get(i).getAsJsonObject();
                    int need = Content.num(o, "count", 1);
                    if (pr[i] >= need) continue;
                    String s = Content.str(o, "text", "") + (need > 1 ? " (" + pr[i] + "/" + need + ")" : "");
                    g.drawString(mc.font, s, x - mc.font.width(s), y, 0xFFFFFFFF, true);
                    y += 10;
                }
            }
        }
        // compass hint
        if (main.getItem() instanceof ModItems.CompassItem && ClientState.compassValid) {
            double dx = ClientState.compassX + 0.5 - mc.player.getX(), dz = ClientState.compassZ + 0.5 - mc.player.getZ();
            double dist = Math.sqrt(dx * dx + dz * dz);
            double ang = Math.toDegrees(Math.atan2(dz, dx)) - 90.0 - mc.player.getYRot();
            ang = ((ang % 360) + 540) % 360 - 180;
            String arrow = Math.abs(ang) < 20 ? "^" : (ang > 0 ? ">>" : "<<");
            String s = arrow + "  " + ClientState.compassName + "  " + (int) dist + "m  " + arrow;
            g.drawCenteredString(mc.font, s, w / 2, 18, 0xFFE9C46A);
        }
    }
}
