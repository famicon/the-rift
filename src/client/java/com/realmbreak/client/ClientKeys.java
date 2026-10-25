package com.realmbreak.client;

import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.KeyMapping;
import org.lwjgl.glfw.GLFW;

public final class ClientKeys {
    public static final String CAT = "key.categories.realmbreak";
    public static final KeyMapping QUEST_LOG = new KeyMapping("key.realmbreak.quest_log", GLFW.GLFW_KEY_J, CAT);
    public static final KeyMapping SKILLS = new KeyMapping("key.realmbreak.skill_tree", GLFW.GLFW_KEY_K, CAT);
    public static final KeyMapping CYCLE = new KeyMapping("key.realmbreak.cycle", GLFW.GLFW_KEY_V, CAT);
    public static final KeyMapping SKIP = new KeyMapping("key.realmbreak.skip", GLFW.GLFW_KEY_BACKSPACE, CAT);

    private ClientKeys() {}

    public static void register() {
        KeyBindingHelper.registerKeyBinding(QUEST_LOG);
        KeyBindingHelper.registerKeyBinding(SKILLS);
        KeyBindingHelper.registerKeyBinding(CYCLE);
        KeyBindingHelper.registerKeyBinding(SKIP);
    }
}
