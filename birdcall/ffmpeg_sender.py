import subprocess
import discord
from .config import STREAM_URL
from .log import logger

class PCMRecorder(discord.AudioSink):
    def __init__(self, ffmpeg_process):
        super().__init__()
        self.ffmpeg = ffmpeg_process

    def write(self, data):
        try:
            self.ffmpeg.stdin.write(data.pcm)
        except BrokenPipeError:
            logger.error("FFmpeg pipe broken")

async def start_ffmpeg():
    cmd = [
        "ffmpeg",
        "-f", "s16le",
        "-ar", "48000",
        "-ac", "2",
        "-i", "-",
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "flv",
        STREAM_URL
    ]

    logger.info(f"Starting FFmpeg → {STREAM_URL}")

    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

async def start_recording(vc):
    ffmpeg = await start_ffmpeg()
    sink = PCMRecorder(ffmpeg)
    vc.start_recording(sink, finished_callback=None)
    return ffmpeg

async def stop_recording(vc, ffmpeg):
    logger.info("Stopping FFmpeg")
    vc.stop_recording()
    if ffmpeg:
        ffmpeg.stdin.close()
        ffmpeg.kill()
