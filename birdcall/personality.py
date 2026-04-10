import random

JOIN_PUNS = [
    "🪶 I’ve fluttered into your channel — tuning my feathers to the forest frequencies!",
    "🪺 I’ve landed! Let’s see what the wild is whispering today.",
    "🐦 Perched and ready — let the chirps commence.",
    "🌿 I’m in! Time to eavesdrop on nature’s gossip.",
]

STOP_PUNS = [
    "🌙 I’m gliding out — may your skies stay clear and your birds stay chatty.",
    "🪽 I’m off to another branch. Stream ended!",
    "🍃 I’ve taken wing — silence returns to the forest.",
    "🐤 Stream stopped! I’ll be nesting until you need me again.",
]

STATUS_ON_PUNS = [
    "👂 My little bird ears are wide open — stream is soaring smoothly!",
    "🦅 I hear everything — the forest is alive.",
    "🌤️ Clear skies and clean audio — all good!",
]

STATUS_OFF_PUNS = [
    "🪺 I’m perched quietly in my nest — no stream at the moment.",
    "🌙 Not a chirp to hear — I’m resting.",
    "🍂 No stream right now — just rustling leaves.",
]

RECONNECT_PUNS = [
    "🔄 Flapping my wings and re‑perching — stream refreshed and chirping again!",
    "🦅 Quick loop‑de‑loop! I’m back on the branch.",
    "🌬️ A gust knocked me off — but I’m back and listening.",
]

SETRTMP_PUNS = [
    "📡 New nest located! I’ll stream my chirps to that branch from now on.",
    "🪶 RTMP updated — aiming my beak at the new destination.",
    "🐣 Got it! I’ll send all future squawks there.",
]

PING_PUNS = [
    "🫧 Chirp‑chirp! Systems are flapping beautifully.",
    "🐦 Still perched, still listening, still fabulous.",
    "🌤️ All clear skies — no storms in sight.",
]

def pick(pun_list):
    return random.choice(pun_list)
