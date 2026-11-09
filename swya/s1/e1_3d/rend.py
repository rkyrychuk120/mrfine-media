import asyncio,os,sys,subprocess,time
from playwright.async_api import async_playwright
async def m():
    mode=sys.argv[1]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--allow-file-access-from-files'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath(sys.argv[2]));await pg.wait_for_function('window.done===true',timeout=120000)
        if mode=='stills':
            for t in sys.argv[3:]:
                await pg.evaluate(f'render({t})');await pg.screenshot(path=f'st_{float(t):05.2f}.png')
        else:
            a,bb,out=float(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
            ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',out],stdin=subprocess.PIPE)
            n=int(round((bb-a)*30));t0=time.time()
            for i in range(n):
                await pg.evaluate(f'render({a+i/30:.4f})');ff.stdin.write(await pg.screenshot(type='jpeg',quality=92))
            ff.stdin.close();ff.wait();print('sec/frame',round((time.time()-t0)/n,2))
        print('errors',errs);await b.close()
asyncio.run(m())
