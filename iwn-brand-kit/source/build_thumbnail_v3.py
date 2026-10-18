from pathlib import Path
import base64, json
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'thumbnails-v3'
OUT.mkdir(exist_ok=True)
photo = base64.b64encode((ROOT/'references/gwn-new-mexico-hq.png').read_bytes()).decode()
fonts = [str(ROOT/'fonts/Anton-Regular.ttf'), str(ROOT/'fonts/Manrope-Bold.ttf')]
variants = [('red','Signal red','#D92332'),('green','Emerald green','#087F5B'),('blue','Royal blue','#174DC9'),('iwn','IWN charcoal + red','#17191D')]
mark = '<path fill="#F5F2EB" d="M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z"/><circle fill="#EF343D" cx="11.5" cy="12" r="12"/>'
for key,label,color in variants:
    accent = '#EF343D' if key=='iwn' else color
    # Native SVG viewport crop; original raster is preserved without alteration.
    body = f'<defs><clipPath id="photo-window"><rect width="1280" height="620"/></clipPath></defs><g clip-path="url(#photo-window)"><image href="data:image/png;base64,{photo}" x="-358.4" y="0" width="1638.4" height="921.6"/></g>'
    body += '<circle cx="77" cy="77" r="53" fill="#17191D" stroke="#F5F2EB" stroke-width="2"/>'
    body += f'<g transform="translate(39 59) scale(.335)">{mark}</g>'
    body += f'<rect x="145" y="48" width="117" height="48" rx="8" fill="{accent}"/><circle cx="165" cy="72" r="5" fill="#F5F2EB"/><text x="178" y="82" font-family="Manrope" font-weight="700" font-size="27" fill="#F5F2EB">LIVE</text>'
    body += f'<rect y="620" width="1280" height="100" fill="{color}"/>'
    if key=='iwn': body += '<rect y="615" width="1280" height="5" fill="#EF343D"/>'
    body += '<text x="640" y="696" text-anchor="middle" font-family="Anton" font-size="78" fill="#F5F2EB" letter-spacing="2">NEW MEXICO FLOODS</text>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><title>IWN {label} thumbnail design demo</title>{body}</svg>'
    (OUT/f'{key}.svg').write_text(svg,encoding='utf8')
    (OUT/f'{key}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,font_files=fonts))

# Native vector comparison sheet, using finished previews without altering their pixels.
board = '<rect width="1360" height="920" fill="#F5F2EB"/>'
for i,(key,label,color) in enumerate(variants):
    x=30+(i%2)*665; y=25+(i//2)*445
    pic=base64.b64encode((OUT/f'{key}.png').read_bytes()).decode()
    board += f'<text x="{x}" y="{y+25}" font-family="Manrope" font-weight="700" font-size="23" fill="#17191D">0{i+1} / {label}</text><image x="{x}" y="{y+43}" width="635" height="357.1875" href="data:image/png;base64,{pic}"/>'
board += '<text x="30" y="905" font-family="Manrope" font-size="14" fill="#17191D">DESIGN COMPARISON · GWN source imagery · LIVE shown as a branding demo</text>'
board = f'<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="920">{board}</svg>'
(OUT/'comparison.png').write_bytes(resvg_py.svg_to_bytes(svg_string=board,font_files=fonts))
(OUT/'README.txt').write_text('IWN thumbnail revision 3\nFour color options; no winner selected yet.\n1280 x 720 PNGs and editable SVGs.\nHeadline strip: bottom 100 px (13.9%); photo area: 86.1%.\nReference image: https://www.youtube.com/watch?v=Ui4ojN24Bg8\nThird-party source imagery for design comparison only, not verified documentary evidence or cleared publishing material. Replace with episode footage before publication. LIVE is a demo state.\nSVG text uses supplied Anton and Manrope fonts.\nBuilt locally from native SVG after the image-generation service failed. Original source pixels remain embedded intact; viewport crop changes framing.\n',encoding='utf8')

page = (ROOT/'index.html').read_text(encoding='utf8')
start = page.index('<h2 id="thumbnails">')
end = page.index('<h2>04 /',start)
cards = ''.join(f'<div class="card"><img src="thumbnails-v3/{key}.png" alt="IWN {label} image-first thumbnail"><p><b>0{i+1} / {label}</b></p><a href="thumbnails-v3/{key}.png" download>PNG</a><a href="thumbnails-v3/{key}.svg" download>Editable SVG</a></div>' for i,(key,label,color) in enumerate(variants))
section = '<h2 id="thumbnails">03 / Thumbnails — more room for the image</h2><p><b>Four new color options.</b> The visual fills 86% of the frame. A small circular IWN logo and LIVE badge sit above a single slim headline strip. The previous large rounded cards have been superseded; no new color winner has been selected yet.</p><div class="grid">'+cards+'</div><p><a href="thumbnails-v3/comparison.png">View comparison sheet</a><a href="thumbnails-v3/IWN-thumbnails-v3.zip" download>Download all four</a></p><p class="small">Design demos using a viewport crop of the previously supplied GWN reference thumbnail. Source imagery is not verified documentary evidence or cleared publication footage. LIVE demonstrates the badge; use it for genuine live coverage. <a href="https://www.youtube.com/watch?v=Ui4ojN24Bg8">Source video</a>.</p>\n'
(ROOT/'index.html').write_text(page[:start]+section+page[end:],encoding='utf8')
decisions=json.loads((ROOT/'source/brand-decisions.json').read_text(encoding='utf8'))
decisions['thumbnail_revision_3']={'date':'2026-10-04','status':'four color options awaiting selection','layout':'86% photo, small circular badge, slim single-line bottom headline','variants':[x[0] for x in variants],'supersedes':['thumbnail-rain-selected','thumbnail-heat-selected']}
decisions['approved_thumbnail_system']=[]
(ROOT/'source/brand-decisions.json').write_text(json.dumps(decisions,indent=2),encoding='utf8')
import zipfile
with zipfile.ZipFile(OUT/'IWN-thumbnails-v3.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.suffix!='.zip': z.write(p,p.name)
    for p in (ROOT/'fonts').iterdir(): z.write(p,'fonts/'+p.name)
print('Created four PNG/SVG variants, comparison, ZIP, and updated gallery.')
