# ===== ep19: deep hole at the beach. Music per scene: sunny ukulele/steel-drum beach tune + waves + gulls (the dare, shovel scrapes)
# -> tune thins into a low tense pulse + sand trickle hiss + creaks (top sand slides) -> WHUMP + music cut (wall falls)
# -> heartbeat + slow squeezed breaths + low pulse (stuck) -> sting + silence (freeze) -> thinking keys (pause: scale ticks + ding, chest squeeze creak, warning beeps)
# -> rewind sweep -> bright beach tune again (right move: scrapes, plop + sigh, sunglasses ting, rubber-duck squeak + bubbles)
# -> descending 'dig' whoosh + cozy-spooky music-box waltz under the sand (punchline, door creak, wink ding) -> calm tip pad + keys -> end chime
n10=P('n1.0'); n11=P('n1.1'); f10=P('f1.0'); f11=P('f1.1'); h10=P('h1.0'); h11=P('h1.1')
n20=P('n2.0'); n21=P('n2.1'); n21e=PE('n2.1'); h20=P('h2.0'); h21=P('h2.1'); n30=P('n3.0'); n31=P('n3.1'); n32=P('n3.2')
FA=n21e+0.02; FZ=n32+0.42
pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.0
v1=P('m1.1'); v1e=PE('m1.1'); lk=P('m1.2'); wl=P('m1.3'); wle=PE('m1.3'); rw=P('m1.4')
a0=P('n4.0'); a1=P('n4.1'); a2=P('n4.2'); a2e=PE('n4.2'); STOP=a2+(a2e-a2)*0.55
h30=P('h3.0'); h31=P('h3.1'); f20=P('f2.0'); f21=P('f2.1'); f2e=PE('f2.1')
m2=C['m2']['start']; b1=P('m2.1'); b2=P('m2.2'); b2e=PE('m2.2'); tip=C['m3']['start']; end=C['m4']['start']-0.2
def lp(x,k): return np.convolve(x,np.ones(k)/k,'same')
def waves(a,b,g=0.08):
    n=int((b-a)*sr); tt=np.arange(n)/sr; x=lp(rng.standard_normal(n),18)*3
    sw=0.35+0.65*np.clip(np.sin(2*np.pi*tt/5.2+0.6),0,1)**2; x2=(rng.standard_normal(n)-lp(rng.standard_normal(n),3))*0.25*np.clip(np.sin(2*np.pi*tt/5.2+0.3),0,1)**4
    add(sfx,a,(x*sw+x2)*np.minimum(1,tt/0.5)*np.minimum(1,((b-a)-tt)/0.5)*g)
def gull(t,g=0.05):
    for k,o in enumerate([0,0.22,0.4]):
        n=int(0.2*sr); tt=np.arange(n)/sr; f=1900-700*tt/0.2+80*np.sin(2*np.pi*30*tt)
        x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.3*np.sin(4*np.pi*np.cumsum(f)/sr); add(sfx,t+o,x*np.sin(np.pi*tt/0.2)*g*(1-0.25*k))
def steel(t,m,g=0.12,d=0.5):
    n=int(d*sr); tt=np.arange(n)/sr; f=440*2**((m-69)/12)
    x=(np.sin(2*np.pi*f*tt)+0.5*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt/0.08)+0.3*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt/0.04))*env(n,0.003,d*0.35); add(mus,t,x*g)
BMEL=[72,None,76,79,None,76,74,None,72,None,69,72,None,None,74,None,76,None,79,81,None,79,76,None,74,None,72,74,None,None,None,None]
BCH=[[60,64,67],[65,69,72],[67,71,74],[60,64,67]]
def beach(a,b,g=1.0,bpm=112,mel=True):
    beat=60/bpm; t=a; i=0
    while t<b:
        ch=BCH[(i//8)%4]
        if mel and BMEL[i%32]: steel(t,BMEL[i%32],0.11*g)
        if i%4==0: add(mus,t,note(ch[0]-24,beat*1.5,0.22*g,0.5))
        if i%4==2: add(mus,t,note(ch[2]-24,beat*1.1,0.14*g,0.5))
        if i%2==1: pluck(t,ch[(i//2)%3]+12,0.08*g,0.28)            # ukulele off-beat strum
        if i%2==1: pluck(t+0.012,ch[((i//2)+1)%3]+12,0.05*g,0.25)
        n=int(0.02*sr); add(mus,t,(rng.standard_normal(n)-lp(rng.standard_normal(n),2))*env(n,0.001,0.008)*0.05*g)  # shaker
        t+=beat/2; i+=1
def sandhiss(a,b,g=0.08):
    n=int((b-a)*sr); tt=np.arange(n)/sr; x=rng.standard_normal(n); x=x-lp(x,3); x*=0.6+0.4*np.abs(np.sin(2*np.pi*3.1*tt))
    add(sfx,a,x*np.minimum(1,tt/0.3)*np.minimum(1,((b-a)-tt)/0.15)*g)
def creak(t,d=0.5,g=0.08,f0=140):
    n=int(d*sr); tt=np.arange(n)/sr; f=f0+30*np.sin(2*np.pi*2*tt)
    x=np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*(0.5+0.5*np.sin(2*np.pi*37*tt)); x=lp(x,6); add(sfx,t,x*np.sin(np.pi*tt/d)*g)
def whump(t,g=0.5):
    boom(t,0.6*g); thunk(t+0.02,0.5*g)
    n=int(1.1*sr); tt=np.arange(n)/sr; add(sfx,t,lp(rng.standard_normal(n),12)*3*np.exp(-tt/0.35)*np.minimum(1,tt/0.01)*g*0.5)
def patter(t,g=0.05):
    for i in range(10):
        n=int(0.01*sr); x=rng.standard_normal(n)-lp(rng.standard_normal(n),2); add(sfx,t+i*0.02+rng.random()*0.02,x*env(n,0.0005,0.004)*g)
def breathin(t,d=0.7,g=0.06):
    n=int(d*sr); tt=np.arange(n)/sr; x=lp(rng.standard_normal(n),4)*np.sin(np.pi*tt/d)**2*(0.6+0.4*np.sin(2*np.pi*9*tt)); add(sfx,t,x*g)
def squeak(t,g=0.14):
    for o,f0,f1 in [(0,1300,1900),(0.13,1500,2100)]:
        n=int(0.12*sr); tt=np.arange(n)/sr; f=np.linspace(f0,f1,n); add(sfx,t+o,np.sin(2*np.pi*np.cumsum(f)/sr)*np.sin(np.pi*tt/0.12)*g)
def bubble(t,g=0.06):
    n=int(0.07*sr); tt=np.arange(n)/sr; f=np.linspace(400,1200,n); add(sfx,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.03)*g)
def plop(t,g=0.2):
    n=int(0.25*sr); tt=np.arange(n)/sr; add(sfx,t,lp(rng.standard_normal(n),20)*4*env(n,0.002,0.06)*g); thunk(t,0.3*g)
def sigh(t,g=0.05):
    n=int(0.8*sr); tt=np.arange(n)/sr; x=lp(rng.standard_normal(n),10)*3*np.sin(np.pi*tt/0.8)**2; add(sfx,t,x*g)
def waltz(a,b,g=1.0):
    beat=60/132; t=a; i=0; prog=[[57,60,64],[52,56,59],[57,60,64],[53,57,60]]; mel=[69,72,76,75,76,72,71,72,69,None,64,None]
    while t<b:
        ch=prog[(i//3)%4]
        if i%3==0: add(mus,t,note(ch[0]-12,beat*1.2,0.2*g,0.6))
        else: pluck(t,ch[1+(i%3)%2],0.07*g,0.3)
        m=mel[i%12]
        if m: mbox(t,m+12,0.12*g)
        t+=beat; i+=1
# ---------------- MUSIC
beach(0.0,n20+0.25,1.0,112)
pulse(n20+0.1,FA-0.03,80,100,0.45,40)
heartbeat(FA+0.5,FZ,0.2); pulse(h21,FZ-0.05,70,90,0.3,40)
sting(FZ-0.05,0.65)
keys(pause+0.25,rwS,1.05)
beach(rwE+0.1,m2-0.05,0.8,112)
waltz(b1-0.25,tip-0.1,0.9)
pad(tip,end,[57,60,64,67],0.14); keys(tip+0.1,end,0.55); pad(end+0.2,D,[60,64,67,72],0.08)
for m_,a_ in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: steel(end+0.4+a_,m_,0.16,1.2)
lvl=np.ones(N)
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(rwS,rwE,0.2); seg(FZ+0.9,pause,0.0); seg(FA,FA+0.5,0.0)
k=int(0.08*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
# ---------------- SFX
waves(0.0,FZ+0.6,0.09); waves(rwE,m2+0.6,0.08)
for tg in [1.2,6.5,32.5]: gull(tg,0.045)
pop(0.05,0.1); pop(0.3,0.12)
# shovel: scrape on push-in, whoosh on toss, sand patter on landing
for i in range(0,40):
    tp=i+0.3; tt_=i+0.72
    if tp<n20: scrape(tp-0.12,0.22,0.09)
    if tt_<n20: whoosh(tt_-0.1,0.3,0.06); patter(tt_+0.62,0.05)
pop(n11-0.1,0.12); ding(n11+0.2,0.06)
pop(f10,0.12)
pop(h11,0.12)
# slide
sandhiss(n20,FA+0.4,0.09); creak(n20+0.6,0.6,0.06,130); creak(n20+1.3,0.5,0.07,110); creak(FA-0.4,0.35,0.08,95)
pop(n20+0.25,0.1)
whump(FA,0.55); sandhiss(FA,FA+1.2,0.07)
pop(h21-0.1,0.14)
for i in range(5): breathin(n30+0.3+i*0.95,0.6,0.05*(1-0.12*i))
pop(n30+0.3,0.1); pop(n32,0.16)
n_=int(0.35*sr); tt=np.arange(n_)/sr; f=np.linspace(300,30,n_); add(sfx,FZ,np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt/0.2)*0.25)
n_=int(0.05*sr); add(sfx,pause,rng.standard_normal(n_)*env(n_,0.001,0.01)*0.6)
# pause diagram
whoosh(v1-0.4,0.6,0.14); pop(v1+0.15,0.14); thunk(v1+(v1e-v1)*0.45,0.12)
for i in range(9): tick(v1+(v1e-v1)*0.45+i*((v1e-v1)*0.4/9),0.08)
ding(v1+(v1e-v1)*0.86,0.1)
pop(lk+0.05,0.15); pop(lk+0.3,0.1)
whoosh(wl-0.2,0.5,0.1); creak(wl+0.3,0.9,0.07,120); beep(wl+(wle-wl)*0.62,0.06); beep(wl+(wle-wl)*0.62+0.14,0.06); pop(wl+(wle-wl)*0.62,0.12)
pop(rw-0.2); click(rw,0.2); ding(rw+0.3,0.12)
n_=int(1.0*sr); tt=np.arange(n_)/sr; f=np.linspace(1800,300,n_)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n_),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.0))
# right move
pop(a0+0.05,0.12)
for i in range(0,8):
    tp=a0-0.3+i+0.3; tt_=a0-0.3+i+0.72
    if tp<STOP: scrape(tp-0.12,0.22,0.08)
    if tt_<STOP: whoosh(tt_-0.1,0.3,0.05); patter(tt_+0.62,0.04)
pop(STOP,0.12); ding(STOP+0.1,0.07)
plop(h30+0.35,0.25); sigh(h30+0.5,0.05); ding(h30+0.62,0.05)
pop(h31,0.12)
squeak(f21,0.13)
for i in range(7): bubble(f21+0.1+i*0.13,0.05)
pop(f2e,0.14)
for m_,a_ in [(72,0),(76,0.1),(79,0.2),(84,0.3)]: pluck(f2e+0.15+a_,m_,0.15,0.6)
# punchline
n_=int(1.1*sr); tt=np.arange(n_)/sr; f=np.linspace(900,120,n_)
add(sfx,m2+0.05,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.06+lp(rng.standard_normal(n_),10)*0.25)*np.sin(np.pi*tt/1.1))
creak(b1-0.1,0.7,0.06,200); pop(b1+0.05,0.14)
pop(b2,0.14); ding(b2e-0.05,0.1)
for k2 in ['m3.0','m3.1','m3.2','m3.3']: blip(P(k2))
