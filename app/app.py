from __future__ import annotations

import asyncio
import json
import os
import threading
from typing import Optional

from flask import Flask, jsonify, render_template, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription
from av.audio.resampler import AudioResampler

AUDIO_FIFO = os.environ.get("AUDIO_FIFO", "/audio/in.pcm")

app = Flask(__name__, static_folder="static", template_folder="templates")

pcs = set()


class AudioPipe:
    def __init__(self, path: str) -> None:
        self.path = path
        self._file: Optional[object] = None
        self._lock = threading.Lock()
        self._opening = False

        self._ensure_fifo()
        self._open_in_background()

    def _ensure_fifo(self) -> None:
        if os.path.exists(self.path):
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            os.mkfifo(self.path)
        except FileExistsError:
            pass

    def _open_in_background(self) -> None:
        if self._opening:
            return
        self._opening = True

        def _worker() -> None:
            try:
                # This blocks until a reader opens the FIFO.
                with open(self.path, "wb", buffering=0) as f:
                    with self._lock:
                        self._file = f
                    while True:
                        # Keep the handle open until we are replaced.
                        if self._file is not f:
                            break
                        threading.Event().wait(0.5)
            except Exception:
                pass
            finally:
                with self._lock:
                    if self._file is not None:
                        try:
                            self._file.close()
                        except Exception:
                            pass
                        self._file = None
                self._opening = False

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def write(self, data: bytes) -> None:
        with self._lock:
            f = self._file
        if f is None:
            if not self._opening:
                self._open_in_background()
            return
        try:
            f.write(data)
        except BrokenPipeError:
            with self._lock:
                try:
                    f.close()
                except Exception:
                    pass
                self._file = None
            self._open_in_background()


audio_pipe = AudioPipe(AUDIO_FIFO)


async def _consume_audio(track) -> None:
    resampler = AudioResampler(format="s16", layout="mono", rate=48000)
    try:
        while True:
            frame = await track.recv()
            frames = resampler.resample(frame)
            if not frames:
                continue
            if not isinstance(frames, list):
                frames = [frames]
            for item in frames:
                data = item.to_ndarray().tobytes()
                audio_pipe.write(data)
    except Exception:
        return


async def _handle_offer(offer_sdp: str, offer_type: str) -> dict:
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            asyncio.create_task(_consume_audio(track))

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type=offer_type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(app.static_folder, "manifest.webmanifest")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(app.static_folder, "service-worker.js")


@app.route("/offer", methods=["POST"])
def offer():
    params = request.get_json(force=True)
    offer_sdp = params.get("sdp")
    offer_type = params.get("type")
    if not offer_sdp or not offer_type:
        return jsonify({"error": "Invalid SDP offer"}), 400

    result = asyncio.run(_handle_offer(offer_sdp, offer_type))
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
