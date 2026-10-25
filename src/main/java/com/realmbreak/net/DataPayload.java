package com.realmbreak.net;

import com.realmbreak.Content;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** One generic payload used both directions; the channel string selects the handler. */
public record DataPayload(String channel, CompoundTag tag) implements CustomPacketPayload {
    public static final CustomPacketPayload.Type<DataPayload> TYPE = new CustomPacketPayload.Type<>(Content.id("data"));
    public static final StreamCodec<RegistryFriendlyByteBuf, DataPayload> CODEC = StreamCodec.composite(
            ByteBufCodecs.STRING_UTF8, DataPayload::channel,
            ByteBufCodecs.COMPOUND_TAG, DataPayload::tag,
            DataPayload::new);

    @Override
    public CustomPacketPayload.Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
