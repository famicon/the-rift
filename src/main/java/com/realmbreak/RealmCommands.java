package com.realmbreak;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.realmbreak.data.PData;
import com.realmbreak.entity.RiftBoss;
import com.realmbreak.net.Net;
import com.realmbreak.quest.Quests;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;

/** /realmbreak debug and convenience commands (op level 2). */
public final class RealmCommands {
    private RealmCommands() {}

    public static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, access, env) -> dispatcher.register(
                Commands.literal("realmbreak").requires(s -> s.hasPermission(2))
                        .then(Commands.literal("rift").executes(ctx -> {
                            ServerPlayer p = ctx.getSource().getPlayerOrException();
                            ServerLevel rift = p.getServer().getLevel(RiftTravel.RIFT);
                            if (rift == null) return 0;
                            if (p.level().dimension() == RiftTravel.RIFT) RiftTravel.leave(p);
                            else RiftTravel.enter(p, p.blockPosition(), rift);
                            return 1;
                        }))
                        .then(Commands.literal("kit").executes(ctx -> {
                            ServerPlayer p = ctx.getSource().getPlayerOrException();
                            for (String id : new String[]{"quest_journal", "seekers_compass", "apprentice_staff", "rift_anchor", "mana_elixir", "vitality_elixir", "tome_of_insight"}) {
                                p.getInventory().add(new net.minecraft.world.item.ItemStack(ModItems.get(id), id.equals("rift_anchor") ? 4 : 2));
                            }
                            return 1;
                        }))
                        .then(Commands.literal("points").then(Commands.argument("n", IntegerArgumentType.integer(0, 100)).executes(ctx -> {
                            ServerPlayer p = ctx.getSource().getPlayerOrException();
                            PData.of(p).addPoints(IntegerArgumentType.getInteger(ctx, "n"));
                            Net.sync(p);
                            return 1;
                        })))
                        .then(Commands.literal("quest")
                                .then(Commands.literal("start").then(Commands.argument("id", StringArgumentType.word()).executes(ctx -> {
                                    ServerPlayer p = ctx.getSource().getPlayerOrException();
                                    var q = Quests.quest(StringArgumentType.getString(ctx, "id"));
                                    if (q == null) { ctx.getSource().sendFailure(Component.literal("No such quest (ids look like l1q1 .. l5q6)")); return 0; }
                                    Quests.start(p, q);
                                    return 1;
                                })))
                                .then(Commands.literal("complete").then(Commands.argument("id", StringArgumentType.word()).executes(ctx -> {
                                    ServerPlayer p = ctx.getSource().getPlayerOrException();
                                    Quests.forceComplete(p, StringArgumentType.getString(ctx, "id"));
                                    return 1;
                                })))
                                .then(Commands.literal("reset").executes(ctx -> {
                                    ServerPlayer p = ctx.getSource().getPlayerOrException();
                                    PData d = PData.of(p);
                                    d.tag.remove("quests");
                                    d.tag.remove("sites");
                                    d.dirty();
                                    Net.sync(p);
                                    return 1;
                                })))
                        .then(Commands.literal("boss").then(Commands.argument("id", StringArgumentType.word()).executes(ctx -> {
                            ServerPlayer p = ctx.getSource().getPlayerOrException();
                            EntityType<?> t = ModEntities.TYPES.get(StringArgumentType.getString(ctx, "id"));
                            if (t == null) return 0;
                            ServerLevel lv = p.serverLevel();
                            Entity e = t.create(lv);
                            if (e instanceof Mob m) {
                                m.moveTo(p.getX() + 4, p.getY(), p.getZ(), 0f, 0f);
                                m.finalizeSpawn(lv, lv.getCurrentDifficultyAt(p.blockPosition()), MobSpawnType.COMMAND, null);
                                lv.addFreshEntity(m);
                            }
                            return 1;
                        })))
                        .then(Commands.literal("cutscene").then(Commands.argument("id", StringArgumentType.word()).executes(ctx -> {
                            ServerPlayer p = ctx.getSource().getPlayerOrException();
                            Cutscenes.play(p, StringArgumentType.getString(ctx, "id"), p.position());
                            return 1;
                        })))
        ));
    }
}
