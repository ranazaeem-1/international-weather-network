from pathlib import Path
import base64,json,zipfile
import resvg_py
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'thumbnails-victoria'
OUT.mkdir(exist_ok=True)
background=OUT/'victoria-scene.png'
image=base64.b64encode(background.read_bytes()).decode()
font=TTFont(ROOT/'fonts/Manrope-Bold.ttf')
glyphs=font.getGlyphSet(); cmap=font.getBestCmap()

def headline(text,x,y,width,height,fill='#101114'):
    # Outlined lettering keeps exported typography identical on every computer.
    parts=[]; offset=0
    for ch in text:
        name=cmap[ord(ch)]; pen=SVGPathPen(glyphs);glyphs[name].draw(pen)
        parts.append(f'<g transform="translate({offset} 0)"><path d="{pen.getCommands()}"/></g>')
        offset+=font['hmtx'].metrics[name][0]
    cap=font['OS/2'].sCapHeight
    return f'<g aria-label="{text}" fill="{fill}" transform="translate({x} {y}) scale({width/offset} {-height/cap})">'+''.join(parts)+'</g>'

mark='<path fill="#FFFFFF" d="M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z"/><circle fill="#EF343D" cx="11.5" cy="12" r="12"/>'
variants=[('red','Red','#C9192C'),('green','Green','#087B4C'),('blue','Blue','#0648B4'),('iwn','IWN charcoal + red','#17191D')]
for key,label,color in variants:
    tab='#EF343D' if key in ('blue','iwn') else ('#960D1F' if key=='red' else '#065C39')
    body=f'<image href="data:image/png;base64,{image}" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/>'
    body+=f'<rect width="278" height="157" fill="{color}"/>'
    body+='<circle cx="89" cy="23" r="11" fill="#EF343D"/>'
    body+=headline('LIVE',108,34,94,27,'#FFFFFF')
    body+=f'<g transform="translate(24 46) scale(1.01)">{mark}</g>'
    body+=f'<path d="M16 539H315L345 588H16Z" fill="{tab}"/>'
    body+=headline('BREAKING NEWS',27,575,282,29,'#FFFFFF')
    body+=f'<rect x="0" y="588" width="1195" height="132" fill="{color}"/><rect x="16" y="604" width="1163" height="100" fill="#FFFFFF"/>'
    body+=headline('VICTORIA FLOODS',30,689,1133,68)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><title>IWN Victoria floods — {label} concept</title>{body}</svg>'
    (OUT/f'victoria-{key}.svg').write_text(svg,encoding='utf8')
    (OUT/f'victoria-{key}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg))
board='<rect width="1360" height="900" fill="#F5F2EB"/>'
for i,(key,label,color) in enumerate(variants):
    x=30+i%2*665;y=20+i//2*435
    board+=headline(f'0{i+1} / {label.upper()}',x,y+26, min(340,len(label)*14+65),21)
    pic=base64.b64encode((OUT/f'victoria-{key}.png').read_bytes()).decode()
    board+=f'<image x="{x}" y="{y+42}" width="635" height="357.2" href="data:image/png;base64,{pic}"/>'
board=f'<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="900">{board}</svg>'
(OUT/'comparison.png').write_bytes(resvg_py.svg_to_bytes(svg_string=board))
titles=['AUSTRALIA HIT by Flash Floods – 6 Rescues as Heavy Rain Batters Victoria (Latest Updates)','MELBOURNE HIT by Flash Floods – Heavy Rain & Storms Slam Victoria (Latest Updates)','AUSTRALIA FLOOD EMERGENCY – 200 Calls for Help as Storms Batter Victoria']
(OUT/'README.txt').write_text('IWN Victoria thumbnail concepts — 4 October 2026\nFour PNG/SVG versions: red, green, blue, and IWN charcoal/red.\nLayout follows the user-supplied GWN reference: rectangular upper-left logo, LIVE above the mark, breaking-news tab, white headline panel with colored border. IWN replaces GWN.\nBackground: AI-generated illustrative Victoria scene, not verified event footage. LIVE is a mockup state; use only for actual live coverage.\nShared thumbnail headline: VICTORIA FLOODS.\nUser-supplied alternative video titles (claims not independently verified):\n'+'\n'.join(titles)+'\n\nSVG lettering is outlined for portability; edit wording in source/build_victoria_thumbnails.py and regenerate.\n',encoding='utf8')
page=(ROOT/'index.html').read_text(encoding='utf8');a=page.index('<h2 id="thumbnails">');b=page.index('<h2>04 /',a)
cards=''.join(f'<div class="card"><img src="thumbnails-victoria/victoria-{k}.png" alt="Victoria floods {label} thumbnail"><p><b>{label}</b></p><a href="thumbnails-victoria/victoria-{k}.png" download>PNG</a><a href="thumbnails-victoria/victoria-{k}.svg" download>SVG</a></div>' for k,label,c in variants)
section='<h2 id="thumbnails">03 / Victoria floods — four colors</h2><p>GWN-reference layout with IWN branding: rectangular logo panel, BREAKING NEWS tab, and bold black headline on white. Red, green, blue, and IWN charcoal/red versions.</p><div class="grid">'+cards+'</div><p><a href="thumbnails-victoria/IWN-Victoria-thumbnails.zip" download>Download all four</a></p><p class="small">AI-generated illustrative scene, not verified footage of the reported event. LIVE is a design mockup. The three supplied titles remain alternatives; rescue and call counts have not been independently verified.</p>\n'
(ROOT/'index.html').write_text(page[:a]+section+page[b:],encoding='utf8')
decisions=json.loads((ROOT/'source/brand-decisions.json').read_text(encoding='utf8'))
decisions['current_thumbnail_direction']={'date':'2026-10-04','layout':'GWN-reference rectangular logo and white bordered headline panel','colors':[v[0] for v in variants],'status':'four Victoria concepts awaiting color selection','folder':'thumbnails-victoria'}
(ROOT/'source/brand-decisions.json').write_text(json.dumps(decisions,indent=2),encoding='utf8')
with zipfile.ZipFile(OUT/'IWN-Victoria-thumbnails.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.suffix!='.zip':z.write(p,p.name)
print('Four Victoria thumbnail variants and updated gallery complete.')
