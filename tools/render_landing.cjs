// Fixed-purpose browser worker. Project code runs only in the browser sandbox.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const {chromium} = require('playwright');

async function main() {
  const request = JSON.parse(fs.readFileSync(0, 'utf8'));
  const root = fs.realpathSync(request.root);
  const token = crypto.randomBytes(24).toString('hex');
  const types = {'.html':'text/html', '.css':'text/css', '.js':'application/javascript',
    '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp',
    '.svg':'image/svg+xml', '.woff2':'font/woff2', '.json':'application/json', '.glb':'model/gltf-binary'};
  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      if (!url.pathname.startsWith(`/${token}/`)) {res.writeHead(403).end(); return;}
      const relative = decodeURIComponent(url.pathname.slice(token.length + 2));
      const target = fs.realpathSync(path.resolve(root, relative || 'index.html'));
      const rel = path.relative(root, target);
      if (rel.startsWith('..') || path.isAbsolute(rel) || !fs.statSync(target).isFile()) {
        res.writeHead(403).end(); return;
      }
      res.setHeader('Content-Type', types[path.extname(target)] || 'application/octet-stream');
      res.setHeader('Cache-Control', 'no-store');
      fs.createReadStream(target).pipe(res);
    } catch {res.writeHead(404).end();}
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  try {
    browser = await chromium.launch({headless:true, ...(process.env.AGENTIC_BROWSER_CHANNEL ? {channel:process.env.AGENTIC_BROWSER_CHANNEL} : {})});
    const origin = `http://127.0.0.1:${server.address().port}`;
    const base = `${origin}/${token}/`;
    const captures = [];
    for (const [name, width, height] of [['desktop',1440,1000], ['mobile',390,844]]) {
      const context = await browser.newContext({viewport:{width,height}, serviceWorkers:'block', acceptDownloads:false});
      await context.route('**/*', route => {
        const url = route.request().url();
        return url.startsWith(base) || url.startsWith('data:') ? route.continue() : route.abort();
      });
      if (context.routeWebSocket) await context.routeWebSocket(/.*/, socket => socket.close());
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      const response = await page.goto(base + request.entry, {waitUntil:'networkidle', timeout:20000});
      if (!response || !response.ok()) throw new Error('Landing entry could not be loaded');
      await page.evaluate(() => document.fonts.ready);
      const totalHeight = await page.evaluate(() => document.documentElement.scrollHeight);
      if (totalHeight > 30000) throw new Error('Page exceeds bounded capture height');
      for (let y=0; y<totalHeight; y+=height) {await page.evaluate(y=>scrollTo(0,y),y); await page.waitForTimeout(80);}
      await page.evaluate(()=>scrollTo(0,0));
      await page.waitForTimeout(250);
      const whole = path.join(request.output, `${name}.png`);
      await page.screenshot({path:whole, fullPage:true});
      const observations = await page.evaluate(() => ({
        overflow:document.documentElement.scrollWidth > innerWidth + 1,
        missingImages:[...document.images].filter(i=>!i.complete || !i.naturalWidth).map(i=>i.getAttribute('src')),
        headings:[...document.querySelectorAll('h1,h2')].map(e=>e.textContent),
      }));
      captures.push({viewport:name, file:whole, kind:'whole-page', observations, errors});
      for (const id of request.scenes) {
        const scene = page.locator(`[data-scene-id="${id}"]`);
        if (await scene.count() !== 1) throw new Error(`Expected exactly one data-scene-id=${id}`);
        await scene.scrollIntoViewIfNeeded();
        await page.waitForTimeout(300);
        const file = path.join(request.output, `${id}-${name}.png`);
        await page.screenshot({path:file});
        captures.push({viewport:name, scene:id, kind:'scroll-viewport', file});
      }
      for (const [index, action] of (request.actions || []).entries()) {
        if (action.type === 'click') await page.locator(action.selector).click({timeout:3000});
        else if (action.type === 'hover') await page.locator(action.selector).hover({timeout:3000});
        else if (action.type === 'tab') await page.keyboard.press('Tab');
        else if (action.type === 'reduced-motion') await page.emulateMedia({reducedMotion:'reduce'});
        else throw new Error('Unsupported interaction');
        await page.waitForTimeout(200);
        const file = path.join(request.output, `action-${index}-${name}.png`);
        await page.screenshot({path:file});
        const observed = await page.evaluate(() => ({url:location.pathname,
          focusTag:document.activeElement?.tagName, focusText:document.activeElement?.textContent?.slice(0,120),
          visibleText:document.body.innerText.slice(0,4000), reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches}));
        captures.push({viewport:name, kind:'interaction', action, observed, file});
      }
      await context.close();
    }
    process.stdout.write(JSON.stringify({captures, limitations:['Network blocked: use locally bundled dependencies.',
      'Captures and interaction observations require review; they do not prove visual quality or external form delivery.']}));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
}
main().catch(error=>{process.stderr.write(error.message); process.exitCode=1;});
