import numpy as np, wave, json
sr=48000; tl=json.load(open('timeline.json')); D=tl['total']; N=int(D*sr); PH=tl['ph']
C={c['name']:c for c in tl['clips']}
P=lambda k:PH[k][0]
PE=lambda k:PH[k][1]
mus=np.zeros(N); sfx=np.zeros(N); rng=np.random.default_rng(4)
def add(buf,t,x,g=1.0):
    i=int(t*sr)
    if i>=N or i<0: return
    j=min(N,i+len(x)); buf[i:j]+=x[:j-i]*g
def env(n,a=0.005,r=0.2):
    t=np.arange(n)/sr; return np.minimum(1,t/a)*np.exp(-t/r)
def note(m,dur,amp,bright=1.0):
    n=int(dur*sr); t=np.arange(n)/sr; f=440*2**((m-69)/12)
    return (np.sin(2*np.pi*f*t)+0.3*bright*np.sin(4*np.pi*f*t)+0.1*bright*np.sin(6*np.pi*f*t))*env(n,0.004,0.35)*amp
def kick(t,g,f0=110):
    n=int(0.25*sr); tt=np.arange(n)/sr; f=np.linspace(f0,45,n); add(mus,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.09)*g)
def gymbeat(a,b,bpm=118,warp=None):
    beat=60/bpm; t=a; i=0
    while t<b:
        w=1.0 if warp is None else warp(t)
        kick(t,0.9,110*w)
        m=[45,45,48,43][(i//4)%4]
        add(mus,t+beat/2,note(m*1+0,beat*0.45,0.28,0.8) if w==1 else note(m-12*(1-w),beat*0.45,0.28,0.8))
        n=int(0.02*sr); add(mus,t+beat/2,rng.standard_normal(n)*env(n,0.001,0.006)*0.12)
        t+=beat/w; i+=1
def pad(a,b,ch,amp):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=sum(np.sin(2*np.pi*440*2**((m-69)/12)*t) for m in ch)/len(ch)
    w=np.minimum(1,t/0.6)*np.minimum(1,(n/sr-t)/0.6); add(mus,a,x*w*amp)
def bounce(a,b):
    beat=60/112; t=a; bar=0; prog=[[60,64,67],[65,69,72],[67,71,74],[60,64,67]]
    while t<b:
        ch=prog[bar%4]
        for k in range(4):
            tb=t+k*beat
            if tb>=b: break
            if k in (0,2): add(mus,tb,note(ch[0]-12,beat*0.9,0.32))
            add(mus,tb+beat/2,note(ch[(k+1)%3]+12,beat/2,0.14))
        t+=4*beat; bar+=1
def heartbeat(a,b,g):
    t=a
    while t<b:
        for off,amp in [(0,1),(0.18,0.7)]:
            n=int(0.12*sr); tt=np.arange(n)/sr; add(mus,t+off,np.sin(2*np.pi*55*tt)*env(n,0.004,0.05)*g*amp)
        t+=0.7
pause0=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.1
tip=C['m3']['start']; end=C['m4']['start']-0.2
m2=C['m2']['start']
def A_(t,a,b):
    v=min(1,max(0,(t-a)/max(1e-6,b-a))); return v*v*(3-2*v)
def drone(a,b,g,f=55):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=(np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*1.5*t+np.sin(2*np.pi*0.3*t))+0.3*np.sin(2*np.pi*f*2.02*t))
    w=np.minimum(1,t/0.3)*np.minimum(1,(n/sr-t)/0.3); add(mus,a,x*w*g)
def drums(a,b,bpm0,bpm1,g):
    t=a; i=0
    while t<b:
        k=(t-a)/max(1e-6,b-a); bpm=bpm0+(bpm1-bpm0)*k; beat=60/bpm
        kick(t,0.9*g,90)
        if i%2: n=int(0.05*sr); add(mus,t,rng.standard_normal(n)*env(n,0.001,0.03)*0.35*g)
        add(mus,t,note([45,45,46,44][(i//4)%4],beat*0.5,0.22*g,1.2))
        t+=beat; i+=1
# ep15: car stuck on the tracks. Music changes per scene: rail-rhythm tension -> cut on impact -> thinking keys (pause) -> urgent drums (right move) -> relief -> comic bounce (punchline) -> calm tip -> chime
h1=C['h1']['start']; n2=P('n2.0'); w1=P('n1.1')
I1=P('n2.2')-0.15; FZ=PE('n2.2')+0.3; O1=P('n2.1')+0.02
pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.0
a0=P('n4.0'); a1=P('n4.1'); a2=P('n4.2'); I2=PE('n4.3')+0.02; O2=P('n4.0')+1.9
hS=C['h2']['start']; h23=P('h2.3'); m2=C['m2']['start']; b1=P('m2.1'); be=PE('m2.1')
tip=C['m3']['start']; end=C['m4']['start']-0.2
# --- SFX
def hum(a,b,g):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=(np.sin(2*np.pi*120*t)*0.5+np.sin(2*np.pi*240*t)*0.2)*np.minimum(1,t/0.1)*np.minimum(1,(n/sr-t)/0.05); add(sfx,a,x*g)
def ding(t,g=0.35):
    n=int(1.2*sr); tt=np.arange(n)/sr; add(sfx,t,(np.sin(2*np.pi*1568*tt)+0.5*np.sin(2*np.pi*3136*tt))*env(n,0.002,0.4)*g)
def whoosh(t,d,g):
    n=int(d*sr); x=np.convolve(rng.standard_normal(n),np.ones(40)/40,'same'); w=np.sin(np.pi*np.arange(n)/n)**2; add(sfx,t,x*w*g)
def boom(t,g):
    n=int(0.6*sr); tt=np.arange(n)/sr; f=np.linspace(140,40,n)
    add(sfx,t,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.9+rng.standard_normal(n)*0.5)*env(n,0.001,0.12)*g)
def tick(t,g=0.12):
    n=int(0.03*sr); add(sfx,t,np.sin(2*np.pi*2000*np.arange(n)/sr)*env(n,0.001,0.01)*g)
def blip(t):
    n=int(0.08*sr); f=np.linspace(500,900,n); add(sfx,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.03)*0.16)

def engine(a,b,g,f0=48):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=(np.sin(2*np.pi*f0*t+np.sin(2*np.pi*3*t))*0.6+np.convolve(rng.standard_normal(n),np.ones(200)/200,'same')*3)*np.minimum(1,t/0.2)*np.minimum(1,(n/sr-t)/0.2); add(sfx,a,x*g)
def horn(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=(np.sign(np.sin(2*np.pi*370*tt))*0.5+np.sign(np.sin(2*np.pi*466*tt))*0.5)*np.minimum(1,tt/0.02)*np.minimum(1,(d-tt)/0.05)
    x=np.convolve(x,np.ones(6)/6,'same'); add(sfx,t,x*g)
def clank(t,g=0.25):
    n=int(0.4*sr); tt=np.arange(n)/sr; add(sfx,t,(np.sin(2*np.pi*620*tt)+0.6*np.sin(2*np.pi*1340*tt)+0.4*np.sin(2*np.pi*2210*tt))*env(n,0.001,0.08)*g)
def cough(t,g=0.5):
    for k in range(2):
        n=int(0.18*sr); x=np.convolve(rng.standard_normal(n),np.ones(12)/12,'same')*env(n,0.005,0.06); add(sfx,t+k*0.22,x*g)
def growl(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(60)/60,'same')*(1+0.6*np.sin(2*np.pi*28*tt))
    x+=0.4*np.sin(2*np.pi*(70+20*np.sin(2*np.pi*3*tt))*tt); w=np.minimum(1,tt/0.08)*np.minimum(1,(d-tt)/0.25); add(sfx,t,x*w*g)
def step(t,g,f=70):
    n=int(0.09*sr); tt=np.arange(n)/sr; add(sfx,t,(np.sin(2*np.pi*f*tt)+np.convolve(rng.standard_normal(n),np.ones(30)/30,'same')*2)*env(n,0.002,0.03)*g)
def chirp(t):
    for k in range(3):
        n=int(0.07*sr); f=np.linspace(2800,3600,n); add(sfx,t+k*0.11,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.003,0.03)*0.08)
def splash(t,g):
    n=int(0.9*sr); x=np.convolve(rng.standard_normal(n),np.ones(5)/5,'same')*env(n,0.004,0.25); add(sfx,t,x*g)
def gurgle(a,b,g):
    t=a
    while t<b:
        n=int(0.06*sr); tt_=np.arange(n)/sr; f=300+rng.random()*500; add(sfx,t,np.sin(2*np.pi*f*tt_*(1+tt_*8))*env(n,0.003,0.02)*g); t+=0.08+rng.random()*0.18
def click(t,g=0.4):
    n=int(0.03*sr); add(sfx,t,rng.standard_normal(n)*env(n,0.0005,0.006)*g); clank(t+0.05,0.12)
def zipdown(t,d,g):
    n=int(d*sr); tt_=np.arange(n)/sr; f=np.linspace(260,140,n); add(sfx,t,np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*0.3*np.sin(np.pi*tt_/d)*g)
def screech(a,b,g):
    n=int((b-a)*sr); tt_=np.arange(n)/sr; x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(6)/6,'same')
    x+=0.5*np.sin(2*np.pi*(1900+300*np.sin(2*np.pi*5*tt_))*tt_)
    w=np.minimum(1,tt_/0.08)*np.minimum(1,(b-a-tt_)/0.2); add(sfx,a,x*w*g)
def flaps(a,b,g,p0=0.09,p1=0.16):
    t=a
    while t<b:
        k=(t-a)/max(1e-6,b-a); n=int(0.05*sr); tt_=np.arange(n)/sr
        add(sfx,t,(np.sin(2*np.pi*90*tt_)+rng.standard_normal(n)*0.4)*env(n,0.001,0.02)*g)
        t+=p0+(p1-p0)*k
def shutter(t,g=0.45):
    n=int(0.04*sr); add(sfx,t,rng.standard_normal(n)*env(n,0.0005,0.008)*g); add(sfx,t+0.07,rng.standard_normal(n)*env(n,0.0005,0.01)*g*0.7)
def grunt(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(80)/80,'same')*6*(1+0.5*np.sin(2*np.pi*22*tt))+0.5*np.sin(2*np.pi*(85-20*tt/d)*tt)
    add(sfx,t,x*np.minimum(1,tt/0.05)*np.minimum(1,(d-tt)/0.15)*g)
def crackle(a,b,g,dens=30):
    t=a
    while t<b:
        n=int(0.012*sr); add(sfx,t,rng.standard_normal(n)*env(n,0.0005,0.003)*g*(0.5+rng.random()))
        t+=rng.exponential(1/dens)
def roarF(a,b,g,f=1.0):
    n=int((b-a)*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(int(40/f))/int(40/f),'same')*(0.7+0.3*np.sin(2*np.pi*3*tt))
    w=np.minimum(1,tt/0.15)*np.minimum(1,(n/sr-tt)/0.2); add(sfx,a,x*w*g)
def whoomph(t,g):
    n=int(1.2*sr); tt=np.arange(n)/sr; f=np.linspace(90,35,n); x=np.sin(2*np.pi*np.cumsum(f)/sr)*0.9+np.convolve(rng.standard_normal(n),np.ones(25)/25,'same')*3
    add(sfx,t,x*np.minimum(1,tt/0.03)*np.exp(-tt/0.45)*g)
def beep(t,g=0.06):
    n=int(0.09*sr); tt=np.arange(n)/sr; add(sfx,t,np.sign(np.sin(2*np.pi*3100*tt))*np.minimum(1,tt/0.005)*np.minimum(1,(0.09-tt)/0.005)*g)
def sizzle(a,b,g):
    n=int((b-a)*sr); x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(4)/4,'same'); tt=np.arange(n)/sr
    add(sfx,a,x*(0.6+0.4*np.sin(2*np.pi*7*tt))*np.minimum(1,tt/0.1)*np.minimum(1,(n/sr-tt)/0.1)*g)
def hissOut(t,d,g):
    n=int(d*sr); x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(3)/3,'same'); tt=np.arange(n)/sr; add(sfx,t,x*np.exp(-tt/(d*0.4))*g)
def scrape(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(3)/3,'same')*(0.5+0.5*np.sin(2*np.pi*45*tt))+0.2*np.sin(2*np.pi*(900+300*tt/d)*tt)
    add(sfx,t,x*np.sin(np.pi*tt/d)*g)
def doorbell(t):
    for m_,o in [(76,0),(72,0.45)]: add(sfx,t+o,note(m_,1.0,0.22,0.3))
def pop(t,g=0.18):
    n=int(0.06*sr); f=np.linspace(300,900,n); add(sfx,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.02)*g)

def pluck(t,m,g=0.2,d=0.35):
    n=int(d*sr); tt=np.arange(n)/sr; f=440*2**((m-69)/12)
    x=(np.sin(2*np.pi*f*tt)+0.4*np.sin(4*np.pi*f*tt)+0.15*np.sin(6*np.pi*f*tt))*env(n,0.002,d*0.25); add(mus,t,x*g)
def pulse(a,b,bpm0,bpm1,g,root=45):
    t=a; i=0
    while t<b:
        k=(t-a)/max(1e-6,b-a); beat=60/(bpm0+(bpm1-bpm0)*k)
        add(mus,t,note(root+[0,0,3,0,1,0,3,5][i%8],beat*0.4,0.2*g,1.3))
        if i%2==0: kick(t,0.55*g,80)
        n=int(0.015*sr); add(mus,t+beat/2,rng.standard_normal(n)*env(n,0.001,0.005)*0.08*g)
        t+=beat/2; i+=1
def keys(a,b,g=1):
    prog=[[57,60,64],[53,57,60],[55,59,62],[52,55,59]]; beat=60/88; t=a; i=0
    while t<b:
        ch=prog[(i//4)%4]; pluck(t,ch[i%3]+12,0.16*g,0.6)
        if i%4==0: add(mus,t,note(ch[0]-12,beat*3.5,0.16*g,0.5))
        t+=beat; i+=1
def groove(a,b,g=1,bpm=104):
    prog=[[60,64,67],[57,60,64],[65,69,72],[67,71,74]]; beat=60/bpm; t=a; i=0
    while t<b:
        ch=prog[(i//4)%4]
        if i%2==0: kick(t,0.5*g,90); add(mus,t,note(ch[0]-12,beat*0.8,0.26*g))
        else: n=int(0.03*sr); add(mus,t,rng.standard_normal(n)*env(n,0.001,0.015)*0.12*g)
        pluck(t+beat/2,ch[(i+1)%3]+12,0.12*g,0.3)
        t+=beat; i+=1
# ---- MUSIC
pulse(0.0,h1,126,136,0.85)
# key cranking: tick-tock clock + low pulse (time running out)
t_=h1
while t_<O1: add(mus,t_,note(81 if int((t_-h1)*2.6)%2 else 76,0.08,0.12,0.4)); t_+=1/2.6
pulse(h1,O1,100,112,0.55,43)
drums(O1,I1,150,186,0.9)
keys(pause+0.25,rwS,0.9)
drums(rwE+0.1,I2,138,170,0.75)
for m_,a_ in [(60,0),(64,0.0),(67,0.0)]: add(mus,I2+0.9,note(m_,2.4,0.12,0.4))
for m_,a_ in [(72,0),(76,0.1),(79,0.2),(84,0.3)]: pluck(h23+0.05+a_,m_,0.22,0.6)
bounce(m2+0.05,tip-0.1)
pad(tip,end,[60,64,67,71],0.14); keys(tip+0.1,end,0.55)
for m_,a_ in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: add(mus,end+0.4+a_,note(m_,1.4,0.18))
lvl=np.ones(N)
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(rwS,rwE,0.2); seg(I1,FZ,0.0); seg(I2,I2+0.8,0.0); seg(hS,h23,0.35)
k=int(0.08*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
# ---- SFX
def bell(a,b,g):
    t=np.floor(a*2.4)/2.4
    while t<b:
        if t>=a:
            n=int(0.35*sr); tt=np.arange(n)/sr; f=1250 if int(round(t*2.4))%2 else 1180
            add(sfx,t,(np.sin(2*np.pi*f*tt)+0.6*np.sin(2*np.pi*f*2.76*tt)+0.3*np.sin(2*np.pi*f*5.4*tt))*env(n,0.001,0.09)*g)
        t+=1/2.4
def rumble(a,b,gfun):
    n=int((b-a)*sr); x=np.convolve(rng.standard_normal(n),np.ones(300)/300,'same')*9; tt=np.arange(n)/sr
    x+=0.4*np.sin(2*np.pi*38*tt)+0.3*np.sin(2*np.pi*57*tt)
    gg=np.array([gfun(a+u) for u in tt[::480]]); gg=np.repeat(gg,480)[:n]; add(sfx,a,x*gg)
def clacks(a,b,xfun,gfun):
    # rail-joint pairs: every 350 px of train travel a double clack
    t=a; last=xfun(a)
    while t<b:
        x=xfun(t)
        if abs(last-x)>=175:
            for o in (0,0.07): clank(t+o,0.08*gfun(t)); step(t+o,0.25*gfun(t),55)
            last=x
        t+=0.01
def crank(a,b,g):
    t=a
    while t<b:
        d=0.29; n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(20)/20,'same')*4*(0.5+0.5*np.sign(np.sin(2*np.pi*24*tt)))+0.5*np.sin(2*np.pi*90*tt)
        add(sfx,t,x*np.sin(np.pi*tt/d)*g); t+=1/1.9
def crash(t,g):
    boom(t,1.0*g); n=int(0.9*sr); tt=np.arange(n)/sr
    x=np.convolve(rng.standard_normal(n),np.ones(4)/4,'same')*np.exp(-tt/0.22)
    for f in (310,520,870,1330,2210): x+=0.5*np.sin(2*np.pi*f*tt+rng.random()*6)*np.exp(-tt/(0.1+rng.random()*0.2))
    add(sfx,t,x*g*0.9)
    for i in range(14):   # glass
        tg=t+0.05+rng.random()*0.5; m=int(0.12*sr); q=np.arange(m)/sr; ff=3000+rng.random()*4000
        add(sfx,tg,np.sin(2*np.pi*ff*q)*env(m,0.001,0.03)*0.12*g)
def vibrate(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; add(sfx,t,np.sign(np.sin(2*np.pi*150*tt))*(0.5+0.5*np.sign(np.sin(2*np.pi*6*tt)))*g*np.minimum(1,tt/0.01))
import math
V0=(2150-662)/I1
def tx1(t): return 662+V0*(I1-t) if t<I1 else 662-(V0*0.8*(t-I1))
def tx2(t): return 662+V0*(I2-t) if t<I2 else 662-(V0*0.8*(t-I2)-9*(t-I2)**2)
prox=lambda x: min(1.0, 220/max(60,abs(x-620)))
# bad path
bell(0.0,FZ,0.10)
for t_,d_ in [(0.1,0.95),(1.25,0.95),(2.45,0.35),(2.95,1.1)]: horn(t_,d_,0.07)
horn(O1+0.6,I1-O1-0.6,0.07)
rumble(0.0,FZ,lambda t: 0.04+0.2*prox(tx1(t)))
clacks(0.0,FZ,tx1,lambda t: 0.2+0.5*prox(tx1(t)))
screech(w1+0.3,I1,0.035)
crank(h1+0.02,n2+0.2,0.35)
click(O1,0.4); whoosh(O1+0.1,0.35,0.15)
for i_ in range(40):
    t_=O1+0.5+i_/(2.7*2)
    if t_>FZ: break
    step(t_,0.35,80)
crash(I1,0.6)
# freeze: tape stop
n=int(0.35*sr); tt=np.arange(n)/sr; f=np.linspace(300,30,n); add(sfx,FZ,np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt/0.2)*0.25)
n=int(0.05*sr); add(sfx,pause,rng.standard_normal(n)*env(n,0.001,0.01)*0.6)
wn=P('m1.1'); wr=P('m1.2'); pf=wn+(PE('m1.1')-wn)*0.3; sw=wn+(PE('m1.1')-wn)*0.62
whoosh(wn,0.8,0.18); boom(wn+0.85,0.25); pop(pf+0.1); whoosh(sw,0.4,0.12); pop(wr+0.1); boom(wr+0.8,0.12); n=int(0.05*sr); add(sfx,P('m1.3')+0.1,rng.standard_normal(n)*env(n,0.001,0.01)*0.5)
n=int(1.0*sr); tt=np.arange(n)/sr; f=np.linspace(1800,300,n)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.0))
# right move
bell(rwE,m2,0.09)
horn(rwE+0.15,1.1,0.09); horn(a1,0.9,0.1); horn(a2,1.0,0.11)
rumble(rwE,m2,lambda t: 0.04+0.2*prox(tx2(t)))
clacks(rwE,m2,tx2,lambda t: 0.2+0.5*prox(tx2(t)))
screech(a0+0.5,I2+1.5,0.03)
click(O2,0.4); whoosh(O2+0.1,0.35,0.15)
for i_ in range(40):
    t_=O2+0.6+i_/(2.8*2)
    if t_>O2+3.7: break
    step(t_,0.35,80)
crash(I2,0.55)
import json as _j
for d_ in [(-240,-260,0.6),(-360,-470,0.9),(-420,-160,0.4),(-300,-430,0.95)]:
    clank(I2+d_[2],0.1)
# punchline
bell(m2,tip,0.04)
vibrate(b1+0.1,0.5,0.06); ding(b1+0.3,0.14)
for k_ in range(5): clank(be-0.6+k_*0.18,0.05*(1-k_*0.15))
clank(be+0.32,0.16)
for k_ in ['m3.1','m3.2','m3.3','m3.5','m3.6']: blip(P(k_))
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
sduck=1-0.65*np.clip(e/0.05,0,1)
out=v+mus*0.13*duck+sfx*0.7*sduck
pk=np.percentile(np.abs(out),99.9); out=out*min(1.0,0.8/pk); out=np.tanh(out*1.1)/np.tanh(1.1)*0.95
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
