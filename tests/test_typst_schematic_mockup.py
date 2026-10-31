"""Exercise the offline draft in real Chrome via its dependency-free CDP pipe.

SCHEMATIC_PLUGIN_ROOT can point at an actual manifest copy. Set
SCHEMATIC_EVIDENCE_DIR to retain downloads/screenshots (normally temporary).
Node >=22 and an installed Chrome/Chromium are optional for ordinary suites.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(os.environ.get('SCHEMATIC_PLUGIN_ROOT', ROOT / 'config/codex/plugins/ryo-workflows'))
HTML = PLUGIN / 'skills/creating-and-editing-typst-schematics/assets/layout-mockup.html'
CHROME = next((shutil.which(n) for n in ('google-chrome', 'chromium', 'chromium-browser') if shutil.which(n)), None)

# Browser operations use mouse/key events, the native file input, and actual
# downloaded files. Runtime inspection checks invariants that screenshots cannot.
RUNNER = r'''
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [chrome, html, out] = process.argv.slice(2);
const delay = ms => new Promise(r => setTimeout(r, ms));
const seenDownloads=new Map(fs.readdirSync(out).map(n=>[n,fs.statSync(path.join(out,n)).mtimeMs]));
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
async function downloaded(suffix){for(let i=0;i<100;i++){const f=fs.readdirSync(out).find(n=>n.startsWith('generic-selection-')&&n.endsWith(suffix)&&seenDownloads.get(n)!==fs.statSync(path.join(out,n)).mtimeMs);if(f){seenDownloads.set(f,fs.statSync(path.join(out,f)).mtimeMs);return path.join(out,f);}await delay(30);}throw Error('missing download '+suffix);}
try{
  const t=await call('Target.createTarget',{url:'about:blank'},null);
  session=(await call('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
  await call('Page.enable');await call('Runtime.enable');
  await call('Network.enable');await call('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await call('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:out},null);
  await call('Emulation.setDeviceMetricsOverride',{width:1280,height:960,deviceScaleFactor:1,mobile:false});
  await open(html);
  const initial=await js('structuredClone(doc)');
  await click('#png');fs.copyFileSync(await downloaded('.png'),path.join(out,'proposal-a.png'));
  await variant('vertical');await click('#png');fs.copyFileSync(await downloaded('.png'),path.join(out,'proposal-b.png'));await variant('horizontal');
  assert.notDeepEqual(fs.readFileSync(path.join(out,'proposal-a.png')),fs.readFileSync(path.join(out,'proposal-b.png')));
  await select('stage-1');
  const start=await js(`(()=>{const b=document.querySelector('[data-id="stage-1"] rect').getBoundingClientRect();return {x:b.x+12,y:b.y+12}})()`);
  await mouse('mousePressed',start,1);await mouse('mouseMoved',{x:start.x+17,y:start.y+9},1);await mouse('mouseReleased',{x:start.x+17,y:start.y+9},1);
  assert.notEqual(await js('current().elements[0].x'),initial.variants[0].current.elements[0].x);
  await select('stage-1');await fill('#x',43.7);await fill('#y',88.4);await fill('#width',162.6);await fill('#height',72.8);await click('#apply');
  await select('label-1');await fill('#text','候補 α <tag> & "引用"\nsecond line');await fill('#x',81.3);await fill('#y',36.4);await fill('#fontSize',18);await click('#apply');
  await select('flow-12');await fill('#waypoints','340.2, 177.8\n350.3, 177.8');await click('#apply');
  await select('edge-label');await fill('#text','選択へ\nroute');await fill('#x',351.7);await fill('#y',124.2);await click('#apply');
  const beforeGroup=await js('structuredClone(current())');
  assert.deepEqual([beforeGroup.elements[0].x,beforeGroup.elements[0].y,beforeGroup.elements[0].width,beforeGroup.elements[0].height],[43.7,88.4,162.6,72.8]);
  assert.equal(beforeGroup.labels[0].text,'候補 α <tag> & \"引用\"\nsecond line');assert.equal(beforeGroup.labels[0].fontSize,18);
  assert.deepEqual(beforeGroup.connections[0].waypoints,[{x:340.2,y:177.8},{x:350.3,y:177.8}]);
  await select('cycle');await fill('#x',52.3);await fill('#y',61.7);await fill('#width',704.8);await fill('#height',312.6);await click('#apply');
  const afterGroup=await js('structuredClone(current())');
  for(let i=0;i<beforeGroup.elements.length;i++){
    const a=beforeGroup.elements[i],b=afterGroup.elements[i];if(a.group_id!=='cycle')continue;
    assert.ok(Math.abs(b.x/a.x-704.8/beforeGroup.groups[0].width)<1e-9, JSON.stringify({a,b,g:afterGroup.groups,status:await js("document.querySelector('#status').textContent")}));
    assert.ok(Math.abs(b.y/a.y-312.6/beforeGroup.groups[0].height)<1e-9);
    assert.ok(Math.abs(b.width/a.width-704.8/beforeGroup.groups[0].width)<1e-9);
    assert.ok(Math.abs(b.height/a.height-312.6/beforeGroup.groups[0].height)<1e-9);
  }
  assert.deepEqual(afterGroup.connections,beforeGroup.connections,'waypoints/direction preserved');
  assert.equal(afterGroup.groups[0].x,52.3);assert.equal(afterGroup.groups[0].y,61.7);
  const e=afterGroup.elements[0],g=afterGroup.groups[0];
  const rendered=await js(`document.querySelector('[data-id=\"flow-12\"] polyline').getAttribute('points').split(' ')[0].split(',').map(Number)`);
  assert.deepEqual(rendered,[g.x+e.x+e.width,g.y+e.y+e.height/2]);
  for(const a of beforeGroup.labels){const b=afterGroup.labels.find(x=>x.id===a.id);assert.equal(b.text,a.text);assert.equal(b.fontSize,a.fontSize);}
  assert.deepEqual(await js('anchor(current().connections[0].from)'),await js(`(()=>{const e=worldElement('stage-1');return {x:e.x+e.width,y:e.y+e.height/2}})()`));
  await variant('vertical');await select('label-1');await fill('#text','Bだけの編集 <tag> & \"引用\" </script> $&\n第二行 β');await click('#apply');
  const editedB=await js('structuredClone(current())');
  await variant('horizontal');await click('#reset');
  assert.deepEqual(await js('current()'),initial.variants[0].initial);
  await variant('vertical');assert.deepEqual(await js('current()'),editedB);
  // Re-edit A as a non-integer fixture for the tidy-coordinate demonstration.
  await variant('horizontal');await select('cycle');await fill('#x',50.3);await fill('#y',60.2);await fill('#width',700.4);await fill('#height',310.6);await click('#apply');
  await select('label-1');await fill('#text','候補 α\nCandidates');await click('#apply');
  await select('edge-label');await fill('#text','選択へ\nselect');await fill('#x',279.8);await fill('#y',281.2);await click('#apply');
  await select('flow-12');await fill('#waypoints','280.2, 195.1\n290.4, 195.1');await click('#apply');
  const expected=await js('structuredClone(doc)');
  await js('window.showSaveFilePicker=undefined');await click('#confirm');const saved=await downloaded('.json');const actual=JSON.parse(fs.readFileSync(saved,'utf8'));
  assert.deepEqual(actual.variants,expected.variants);assert.equal(actual.selected_variant_id,'horizontal');
  assert.equal(actual.variants[0].current.labels[0].text,'候補 α\nCandidates');
  assert.equal(actual.variants[0].current.labels.find(l=>l.id==='edge-label').text,'選択へ\nselect');
  await open(html);await load(saved);assert.deepEqual(await js('doc.variants'),actual.variants);
  assert.equal(await js('doc.selected_variant_id'),actual.selected_variant_id);
  await variant('vertical');
  assert.equal(await js(`document.querySelectorAll('svg tag').length`),0,'labels are text, not markup');
  assert.match(await js(`document.querySelector('[data-id=\"label-1\"] text').textContent`),/<tag> & \"引用\"/);
  await variant('horizontal');
  const valid=await js('JSON.stringify(doc)');
  const invalid=[['broken','{'],['version',JSON.stringify({...actual,schema_version:2})],['figure',JSON.stringify({...actual,figure_id:'another'})],['revision',JSON.stringify({...actual,base_revision:'other'})]];
  for(const [name,mutate] of [
    ['duplicate', d=>d.variants[0].current.labels[1]={...d.variants[0].current.labels[0]}],
    ['reference', d=>d.variants[0].current.connections[0].from.element_id='missing'],
    ['coordinate', d=>d.variants[0].current.elements[0].x=null],
    ['dimension', d=>d.variants[0].current.elements[0].width=-1],
    ['reset-tamper', d=>d.variants[0].initial.labels[0].text='changed'],
    ['direction', d=>d.variants[0].current.connections[0].to.element_id='stage-1']
  ]){let d=structuredClone(actual);mutate(d);invalid.push([name,JSON.stringify(d)]);}
  for(const [name,content] of invalid){const f=path.join(out,'invalid-'+name+'.json');fs.writeFileSync(f,content);await load(f);assert.equal(await js('JSON.stringify(doc)'),valid,name+' must preserve edits');assert.match(await js(`document.querySelector('#status').textContent`),/読込失敗/);}
  await js(`window.showSaveFilePicker=async()=>{throw new Error('test write failure')}`);await click('#confirm');
  assert.match(await js(`document.querySelector('#status').textContent`),/保存失敗/);assert.equal(await js('JSON.stringify(doc)'),valid);
  await click('#png');fs.copyFileSync(await downloaded('.png'),path.join(out,'accepted-fixture.png'));
  fs.writeFileSync(path.join(out,'browser-wide.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await call('Emulation.setDeviceMetricsOverride',{width:560,height:1000,deviceScaleFactor:1,mobile:false});
  assert.equal(await js('document.documentElement.scrollWidth<=innerWidth'),true);
  fs.writeFileSync(path.join(out,'browser-narrow.png'),Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
  // Codex redraw: take the LAST file, preserve untouched IDs in BOTH states,
  // then explicitly add a new element and bump the revision in generated HTML.
  const next=structuredClone(actual);next.base_revision='fixture-r2';delete next.snapshot;
  for(const v of next.variants)for(const s of [v.initial,v.current])s.elements.push({id:'new-note',group_id:null,x:800,y:480,width:70,height:40});
  for(let i=0;i<actual.variants.length;i++)for(const k of ['elements','labels','groups','connections','constraints'])assert.deepEqual(next.variants[i].current[k].filter(x=>x.id!=='new-note'),actual.variants[i].current[k]);
  const redraw=path.join(out,'redraw.html');fs.writeFileSync(redraw,fs.readFileSync(html,'utf8').replace(/^const INITIAL = .*;$/m,()=> 'const INITIAL = '+JSON.stringify(next).replaceAll('<','\\u003c')+';'));
  await open(redraw);assert.deepEqual(await js('doc.variants'),next.variants);
  const redrawn=await js('JSON.stringify(doc)');await load(saved);assert.equal(await js('JSON.stringify(doc)'),redrawn);assert.match(await js(`document.querySelector('#status').textContent`),/読込失敗/);
  console.log(JSON.stringify({browser:await call('Browser.getVersion',{},null),download:saved,checks:'UI edit/drag, anchors, group affine resize, two-variant reset, file roundtrip, invalid input atomicity, save failure, PNG, narrow viewport, ID-preserving redraw'}));
} finally {browser.kill();}
'''


@unittest.skipUnless(CHROME and shutil.which('node'), 'installed Chrome and Node required')
class MockupBrowserTests(unittest.TestCase):
    def test_browser_edit_download_reload_and_protection(self):
        self.assertTrue(HTML.is_file(), HTML)
        with tempfile.TemporaryDirectory(prefix='schematic-browser-', dir='/tmp') as tmp:
            out = Path(os.environ.get('SCHEMATIC_EVIDENCE_DIR', tmp))
            out.mkdir(parents=True, exist_ok=True)
            runner = Path(tmp) / 'browser.mjs'
            runner.write_text(RUNNER)
            result = subprocess.run(['node', str(runner), CHROME, str(HTML), str(out)], text=True, capture_output=True, timeout=110)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main()
