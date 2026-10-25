package com.realmbreak.client;

import com.realmbreak.net.DataPayload;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;

import java.util.ArrayList;
import java.util.List;

/** NPC conversation box: pages of text, then the server-provided action buttons. */
public class DialogueScreen extends Screen {
    private final String npc;
    private final String name;
    private final String title;
    private final List<String> lines = new ArrayList<>();
    private final List<String[]> buttons = new ArrayList<>();
    private int page = 0;

    public DialogueScreen(CompoundTag tag) {
        super(Component.literal(tag.getString("name")));
        this.npc = tag.getString("npc");
        this.name = tag.getString("name");
        this.title = tag.getString("title");
        ListTag l = tag.getList("lines", Tag.TAG_STRING);
        for (int i = 0; i < l.size(); i++) lines.add(l.getString(i));
        ListTag b = tag.getList("buttons", Tag.TAG_COMPOUND);
        for (int i = 0; i < b.size(); i++) {
            CompoundTag bt = b.getCompound(i);
            buttons.add(new String[]{bt.getString("id"), bt.getString("label")});
        }
    }

    @Override
    protected void init() {
        rebuild();
    }

    private void rebuild() {
        clearWidgets();
        int w = Math.min(width - 40, 420);
        int x = (width - w) / 2;
        int bottom = height - 14;
        if (page < lines.size() - 1) {
            addRenderableWidget(Button.builder(Component.literal("Continue"), b -> {
                page++;
                rebuild();
            }).bounds(x + w - 90, bottom - 20, 90, 20).build());
        } else {
            int n = buttons.size();
            int bh = 20;
            int y = bottom - n * (bh + 3);
            for (String[] bt : buttons) {
                final String id = bt[0];
                addRenderableWidget(Button.builder(Component.literal(bt[1]), btn -> act(id)).bounds(x, y, w, bh).build());
                y += bh + 3;
            }
        }
    }

    private void act(String id) {
        if (id.equals("close")) {
            onClose();
            return;
        }
        CompoundTag t = new CompoundTag();
        t.putString("npc", npc);
        t.putString("act", id);
        ClientPlayNetworking.send(new DataPayload("dialogue", t));
        // the server answers with a new dialogue (which replaces this screen) or nothing (so we close)
        if (id.startsWith("complete:") || id.startsWith("accept:") || id.equals("trade") || id.startsWith("buy:")) {
            // keep open; server reply will replace us. Close ourselves if no reply arrives.
            buttons.clear();
            rebuild();
        } else {
            onClose();
        }
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float delta) {
        super.render(g, mouseX, mouseY, delta);
        int w = Math.min(width - 40, 420);
        int x = (width - w) / 2;
        int btnH = page < lines.size() - 1 ? 26 : buttons.size() * 23 + 6;
        int boxBottom = height - 14 - btnH;
        int boxH = 110;
        int boxTop = boxBottom - boxH;
        g.fill(x - 4, boxTop - 4, x + w + 4, boxBottom + 2, 0xE0100818);
        g.fill(x - 3, boxTop - 3, x + w + 3, boxTop - 2, 0xFFB08AF0);
        g.fill(x - 3, boxBottom + 1, x + w + 3, boxBottom + 2, 0xFFB08AF0);
        g.drawString(font, Component.literal(name), x + 4, boxTop + 2, 0xFFE9C46A, true);
        if (!title.isEmpty()) g.drawString(font, Component.literal(title), x + 8 + font.width(name), boxTop + 2, 0xFF9A8FB8, false);
        String text = lines.isEmpty() ? "..." : lines.get(Math.min(page, lines.size() - 1));
        List<FormattedCharSequence> wrapped = font.split(Component.literal(text), w - 8);
        int ty = boxTop + 18;
        for (FormattedCharSequence s : wrapped) {
            g.drawString(font, s, x + 4, ty, 0xFFFFFFFF, false);
            ty += 11;
        }
    }
}
