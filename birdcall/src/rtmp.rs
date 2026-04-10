use std::fs;

pub fn get_rtmp_url() -> String {
    dotenv::var("RTMP_URL").unwrap_or("rtmp://localhost/live/stream".into())
}

pub fn set_rtmp_url(url: &str) {
    let mut env = fs::read_to_string(".env").unwrap_or_default();
    env = env.replace("RTMP_URL=", &format!("RTMP_URL={}", url));
    let _ = fs::write(".env", env);
}
