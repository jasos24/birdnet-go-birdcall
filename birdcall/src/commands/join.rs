use serenity::prelude::*;
use serenity::model::prelude::*;
use songbird::SerenityInit;

use crate::pipeline;
use crate::rtmp;

pub async fn run(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let guild_id = cmd.guild_id.unwrap();

    let guild = ctx.http.get_guild(guild_id).await.unwrap();
    let voice_state = guild.voice_states.get(&cmd.user.id);

    let channel = match voice_state.and_then(|vs| vs.channel_id) {
        Some(ch) => ch,
        None => {
            cmd.create_interaction_response(&ctx.http, |r| {
                r.interaction_response_data(|d| d.content("🪺 You must be in a voice channel."))
            })
            .await
            .ok();
            return;
        }
    };

    let manager = songbird::get(ctx).await.unwrap().clone();
    let (_, handler) = manager.join(guild_id, channel).await;

    // Start GStreamer → FFmpeg → RTMP pipeline
    let rtmp_url = rtmp::get_rtmp_url();
    pipeline::start_pipeline(handler.lock().await, rtmp_url);

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|d| d.content("🪶 BirdCall is perched and listening…"))
    })
    .await
    .ok();
}
