// Usage: node check-mockup-colors.mjs CHROME HTML OUTPUT_DIRECTORY
// Chrome uses an isolated temporary profile and offline network emulation.

import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [chrome, html, out] = process.argv.slice(2);
if(!chrome||!html||!out)throw Error('Usage: node check-mockup-colors.mjs CHROME HTML OUTPUT_DIRECTORY');
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
 await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
 await call('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await call('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:out},null);
 await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1100,deviceScaleFactor:1,mobile:false});
 await open(html);
 const initial=await js('structuredClone(doc)'),spectrum=initial.figure_id==='turbulence-spectrum';
 const expected={black:'#000000',gray:'#aaaaaa',silver:'#dddddd',white:'#ffffff',navy:'#001f3f',blue:'#0074d9',aqua:'#7fdbff',teal:'#39cccc',eastern:'#239dad',purple:'#b10dc9',fuchsia:'#f012be',maroon:'#85144b',red:'#ff4136',orange:'#ff851b',yellow:'#ffdc00',olive:'#3d9970',green:'#2ecc40',lime:'#01ff70'};
 const targets=spectrum?[['spectrum','stroke','path'],['region-energy','fill','rect'],['label-title','fill','text'],['axis-x','stroke','path']]:[['stage-1','fill','rect'],['stage-1','stroke','rect'],['cycle','fill','rect'],['cycle','stroke','rect'],['label-1','fill','text'],['flow-12','stroke','polyline']];
 assert.ok(await js("!!document.querySelector('#color-fields')"),'color controls missing');
 for(const [id,field,tag] of targets){
  await select(id);
  assert.deepEqual(await js(`Array.from(document.querySelector('#${field}').options).filter(o=>o.value).map(o=>o.value)`),Object.keys(expected));
  const before=await js('structuredClone(doc)');
  // Each built-in must use Typst's RGB, including CSS names with different values.
  for(const [name,hex] of Object.entries(expected)){
   await js(`document.querySelector('#${field}').value=${JSON.stringify(name)};document.querySelector('#${field}').dispatchEvent(new Event('change'))`);
   await click('#apply');
   assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),name);
   assert.equal(await js(`document.querySelector('[data-id="${id}"] ${tag}').getAttribute('${field}')`),hex,id+'/'+name);
   if(id==='flow-12'||id==='axis-x')assert.equal(await js(`(()=>{const p=document.querySelector('[data-id="${id}"] ${tag}');return document.querySelector(p.getAttribute('marker-end').slice(4,-1)+' path').getAttribute('fill')})()`),hex,'arrowhead');
  }
  await click('#undo');assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),'green');
  await click('#redo');assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),'lime');
  // Returning to the initial color does not add an empty override to legacy objects.
  await js(`document.querySelector('#${field}').value='';document.querySelector('#${field}').dispatchEvent(new Event('change'))`);await click('#apply');
  assert.deepEqual(await js('doc.variants'),before.variants);
 }
 await open(html);
 const fillId=spectrum?'region-energy':'stage-1',edgeId=spectrum?'axis-x':'flow-12',labelId=spectrum?'label-title':'label-1';
 for(const [id,field,name] of [[fillId,'fill','red'],[edgeId,'stroke','eastern'],[labelId,'fill','blue']]){
  await select(id);await js(`document.querySelector('#${field}').value='${name}'`);await click('#apply');
 }
 const edited=await js('structuredClone(doc)');
 await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial);await click('#undo');assert.deepEqual(await js('doc.variants'),edited.variants);
 await variant(initial.variants[1].id);assert.deepEqual(await js('current()'),initial.variants[1].initial);await click('#undo');
 await js('window.showSaveFilePicker=undefined');await click('#confirm');
 let saved;
 for(let i=0;i<100;i++){saved=fs.readdirSync(out).find(n=>n.startsWith(initial.figure_id+'-')&&n.endsWith('.json'));if(saved)break;await delay(30);}
 assert.ok(saved,'missing color JSON');const exported=JSON.parse(fs.readFileSync(path.join(out,saved),'utf8'));assert.deepEqual(exported.variants,edited.variants);
 await open(html);await load(path.join(out,saved));assert.deepEqual(await js('doc.variants'),edited.variants);
 // Reject invalid colors atomically, including prototype property names and CSS injection.
 for(const badColor of ['constructor','rebeccapurple','#123456','url(https://example.org/x)',null]){
  const bad=structuredClone(edited);const objects=spectrum?bad.variants[0].current.paths:bad.variants[0].current.connections;objects[0].stroke=badColor;
  const file=path.join(out,'invalid-color.json');fs.writeFileSync(file,JSON.stringify(bad));const before=await js('JSON.stringify(doc)');await load(file);assert.equal(await js('JSON.stringify(doc)'),before);assert.match(await js("document.querySelector('#status').textContent"),/失敗/);
 }
 const legacy=path.join(out,'legacy.json');fs.writeFileSync(legacy,JSON.stringify(initial));await load(legacy);assert.deepEqual(await js('doc.variants'),initial.variants);await click('#undo');assert.deepEqual(await js('doc.variants'),edited.variants);
 await click('#png');const png=path.join(out,initial.figure_id+'-'+initial.selected_variant_id+'.png');for(let i=0;i<100&&!fs.existsSync(png);i++)await delay(30);assert.ok(fs.existsSync(png),'missing color PNG');
 const data='data:image/png;base64,'+fs.readFileSync(png).toString('base64');
 const pixel=await js(`(async()=>{const img=new Image();img.src=${JSON.stringify(data)};await img.decode();const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const ctx=c.getContext('2d');ctx.drawImage(img,0,0);const o=find('${fillId}');const p=${spectrum?'o':'worldElement(o.id)'};return Array.from(ctx.getImageData((p.x+10)*2,(p.y+10)*2,1,1).data)})()`);
 assert.deepEqual(pixel,[255,65,54,255],'exported PNG must contain Typst red');
 await select(fillId);fs.writeFileSync(path.join(out,'colors-wide.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 await call('Emulation.setDeviceMetricsOverride',{width:560,height:1100,deviceScaleFactor:1,mobile:false});assert.equal(await js('document.documentElement.scrollWidth<=innerWidth'),true);
 fs.writeFileSync(path.join(out,'colors-narrow.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 console.log(JSON.stringify({result:'PASS',figure:initial.figure_id,checks:'18 official names/RGB, all object styles, arrowheads, history/reset/variants, legacy JSON, invalid colors, offline JSON/PNG pixels, narrow layout',out}));
}finally{browser.kill();}
