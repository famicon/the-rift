package com.realmbreak;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/** Loads the generated JSON manifests (shared by client and server). */
public final class Content {
    public static JsonObject content = new JsonObject();
    public static JsonObject story = new JsonObject();
    public static final Map<String, JsonObject> QUESTS = new HashMap<>();
    public static final Map<String, JsonObject> NPCS = new HashMap<>();
    public static final Map<String, JsonObject> MOBS = new HashMap<>();
    private static boolean loaded = false;

    private Content() {}

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(Realmbreak.MOD_ID, path);
    }

    public static synchronized void load() {
        if (loaded) return;
        loaded = true;
        content = read("/realmbreak_content.json");
        story = read("/realmbreak_story.json");
        for (JsonElement e : story.getAsJsonArray("quests")) {
            JsonObject q = e.getAsJsonObject();
            QUESTS.put(q.get("id").getAsString(), q);
        }
        for (JsonElement e : content.getAsJsonArray("npcs")) {
            JsonObject n = e.getAsJsonObject();
            NPCS.put(n.get("id").getAsString(), n);
        }
        for (JsonElement e : content.getAsJsonArray("mobs")) {
            JsonObject n = e.getAsJsonObject();
            MOBS.put(n.get("id").getAsString(), n);
        }
        for (JsonElement e : content.getAsJsonArray("bosses")) {
            JsonObject n = e.getAsJsonObject();
            MOBS.put(n.get("id").getAsString(), n);
        }
    }

    private static JsonObject read(String path) {
        try (InputStream in = Content.class.getResourceAsStream(path)) {
            if (in == null) throw new IllegalStateException("Missing resource " + path);
            return JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (Exception ex) {
            throw new RuntimeException("Failed to load " + path, ex);
        }
    }

    public static JsonArray array(JsonObject o, String key) {
        return o.has(key) && o.get(key).isJsonArray() ? o.getAsJsonArray(key) : new JsonArray();
    }

    public static String str(JsonObject o, String key, String def) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsString() : def;
    }

    public static int num(JsonObject o, String key, int def) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsInt() : def;
    }

    public static double dbl(JsonObject o, String key, double def) {
        return o.has(key) && !o.get(key).isJsonNull() ? o.get(key).getAsDouble() : def;
    }

    public static String npcName(String id) {
        JsonObject n = NPCS.get(id);
        return n == null ? id : str(n, "name", id);
    }
}
