// Usage: node check-mockup-deletion.mjs CHROME HTML OUTPUT_DIRECTORY
// Chrome uses an isolated temporary profile and offline network emulation.

import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [chrome, html, out] = process.argv.slice(2);
if(!chrome||!html||!out)throw Error('Usage: node check-mockup-deletion.mjs CHROME HTML OUTPUT_DIRECTORY');
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
async function click(selector){const b=await js(`(()=>{const target=document.querySelector(${JSON.stringify(selector)});target.scrollIntoView({block:'nearest'});const b=target.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2}})()`);await mouse('mousePressed',b,1);await mouse('mouseReleased',b,1);}
async function mouse(type,p,buttons=0){await call('Input.dispatchMouseEvent',{type,...p,button:buttons?'left':'none',buttons,clickCount:type==='mouseMoved'?0:1});}
async function fill(selector,text){await click(selector);await js(`document.querySelector(${JSON.stringify(selector)}).select()`);await call('Input.insertText',{text:String(text)});}
async function select(id){await js(`document.querySelector('#selection').value=${JSON.stringify(id)};document.querySelector('#selection').dispatchEvent(new Event('change'))`);}
async function variant(id){await js(`document.querySelector('#variant').value=${JSON.stringify(id)};document.querySelector('#variant').dispatchEvent(new Event('change'))`);}
async function open(file){await call('Page.navigate',{url:pathToFileURL(file).href});for(let i=0;i<100;i++){if(await js(`document.readyState==='complete' && (!!document.querySelector('#selection option') || document.querySelector('#selection')?.disabled)`))return;await delay(30);}throw Error('page not ready');}
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
 assert.ok(await js("!!document.querySelector('#delete')"),'delete control missing');
 const cases=spectrum?['spectrum','region-energy','label-law','axis-x']:['label-1','flow-12','stage-2','cycle'];
 for(const id of cases){
  await open(html);await select(id);await click('#delete');
  const after=await js('structuredClone(doc)'),scene=after.variants[0].current;
  const removed=spectrum?[id]:id==='stage-2'?['stage-2','label-2','flow-12','flow-23']:id==='cycle'?['cycle','stage-1','stage-2','stage-3','label-1','label-2','label-3','group-label','flow-12','flow-23','return','exit']:[id];
  const keys=spectrum?['paths','regions','labels']:['elements','groups','labels','connections'];
  for(const key of keys)assert.deepEqual(scene[key],initial.variants[0].current[key].filter(o=>!removed.includes(o.id)),id+'/'+key);
  if(!spectrum)assert.deepEqual(scene.constraints,['stage-2','cycle'].includes(id)?[]:initial.variants[0].current.constraints);
  assert.deepEqual(after.variants[0].initial,initial.variants[0].initial,'reset baseline must remain exact');
  assert.deepEqual(after.variants[1],initial.variants[1],'deletion is local to one variant');
  assert.equal(await js(`!!document.querySelector('[data-id="${id}"]')`),false,'deleted item remains in SVG');
  assert.equal(await js(`!!document.querySelector('#selection option[value="${id}"]')`),false);
  assert.deepEqual(await js('validate(doc)'),after);
  // Remaining objects remain editable without resurrecting deleted objects.
  const survivor=scene.labels[0].id;await select(survivor);await fill('#text','surviving label');assert.equal(await js(`find('${survivor}').text`),'surviving label');
  await click('#undo');assert.deepEqual(await js('doc.variants'),after.variants);
  await click('#undo');assert.deepEqual(await js('doc.variants'),initial.variants);assert.equal(await js('selected'),id);
  await click('#redo');assert.deepEqual(await js('doc.variants'),after.variants);
  await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial);await click('#undo');assert.deepEqual(await js('doc.variants'),after.variants);
  const file=path.join(out,'deleted-'+id+'.json');fs.writeFileSync(file,JSON.stringify(after));await open(html);await load(file);assert.deepEqual(await js('doc.variants'),after.variants,'subset snapshot roundtrip');
  // A regenerated HTML can start with a deleted current state and retain a full reset state.
  const redraw=path.join(out,'redraw-'+id+'.html');
  fs.writeFileSync(redraw,fs.readFileSync(html,'utf8').replace(/^const INITIAL = .*;$/m,()=> 'const INITIAL = '+JSON.stringify(after).replace(/</g,'\\u003c')+';'));
  await open(redraw);assert.deepEqual(await js('doc.variants'),after.variants);
  await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial,'reset after redraw must restore deleted objects');
  await click('#undo');assert.deepEqual(await js('doc.variants'),after.variants);

 }
 // Subset support must not permit additions, duplicate IDs, rewiring, or dangling ownership.
 await open(html);
 const invalid=[['unknown',d=>(spectrum?d.variants[0].current.paths:d.variants[0].current.elements)[0].id='unknown-object'],['duplicate',d=>{const a=spectrum?d.variants[0].current.paths:d.variants[0].current.elements;a[1].id=a[0].id;}],['initial',d=>d.variants[0].initial.labels.pop()]];
 if(!spectrum){invalid.push(['dangling',d=>d.variants[0].current.elements.splice(0,1)],['rewired',d=>d.variants[0].current.connections[0].from.element_id='stage-3'],['constraint',d=>d.variants[0].current.constraints.pop()]);}
 for(const [name,change] of invalid){const bad=structuredClone(initial);change(bad);const file=path.join(out,'invalid-'+name+'.json');fs.writeFileSync(file,JSON.stringify(bad));await load(file);assert.deepEqual(await js('doc.variants'),initial.variants,name);assert.match(await js("document.querySelector('#status').textContent"),/失敗/);assert.equal(await js('undoStack.length'),0);}
 await open(html);await select(cases[0]);await click('#delete');
 fs.writeFileSync(path.join(out,'deleted-wide.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 // Delete every object, including the currently selected last item.
 for(let i=0;i<100&&await js('!!find(selected)');i++)await click('#delete');
 assert.equal(await js('categories.flatMap(k=>current()[k]).length'),0);
 assert.equal(await js('selected'),null);assert.equal(await js("document.querySelector('#delete').disabled"),true);
 assert.equal(await js("document.querySelector('#editor').classList.contains('hidden')"),true);
 assert.deepEqual(await js('validate(doc)'),await js('structuredClone(doc)'));
 const empty=await js('structuredClone(doc)');await click('#undo');assert.ok(await js('categories.flatMap(k=>current()[k]).length')>0);await click('#redo');assert.deepEqual(await js('doc.variants'),empty.variants);
 await js('window.showSaveFilePicker=undefined');await click('#confirm');await click('#png');
 let saved,png;
 for(let i=0;i<100;i++){const files=fs.readdirSync(out);saved=files.find(n=>n.startsWith(initial.figure_id+'-')&&n.endsWith('.json'));png=files.find(n=>n.startsWith(initial.figure_id+'-')&&n.endsWith('.png'));if(saved&&png)break;await delay(30);}
 assert.ok(saved&&png,'empty drafts must export JSON and PNG');assert.deepEqual(JSON.parse(fs.readFileSync(path.join(out,saved),'utf8')).variants,empty.variants);
 await open(html);await load(path.join(out,saved));assert.deepEqual(await js('doc.variants'),empty.variants);
 await click('#undo');assert.deepEqual(await js('doc.variants'),initial.variants);await click('#redo');
 await variant(initial.variants[1].id);assert.deepEqual(await js('current()'),initial.variants[1].initial);await click('#undo');assert.equal(await js('categories.flatMap(k=>current()[k]).length'),0);
 await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial);
 await click('#undo');assert.equal(await js('categories.flatMap(k=>current()[k]).length'),0);

 const emptyHtml=path.join(out,'empty-seed.html');
 fs.writeFileSync(emptyHtml,fs.readFileSync(html,'utf8').replace(/^const INITIAL = .*;$/m,()=> 'const INITIAL = '+JSON.stringify(empty).replace(/</g,'\\u003c')+';'));
 await open(emptyHtml);assert.deepEqual(await js('doc.variants'),empty.variants,'an initially empty draft must start cleanly');
 await click('#reset');assert.deepEqual(await js('current()'),initial.variants[0].initial);await click('#undo');assert.equal(await js('categories.flatMap(k=>current()[k]).length'),0);
 await call('Emulation.setDeviceMetricsOverride',{width:560,height:1000,deviceScaleFactor:1,mobile:false});assert.equal(await js('document.documentElement.scrollWidth<=innerWidth'),true);
 fs.writeFileSync(path.join(out,'deleted-empty-narrow.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 console.log(JSON.stringify({result:'PASS',figure:initial.figure_id,checks:'all object kinds, dependent deletion, surviving edits, undo/redo/reset/variants, subset import and validation, empty scene, JSON/PNG, narrow layout',out}));
}finally{browser.kill();}
