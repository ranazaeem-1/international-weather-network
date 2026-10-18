"""Write an episode's pronunciation table and graphics copy into its project scripts.

Put a `project/episode_copy.py` in the episode defining SAY (dict), LOWER_THIRDS (dict), TICKER_ITEMS (list of str),
TICKER_LABEL and TICKER_STATUS, then run:  python set_copy.py   (from the episode's project/ folder)
"""
import re, runpy
from pathlib import Path

P = Path.cwd()
c = runpy.run_path(str(P / "episode_copy.py"))
say = "SAY = {\n" + "".join(f"    {k!r}: {v!r},\n" for k, v in c["SAY"].items()) + "}"
lt = "LOWER_THIRDS = {\n" + "".join(f"    {k!r}: {tuple(v)!r},\n" for k, v in c["LOWER_THIRDS"].items()) + "}\n"
tk = ("TICKER_COPY = (\n" + "".join(f"    {(s + '     ' + chr(0x2022) + '     ')!r}\n" for s in c["TICKER_ITEMS"]) + ")\n"
      f"TICKER_LABEL, TICKER_STATUS = {c['TICKER_LABEL']!r}, {c['TICKER_STATUS']!r}\n")
m = P / "make_narration.py"
m.write_text(re.sub(r"SAY = \{.*?\n\}", lambda _: say, m.read_text(encoding="utf8"), count=1, flags=re.S), encoding="utf8")
g = P / "build_graphics.py"
t = g.read_text(encoding="utf8")
t = re.sub(r"LOWER_THIRDS = \{.*?\n\}\n", lambda _: lt, t, count=1, flags=re.S)
t = re.sub(r"TICKER_COPY = \(.*?\n\)\nTICKER_LABEL.*?\n", lambda _: tk, t, count=1, flags=re.S)
g.write_text(t, encoding="utf8")
print("copy set:", len(c["SAY"]), "pronunciations,", len(c["LOWER_THIRDS"]), "lower-thirds,", len(c["TICKER_ITEMS"]), "ticker items")
