const startBtn = document.getElementById("startBtn");
const statusBadge = document.getElementById("statusBadge");

let pc = null;
let wakeLock = null;

function setStatus(text) {
  statusBadge.textContent = text;
}

async function requestWakeLock() {
  if (!("wakeLock" in navigator)) return;
  try {
    wakeLock = await navigator.wakeLock.request("screen");
  } catch (err) {
    console.warn("Wake lock failed", err);
  }
}

async function startMic() {
  startBtn.disabled = true;
  setStatus("requesting mic");

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    },
  });

  pc = new RTCPeerConnection({ iceServers: [] });
  stream.getTracks().forEach((track) => pc.addTrack(track, stream));

  pc.onconnectionstatechange = () => {
    setStatus(pc.connectionState || "connecting");
  };

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const response = await fetch("/offer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sdp: pc.localDescription.sdp,
      type: pc.localDescription.type,
    }),
  });

  if (!response.ok) {
    throw new Error("Offer rejected");
  }

  const answer = await response.json();
  await pc.setRemoteDescription(answer);

  setStatus("streaming");
  await requestWakeLock();
}

startBtn.addEventListener("click", async () => {
  try {
    await startMic();
  } catch (err) {
    console.error(err);
    setStatus("error");
    startBtn.disabled = false;
  }
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js").catch(() => {});
}
