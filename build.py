from pathlib import Path
import re,json,base64,hashlib
ROOT=Path(__file__).resolve().parent
reg=(ROOT/'vendor/inter-regular.b64').read_text().strip()
bold=(ROOT/'vendor/inter-bold.b64').read_text().strip()
icon='data:image/png;base64,'+base64.b64encode((ROOT/'assets/icon-192.png').read_bytes()).decode()
(ROOT/'dist').mkdir(exist_ok=True)
for size in [192,512]:
    (ROOT/'dist'/f'icon-{size}.png').write_bytes((ROOT/'assets'/f'icon-{size}.png').read_bytes())
vendor=(ROOT/'vendor/jspdf.js').read_text()+'\n/*\n'+(ROOT/'vendor/QR-LICENSE.txt').read_text()+'\n*/\n'+(ROOT/'vendor/qrcode.js').read_text()+'\n/* Inter font license:\n'+(ROOT/'vendor/INTER-LICENSE.txt').read_text()+'\n*/'
vendor=re.sub(r'//# sourceMappingURL=.*','',vendor)
template=(ROOT/'src/template.html').read_text()
for token,value in {'/*STYLE*/':(ROOT/'src/style.css').read_text(),'/*VENDOR*/':vendor,'/*CORE*/':(ROOT/'src/core.js').read_text(),'/*EXPORT*/':f"const ROTA_FONT_REGULAR='{reg}', ROTA_FONT_BOLD='{bold}';\n"+(ROOT/'src/export.js').read_text(),'/*APP*/':(ROOT/'src/animations.js').read_text()+'\n'+(ROOT/'src/app.js').read_text(),'<!--ICON-->':f'<link rel="icon" href="{icon}">','<!--MANIFEST-->':'<link rel="manifest" href="./manifest.webmanifest">'}.items():
    template=template.replace(token,value)
(ROOT/'dist/index.html').write_text(template)
manifest={'id':'./','name':'ROTA · Grafik rotacji','short_name':'ROTA','start_url':'./','scope':'./','display':'standalone','background_color':'#F4F5F1','theme_color':'#176C58','lang':'pl','icons':[{'src':f'./icon-{size}.png','sizes':f'{size}x{size}','type':'image/png','purpose':'any'} for size in [192,512]]}
(ROOT/'dist/manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
version=hashlib.sha256(template.encode()).hexdigest()[:12]
(ROOT/'dist/sw.js').write_text('const CACHE='+json.dumps('rota-'+version)+';\n'+'''const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('rota-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin||u.pathname.includes('/api/'))return;
if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).then(async r=>{if(r.ok&&r.type==='basic'){const c=await caches.open(CACHE);await c.put('./index.html',r.clone());}return r;}).catch(()=>caches.match('./index.html')));return;}
e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(self.clients.matchAll({type:'window'}).then(cs=>{const c=cs.find(c=>c.url.startsWith(self.registration.scope));return c?c.focus():self.clients.openWindow('./');}));});
''')
print('Built',len(template.encode()),'bytes; version',version)
