from pathlib import Path
import math, json
import resvg_py
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT=Path(__file__).resolve().parents[1]
DARK='#17191D'; WHITE='#F5F2EB'; RED='#EF343D'
font=TTFont(ROOT/'fonts/Manrope.ttf')
font=instantiateVariableFont(font,{'wght':700},inplace=True)
font.save(ROOT/'fonts/Manrope-Bold.ttf')
W='M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z'
N='M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z'
def mark(x,y,s,ink=WHITE):
    return f'<g transform="translate({x} {y}) scale({s})"><path fill="{ink}" d="M0 35H23V100H0Z {W} {N}"/><circle fill="{RED}" cx="11.5" cy="12" r="12"/></g>'
def badge(x,y,d):
    return f'<circle cx="{x+d/2}" cy="{y+d/2}" r="{d*.495}" fill="{DARK}" stroke="{WHITE}" stroke-width="{d*.01}"/>'+mark(x+d*.15,y+d*.32,d*.7/226)
def text(x,y,s,t,fill=WHITE,family='Manrope',weight=700,spacing=0):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-weight="{weight}" font-size="{s}" letter-spacing="{spacing}" fill="{fill}">{t}</text>'
def save(name,w,h,body):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
    (ROOT/(name+'.svg')).write_text(svg,encoding='utf8')
    (ROOT/(name+'.png')).write_bytes(resvg_py.svg_to_bytes(svg_string=svg,font_files=[str(ROOT/'fonts/Anton-Regular.ttf'),str(ROOT/'fonts/Manrope-Bold.ttf')]))
    return svg
save('logo-avatar',800,800,badge(0,0,800))
save('logo-white-transparent',904,448,mark(0,8,4))
save('logo-dark-transparent',904,448,mark(0,8,4,DARK))

# Exact-size production banner. All identity content is within the central 1546 x 423 area.
contours=''
for i in range(16):
    r=180+i*66
    contours+=f'<ellipse cx="2310" cy="580" rx="{r}" ry="{r*.68}" transform="rotate(-22 2310 580)" fill="none" stroke="{WHITE}" stroke-opacity=".09" stroke-width="2"/>'
body=f'<rect width="2560" height="1440" fill="{DARK}"/>'+contours
body+=f'<path d="M0 1160 C650 920 1700 1540 2560 1060" stroke="{RED}" stroke-width="4" fill="none"/>'
body+=badge(595,590,260)+f'<circle cx="725" cy="720" r="130" fill="none" stroke="{WHITE}" stroke-width="2"/>'
body+=text(925,695,66,'International')+text(925,777,66,'Weather Network')+text(930,830,21,'PEOPLE. PLACES. WEATHER.',spacing=5)
save('channel-banner-2560x1440',2560,1440,body)

# Approved channel thumbnail system: rounded bottom card, circular badge, LIVE pill.
for name,lines in [('rain',('RAIN','RETURNS')),('heat',('HEAT','BUILDS'))]:
    art=f'<rect width="1280" height="720" fill="{DARK}"/>'
    for i in range(10):
        art+=f'<ellipse cx="990" cy="310" rx="{95+i*35}" ry="{65+i*24}" fill="none" stroke="{WHITE}" stroke-opacity=".15" stroke-width="3"/>'
    art+=f'<circle cx="990" cy="310" r="42" fill="{RED}"/>'+badge(44,38,108)
    art+=f'<g id="live-badge"><rect x="183" y="59" width="126" height="49" rx="24.5" fill="{RED}"/><circle cx="204" cy="83.5" r="5" fill="{WHITE}"/>'+text(219,92,25,'LIVE')+'</g>'
    art+=text(338,92,21,'WEATHER OUTLOOK',spacing=2)
    art+=f'<rect x="42" y="400" width="865" height="260" rx="44" fill="{WHITE}"/>'
    art+=text(78,505,91,lines[0],DARK,'Anton')+text(78,617,91,lines[1],DARK,'Anton')
    art+=text(45,695,15,'DEMO • ABSTRACT ILLUSTRATION',spacing=2)
    save('thumbnail-'+name+'-selected',1280,720,art)
print('Static assets exported')
