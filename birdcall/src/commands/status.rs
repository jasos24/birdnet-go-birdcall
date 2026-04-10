use serenity::prelude::*;
use serenity::model::prelude::*;
use songbird::SerenityInit;

pub async fn run_status(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let guild_id = cmd.guild_id.unwrap();
    let manager = songbird::get(ctx).await.unwrap().clone();
    let call = manager.get(guild_id);

    let msg = if call.is_some() {
        "👂 BirdCall is perched and listening to the forest right now."
    } else {
        "🪺 BirdCall is resting in its nest — not streaming at the moment."
    };

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|m| m.content(msg))
    }).await.ok();
}
