from pathlib import Path
import subprocess,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def run(a):
 r=subprocess.run(a,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr)
 return r.stdout
reports=[]
for name in ['subscribe','ticker','broadcast']:
 src=ROOT/'motion'/f'{name}-transparent.mov'
 reports.append(json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(src)])))
 # MP4s are review copies; MOVs retain transparency for editing.
 run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=0x717571:s=1920x1080:r=30','-i',str(src),'-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto,format=yuv420p[v]','-map','[v]','-c:v','libx264','-crf','19','-preset','fast','-an',str(ROOT/'motion'/f'{name}-preview.mp4')])
 run(['ffmpeg','-y','-v','error','-ss','2','-i',str(src),'-vf','alphaextract','-frames:v','1',str(ROOT/'previews'/f'{name}-alpha.png')])
 alpha=Image.open(ROOT/'previews'/f'{name}-alpha.png').convert('L')
 assert alpha.getextrema()==(0,255),(name,alpha.getextrema())
 for color in ['F5F2EB','34383D']:
  run(['ffmpeg','-y','-v','error','-f','lavfi','-i',f'color=c=0x{color}:s=1920x1080:r=30','-ss','2','-i',str(src),'-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto[v]','-map','[v]','-frames:v','1',str(ROOT/'previews'/f'{name}-on-{color}.png')])
(ROOT/'source/export-checks.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
print('Three alpha exports verified; MP4 previews and light/dark composites created.')
