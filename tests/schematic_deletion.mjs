// Repository regression; HTML and its snapshots are the only draft inputs.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {withBrowser} from './schematic_browser.mjs';
const [chrome, html, out] = process.argv.slice(2);
await withBrowser({chrome, html, out}, async ({call, js, click, fill, select, variant, open, load, delay}) => {
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
});
