import sys,subprocess,asyncio,os
from playwright.async_api import async_playwright
async def main():
    mode=sys.argv[1]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file://'+os.path.abspath('scene.html')); await pg.wait_for_timeout(300)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        if mode=='stills':
            for t in [float(x) for x in sys.argv[2:]]:
                await pg.evaluate(f'render({t})')
                await pg.screenshot(path=f'st_{t:06.2f}.png',clip={'x':0,'y':440,'width':1080,'height':980})
        else:
            a,b_,out=float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
            ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-vf','scale=out_color_matrix=bt709:out_range=tv',out+'.tmp.mp4'],stdin=subprocess.PIPE)
            n=int(round((b_-a)*30))
            for i in range(n):
                await pg.evaluate(f'render({a+i/30:.4f})')
                ff.stdin.write(await pg.screenshot(type='jpeg',quality=92))
            ff.stdin.close(); ff.wait()
            if ff.returncode==0: os.rename(out+'.tmp.mp4',out)
        print('errors',errs)
        await b.close()
asyncio.run(main())
