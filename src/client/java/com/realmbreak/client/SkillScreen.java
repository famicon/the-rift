package com.realmbreak.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import com.realmbreak.net.DataPayload;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Five elemental skill trees. */
public class SkillScreen extends Screen {
    private static final String[] ELS = {"flame", "frost", "storm", "verdant", "void"};
    private static final int[] COLORS = {0xFFFF7A2A, 0xFF7FD4FF, 0xFFF3D84A, 0xFF7CD65C, 0xFFB07CFF};
    private int tab = 0;

    public SkillScreen() {
        super(Component.literal("Elemental Skills"));
    }

    @Override
    protected void init() {
        int bw = 72;
        int x0 = width / 2 - (ELS.length * (bw + 4)) / 2;
        for (int i = 0; i < ELS.length; i++) {
            final int idx = i;
            String label = Character.toUpperCase(ELS[i].charAt(0)) + ELS[i].substring(1);
            addRenderableWidget(Button.builder(Component.literal(label), b -> tab = idx).bounds(x0 + i * (bw + 4), 30, bw, 20).build());
        }
        CompoundTag t = new CompoundTag();
        ClientPlayNetworking.send(new DataPayload("request_sync", t));
    }

    private JsonArray nodes() {
        return Content.story.getAsJsonObject("skills").getAsJsonArray(ELS[tab]);
    }

    private int nx(JsonObject n) {
        return width / 2 + Content.num(n, "x", 0) * 70;
    }

    private int ny(JsonObject n) {
        return 76 + Content.num(n, "y", 0) * 44;
    }

    private boolean available(JsonObject n) {
        if (ClientState.hasSkill(n.get("id").getAsString())) return false;
        for (JsonElement r : n.getAsJsonArray("requires")) if (!ClientState.hasSkill(r.getAsString())) return false;
        return true;
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (super.mouseClicked(mx, my, button)) return true;
        for (JsonElement e : nodes()) {
            JsonObject n = e.getAsJsonObject();
            int x = nx(n), y = ny(n);
            if (mx >= x - 15 && mx <= x + 15 && my >= y - 15 && my <= y + 15 && available(n)) {
                CompoundTag t = new CompoundTag();
                t.putString("id", n.get("id").getAsString());
                ClientPlayNetworking.send(new DataPayload("unlock", t));
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float delta) {
        super.render(g, mx, my, delta);
        g.drawCenteredString(font, "Elemental Skills  -  Points: " + ClientState.points(), width / 2, 12, 0xFFE9C46A);
        Map<String, JsonObject> byId = new HashMap<>();
        for (JsonElement e : nodes()) byId.put(e.getAsJsonObject().get("id").getAsString(), e.getAsJsonObject());
        int col = COLORS[tab];
        // connectors
        for (JsonObject n : byId.values()) {
            for (JsonElement r : n.getAsJsonArray("requires")) {
                JsonObject p = byId.get(r.getAsString());
                if (p == null) continue;
                boolean on = ClientState.hasSkill(r.getAsString());
                int x0 = nx(p), y0 = ny(p), x1 = nx(n), y1 = ny(n);
                int steps = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
                for (int i = 0; i <= steps; i += 2) {
                    int px = x0 + (x1 - x0) * i / Math.max(1, steps);
                    int py = y0 + (y1 - y0) * i / Math.max(1, steps);
                    g.fill(px - 1, py - 1, px + 1, py + 1, on ? col : 0xFF3A3450);
                }
            }
        }
        List<Component> tip = null;
        for (JsonObject n : byId.values()) {
            int x = nx(n), y = ny(n);
            boolean has = ClientState.hasSkill(n.get("id").getAsString());
            boolean av = available(n);
            int fill = has ? 0xFF1E5A2A : (av ? 0xFF5A4A12 : 0xFF2A2638);
            int border = has ? col : (av ? 0xFFFFD166 : 0xFF4A4660);
            g.fill(x - 15, y - 15, x + 15, y + 15, border);
            g.fill(x - 13, y - 13, x + 13, y + 13, fill);
            String lbl = n.has("spell") ? "*" : (n.has("passive") ? "P" : String.valueOf(n.get("cost").getAsInt()));
            g.drawCenteredString(font, lbl, x, y - 4, has ? col : 0xFFFFFFFF);
            if (mx >= x - 15 && mx <= x + 15 && my >= y - 15 && my <= y + 15) {
                tip = new ArrayList<>();
                tip.add(Component.literal(n.get("name").getAsString()));
                tip.add(Component.literal(n.get("desc").getAsString()));
                tip.add(Component.literal(has ? "Unlocked" : "Cost: " + n.get("cost").getAsInt() + (av ? "  (click to unlock)" : "  (locked)")));
            }
        }
        if (tip != null) g.renderComponentTooltip(font, tip, mx, my);
    }
}
