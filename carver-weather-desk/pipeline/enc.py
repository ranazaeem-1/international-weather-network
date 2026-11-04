"""Video encoder choice for the Carver pipeline: NVIDIA NVENC when this machine has it, else libx264 (CPU).

    from enc import h264   ->   h264("final") / h264("inter") / h264("fast") return ffmpeg -c:v argument lists
Set CARVER_ENCODER=cpu to force libx264 (for example on a machine whose NVENC sessions are busy).
"""
import os, subprocess
from functools import lru_cache


@lru_cache(None)
def has_nvenc():
    if os.environ.get("CARVER_ENCODER", "").lower() == "cpu":
        return False
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=256x144:d=0.1", "-frames:v", "1",
                        "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
    return r.returncode == 0


def h264(kind="inter"):
    """final: the delivery render; inter: high-quality intermediates (host, base shots); fast: tests and stand-ins."""
    if has_nvenc():
        return {"final": ["-c:v", "h264_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0", "-maxrate", "28M", "-bufsize", "56M"],
                "inter": ["-c:v", "h264_nvenc", "-preset", "p5", "-tune", "hq", "-rc", "vbr", "-cq", "16", "-b:v", "0"],
                "fast": ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "20"]}[kind]
    return {"final": ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-maxrate", "28M", "-bufsize", "56M"],
            "inter": ["-c:v", "libx264", "-preset", "fast", "-crf", "15"],
            "fast": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]}[kind]
