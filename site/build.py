"""Build the site, the demo and the sheet from src/ into dist/."""
import json, os, shutil, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(ROOT, 'src')
D = os.path.join(ROOT, 'dist')
rd = lambda name: open(os.path.join(S, name), encoding='utf-8').read()

shared = rd('shared.css')
fav = "data:image/svg+xml," + urllib.parse.quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><g transform='translate(32 32) rotate(-28)'>"
    "<ellipse rx='20' ry='27' fill='#6B4226'/><ellipse cx='-6' cy='-8' rx='7' ry='11' fill='#8F5E38' opacity='.55'/>"
    "<path d='M1 -24 C -9 -13 9 -3 0 7 C -7 15 2 20 0 25' stroke='#2B180C' stroke-width='4' fill='none' stroke-linecap='round'/></g></svg>")
geo = json.load(open(os.path.join(S, 'geo.json')))

site = rd('site.html')
site = (site.replace('{{TL}}', geo['tl']).replace('{{ID}}', geo['id'])
            .replace('{{PTS}}', json.dumps(geo['pts']))
            .replace('/*FIGS*/', rd('figs.js'))
            .replace('/*LENIS*/', '/*! lenis 1.1.13 | MIT | darkroom.engineering */' + rd('lenis.min.js'))
            .replace('/*SHARED*/', shared).replace('/*FAVICON*/', fav))


os.makedirs(D, exist_ok=True)
open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(site)
open(os.path.join(D, 'demo.html'), 'w', encoding='utf-8').write(rd('demo_map.html'))
shutil.copytree(os.path.join(S, 'assets'), os.path.join(D, 'assets'), dirs_exist_ok=True)
if os.path.exists(os.path.join(S, 'sheet.html')):
    open(os.path.join(D, 'sheet.html'), 'w', encoding='utf-8').write(
        rd('sheet.html').replace('/*SHARED*/', shared).replace('/*FAVICON*/', fav)
        .replace('/*CORE*/', rd('sheet_core.js')).replace('/*BRIEFGEN*/', rd('brief_gen.js') if os.path.exists(os.path.join(S,'brief_gen.js')) else '').replace('/*DATA*/', rd('sheet_data.json')).replace('/*AIBRIEF*/', (rd('brief_ai.json') if os.path.exists(os.path.join(S,'brief_ai.json')) else 'null')))
if os.path.exists(os.path.join(ROOT, 'og.png')):
    shutil.copy(os.path.join(ROOT, 'og.png'), os.path.join(D, 'og.png'))
shutil.copy(os.path.join(S, '_headers'), os.path.join(D, '_headers'))
if os.path.exists(os.path.join(S, 'm_proto.html')):   # phone and tablet edition
    shutil.copy(os.path.join(S, 'm_proto.html'), os.path.join(D, 'm.html'))   # the phone and tablet edition; index.html sends touch devices here
if os.path.exists(os.path.join(S, 'm_next.html')):   # summit edition draft (preview branch only)
    shutil.copy(os.path.join(S, 'm_next.html'), os.path.join(D, 'm-next.html'))
print('built', len(site) // 1024, 'KB site')
