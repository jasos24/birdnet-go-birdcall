use serenity::prelude::*;
use serenity::model::prelude::*;
use songbird::SerenityInit;
use crate::streamer;
use std::env;

pub async fn run_join(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let guild_id = match cmd.guild_id {
        Some(id) => id,
        None => {
            cmd.create_interaction_response(&ctx.http, |r| {
                r.interaction_response_data(|m| m.content("This command can only be used in a server."))
            }).await.ok();
            return;
        }
    };

    let guild = match guild_id.to_guild_cached(&ctx.cache) {
        Some(g) => g,
        None => {
            cmd.create_interaction_response(&ctx.http, |r| {
                r.interaction_response_data(|m| m.content("Could not fetch guild data."))
            }).await.ok();
            return;
        }
    };

    let voice_state = guild.voice_states.get(&cmd.user.id);
    let connect_to = match voice_state.and_then(|vs| vs.channel_id) {
        Some(ch) => ch,
        None => {
            cmd.create_interaction_response(&ctx.http, |r| {
                r.interaction_response_data(|m| m.content("🪺 You need to be in a voice channel for BirdCall to perch with you"))
            }).await.ok();
            return;
        }
    };

    let manager = songbird::get(ctx).await.unwrap().clone();
    let _ = manager.join(guild_id, connect_to).await;

    let rtmp_url = env::var("RTMP_URL").unwrap();

    tokio::spawn(async move {
        streamer::start_stream(rtmp_url).await;
    });

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|m| {
            m.content("🪶 BirdCall has perched in your channel and is now listening to the wild…")
        })
    }).await.ok();
}
