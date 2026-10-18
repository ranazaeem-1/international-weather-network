import build_motion as m
import json
m.duration=8000
p=m.ROOT/'motion/broadcast.tsrct'
print(m.run('project','create','--project',p))
m.run('project','import-font','--project',p,'--file',m.ROOT/'fonts/Manrope.ttf')
f=m.ROOT/'source/broadcast.json';m.run('project','checkout','--project',p,'--output',f)
d=json.loads(f.read_text(encoding='utf8'));d['duration']=8;d['dimensions']={'width':1920,'height':1080};f.write_text(json.dumps(d),encoding='utf8');m.run('project','commit','--project',p,'--file',f)
a=[m.rect(1,'Headline panel',164,848,1658,150,m.D,36),m.rect(2,'Update category pill',291,811,275,49,m.R,24),m.text(3,'Category',315,845,23,'WEATHER UPDATE',m.W),m.text(4,'Headline line one',291,910,35,'STORM SYSTEM DEVELOPING',m.W),m.text(5,'Headline line two - example',291,961,28,'DEMO HEADLINE  /  Replace with verified reporting',m.W)]
a+=m.badge(10,82,832,184)
a+=[m.group([12,11,10,5,4,3,2,1]),m.anim(100,'positionY','const t=input.time.seconds; const a=1-Math.pow(1-Math.min(1,t/.45),3); const b=Math.max(0,Math.min(1,(t-7.4)/.45)); return 260*(1-a+b*b);'),m.anim(100,'opacity','const t=input.time.seconds;return Math.min(1,t/.2)*Math.max(0,1-(t-7.4)/.45)*100;')]
a += [m.rect(20,'Location capsule',96,74,655,76,m.D,38),m.rect(21,'Location signal',119,95,34,34,m.R,17),m.text(22,'Location - edit per story',171,122,27,'LOCATION',m.W),m.rect(23,'Date separator',376,92,2,38,m.W),m.text(24,'Date - edit per story',404,122,24,'DD MMM YYYY',m.W)]
a += [dict(type='groupFxCompositionLayers',compositionId='main',layerIds=[24,23,22,21,20],groupLayerId=200,name='Location and date',transform=m.tr()),m.anim(200,'positionX','const t=input.time.seconds;return -820*Math.pow(1-Math.min(1,t/.4),3);')]
a += [dict(type='groupFxCompositionLayers',compositionId='main',layerIds=[200,100],groupLayerId=300,name='Broadcast package - alpha export',transform=m.tr())]
f=m.ROOT/'source/broadcast-actions.json';f.write_text(json.dumps(a),encoding='utf8');print(m.run('project','apply','--project',p,'--actions',f))
print(m.run('preview','--project',p,'--time',2,'--output',m.ROOT/'previews/broadcast.png'))
print(m.run('filmstrip','--project',p,'--timestamps-ms','0,200,500,2000,7300,7600','--tile-width',480,'--tile-height',270,'--items-per-row',3,'--output',m.ROOT/'previews/broadcast-filmstrip.png'))
