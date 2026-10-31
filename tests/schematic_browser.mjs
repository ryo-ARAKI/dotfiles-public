// Test-only Chrome pipe transport. Delivered drafts have no dependency on this helper.
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export async function withBrowser({chrome, html, out}, check) {
  if (!chrome || !html || !out) throw Error('Usage: node CHECK.mjs CHROME HTML OUTPUT_DIRECTORY');
  out = path.resolve(out);
  fs.mkdirSync(out, {recursive: true});
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
  const seenDownloads = new Map(fs.readdirSync(out).map(name => [name, fs.statSync(path.join(out, name)).mtimeMs]));
  const browser = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu',
    '--no-first-run', '--no-default-browser-check', '--remote-debugging-pipe',
    '--user-data-dir=' + path.join(out, 'profile'), 'about:blank'],
    {stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe']});
  let seq = 0, buffer = '', session, stopped;
  const pending = new Map(), errors = [];
  function stop(error) {
    stopped = error;
    for (const {reject, timer} of pending.values()) { clearTimeout(timer); reject(error); }
    pending.clear();
  }
  browser.stderr.setEncoding('utf8').on('data', text => errors.push(text));
  browser.on('error', stop);
  browser.on('exit', code => stop(Error('Chrome exited ' + code + ' ' + errors.slice(-3).join(''))));
  browser.stdio[3].on('error', stop);
  browser.stdio[4].on('error', stop);
  browser.stdio[4].setEncoding('utf8').on('data', text => {
    buffer += text;
    let i;
    while ((i = buffer.indexOf('\0')) >= 0) {
      const message = JSON.parse(buffer.slice(0, i));
      buffer = buffer.slice(i + 1);
      const request = pending.get(message.id);
      if (!request) continue;
      clearTimeout(request.timer);
      pending.delete(message.id);
      message.error ? request.reject(Error(JSON.stringify(message.error))) : request.resolve(message.result);
    }
  });
  function call(method, params = {}, sid = session) {
    if (stopped) return Promise.reject(stopped);
    return new Promise((resolve, reject) => {
      const id = ++seq, timer = setTimeout(() => {
        pending.delete(id);
        reject(Error('CDP timeout ' + method + ' ' + errors.slice(-2)));
      }, 12000);
      pending.set(id, {resolve, reject, timer});
      browser.stdio[3].write(JSON.stringify({id, method, params, ...(sid ? {sessionId: sid} : {})}) + '\0');
    });
  }
  async function js(expression) {
    const result = await call('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true, userGesture: true});
    if (result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  }
  async function mouse(type, position, buttons = 0) {
    await call('Input.dispatchMouseEvent', {type, ...position, button: buttons ? 'left' : 'none', buttons, clickCount: type === 'mouseMoved' ? 0 : 1});
  }
  async function click(selector) {
    const position = await js(`(() => {const target = document.querySelector(${JSON.stringify(selector)}); target.scrollIntoView({block:'nearest'}); const b = target.getBoundingClientRect(); return {x:b.x+b.width/2,y:b.y+b.height/2}})()`);
    await mouse('mousePressed', position, 1);
    await mouse('mouseReleased', position, 1);
  }
  async function fill(selector, text) {
    await click(selector);
    await js(`document.querySelector(${JSON.stringify(selector)}).select()`);
    await call('Input.insertText', {text: String(text)});
  }
  async function choose(selector, value) {
    await js(`document.querySelector(${JSON.stringify(selector)}).value=${JSON.stringify(value)}; document.querySelector(${JSON.stringify(selector)}).dispatchEvent(new Event('change'))`);
  }
  async function open(file) {
    await call('Page.navigate', {url: pathToFileURL(path.resolve(file)).href});
    for (let i = 0; i < 100; i++) {
      if (await js(`document.readyState==='complete' && (!!document.querySelector('#selection option') || document.querySelector('#selection')?.disabled)`)) return;
      await delay(30);
    }
    throw Error('page not ready');
  }
  async function load(file) {
    const document = await call('DOM.getDocument');
    const input = await call('DOM.querySelector', {nodeId: document.root.nodeId, selector: '#load'});
    await js(`document.querySelector('#status').textContent='loading'`);
    await call('DOM.setFileInputFiles', {nodeId: input.nodeId, files: [path.resolve(file)]});
    for (let i = 0; i < 100; i++) {
      if (await js(`document.querySelector('#status').textContent!=='loading'`)) return;
      await delay(20);
    }
    throw Error('file read timeout');
  }
  async function shortcut(letter, modifiers = 2) {
    const key = {key: letter, code: 'Key' + letter.toUpperCase(), windowsVirtualKeyCode: letter.toUpperCase().charCodeAt(0), modifiers};
    await call('Input.dispatchKeyEvent', {type: 'rawKeyDown', ...key});
    await call('Input.dispatchKeyEvent', {type: 'keyUp', ...key});
  }
  async function downloaded(suffix) {
    const figure = await js('doc.figure_id');
    for (let i = 0; i < 100; i++) {
      const name = fs.readdirSync(out).find(name => name.startsWith(figure + '-') && name.endsWith(suffix) && seenDownloads.get(name) !== fs.statSync(path.join(out, name)).mtimeMs);
      if (name) { seenDownloads.set(name, fs.statSync(path.join(out, name)).mtimeMs); return path.join(out, name); }
      await delay(30);
    }
    throw Error('missing download ' + suffix);
  }
  try {
    const target = await call('Target.createTarget', {url: 'about:blank'}, null);
    session = (await call('Target.attachToTarget', {targetId: target.targetId, flatten: true}, null)).sessionId;
    await call('Page.enable');
    await call('Runtime.enable');
    await call('Network.enable');
    await call('Network.emulateNetworkConditions', {offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0});
    await call('Browser.setDownloadBehavior', {behavior: 'allow', downloadPath: out}, null);
    await call('Emulation.setDeviceMetricsOverride', {width: 1280, height: 1100, deviceScaleFactor: 1, mobile: false});
    await open(html);
    await check({call, js, click, mouse, fill, select: id => choose('#selection', id), variant: id => choose('#variant', id), open, load, shortcut, downloaded, delay});
  } finally {
    browser.kill();
  }
}
