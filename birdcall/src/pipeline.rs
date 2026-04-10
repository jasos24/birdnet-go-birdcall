use gstreamer as gst;
use gstreamer::prelude::*;
use songbird::input::reader::Reader;
use songbird::Call;
use std::process::{Command, Stdio};
use std::sync::{Arc, Mutex};

static mut PIPELINE: Option<Arc<Mutex<gst::Pipeline>>> = None;

pub fn start_pipeline(handler: std::sync::Arc<tokio::sync::Mutex<Call>>, rtmp_url: String) {
    gst::init().unwrap();

    let pipeline = gst::Pipeline::new(None);

    let appsrc = gst::ElementFactory::make("appsrc", None).unwrap();
    let wavenc = gst::ElementFactory::make("wavenc", None).unwrap();
    let filesink = gst::ElementFactory::make("filesink", None).unwrap();

    filesink.set_property("location", "/tmp/birdcall.wav");

    pipeline.add_many(&[&appsrc, &wavenc, &filesink]).unwrap();
    gst::Element::link_many(&[&appsrc, &wavenc, &filesink]).unwrap();

    pipeline.set_state(gst::State::Playing).unwrap();

    unsafe {
        PIPELINE = Some(Arc::new(Mutex::new(pipeline)));
    }

    tokio::spawn(async move {
        let mut handler = handler.lock().await;
        let mut reader = Reader::new(&mut handler);

        let mut ffmpeg = Command::new("ffmpeg")
            .arg("-re")
            .arg("-i")
            .arg("/tmp/birdcall.wav")
            .arg("-c:a")
            .arg("aac")
            .arg("-f")
            .arg("flv")
            .arg(&rtmp_url)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .unwrap();

        let _ = ffmpeg.wait();
    });
}

pub fn restart_pipeline(rtmp_url: String) {
    stop_pipeline();
    // restart logic handled by join or reconnect
}

pub fn stop_pipeline() {
    unsafe {
        if let Some(p) = &PIPELINE {
            let p = p.lock().unwrap();
            p.set_state(gst::State::Null).unwrap();
        }
    }
}
