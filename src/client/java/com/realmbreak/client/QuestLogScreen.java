package com.realmbreak.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.realmbreak.Content;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;

/** Scrollable journal: five questlines, current objectives with progress. */
public class QuestLogScreen extends Screen {
    private record Row(String text, int color, int indent) {}

    private int scroll = 0;
    private final List<Row> rows = new ArrayList<>();

    public QuestLogScreen() {
        super(Component.literal("Riftwalker's Journal"));
    }

    @Override
    protected void init() {
        build();
    }

    private void build() {
        rows.clear();
        String[] roman = {"I", "II", "III", "IV", "V"};
        JsonArray lines = Content.story.getAsJsonArray("lines");
        List<JsonObject> quests = ClientState.quests();
        for (JsonElement le : lines) {
            JsonObject line = le.getAsJsonObject();
            int id = line.get("id").getAsInt();
            int done = 0, total = 0;
            List<JsonObject> mine = new ArrayList<>();
            for (JsonObject q : quests) if (q.get("line").getAsInt() == id) { mine.add(q); total++; if (ClientState.questState(q.get("id").getAsString()) == 2) done++; }
            rows.add(new Row(roman[id - 1] + ". " + line.get("name").getAsString() + "  (" + done + "/" + total + ")", 0xFFE9C46A, 0));
            if (done == 0 && ClientState.questState(mine.get(0).get("id").getAsString()) == -1) {
                boolean unlocked = id == 1 || ClientState.questState("l1q2") == 2;
                rows.add(new Row(unlocked ? "Seek " + Content.npcName(line.get("npc").getAsString()) + " to begin." : "Locked: finish 'Through the Scar' first.", 0xFF8A8A9A, 1));
                continue;
            }
            for (JsonObject q : mine) {
                String qid = q.get("id").getAsString();
                int st = ClientState.questState(qid);
                if (st == -1) continue;
                String title = q.get("title").getAsString();
                if (st == 2) {
                    rows.add(new Row("[x] " + title, 0xFF6FBF73, 1));
                    continue;
                }
                rows.add(new Row((st == 1 ? "[!] " : "[ ] ") + title + (st == 1 ? "  - return to " + Content.npcName(Content.str(q, "turnin", "")) : ""), st == 1 ? 0xFFFFD166 : 0xFFFFFFFF, 1));
                if (st == 0) {
                    JsonArray objs = q.getAsJsonArray("objectives");
                    int[] pr = ClientState.questProg(qid, objs.size());
                    for (int i = 0; i < objs.size(); i++) {
                        JsonObject o = objs.get(i).getAsJsonObject();
                        int need = Content.num(o, "count", 1);
                        String txt = Content.str(o, "text", o.get("type").getAsString());
                        String prog = need > 1 ? " (" + Math.min(pr[i], need) + "/" + need + ")" : "";
                        boolean ok = pr[i] >= need;
                        String tag = Content.str(o, "dim", "").equals("rift") ? " [Rift]" : "";
                        rows.add(new Row((ok ? "  + " : "  - ") + txt + prog + tag, ok ? 0xFF6FBF73 : 0xFFC9C9D6, 2));
                    }
                }
            }
        }
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        scroll = Math.max(0, Math.min(Math.max(0, rows.size() * 11 - (height - 60)), scroll - (int) (sy * 22)));
        return true;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void render(GuiGraphics g, int mx, int my, float delta) {
        build();
        super.render(g, mx, my, delta);
        int w = Math.min(width - 30, 440);
        int x = (width - w) / 2;
        g.fill(x - 6, 14, x + w + 6, height - 14, 0xE0100818);
        g.drawCenteredString(font, "Riftwalker's Journal", width / 2, 20, 0xFFE9C46A);
        g.drawString(font, "Skill points: " + ClientState.points() + "   Mana: " + ClientState.mana + "/" + ClientState.maxMana, x, 20, 0xFF9AD0FF, false);
        g.enableScissor(x - 4, 36, x + w + 4, height - 18);
        int y = 40 - scroll;
        for (Row r : rows) {
            g.drawString(font, r.text, x + r.indent * 10, y, r.color, false);
            y += 11;
        }
        g.disableScissor();
    }
}
