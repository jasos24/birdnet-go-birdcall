use serenity::prelude::*;
use serenity::model::prelude::*;
use songbird::SerenityInit;

pub async fn run(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let guild_id = cmd.guild_id.unwrap();
    let manager = songbird::get(ctx).await.unwrap().clone();

    let msg = if manager.get(guild_id).is_some() {
        "👂 BirdCall is listening to the forest."
    } else {
        "🪺 BirdCall is resting in its nest."
    };

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|d| d.content(msg))
    })
    .await
    .ok();
}
