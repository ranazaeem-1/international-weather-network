from pathlib import Path
import base64, json, zipfile
import resvg_py
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
R=Path(__file__).resolve().parents[1];O=R/'thumbnails-impact';O.mkdir(exist_ok=True)
photo=base64.b64encode((R/'thumbnails-victoria/victoria-scene.png').read_bytes()).decode()
font=TTFont(R/'fonts/Anton-Regular.ttf');sans=TTFont(R/'fonts/Manrope-Bold.ttf')
def width(s,size,f=font):
    return sum(f['hmtx'].metrics[f.getBestCmap()[ord(c)]][0] for c in s)*size/f['head'].unitsPerEm
def text(s,x,y,size,fill='#FFF',f=font):
    gs=f.getGlyphSet();cm=f.getBestCmap();sc=size/f['head'].unitsPerEm;p=0;out=''
    for c in s:
        n=cm[ord(c)];pen=SVGPathPen(gs);gs[n].draw(pen);out+=f'<g transform="translate({p} 0)"><path d="{pen.getCommands()}"/></g>';p+=f['hmtx'].metrics[n][0]
    return f'<g aria-label="{s}" fill="{fill}" transform="translate({x} {y}) scale({sc} {-sc})">{out}</g>'
mark='<path fill="#FFF" d="M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z"/><circle fill="#EF343D" cx="11.5" cy="12" r="12"/>'
variants=[('red','RED','#DE152A'),('green','GREEN','#006B44'),('blue','BLUE','#094DCB'),('iwn','IWN','#17191D')]
for key,label,color in variants:
    body='<defs><linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".68"/></linearGradient></defs>'
    if key=='red':
        body+=f'<image x="-64" y="-90" width="1408" height="810" href="data:image/png;base64,{photo}" preserveAspectRatio="xMidYMid slice"/><rect y="440" width="1280" height="280" fill="url(#shade)"/>'
    else:
        body+=f'<image width="1280" height="720" href="data:image/png;base64,{photo}" preserveAspectRatio="xMidYMid slice"/><rect y="440" width="1280" height="130" fill="url(#shade)"/>'
    # Strong, compact branding and a large separate live indicator.
    if key=='red':
        body+=f'<rect x="0" y="0" width="14" height="720" fill="{color}"/><path d="M0 0H199Q219 0 219 20V109Q219 129 199 129H0Z" fill="{color}"/>'
        black_dot_mark=mark.replace('fill="#EF343D"','fill="#000000"')
        body+=f'<g transform="translate(21 20) scale(.78)">{black_dot_mark}</g>'
    else:
        body+=f'<path d="M0 0H219V122H0Z" fill="{color}"/><path d="M0 122H219V129H0Z" fill="#FFFFFF"/>'
        body+=f'<g transform="translate(21 20) scale(.78)">{mark}</g>'
    live_radius=16 if key=='red' else 4
    body+=f'<rect x="1066" y="26" width="188" height="62" rx="{live_radius}" fill="#E51D32"/><circle cx="1092" cy="57" r="8" fill="#FFFFFF"/>'
    body+=text('LIVE',1113,73,41,f=sans)
    # Yellow is reserved for the emergency ribbon, with large black lettering.
    body+='<path d="M26 507H449L478 562H26Z" fill="#FFE44A"/>'
    body+=text('FLOOD EMERGENCY',43,549,36,'#0D1117',f=sans)
    if key=='red':
        body+=f'<path d="M0 554H1118Q1146 554 1146 582V720H0Z" fill="{color}"/>'
        body+='<rect x="10" y="564" width="1126" height="146" rx="12" fill="#FFFFFF"/>'
    else:
        body+=f'<rect y="562" width="1280" height="158" fill="{color}"/>'
    if key=='iwn':body+='<rect y="562" width="1280" height="8" fill="#EF343D"/>'
    s='VICTORIA FLOODS'
    if key=='red':
        size=min(116,1066/width(s,1,sans));w=width(s,size,sans)
        cap=sans['OS/2'].sCapHeight/sans['head'].unitsPerEm*size
        body+=text(s,10+(1126-w)/2,637+cap/2,size,'#08090B',f=sans)
    else:
        size=min(156,1195/width(s,1));w=width(s,size)
        body+=text(s,(1280-w)/2,703,size)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><title>IWN Victoria floods / bold {label} concept</title>{body}</svg>'
    (O/f'{key}.svg').write_text(svg,encoding='utf8');(O/f'{key}.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg))
board='<rect width="1400" height="920" fill="#F5F2EB"/>'
for i,(key,label,color) in enumerate(variants):
    x=30+i%2*695;y=20+i//2*450
    board+=text(f'0{i+1} / {label}',x,y+28,25,'#17191D',f=sans)
    p=base64.b64encode((O/f'{key}.png').read_bytes()).decode();board+=f'<image x="{x}" y="{y+48}" width="645" height="362.8125" href="data:image/png;base64,{p}"/>'
(O/'comparison.png').write_bytes(resvg_py.svg_to_bytes(svg_string=f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920">{board}</svg>'))
(O/'README.txt').write_text('IWN bold thumbnail direction — 5 October 2026\nLarge natural-proportion type, saturated headline panel, yellow emergency ribbon, larger wordmark, unchanged approved visual. No illustrative-image tag on artwork, as requested.\nScene remains AI-generated illustrative artwork. LIVE is a mockup state. FLOOD EMERGENCY follows the supplied title; verify the event claims before publication.\nFour colors are proposals, not user-approved selections.\n',encoding='utf8')
page=(R/'index.html').read_text(encoding='utf8');a=page.index('<h2 id="thumbnails">');b=page.index('<h2>04 /',a)
cards=''.join(f'<div class="card"><img src="thumbnails-impact/{k}.png" alt="IWN {label} bold flood thumbnail"><p><b>{label}</b></p><a href="thumbnails-impact/{k}.png" download>PNG</a><a href="thumbnails-impact/{k}.svg" download>SVG</a></div>' for k,label,c in variants)
section='<h2 id="thumbnails">03 / Bold weather thumbnails</h2><p>Larger type and branding, high-contrast emergency ribbon, and the approved flood visual. Four color proposals.</p><div class="grid">'+cards+'</div><p><a href="thumbnails-impact/IWN-bold-thumbnails.zip" download>Download all four</a></p><p class="small">AI-generated scene; LIVE is a design mockup. Event claims require verification before publication.</p>\n'
(R/'index.html').write_text(page[:a]+section+page[b:],encoding='utf8')
d=json.loads((R/'source/brand-decisions.json').read_text(encoding='utf8'));d['current_thumbnail_direction']={'date':'2026-10-05','layout':'bold full-width headline, yellow emergency ribbon, larger branding','status':'awaiting user selection','folder':'thumbnails-impact'};(R/'source/brand-decisions.json').write_text(json.dumps(d,indent=2),encoding='utf8')
with zipfile.ZipFile(O/'IWN-bold-thumbnails.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in O.iterdir():
        if p.suffix!='.zip':z.write(p,p.name)
print('Four bold thumbnail variants exported; gallery updated.')
