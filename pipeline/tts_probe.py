"""Check whether the edge-tts service is answering. Usage: python tts_probe.py [tries] [seconds between tries] [--new-host]"""
import asyncio, sys, time
import edge_tts
import edge_tts.communicate as _c
from edge_tts.constants import TRUSTED_CLIENT_TOKEN

if "--new-host" in sys.argv:
    # Workaround from edge-tts PR #491 (Oct 2026): the legacy Bing host answers 403; Edge now uses this Microsoft host.
    _c.WSS_URL = "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=" + TRUSTED_CLIENT_TOKEN
args = [a for a in sys.argv[1:] if not a.startswith("--")]


async def once():
    n = 0
    async for chunk in edge_tts.Communicate("Testing one two three.", "en-US-AndrewMultilingualNeural").stream():
        if chunk["type"] == "audio":
            n += len(chunk["data"])
    return n


tries, gap = int(args[0]) if args else 1, int(args[1]) if len(args) > 1 else 20
for i in range(tries):
    try:
        print(time.strftime("%H:%M:%S"), "OK", asyncio.run(asyncio.wait_for(once(), 30)), "bytes", flush=True)
        sys.exit(0)
    except Exception as e:
        print(time.strftime("%H:%M:%S"), "FAIL", type(e).__name__, str(e)[:60], flush=True)
        time.sleep(gap)
sys.exit(1)
