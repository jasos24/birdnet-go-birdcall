import asyncio
from .log import logger
from .ffmpeg_sender import start_ffmpeg
from .mediamtx import is_mediamtx_alive

async def watchdog(bot):
    await bot.wait_until_ready()
    logger.info("Watchdog started")

    while True:
        try:
            for guild in bot.guilds:
                vc = guild.voice_client

                if not vc:
                    continue

                # FFmpeg crashed?
                if vc.recording and vc.sink.ffmpeg.poll() is not None:
                    logger.error("FFmpeg crashed — restarting")
                    vc.sink.ffmpeg = await start_ffmpeg()

                # MediaMTX health
                if not is_mediamtx_alive():
                    logger.error("MediaMTX unreachable")
                else:
                    logger.info("MediaMTX OK")

        except Exception as e:
            logger.error(f"Watchdog error: {e}")

        await asyncio.sleep(5)
