from pathlib import Path
import json, subprocess, os
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
ROOT=Path(__file__).resolve().parents[1]
CLI=Path(os.environ['LOCALAPPDATA'])/'Tesseract/bin/tsrct.cmd'
D='#17191D'; W='#F5F2EB'; R='#EF343D'
def run(*args):
    r=subprocess.run([str(CLI),*map(str,args)],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stderr+r.stdout)
    return r.stdout
def color(h):return [int(h[i:i+2],16)/255 for i in (1,3,5)]+[1]
def tr(x=0,y=0,s=100):return dict(anchorPoint=[0,0],position=[x,y],scale=[s,s],rotation=0,opacity=100)
def rect(i,name,x,y,w,h,c,r=0):return dict(type='createFxRectLayer',compositionId='main',layerId=i,name=name,insertIndex=0,activeRange={'start':0,'duration':duration},transform=tr(x,y),rect={'size':[w,h],'fillColor':color(c),'roundness':r})
def text(i,name,x,y,size,copy,c):return dict(type='createFxTextLayer',compositionId='main',layerId=i,name=name,insertIndex=0,activeRange={'start':0,'duration':duration},transform=tr(x,y),sourceText={'text':copy,'fontFamily':'Manrope ExtraLight','fontStyle':'Bold','fontSize':size,'fillColor':color(c),'justification':'left'})
def shape(i,name,x,y,s,path,c):
    p=RecordingPen();parse_path(path,p);cmd=[]
    for op,pts in p.value:
        if op=='closePath':cmd.append({'type':'close'})
        elif op in ('moveTo','lineTo'):cmd.append({'type':op,'x':pts[0][0],'y':pts[0][1]})
        elif op=='curveTo':cmd.append(dict(type='cubicTo',c1x=pts[0][0],c1y=pts[0][1],c2x=pts[1][0],c2y=pts[1][1],x=pts[2][0],y=pts[2][1]))
    return dict(type='createFxShapeLayer',compositionId='main',layerId=i,name=name,insertIndex=0,activeRange={'start':0,'duration':duration},transform=tr(x,y,s*100),shape={'path':{'commands':cmd},'fills':[{'paint':{'type':'solid','color':color(c)},'opacity':1,'blendMode':'normal','fillRule':'nonZeroWinding'}]})
def badge(ids,x,y,d):
    s=d*.7/226; mx=x+d*.15;my=y+d*.32
    path='M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z'
    return [rect(ids,'IWN circle',x,y,d,d,D,d/2),shape(ids+1,'IWN vector letters',mx,my,s,path,W),rect(ids+2,'Signature red dot',mx-.5*s,my,24*s,24*s,R,12*s)]
def anim(i,prop,code):return {'type':'setFxPropertyAnimator','compositionId':'main','property':{'layerId':i,'propertyType':prop},'dependencies':[],'animator':{'type':'jsScript','layerTimeJsCode':code}}
def group(ids):return dict(type='groupFxCompositionLayers',compositionId='main',layerIds=ids,groupLayerId=100,name='IWN overlay - export this group for alpha',transform=tr())
def build(name,seconds):
    global duration
    duration=seconds*1000;p=ROOT/'motion'/f'{name}.tsrct'
    if not p.exists():run('project','create','--project',p)
    run('project','import-font','--project',p,'--file',ROOT/'fonts/Manrope.ttf')
    work=ROOT/'source'/f'{name}.json'
    run('project','checkout','--project',p,'--output',work)
    doc=json.loads(work.read_text());doc['dimensions']={'width':1920,'height':1080};doc['duration']=seconds
    work.write_text(json.dumps(doc),encoding='utf8');run('project','commit','--project',p,'--file',work)
    if name=='subscribe':
        a=[rect(1,'Warm white pill',172,832,930,148,W,74),rect(2,'Subscribe button',804,870,250,72,R,36),text(3,'Channel name',290,894,28,'International Weather Network',D),text(4,'Supporting label',290,936,21,'People. Places. Weather.',D),text(5,'Subscribe state',835,916,22,'SUBSCRIBE',W)]
        a+=badge(10,90,817,178)
        ids=[12,11,10,5,4,3,2,1];a+=[group(ids)]
        a+=[anim(100,'positionY','const t=input.time.seconds; const e=1-Math.pow(1-Math.min(1,t/.5),3); const o=Math.max(0,Math.min(1,(t-5.3)/.5)); return 250*(1-e)+250*o*o;'),anim(100,'opacity','const t=input.time.seconds; return Math.min(1,t/.18)*Math.max(0,1-(t-5.3)/.5)*100;'),anim(5,'textContent',"return input.time.seconds<3.1?'SUBSCRIBE':'SUBSCRIBED';"),anim(12,'opacity','const t=input.time.seconds; return t<.65?100:80+20*Math.cos((t-.65)*Math.PI*2);')]
    else:
        # Foreground fixed label covers scrolling text at left. Canvas clips the right.
        copy='DEMO  /  WEATHER UPDATE     •     Replace with verified location, forecast and time     •     '
        a=[rect(1,'Ticker background',0,930,1920,106,D),rect(2,'Red rule',0,930,1920,4,R),text(3,'Editable scrolling copy',510,995,31,copy*4,W),rect(4,'Fixed label backing',0,934,490,102,D),text(5,'Ticker label',224,981,27,'WEATHER',W),text(6,'Demo status',225,1010,18,'DEMO UPDATE',R)]
        a+=badge(10,56,896,142)
        a+=[group([12,11,10,6,5,4,3,2,1]),anim(3,'positionX','return 510-input.time.seconds*75;')]
    actions=ROOT/'source'/f'{name}-actions.json';actions.write_text(json.dumps(a),encoding='utf8')
    print(run('project','apply','--project',p,'--actions',actions))
    print(run('preview','--project',p,'--time','2','--output',ROOT/'previews'/f'{name}.png'))
    print(run('filmstrip','--project',p,'--timestamps-ms',('0,200,500,2000,3200,5000,5500,5800' if name=='subscribe' else '0,2000,5000,9000'),'--tile-width','480','--tile-height','270','--items-per-row','4','--output',ROOT/'previews'/f'{name}-filmstrip.png'))
if __name__=='__main__':
    for name,seconds in [('subscribe',6),('ticker',12)]:build(name,seconds)
