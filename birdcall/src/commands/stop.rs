use serenity::prelude::*;
use serenity::model::prelude::*;
use songbird::SerenityInit;

pub async fn run_stop(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let guild_id = cmd.guild_id.unwrap();

    let manager = songbird::get(ctx).await.unwrap().clone();
    let _ = manager.remove(guild_id).await;

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|m| {
            m.content("🌙 BirdCall spreads its wings and glides out of the channel. Stream ended.")
        })
    }).await.ok();
}
