// Usage: node check-spectrum-mockup.mjs CHROME HTML OUTPUT_DIRECTORY
// Chrome uses an isolated temporary profile and offline network emulation.

import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [chrome, html, out] = process.argv.slice(2);
if(!chrome||!html||!out)throw Error('Usage: node check-spectrum-mockup.mjs CHROME HTML OUTPUT_DIRECTORY');
fs.mkdirSync(out,{recursive:true});
const delay = ms => new Promise(r => setTimeout(r, ms));
const browser = spawn(chrome, ['--headless=new','--no-sandbox','--disable-gpu',
  '--no-first-run','--no-default-browser-check','--remote-debugging-pipe',
  '--user-data-dir='+path.join(out,'profile'),'about:blank'],
  {stdio:['ignore','ignore','pipe','pipe','pipe']});
let seq=0, buffer='', session, pending=new Map(), errors=[];
browser.stderr.on('data', b=>errors.push(b.toString()));
browser.stdio[3].on('error',()=>{});browser.stdio[4].on('error',()=>{});
browser.on('exit',(code)=>{for(const {reject,timer} of pending.values()){clearTimeout(timer);reject(Error('Chrome exited '+code+' '+errors.slice(-3).join('')));}pending.clear();});
browser.stdio[4].on('data', b=>{
  buffer+=b;
  let i;
  while((i=buffer.indexOf('\0'))>=0){
    const m=JSON.parse(buffer.slice(0,i)); buffer=buffer.slice(i+1);
    if(pending.has(m.id)) {const {resolve,reject,timer}=pending.get(m.id);clearTimeout(timer);pending.delete(m.id);m.error?reject(Error(JSON.stringify(m.error))):resolve(m.result);}
  }
});
function call(method,params={},sid=session){return new Promise((resolve,reject)=>{
  const id=++seq, timer=setTimeout(()=>reject(Error('CDP timeout '+method+' '+errors.slice(-2))),12000);
  pending.set(id,{resolve,reject,timer});browser.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0');
});}
async function js(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function click(selector){const b=await js(`(()=>{const b=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2}})()`);await mouse('mousePressed',b,1);await mouse('mouseReleased',b,1);}
async function mouse(type,p,buttons=0){await call('Input.dispatchMouseEvent',{type,...p,button:buttons?'left':'none',buttons,clickCount:type==='mouseMoved'?0:1});}
async function fill(selector,text){await click(selector);await js(`document.querySelector(${JSON.stringify(selector)}).select()`);await call('Input.insertText',{text:String(text)});}
async function select(id){await js(`document.querySelector('#selection').value=${JSON.stringify(id)};document.querySelector('#selection').dispatchEvent(new Event('change'))`);}
async function variant(id){await js(`document.querySelector('#variant').value=${JSON.stringify(id)};document.querySelector('#variant').dispatchEvent(new Event('change'))`);}
async function open(file){await call('Page.navigate',{url:pathToFileURL(file).href});for(let i=0;i<100;i++){if(await js(`document.readyState==='complete' && !!document.querySelector('#selection option')`))return;await delay(30);}throw Error('page not ready');}
async function load(file){const d=await call('DOM.getDocument');const q=await call('DOM.querySelector',{nodeId:d.root.nodeId,selector:'#load'});await js(`document.querySelector('#status').textContent='loading'`);await call('DOM.setFileInputFiles',{nodeId:q.nodeId,files:[file]});for(let i=0;i<100;i++){if(await js(`document.querySelector('#status').textContent!=='loading'`))return;await delay(20);}throw Error('file read timeout');}
async function shortcut(letter,modifiers=2){
  const code=letter.toUpperCase().charCodeAt(0);
  await call('Input.dispatchKeyEvent',{type:'rawKeyDown',key:letter,code:'Key'+letter.toUpperCase(),windowsVirtualKeyCode:code,modifiers});
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:letter,code:'Key'+letter.toUpperCase(),windowsVirtualKeyCode:code,modifiers});
}
try{
  const t=await call('Target.createTarget',{url:'about:blank'},null);
  session=(await call('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
  await call('Page.enable');await call('Runtime.enable');
  await call('Network.enable');await call('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await call('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:out},null);
  await call('Emulation.setDeviceMetricsOverride',{width:1280,height:960,deviceScaleFactor:1,mobile:false});
  await open(html);

  const initial=await js('structuredClone(doc)');
  // Keyboard history uses real key events; input fields retain native undo.
  const labelId=initial.variants[0].current.labels[0].id;
  await select(labelId);await fill('#text','keyboard history edit');await click('#apply');
  await click('h1');await shortcut('z');
  assert.deepEqual(await js('doc.variants'),initial.variants,'Ctrl+Z must undo the diagram edit');
  await shortcut('y');assert.equal(await js('find('+JSON.stringify(labelId)+').text'),'keyboard history edit','Ctrl+Y must redo');
  const editedDoc=await js('JSON.stringify(doc)');
  await click('#text');await call('Input.insertText',{text:' unsubmitted'});
  const typed=await js("document.querySelector('#text').value");
  await shortcut('z');assert.notEqual(await js("document.querySelector('#text').value"),typed,'input must keep native undo');
  assert.equal(await js('JSON.stringify(doc)'),editedDoc,'input undo must not undo the diagram');
  await shortcut('y');assert.equal(await js('JSON.stringify(doc)'),editedDoc);
  await click('h1');await shortcut('z',6);assert.equal(await js('JSON.stringify(doc)'),editedDoc,'Alt+Ctrl+Z is not a diagram shortcut');
  await shortcut('z');assert.deepEqual(await js('doc.variants'),initial.variants);
  await shortcut('z');assert.deepEqual(await js('doc.variants'),initial.variants,'empty undo history is a no-op');
  await open(html);

  const eddyIds=['eddy-large','eddy-medium','eddy-small'];
  for(const v of initial.variants){
    for(const id of eddyIds)assert.ok(v.current.paths.some(p=>p.id===id),'missing spiral '+id+' in '+v.id);
    const spans=eddyIds.map(id=>{const pts=v.current.paths.find(p=>p.id===id).points;return Math.max(...pts.map(p=>p.x))-Math.min(...pts.map(p=>p.x));});
    assert.ok(spans[0]>spans[1]&&spans[1]>spans[2],'eddy sizes must decrease with k');
    for(const id of eddyIds)assert.equal(v.current.paths.find(p=>p.id===id).directed,false,'scale glyph must not imply rotation direction');
  }

  // Every region must contain multiple sizes/directions, geometrically below E(k).
  const eddyLayout=await js(`(()=>doc.variants.map(v=>{
    doc.selected_variant_id=v.id;render(false);
    const spectrum=document.querySelector('[data-id="spectrum"] path'),total=spectrum.getTotalLength();
    const samples=Array.from({length:3001},(_,i)=>spectrum.getPointAtLength(total*i/3000));
    const curveY=x=>{let i=1;while(i<samples.length&&samples[i].x<x)i++;if(i===samples.length||x<samples[0].x)return NaN;const a=samples[i-1],b=samples[i];return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x);};
    const axis=v.current.paths.find(p=>p.id==='axis-x').points[0].y;
    return ['energy','inertial','dissipation'].map((name,index)=>{
      const region=v.current.regions.find(r=>r.id==='region-'+name),prefix=['eddy-large','eddy-medium','eddy-small'][index];
      const eddies=v.current.paths.filter(p=>p.id===prefix||p.id.startsWith(prefix+'-'));
      return {variant:v.id,name,count:eddies.length,glyphs:eddies.map(p=>{
        const n=document.querySelector('[data-id="'+p.id+'"] path'),len=n.getTotalLength();
        const points=Array.from({length:101},(_,i)=>n.getPointAtLength(len*i/100));
        let area=0;for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];area+=a.x*b.y-b.x*a.y;}
        return {id:p.id,direction:Math.sign(area),span:Math.max(...points.map(q=>q.x))-Math.min(...points.map(q=>q.x)),fits:points.every(q=>q.x>region.x+2&&q.x<region.x+region.width-2&&q.y>curveY(q.x)+3&&q.y<axis-3)};
      })};
    });
  }))()`);
  for(const regions of eddyLayout)for(const r of regions){
    assert.ok(r.count>=3,'multiple eddies required in '+r.variant+'/'+r.name);
    assert.equal(new Set(r.glyphs.map(g=>g.direction)).size,2,'mix winding directions in '+r.variant+'/'+r.name);
    assert.ok(new Set(r.glyphs.map(g=>Math.round(g.span))).size>=3,'different sizes required');
    for(const g of r.glyphs)assert.ok(g.fits,'eddy must fit below curve and inside region: '+r.variant+'/'+g.id);
  }
  await open(html);
  await select('eddy-large');
  const eddyBefore=await js('structuredClone(find("eddy-large").points)');
  // Keep handles hidden so this gesture targets the spiral body rather than a control point.
  await select('label-title');
  const eddyStart=await js(`(()=>{const n=document.querySelector('[data-id="eddy-large"] path'),p=n.getPointAtLength(n.getTotalLength()*.7),q=new DOMPoint(p.x,p.y).matrixTransform(n.getScreenCTM());return {x:q.x,y:q.y}})()`);
  await mouse('mousePressed',eddyStart,1);await mouse('mouseMoved',{x:eddyStart.x+12,y:eddyStart.y+8},1);await mouse('mouseReleased',{x:eddyStart.x+12,y:eddyStart.y+8},1);
  const eddyAfter=await js('find("eddy-large").points');
  const shift={x:eddyAfter[0].x-eddyBefore[0].x,y:eddyAfter[0].y-eddyBefore[0].y};
  assert.ok(Math.abs(shift.x)>1&&Math.abs(shift.y)>1,'spiral must translate');
  for(let i=0;i<eddyBefore.length;i++){assert.ok(Math.abs(eddyAfter[i].x-eddyBefore[i].x-shift.x)<1e-8);assert.ok(Math.abs(eddyAfter[i].y-eddyBefore[i].y-shift.y)<1e-8);}
  await click('#undo');assert.deepEqual(await js('doc.variants'),initial.variants);
  await click('#redo');assert.deepEqual(await js('find("eddy-large").points'),eddyAfter);await click('#undo');

  assert.equal(await js(`document.querySelectorAll('[data-id="spectrum"] path').length`),1,'spectrum curve missing');
  await select('spectrum');
  const points=await js('structuredClone(find("spectrum").points)');
  assert.equal(await js(`document.querySelectorAll('[data-control="spectrum"]').length`),points.length);
  // One drag is one history item; cubic handles must change the actual path.
  const start=await js(`(()=>{const b=document.querySelector('[data-control="spectrum"][data-point="1"]').getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2}})()`);
  const oldPath=await js(`document.querySelector('[data-id="spectrum"] path').getAttribute('d')`);
  await mouse('mousePressed',start,1);await mouse('mouseMoved',{x:start.x+14,y:start.y+8},1);await mouse('mouseMoved',{x:start.x+24,y:start.y+14},1);await mouse('mouseReleased',{x:start.x+24,y:start.y+14},1);
  assert.notDeepEqual(await js('find("spectrum").points'),points);
  assert.notEqual(await js(`document.querySelector('[data-id="spectrum"] path').getAttribute('d')`),oldPath);
  await click('#undo');assert.deepEqual(await js('find("spectrum").points'),points);
  assert.equal(await js(`document.querySelector('#undo').disabled`),true);
  await click('#redo');assert.notDeepEqual(await js('find("spectrum").points'),points);
  await click('#undo');await select('spectrum');
  const newPoints=structuredClone(points);newPoints[1]={x:185,y:110};
  await fill('#points',newPoints.map(p=>p.x+', '+p.y).join('\n'));await click('#apply');
  assert.deepEqual(await js('find("spectrum").points'),newPoints);
  assert.equal(await js(`document.querySelector('#redo').disabled`),true);
  const beforeBad=await js('JSON.stringify(doc)');
  await fill('#points','NaN, 5');await click('#apply');assert.equal(await js('JSON.stringify(doc)'),beforeBad);
  await click('#undo');assert.deepEqual(await js('doc.variants'),initial.variants);
  await select('region-energy');await fill('#width',220);await click('#apply');assert.equal(await js('find("region-energy").width'),220);
  await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial);
  await click('#undo');assert.equal(await js('find("region-energy").width'),220);
  await variant('callouts');await select('label-law');await fill('#text','k^(−5/3) <tag> & "text"');await click('#apply');
  assert.equal(await js(`document.querySelectorAll('svg tag').length`),0);
  const edited=await js('structuredClone(doc)');
  const loaded=path.join(out,'edited.json');fs.writeFileSync(loaded,JSON.stringify(edited));
  await open(html);await load(loaded);assert.deepEqual(await js('doc.variants'),edited.variants);
  await click('#undo');assert.deepEqual(await js('doc.variants'),initial.variants);await click('#redo');
  for(const [name,change] of [
    ['revision',d=>d.base_revision='wrong'],
    ['points',d=>d.variants[0].current.paths[0].points.pop()],
    ['type',d=>d.variants[0].current.paths[0].type='unknown'],
    ['color',d=>d.variants[0].current.paths[0].stroke='red'],
    ['axis',d=>d.variants[0].current.paths.find(p=>p.id==='axis-x').directed=false],
    ['id',d=>d.variants[0].current.labels[1].id=d.variants[0].current.labels[0].id],
    ['initial',d=>d.variants[0].initial.labels[0].text='tampered'],
  ]){const bad=structuredClone(edited);change(bad);const f=path.join(out,'bad-'+name+'.json');fs.writeFileSync(f,JSON.stringify(bad));const before=await js('JSON.stringify(doc)');await load(f);assert.equal(await js('JSON.stringify(doc)'),before,name);assert.match(await js(`document.querySelector('#status').textContent`),/失敗/);}
  // Actual offline downloads, including an arrowhead and a math-like label.
  await js('window.showSaveFilePicker=undefined');await click('#confirm');
  let saved;
  for(let i=0;i<100;i++){saved=fs.readdirSync(out).find(n=>n.startsWith('turbulence-spectrum-')&&n.endsWith('.json'));if(saved)break;await delay(30);}
  assert.ok(saved,'missing JSON download');assert.deepEqual(JSON.parse(fs.readFileSync(path.join(out,saved),'utf8')).variants,edited.variants);
  for(const id of ['bands','callouts','transfer']){
    await variant(id);await select('label-title');
    await click('#png');
    const name='turbulence-spectrum-'+id+'.png';
    for(let i=0;i<100&&!fs.existsSync(path.join(out,name));i++)await delay(30);
    assert.ok(fs.existsSync(path.join(out,name)),'missing preview '+id);
  }
  fs.writeFileSync(path.join(out,'spectrum-wide.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
  await call('Emulation.setDeviceMetricsOverride',{width:560,height:1000,deviceScaleFactor:1,mobile:false});
  assert.equal(await js('document.documentElement.scrollWidth<=innerWidth'),true);
  fs.writeFileSync(path.join(out,'spectrum-narrow.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
  console.log(JSON.stringify({result:'PASS',browser:(await call('Browser.getVersion',{},null)).product,checks:'Bezier drag/form, history/branch/reset/variant, bands, text safety, snapshot validation/roundtrip, offline PNG/JSON, narrow layout',out}));
} finally {browser.kill();}
