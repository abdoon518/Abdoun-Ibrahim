const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
const [,, html, outDir, spec] = process.argv; // spec: "dur:20" or "t1,t2,..."
(async()=>{ const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  await pg.goto('file://'+path.resolve(html)); await pg.evaluate(()=>document.fonts.ready); fs.mkdirSync(outDir,{recursive:true});
  let times, still=!spec.startsWith('dur:');
  times = still ? spec.split(',').map(Number) : Array.from({length:Math.round(+spec.slice(4)*30)},(_,i)=>i/30);
  for(let i=0;i<times.length;i++){ await pg.evaluate(t=>window.seek(t),times[i]);
    await pg.screenshot({path:path.join(outDir, still?`s_${String(i).padStart(2,'0')}.png`:`f_${String(i).padStart(4,'0')}.png`)}); }
  await b.close(); })();
