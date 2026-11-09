import asyncio,os,sys
from playwright.async_api import async_playwright
# usage: cover.py ep.html t part line1 line2 out.png [cx cy r]
async def m():
    f,t,part,l1,l2,out=sys.argv[1:7];circ=sys.argv[7:10]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--allow-file-access-from-files'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file://'+os.path.abspath(f));await pg.wait_for_function('window.done===true',timeout=120000)
        await pg.evaluate(f'render({t})')
        c=''
        if circ:
            x,y,r=circ;c=f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#E5383B" stroke-width="10"/><circle cx="{x}" cy="{y}" r="{int(r)+18}" fill="none" stroke="#E5383B" stroke-width="4" opacity=".5"/>'
        def T(y,s,col,fs): return f'<text x="540" y="{y}" text-anchor="middle" font-size="{fs}" font-weight="900" fill="{col}" stroke="#000" stroke-width="10" paint-order="stroke" font-family="DejaVu Sans">{s}</text>'
        svg=f'''<rect width="1080" height="1920" fill="url(#g)"/><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".85"/><stop offset=".42" stop-color="#000" stop-opacity="0"/><stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></linearGradient></defs>
{c}
<text x="540" y="300" text-anchor="middle" font-size="34" font-weight="700" fill="#fff" opacity=".85" letter-spacing="4" font-family="DejaVu Sans">SURVIVE WHERE YOU ARE · S1</text>
<rect x="400" y="330" width="280" height="76" rx="38" fill="#FFD23F"/><text x="540" y="383" text-anchor="middle" font-size="44" font-weight="900" fill="#111" font-family="DejaVu Sans">{part}</text>
{T(510,l1,'#fff',84)}{T(610,l2,'#E5383B',84)}'''
        await pg.evaluate('s=>{document.getElementById("ov").innerHTML=s}',svg)
        await pg.screenshot(path=out);await b.close()
asyncio.run(m())
