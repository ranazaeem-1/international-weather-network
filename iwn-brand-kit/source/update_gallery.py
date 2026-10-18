from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=r/'index.html';s=p.read_text(encoding='utf8')
a=s.index('<h2>03 / Thumbnail system</h2>');b=s.index('<h2>04 / In-video packaging</h2>')
s=s[:a]+'''<h2 id="thumbnails">03 / Approved thumbnail system</h2><p><b>Selected: rounded bottom headline cards.</b> Both approved templates use a circular IWN badge, a red LIVE pill, and bold charcoal lettering on warm white. The earlier curved-side layouts have been retired.</p>
<div class="grid"><div class="card"><img src="thumbnail-rain-selected.png" alt="Approved IWN rain thumbnail with LIVE badge"><p><b>01 / Rain template — approved</b></p><a href="thumbnail-rain-selected.svg" download>Editable SVG</a><a href="thumbnail-rain-selected.png" download>PNG</a></div><div class="card"><img src="thumbnail-heat-selected.png" alt="Approved IWN heat thumbnail with LIVE badge"><p><b>02 / Heat template — approved</b></p><a href="thumbnail-heat-selected.svg" download>Editable SVG</a><a href="thumbnail-heat-selected.png" download>PNG</a></div></div>
<h3>Applied demo / New Mexico flooding</h3><div class="card"><img class="banner" src="thumbnail-new-mexico-live-demo.png" alt="IWN New Mexico flooding demo using GWN source imagery"><p><b>NEW MEXICO / FLOODING</b></p><p>Uses the flood scene from GWN’s <a href="https://www.youtube.com/watch?v=Ui4ojN24Bg8">New Mexico flooding video</a>, with IWN’s approved rounded-card design and LIVE badge. The thumbnail headline is shortened from the source video title.</p><a href="thumbnail-new-mexico-live-demo.png" download>Download demo PNG</a><p class="small">Branding demonstration using third-party source imagery; not published or presented as a current live report. The LIVE badge is editable in the SVG templates.</p></div>
''' +s[b:]
s=s.replace('quiet contour lines and broad curved panels','quiet contour lines and rounded bottom headline cards')
s=s.replace('<img class="banner" src="identity-concepts.png">','')
s=s.replace('No reference artwork is included in production assets.','The New Mexico design demo reuses GWN imagery as requested. Core IWN logo and broadcast assets are original.')
p.write_text(s,encoding='utf8')
(r/'source/brand-decisions.json').write_text(json.dumps({'approved_thumbnail_system':['thumbnail-rain-selected','thumbnail-heat-selected'],'retired':['thumbnail-storm-demo','thumbnail-overlay-editable'],'live_badge':'Red pill beside circular IWN logo','demo_source':{'title':'NEW MEXICO HIT by Severe Flooding – Hatch Evacuated, Major Highway Closed (Latest Updates)','url':'https://www.youtube.com/watch?v=Ui4ojN24Bg8','headline':'NEW MEXICO / FLOODING'},'date':'2026-10-03'},indent=2),encoding='utf8')
print('Gallery and brand decisions updated.')
