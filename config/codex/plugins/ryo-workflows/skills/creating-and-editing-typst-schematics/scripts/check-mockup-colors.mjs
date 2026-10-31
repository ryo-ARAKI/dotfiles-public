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
async function click(selector){const b=await js(`(()=>{const target=document.querySelector(${JSON.stringify(selector)});target.scrollIntoView({block:'nearest'});const b=target.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2}})()`);await mouse('mousePressed',b,1);await mouse('mouseReleased',b,1);}
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
 assert.equal(await js("!!document.querySelector('#apply')"),false,'all edits must work without an Apply button');
 const boxId=spectrum?'region-energy':'stage-1',textId=spectrum?'label-title':'label-1';

 // Round only the presentation; editing one point must preserve all other precise components.
 const precise=structuredClone(initial),scene=precise.variants[0].current;
 const preciseBox=(spectrum?scene.regions:scene.elements).find(o=>o.id===boxId);
 Object.assign(preciseBox,{x:137.123456789,y:-0.0000001,width:190.987654321,height:120.333333333});
 const precisePath=(spectrum?scene.paths:scene.connections).find(o=>o.id===(spectrum?'spectrum':'flow-12'));
 if(!spectrum)precisePath.waypoints=[{x:321.123456789,y:195.987654321},{x:350.111111111,y:195.987654321}];
 const pointKey=spectrum?'points':'waypoints',pointField=spectrum?'points':'waypoints';
 precisePath[pointKey][0]={x:321.123456789,y:195.987654321};
 const precisionFile=path.join(out,'precise-input.json');fs.writeFileSync(precisionFile,JSON.stringify(precise));await load(precisionFile);
 await select(boxId);
 for(const [field,value] of [['x','137.12'],['y','0'],['width','190.99'],['height','120.33']])assert.equal(await js(`document.querySelector('#${field}').value`),value,'compact numeric display');
 assert.deepEqual(await js('doc.variants'),precise.variants,'display must not round saved state');
 await fill('#x','141.123456789');assert.equal(await js(`find('${boxId}').x`),141.123456789,'retain typed precision');
 await click('h1');assert.equal(await js("document.querySelector('#x').value"),'141.12','format after editing');
 assert.equal(await js(`find('${boxId}').width`),preciseBox.width,'other values retain precision');
 await select(spectrum?'spectrum':'flow-12');
 const compact=await js(`document.querySelector('#${pointField}').value`);assert.equal(compact.split('\n')[0],'321.12, 195.99');
 await fill('#'+pointField,compact.replace('321.12, 195.99','325.5, 195.99'));
 const preciseExpected=structuredClone(precisePath[pointKey]);preciseExpected[0].x=325.5;
 assert.deepEqual(await js(`find('${precisePath.id}').${pointKey}`),preciseExpected,'unmodified points/components must retain precision');
 await click('#undo');assert.deepEqual(await js(`find('${precisePath.id}').${pointKey}`),precisePath[pointKey]);
 fs.writeFileSync(path.join(out,'coordinate-precision.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 await open(html);
 await select(boxId);const original=await js('structuredClone(doc)');
 // Each keystroke updates the figure; one continuous field edit is one history entry.
 await fill('#x','137');await call('Input.insertText',{text:'.25'});
 assert.equal(await js(`find('${boxId}').x`),137.25);
 assert.equal(await js(`Number(document.querySelector('[data-id="${boxId}"] rect').getAttribute('x'))`),spectrum?137.25:187.25);
 assert.equal(await js("document.activeElement.id"),'x');
 await click('#undo');assert.deepEqual(await js('doc.variants'),original.variants);await click('#redo');assert.equal(await js(`find('${boxId}').x`),137.25);
 for(const [field,value] of [['y',145.5],['width',190.5],['height',120.25]]){
  await fill('#'+field,value);assert.equal(await js(`find('${boxId}').${field}`),value);
 }
 const lastValid=await js('JSON.stringify(doc)');
 await fill('#width',0);assert.equal(await js('JSON.stringify(doc)'),lastValid);
 assert.equal(await js("document.querySelector('#width').getAttribute('aria-invalid')"),'true');
 await fill('#width',190.5);assert.equal(await js('JSON.stringify(doc)'),lastValid);
 await fill('#x','');const xBefore=await js(`find('${boxId}').x`);
 await fill('#y',170.5);assert.equal(await js(`find('${boxId}').x`),xBefore);assert.equal(await js(`find('${boxId}').y`),170.5);
 assert.equal(await js("document.querySelector('#x').value"),'','other fields must not consume or erase incomplete input');
 await select(textId);const labelText='編集 <tag> & text\n第二行';
 await fill('#text',labelText);assert.equal(await js(`find('${textId}').text`),labelText);
 assert.equal(await js("document.activeElement.id"),'text');assert.equal(await js("document.querySelectorAll('svg tag').length"),0);
 await fill('#fontSize',24.5);assert.equal(await js(`find('${textId}').fontSize`),24.5);
 assert.equal(await js(`document.querySelector('[data-id="${textId}"] text').getAttribute('font-size')`),'24.5');
 // IME provisional text remains in the field until composition completes.
 await js("document.querySelector('#text').value='日本語入力';document.querySelector('#text').dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}))");
 assert.equal(await js(`find('${textId}').text`),labelText);
 await js("document.querySelector('#text').dispatchEvent(new CompositionEvent('compositionend',{bubbles:true}))");assert.equal(await js(`find('${textId}').text`),'日本語入力');
 const pathId=spectrum?'spectrum':'flow-12',field=spectrum?'points':'waypoints';await select(pathId);
 const points=spectrum?await js('structuredClone(find("spectrum").points)'):[{x:320.5,y:195.25},{x:350.5,y:195.25}];
 if(spectrum)points[1].y+=12.5;
 await fill('#'+field,points.map(p=>p.x+', '+p.y).join('\n'));
 assert.deepEqual(await js(`find('${pathId}').${spectrum?'points':'waypoints'}`),points);
 const validPath=await js('JSON.stringify(doc)');await fill('#'+field,'12,');assert.equal(await js('JSON.stringify(doc)'),validPath);
 assert.equal(await js(`document.querySelector('#${field}').value`),'12,');
 await click('#undo');await click('#redo');assert.deepEqual(await js(`find('${pathId}').${spectrum?'points':'waypoints'}`),points);
 await open(html);

 for(const [id,field,tag] of targets){
  await select(id);
  assert.deepEqual(await js(`Array.from(document.querySelector('#${field}').options).filter(o=>o.value).map(o=>o.value)`),Object.keys(expected));
  assert.equal(await js(`document.querySelector('#${field}-picker').textContent.includes('#')`),false,'menu must not display color codes');
  const swatches=await js(`Array.from(document.querySelectorAll('#${field}-options button')).map(b=>({name:b.dataset.value,color:b.querySelector('.color-swatch').style.backgroundColor}))`);
  assert.deepEqual(swatches.filter(b=>b.name).map(b=>b.name),Object.keys(expected));
  for(const swatch of swatches.filter(b=>b.name))assert.equal(swatch.color,'rgb('+expected[swatch.name].slice(1).match(/../g).map(h=>parseInt(h,16)).join(', ')+')');
  const before=await js('structuredClone(doc)');
  // Each built-in must use Typst's RGB, including CSS names with different values.
  for(const [name,hex] of Object.entries(expected)){
   await click(`#${field}-picker summary`);
   const option=`#${field}-options button[data-value="${name}"]`;
   await js(`document.querySelector(${JSON.stringify(option)}).scrollIntoView({block:'nearest'})`);await click(option);
   assert.equal(await js(`document.querySelector('#${field}-picker').open`),false,'selection closes menu');
   assert.equal(await js(`document.querySelector('#${field}-name').textContent`),name);
   assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),name);
   assert.equal(await js(`document.querySelector('[data-id="${id}"] ${tag}').getAttribute('${field}')`),hex,id+'/'+name);
   if(id==='flow-12'||id==='axis-x')assert.equal(await js(`(()=>{const p=document.querySelector('[data-id="${id}"] ${tag}');return document.querySelector(p.getAttribute('marker-end').slice(4,-1)+' path').getAttribute('fill')})()`),hex,'arrowhead');
  }
  await click('#undo');assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),'green');
  await click('#redo');assert.equal(await js(`find(${JSON.stringify(id)}).${field}`),'lime');
  // Returning to the initial color does not add an empty override to legacy objects.
  await js(`document.querySelector('#${field}').value='';document.querySelector('#${field}').dispatchEvent(new Event('change'))`);
  assert.deepEqual(await js('doc.variants'),before.variants);
 }
 await open(html);
 const fillId=spectrum?'region-energy':'stage-1',edgeId=spectrum?'axis-x':'flow-12',labelId=spectrum?'label-title':'label-1';
 for(const [id,field,name] of [[fillId,'fill','red'],[edgeId,'stroke','eastern'],[labelId,'fill','blue']]){
  await select(id);await js(`document.querySelector('#${field}').value='${name}';document.querySelector('#${field}').dispatchEvent(new Event('change'))`);
 }
 // Incomplete numeric input stays intact; valid text is already reflected before choosing a color.
 await select(fillId);const originalX=await js(`find('${fillId}').x`);
 await fill('#x','');await click('#fill-picker summary');await click('#fill-options button[data-value="yellow"]');
 assert.equal(await js(`find('${fillId}').fill`),'yellow');assert.equal(await js(`find('${fillId}').x`),originalX);
 assert.equal(await js("document.querySelector('#x').value"),'','invalid unfinished coordinate must be preserved');
 await click('#undo');assert.equal(await js(`find('${fillId}').fill`),'red');
 await select(labelId);const originalText=await js(`find('${labelId}').text`);await fill('#text','pending label draft');
 await click('#fill-picker summary');await click('#fill-options button[data-value="green"]');
 assert.equal(await js(`find('${labelId}').text`),'pending label draft');assert.equal(await js("document.querySelector('#text').value"),'pending label draft');
 assert.equal(await js(`find('${labelId}').fill`),'green');
 await click('#undo');assert.equal(await js(`find('${labelId}').fill`),'blue');await click('#redo');assert.equal(await js(`find('${labelId}').fill`),'green');
 await click('#undo');
 const noChange=await js('JSON.stringify(doc)'),historyLength=await js('undoStack.length'),redoLength=await js('redoStack.length');
 await click('#fill-picker summary');await click('#fill-options button[data-value="blue"]');
 assert.equal(await js('JSON.stringify(doc)'),noChange);assert.equal(await js('undoStack.length'),historyLength);assert.equal(await js('redoStack.length'),redoLength,'same color must preserve redo');
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
 await select(fillId);await click('#fill-picker summary');
 fs.writeFileSync(path.join(out,'colors-menu.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 await js("document.querySelector('#fill-options button').focus()");
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowDown'});
 assert.equal(await js("document.activeElement.dataset.value"),'black');
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape'});
 assert.equal(await js("document.querySelector('#fill-picker').open"),false);
 await click('#fill-picker summary');await click('h1');assert.equal(await js("document.querySelector('#fill-picker').open"),false);
 await select(fillId);fs.writeFileSync(path.join(out,'colors-wide.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 await call('Emulation.setDeviceMetricsOverride',{width:560,height:1100,deviceScaleFactor:1,mobile:false});assert.equal(await js('document.documentElement.scrollWidth<=innerWidth'),true);
 fs.writeFileSync(path.join(out,'colors-narrow.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
 console.log(JSON.stringify({result:'PASS',figure:initial.figure_id,checks:'18 official names/RGB, all object styles, arrowheads, history/reset/variants, legacy JSON, invalid colors, offline JSON/PNG pixels, narrow layout',out}));
}finally{browser.kill();}
