use serenity::prelude::*;
use serenity::model::prelude::*;

use crate::pipeline;
use crate::rtmp;

pub async fn run(ctx: &Context, cmd: &ApplicationCommandInteraction) {
    let rtmp_url = rtmp::get_rtmp_url();

    pipeline::restart_pipeline(rtmp_url);

    cmd.create_interaction_response(&ctx.http, |r| {
        r.interaction_response_data(|d| d.content("🔄 BirdCall refreshed the audio stream."))
    })
    .await
    .ok();
}
