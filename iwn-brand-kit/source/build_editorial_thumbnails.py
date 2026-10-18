from pathlib import Path
import base64,json,zipfile
import resvg_py
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.varLib.instancer import instantiateVariableFont

R=Path(__file__).resolve().parents[1]; O=R/'thumbnails-editorial'; O.mkdir(exist_ok=True)
photo=base64.b64encode((R/'thumbnails-victoria/victoria-scene.png').read_bytes()).decode()
sans=instantiateVariableFont(TTFont(R/'fonts/Manrope.ttf'),{'wght':800},inplace=False)
condensed=TTFont(R/'fonts/Anton-Regular.ttf')

def text(s,x,y,size,fill='#FFFFFF',face=sans,tracking=0):
    gs=face.getGlyphSet();cm=face.getBestCmap(); scale=size/face['head'].unitsPerEm; pos=0; result=''
    for c in s:
        n=cm[ord(c)];p=SVGPathPen(gs);gs[n].draw(p)
        result+=f'<g transform="translate({pos} 0)"><path d="{p.getCommands()}"/></g>'
        pos+=face['hmtx'].metrics[n][0]+tracking/scale
    return f'<g aria-label="{s}" fill="{fill}" transform="translate({x} {y}) scale({scale} {-scale})">{result}</g>'

mark='<path fill="#FFF" d="M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z"/><circle fill="#EF343D" cx="11.5" cy="12" r="12"/>'
variants=[('red','01 / RED','#F33242'),('green','02 / GREEN','#42E4AB'),('blue','03 / BLUE','#5CA8FF'),('iwn','04 / IWN SIGNATURE','#EF343D')]
for key,label,accent in variants:
    defs='<defs><linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#071017" stop-opacity="0"/><stop offset=".45" stop-color="#071017" stop-opacity=".22"/><stop offset="1" stop-color="#071017" stop-opacity=".93"/></linearGradient><linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#071017" stop-opacity=".7"/><stop offset="1" stop-color="#071017" stop-opacity="0"/></linearGradient><linearGradient id="left"><stop stop-color="#071017" stop-opacity=".72"/><stop offset="1" stop-color="#071017" stop-opacity="0"/></linearGradient></defs>'
    body=defs+f'<image width="1280" height="720" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{photo}"/><rect width="1280" height="180" fill="url(#top)"/><rect y="380" width="1280" height="340" fill="url(#bottom)"/>'
    body+=f'<g transform="translate(46 35) scale(.49)">{mark}</g><path d="M181 44V83" stroke="#FFFFFF" stroke-opacity=".45"/>'
    body+=text('WEATHER NETWORK',202,70,18,tracking=2)
    body+='<rect x="1129" y="40" width="105" height="40" rx="5" fill="#FFFFFF"/>'
    body+=f'<circle cx="1148" cy="60" r="5" fill="{accent}"/>'+text('LIVE',1161,68,21,'#11161C')
    if key=='red':
        body+=f'<rect x="48" y="453" width="7" height="206" fill="{accent}"/>'
        body+=text('VICTORIA',77,495,32,tracking=5)
        body+=text('FLASH FLOODS',70,641,116,face=condensed)
    elif key=='green':
        body+=f'<rect x="48" y="478" width="180" height="36" fill="{accent}"/>'+text('AUSTRALIA',61,503,20,'#071017',tracking=2)
        body+=text('Victoria',45,589,80)
        body+=text('under water',45,672,80)
    elif key=='blue':
        body+='<rect x="0" y="265" width="625" height="455" fill="url(#left)"/>'
        body+=text('VICTORIA',48,421,30,tracking=5)
        body+=text('FLASH',42,538,126,face=condensed)
        body+=text('FLOODS',42,667,126,accent,face=condensed)
    else:
        body+=f'<rect x="48" y="468" width="58" height="6" fill="{accent}"/>'
        body+=text('VICTORIA',48,520,30,tracking=6)
        body+=text('FLOODS',40,664,151,face=condensed)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><title>IWN editorial thumbnail / {key}</title>{body}</svg>'
    (O/f'{key}.svg').write_text(svg,encoding='utf8');(O/f'{key}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg))
board='<rect width="1400" height="952" fill="#11161C"/>'
for i,(key,label,accent) in enumerate(variants):
    x=30+i%2*695;y=24+i//2*470
    board+=text(label,x,y+23,21,accent,tracking=1.2)
    pic=base64.b64encode((O/f'{key}.png').read_bytes()).decode()
    board+=f'<image x="{x}" y="{y+44}" width="645" height="362.8125" href="data:image/png;base64,{pic}"/>'
board=f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="952">{board}</svg>'
(O/'comparison.png').write_bytes(resvg_py.svg_to_bytes(svg_string=board))
(O/'README.txt').write_text('IWN editorial redesign — 5 October 2026\nFour fresh layouts retaining the approved Victoria illustration.\nTypography has natural proportions: no horizontal stretching. Compact logo, clean spacing, selective shadow gradients, restrained color.\nThe IWN signature option is the recommended default. No new design is marked user-approved yet.\nPNG:1280x720. SVG: vector lettering and embedded background; source script controls text.\nScene is AI-generated illustration, not documentary footage. LIVE is a design-demo state.\n',encoding='utf8')
page=(R/'index.html').read_text(encoding='utf8');start=page.index('<h2 id="thumbnails">');end=page.index('<h2>04 /',start)
cards=''.join(f'<div class="card"><img src="thumbnails-editorial/{key}.png" alt="{label} IWN editorial thumbnail"><p><b>{label}</b></p><a href="thumbnails-editorial/{key}.png" download>PNG</a><a href="thumbnails-editorial/{key}.svg" download>Vector SVG</a></div>' for key,label,a in variants)
new='<h2 id="thumbnails">03 / Editorial thumbnail redesign</h2><p>Four fresh directions: compact branding, natural typography, clear hierarchy, and the existing Victoria visual. Recommended: IWN Signature.</p><div class="grid">'+cards+'</div><p><a href="thumbnails-editorial/IWN-editorial-thumbnails.zip" download>Download all four designs</a></p><p class="small">Illustrative AI scene. LIVE is a design-demo state. No direction selected yet.</p>\n'
(R/'index.html').write_text(page[:start]+new+page[end:],encoding='utf8')
d=json.loads((R/'source/brand-decisions.json').read_text(encoding='utf8'));d['current_thumbnail_direction']={'date':'2026-10-05','layout':'editorial redesign; natural type, compact logo, selective gradients','status':'awaiting user selection','folder':'thumbnails-editorial','recommended':'iwn'};(R/'source/brand-decisions.json').write_text(json.dumps(d,indent=2),encoding='utf8')
with zipfile.ZipFile(O/'IWN-editorial-thumbnails.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in O.iterdir():
        if p.suffix!='.zip':z.write(p,p.name)
print('Editorial redesign rendered and gallery updated.')
