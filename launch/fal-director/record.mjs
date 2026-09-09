// Local-only capture tool. No paid request without --live. Never deploy this server.
import {createServer} from 'node:http';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve, dirname} from 'node:path';
import {randomBytes} from 'node:crypto';
import {build} from 'esbuild';
import {chromium} from 'playwright';
import {handleRequest} from '@fal-ai/server-proxy';

const root=dirname(fileURLToPath(import.meta.url));
const live=process.argv.includes('--live');
const out=resolve(root,live?'../../tmp/director':'../../tmp/director-dry-run');
await mkdir(out,{recursive:true});
const key=process.env.FAL_KEY;
if(live && !key) throw Error('Set FAL_KEY in the server environment');
const token=randomBytes(24).toString('hex');
const bundle=await build({entryPoints:[resolve(root,'capture.js')],bundle:true,write:false,format:'esm'});
let admissions=0;
const server=createServer(async(req,res)=>{
  try {
    if(req.headers.host!==`127.0.0.1:${server.address().port}`){res.writeHead(403).end();return;}
    const url=new URL(req.url,'http://localhost');
    if(url.pathname==='/api/fal/proxy'){
      if(!live || req.headers['x-capture-token']!==token){res.writeHead(403).end();return;}
      const target=req.headers['x-fal-target-url'];
      if(typeof target!=='string'){res.writeHead(400).end();return;}
      const chunks=[]; for await(const c of req) chunks.push(c);
      const body=Buffer.concat(chunks).toString();
      if(new URL(target).pathname==='/session'){
        if(admissions++>0){res.writeHead(429).end('Only one session per run');return;}
      }
      await handleRequest({id:'local-capture',method:req.method,
        getHeaders:()=>req.headers,getHeader:n=>req.headers[n.toLowerCase()],
        getRequestBody:async()=>body||undefined,
        sendHeader:(n,v)=>res.setHeader(n,v),
        respondWith:(s,d)=>{res.writeHead(s,{'content-type':'application/json'});res.end(JSON.stringify(d));},
        sendResponse:async r=>{res.writeHead(r.status,{'content-type':r.headers.get('content-type')||'application/json'});res.end(Buffer.from(await r.arrayBuffer()));}
      },{allowedEndpoints:['minimax/h3-max/director'],allowUnauthorizedRequests:false,
        isAuthenticated:async()=>req.headers['x-capture-token']===token,
        resolveFalAuth:async()=>`Key ${key}`});
      return;
    }
    const files={'/': ['capture.html','text/html'], '/capture.js':[null,'text/javascript'],
      '/demo.json':['director-demo.json','application/json'],
      '/opening.jpg':['assets/aoi-cafe-opening.jpg','image/jpeg']};
    if(url.pathname.startsWith('/audio/') && /^\/audio\/\d\.mp3$/.test(url.pathname)){
      res.writeHead(200,{'content-type':'audio/mpeg'});res.end(await readFile(resolve(root,'assets'+url.pathname)));return;
    }
    const f=files[url.pathname]; if(!f){res.writeHead(404).end();return;}
    res.writeHead(200,{'content-type':f[1]});
    let data=f[0]?await readFile(resolve(root,f[0])):bundle.outputFiles[0].contents;
    if(url.pathname==='/') data=data.toString().replace('__TOKEN__',token);
    res.end(data);
  }catch(e){res.writeHead(500).end('Local capture failed');console.error(e.message);}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--autoplay-policy=no-user-gesture-required']});
const page=await browser.newPage({viewport:{width:1280,height:900}});
await page.exposeFunction('saveCapture',async b64=>writeFile(resolve(out,'director.webm'),Buffer.from(b64,'base64')));
await page.exposeFunction('saveEvent',async e=>{events.push(e);if(e.type!=='chunk_metrics')console.log(JSON.stringify(e));});
const events=[];
try {
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForFunction(()=>window.captureReady);
  await page.screenshot({path:resolve(out,'preview.png')});
  if(live){
    await page.click('#start');
    await page.waitForFunction(()=>window.captureDone,null,{timeout:130000});
    await page.screenshot({path:resolve(out,'result.png')});
  }
}finally{
  await page.evaluate(()=>window.stopCapture?.('runner-finally')).catch(()=>{});
  await writeFile(resolve(out,'events.json'),JSON.stringify(events,null,2));
  await browser.close(); server.close();
}
console.log(live?'Capture attempt finished; inspect events and media.':'Dry run passed; no fal API requests made.');
