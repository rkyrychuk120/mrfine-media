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
def mbox(t,m,g=0.16,detune=0.0):
    n=int(1.1*sr); tt=np.arange(n)/sr; f=440*2**((m-69+detune)/12)
    x=(np.sin(2*np.pi*f*tt)+0.45*np.sin(2*np.pi*f*2.01*tt)+0.25*np.sin(2*np.pi*f*3.98*tt)+0.1*np.sin(2*np.pi*f*6.3*tt))*env(n,0.002,0.28)
    add(mus,t,x*g)
MEL=[76,74,72,74,76,76,76,None,74,74,74,None,76,79,79,None,76,74,72,74,76,76,76,76,74,74,76,74,72,None,None,None]
BASS=[48,55,52,55]
def lullaby(a,b,bpm=96,g=1.0,det=None,slow=None):
    t=a; i=0
    while t<b:
        beat=60/bpm; k=(t-a)/max(1e-6,b-a)
        d=det(t) if det else 0.0
        m=MEL[i%len(MEL)]
        if m: mbox(t,m,0.13*g,d)
        if i%4==0: mbox(t,BASS[(i//4)%4],0.10*g,d)
        if i%4==2: mbox(t,BASS[(i//4)%4]+7,0.06*g,d)
        t+=beat*(slow(t) if slow else 1); i+=1
def sniff(t,g=0.25):
    for k in range(2):
        n=int(0.16*sr); tt=np.arange(n)/sr; x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(8)/8,'same')
        add(sfx,t+k*0.2,x*np.sin(np.pi*tt/0.16)*g)
def tapeRip(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=rng.standard_normal(n)*(0.6+0.4*np.sign(np.sin(2*np.pi*(60+120*tt/d)*tt)))
    x=x-np.convolve(x,np.ones(3)/3,'same'); add(sfx,t,x*np.minimum(1,tt/0.01)*np.minimum(1,(d-tt)/0.03)*g)
def rustle(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(14)/14,'same')*(0.6+0.4*np.sin(2*np.pi*7*tt))
    add(sfx,t,x*np.sin(np.pi*tt/d)*g)
def nasal(t,d,g,f=900):  # blocked-nose breath with a thin whistle
    n=int(d*sr); tt=np.arange(n)/sr; x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(5)/5,'same')
    x=x*0.6+0.25*np.sin(2*np.pi*(f+80*np.sin(2*np.pi*3*tt))*tt)
    add(sfx,t,x*np.sin(np.pi*tt/d)**2*g)
def mmph(t,g):
    n=int(0.28*sr); tt=np.arange(n)/sr; f=140+60*np.sin(np.pi*tt/0.28)
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.4*np.sin(4*np.pi*np.cumsum(f)/sr); x=np.convolve(x,np.ones(30)/30,'same')
    add(sfx,t,x*np.sin(np.pi*tt/0.28)*g)
def sting(t,g):
    for m_ in (57,58,63,64): add(mus,t,note(m_,1.2,0.25*g,1.6))
    boom(t,0.25*g)
def honk(t,g):
    n=int(0.45*sr); tt=np.arange(n)/sr; f=230-40*tt
    x=np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*0.5+np.convolve(rng.standard_normal(n),np.ones(4)/4,'same')*0.5
    x=np.convolve(x,np.ones(8)/8,'same'); add(sfx,t,x*np.minimum(1,tt/0.02)*np.minimum(1,(0.45-tt)/0.1)*g)
def gulp(t,g):
    n=int(0.12*sr); tt=np.arange(n)/sr; f=np.linspace(260,120,n); add(sfx,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.004,0.04)*g)
def thunk(t,g):
    n=int(0.2*sr); tt=np.arange(n)/sr; add(sfx,t,(np.sin(2*np.pi*180*tt)+0.6*np.sin(2*np.pi*420*tt)+np.convolve(rng.standard_normal(n),np.ones(10)/10,'same')*2)*env(n,0.001,0.05)*g)
def snore(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(50)/50,'same')*7*(0.55+0.45*np.sign(np.sin(2*np.pi*34*tt)))
    x+=0.35*np.sin(2*np.pi*(80+15*tt/d)*tt); add(sfx,t,x*np.sin(np.pi*tt/d)**1.5*g)
def birds(a,b,g):
    t=a
    while t<b:
        for k in range(rng.integers(2,4)):
            n=int(0.06*sr); f=np.linspace(3200+rng.random()*800,4200+rng.random()*600,n); add(sfx,t+k*0.09,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.003,0.025)*g)
        t+=0.5+rng.random()*0.6
def alarm(t,g):
    for k in range(3):
        for j in range(2): beep(t+k*0.35+j*0.11,g)
def folk(a,b,g=1.0,bpm=100):
    prog=[[55,59,62],[60,64,67],[57,60,64],[62,66,69]]; beat=60/bpm; t=a; i=0
    while t<b:
        ch=prog[(i//8)%4]
        if i%4==0: add(mus,t,note(ch[0]-12,beat*1.8,0.22*g,0.6))
        if i%4==2: add(mus,t,note(ch[0]-5,beat*1.2,0.12*g,0.6))
        pluck(t,ch[i%3]+12,0.13*g,0.45)
        if i%2==1: pluck(t,ch[(i+1)%3]+24,0.05*g,0.25)
        if i%8==7: n=int(0.03*sr); add(mus,t,rng.standard_normal(n)*env(n,0.001,0.012)*0.07*g)
        t+=beat/2; i+=1
def sneaky(a,b,g=1.0,bpm=126):
    seq=[45,None,48,None,50,None,48,51,45,None,48,None,52,51,50,None]; beat=60/bpm; t=a; i=0
    while t<b:
        m=seq[i%16]
        if m: pluck(t,m,0.24*g,0.22); pluck(t,m+12,0.06*g,0.15)
        if i%4==0: kick(t,0.25*g,70)
        t+=beat/2; i+=1
def sadbox(a,b,g=1.0):
    mel=[69,67,65,64,65,None,62,None,64,65,64,62,60,None,None,None]; beat=60/72; t=a; i=0
    while t<b:
        m=mel[i%16]
        if m: mbox(t,m,0.12*g,-0.3)
        if i%4==0: mbox(t,[50,46,48,45][(i//4)%4],0.09*g,-0.3)
        t+=beat/2; i+=1
def aww(t,g=0.12,f0=880,f1=620,d=0.7):
    n=int(d*sr); tt=np.arange(n)/sr; f=np.linspace(f0,f1,n)*(1+0.012*np.sin(2*np.pi*6*tt))
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.3*np.sin(4*np.pi*np.cumsum(f)/sr); add(mus,t,x*np.minimum(1,tt/0.08)*np.minimum(1,(d-tt)/0.25)*g)
def whimper(t,g=0.1,d=0.55):
    n=int(d*sr); tt=np.arange(n)/sr; f=980-380*(tt/d)+40*np.sin(2*np.pi*9*tt)
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.25*np.sin(4*np.pi*np.cumsum(f)/sr)+np.convolve(rng.standard_normal(n),np.ones(6)/6,'same')*0.15
    add(sfx,t,x*np.sin(np.pi*tt/d)**1.5*g)
def chomp(t,g=0.2):
    n=int(0.07*sr); x=np.convolve(rng.standard_normal(n),np.ones(3)/3,'same')*env(n,0.001,0.02); add(sfx,t,x*g); add(sfx,t+0.02,note(50,0.08,0.3*g,0.2)[:int(0.06*sr)])
def crunch(a,b,g=0.18):
    t=a
    while t<b: chomp(t,g*(0.7+0.5*rng.random())); t+=0.13+rng.random()*0.06
def paws(a,b,g=0.08,stepd=0.2):
    t=a
    while t<b: tick(t,g); tick(t+0.05,g*0.7); t+=stepd
def snap(t,g=0.3):
    n=int(0.04*sr); add(sfx,t,rng.standard_normal(n)*env(n,0.0005,0.006)*g); clank(t+0.01,0.06)
def woof(t,g=0.18):
    n=int(0.16*sr); tt=np.arange(n)/sr; f=np.linspace(420,260,n)
    x=np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*0.4+np.convolve(rng.standard_normal(n),np.ones(10)/10,'same')*2
    x=np.convolve(x,np.ones(14)/14,'same'); add(sfx,t,x*np.minimum(1,tt/0.01)*np.exp(-tt/0.07)*g)
def printer(a,b,g=0.08):
    t=a
    while t<b: tick(t,g); n=int(0.03*sr); add(sfx,t+0.015,rng.standard_normal(n)*env(n,0.001,0.01)*g*0.6); t+=0.045
def kaching(t,g=0.2):
    for m_,o in [(84,0),(88,0.07),(91,0.14)]: add(sfx,t+o,note(m_,0.6,g,1.4))
    for k_ in range(6): n=int(0.03*sr); add(sfx,t+0.2+k_*0.05,np.sin(2*np.pi*(3000+rng.random()*1500)*np.arange(n)/sr)*env(n,0.001,0.02)*g*0.5)
def plod(a,b,g=1.0):
    seq=[45,None,40,None,45,None,40,None,44,None,40,None,45,47,48,None]; beat=60/92; t=a; i=0
    while t<b:
        m=seq[i%16]
        if m: add(mus,t,note(m,beat*0.5,0.24*g,1.1));
        if i%2==0: pluck(t+beat/2,[64,67,63,67][(i//4)%4],0.08*g,0.2)
        t+=beat/2; i+=1
# ===== ep18: tongue on a frozen pole. Music per scene: ironic sleigh-bell + glockenspiel winter tune (the dare)
# -> drumroll on the lean-in -> record scratch + ice 'TSSS' + metal ting on contact -> panic pizzicato + heartbeat (stuck)
# -> live-stream pings + shutter clicks (friends film) -> rising drums + rubber-stretch squeak (pull) -> sting + silence (freeze)
# -> thinking keys (pause: heat whoosh, ice crackle, warning buzz) -> rewind sweep -> light winter tune again (right move: cocoa sip)
# -> sad-trombone 'wah wah' on 'Boring!' -> thumbs-up chime -> 'viral' beat + notification pings (punchline) -> record stop + wind
# -> calm tip pad + keys -> end chime
k_=lambda n:P(n)
n10=P('n1.0'); n11=P('n1.1'); f10=P('f1.0'); f11=P('f1.1'); h10=P('h1.0'); h11=P('h1.1')
n20=P('n2.0'); n20e=PE('n2.0'); n21=P('n2.1'); n22=P('n2.2'); h20=P('h2.0'); h21=P('h2.1')
n30=P('n3.0'); n31=P('n3.1'); n32=P('n3.2'); n33=P('n3.3'); n34=P('n3.4')
TT=n20+(n20e-n20)*0.78; FZ=n34+0.42
pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.0
v1=P('m1.1'); v1e=PE('m1.1'); sp=P('m1.2'); pl=P('m1.3'); ple=PE('m1.3'); rw=P('m1.4')
a0=P('n4.0'); a1=P('n4.1'); a2=P('n4.2'); a2e=PE('n4.2'); SIP=a2+(a2e-a2)*0.62
h30=P('h3.0'); h31=P('h3.1'); f20=P('f2.0'); f21=P('f2.1')
m2=C['m2']['start']; b1=P('m2.1'); b2=P('m2.2'); b2e=PE('m2.2'); tip=C['m3']['start']; end=C['m4']['start']-0.2
def hp(x,k=6): return x-np.convolve(x,np.ones(k)/k,'same')
def bells(t,g=0.06):
    n=int(0.09*sr); tt=np.arange(n)/sr; x=hp(rng.standard_normal(n),3)*env(n,0.001,0.03)
    x+=0.3*(np.sin(2*np.pi*5200*tt)+np.sin(2*np.pi*6900*tt))*env(n,0.001,0.04); add(mus,t,x*g)
def glock(t,m,g=0.12,d=0.6):
    n=int(d*sr); tt=np.arange(n)/sr; f=440*2**((m-69)/12)
    x=(np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt/0.05)+0.2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt/0.02))*env(n,0.001,d*0.4); add(mus,t,x*g)
WMEL=[79,None,76,77,79,None,84,None,81,None,79,77,76,None,None,None,77,None,74,76,77,None,81,None,79,None,77,76,74,None,72,None]
WCH=[[60,64,67],[65,69,72],[67,71,74],[60,64,67]]
def winter(a,b,g=1.0,bpm=126,mel=True):
    beat=60/bpm; t=a; i=0
    while t<b:
        ch=WCH[(i//8)%4]
        if mel and WMEL[i%32]: glock(t,WMEL[i%32],0.12*g)
        if i%4==0: add(mus,t,note(ch[0]-24,beat*1.6,0.24*g,0.5))
        if i%4==2: add(mus,t,note(ch[2]-24,beat*1.2,0.16*g,0.5))
        if i%2==1: pluck(t,ch[(i//2)%3]+12,0.07*g,0.3)
        bells(t,0.05*g*(1.4 if i%2==0 else 0.8))
        t+=beat/2; i+=1
def roll(a,b,g=0.1):
    t=a
    while t<b:
        k=(t-a)/max(1e-6,b-a); n=int(0.03*sr); add(mus,t,hp(rng.standard_normal(n),4)*env(n,0.001,0.012)*g*(0.4+0.8*k)); t+=0.055-0.02*k
def scratch(t,g=0.3):
    n=int(0.28*sr); tt=np.arange(n)/sr; f=np.concatenate([np.linspace(900,200,n//2),np.linspace(200,700,n-n//2)])
    x=np.sin(2*np.pi*np.cumsum(f)/sr)*0.5+hp(rng.standard_normal(n),3)*0.6; add(sfx,t,x*np.sin(np.pi*tt/0.28)*g)
def hiss(t,d,g):
    n=int(d*sr); tt=np.arange(n)/sr; add(sfx,t,hp(rng.standard_normal(n),2)*np.minimum(1,tt/0.01)*np.exp(-tt/(d*0.4))*g)
def ting(t,g=0.2):
    n=int(1.2*sr); tt=np.arange(n)/sr; x=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt/dd) for f,a,dd in [(1180,1,0.5),(2730,0.6,0.25),(4410,0.4,0.12),(620,0.4,0.6)])
    add(sfx,t,x*np.minimum(1,tt/0.002)*g)
def icecrack(a,b,g=0.12):
    t=a
    while t<b:
        n=int(0.012*sr); add(sfx,t,hp(rng.standard_normal(n),2)*env(n,0.0005,0.004)*g*(0.5+rng.random())); t+=0.02+rng.random()*0.05
def stretch(a,b,g=0.06):
    n=int((b-a)*sr); tt=np.arange(n)/sr; f=320+520*(tt/(b-a))**1.3+30*np.sin(2*np.pi*11*tt)
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.3*np.sin(4*np.pi*np.cumsum(f)/sr); add(sfx,a,x*np.minimum(1,tt/0.05)*np.minimum(1,((b-a)-tt)/0.05)*g)
def ping(t,g=0.1,m=88):
    add(sfx,t,note(m,0.25,g,0.3)); add(sfx,t+0.07,note(m+5,0.3,g*0.8,0.3))
def wah(t,g=0.18):
    for i,(m,d) in enumerate([(55,0.32),(54,0.32),(53,0.32),(52,0.9)]):
        n=int(d*sr); tt=np.arange(n)/sr; f=440*2**((m-69)/12)*(1+(0.02*np.sin(2*np.pi*6*tt) if i==3 else 0))
        ph=2*np.pi*np.cumsum(np.full(n,1.0)*f)/sr; x=sum(np.sin(k*ph)/k for k in range(1,8)); x=np.convolve(x,np.ones(6)/6,'same')
        add(mus,t+i*0.3,x*np.minimum(1,tt/0.03)*np.minimum(1,(d-tt)/0.08)*g)
def slurp(t,d=0.5,g=0.12):
    n=int(d*sr); tt=np.arange(n)/sr; x=rng.standard_normal(n); lo=np.convolve(x,np.ones(30)/30,'same')*5; x=lo*(0.5+0.5*np.sin(2*np.pi*(18+20*tt/d)*tt))
    add(sfx,t,x*np.sin(np.pi*tt/d)*g)
def wind(a,b,g=0.1):
    n=int((b-a)*sr); tt=np.arange(n)/sr; x=np.convolve(rng.standard_normal(n),np.ones(60)/60,'same')*8*(0.6+0.4*np.sin(2*np.pi*0.4*tt))
    add(sfx,a,x*np.minimum(1,tt/0.4)*np.minimum(1,((b-a)-tt)/0.4)*g)
def trap(a,b,g=1.0,bpm=140):
    beat=60/bpm; t=a; i=0
    while t<b:
        if i%8 in (0,3,6): kick(t,0.7*g,70)
        if i%8==4: n=int(0.08*sr); add(mus,t,hp(rng.standard_normal(n),3)*env(n,0.001,0.04)*0.25*g)
        n=int(0.012*sr); add(mus,t,hp(rng.standard_normal(n),2)*env(n,0.0005,0.004)*0.08*g)
        if i%4==0: add(mus,t,note([57,57,53,55][(i//8)%4]-12,beat*1.8,0.22*g,0.7))
        if i%2==0: pluck(t,[69,72,76,72][(i//2)%4],0.06*g,0.25)
        t+=beat/2; i+=1
# ---------------- MUSIC
winter(0.0,TT-0.02,1.0,126)
roll(n20+0.2,TT-0.02,0.12)
sneaky(TT+0.5,n32-0.1,1.1,150)
heartbeat(TT+0.4,n32,0.22)
drums(n32-0.05,FZ,120,190,0.6)
sting(FZ-0.05,0.7)
keys(pause+0.25,rwS,1.1)
winter(rwE+0.1,f21-0.05,0.65,120)
wah(f21-0.02,0.12)
groove(f21+0.85,m2,0.55,104)
trap(m2+0.05,b2-0.05,0.7,140)
pad(tip,end,[57,60,64,67],0.14); keys(tip+0.1,end,0.55); pad(end+0.2,D,[60,64,67,72],0.08)
for m_,a_ in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: glock(end+0.4+a_,m_,0.16,1.2)
lvl=np.ones(N)
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(rwS,rwE,0.2); seg(FZ+0.9,pause,0.0)
k=int(0.08*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
# ---------------- SFX
wind(0.0,FZ,0.05)
pop(0.05,0.1); pop(n11-0.1,0.14); ding(n11+0.2,0.08)
whoosh(f10-0.4,0.4,0.1); pop(f10,0.12); shutter(f10-0.2,0.12)
pop(h10,0.12); rustle(h11,0.35,0.06)
# contact
scratch(TT-0.03,0.32); ting(TT,0.12); hiss(TT,0.6,0.16); icecrack(TT,TT+0.8,0.14); boom(TT,0.1)
pop(n21-0.05,0.16); for_=[tick(n22+i*0.6,0.1) for i in range(3)]
# stuck: friends film
for i in range(4): shutter(n30+0.4+i*0.37,0.08)
for i,tc in enumerate([n31,n31+0.25,n31+0.5,n31+0.75]): ping(tc,0.07,86+i*2)
pop(n31-0.15,0.15)
for i in range(5): pop(n31+0.1+i*0.18,0.05)
# pull
stretch(n32+0.1,FZ-0.02,0.07); grunt(n33,0.4,0.18); boom(n33,0.12)
thunk(n34,0.2); pop(n34,0.16)
n_=int(0.35*sr); tt=np.arange(n_)/sr; f=np.linspace(300,30,n_); add(sfx,FZ,np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt/0.2)*0.25)
n_=int(0.05*sr); add(sfx,pause,rng.standard_normal(n_)*env(n_,0.001,0.01)*0.6)
# pause diagram
whoosh(v1-0.4,0.6,0.14); pop(v1,0.14)
for i in range(4): whoosh(v1+0.7+i*0.55,0.5,0.05)
pop(v1+0.8,0.12)
icecrack(sp+0.2,sp+1.0,0.12); pop(sp+0.2,0.14); ting(sp+0.9,0.05)
whoosh(pl,0.5,0.1); beep(pl+(ple-pl)*0.55,0.06); beep(pl+(ple-pl)*0.55+0.14,0.06); pop(pl+(ple-pl)*0.55,0.12)
pop(rw-0.2); click(rw,0.2); ding(rw+0.3,0.12)
n_=int(1.0*sr); tt=np.arange(n_)/sr; f=np.linspace(1800,300,n_)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n_),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.0))
# right move
wind(rwE,m2,0.035)
pop(a0+0.05,0.12); ting(a0+0.1,0.04); pop(a1+0.05,0.12); shutter(a1+0.3,0.06)
slurp(SIP-0.05,0.55,0.14); pop(a2+0.35,0.12); ding(a2+0.45,0.08)
pop(h30,0.12)
pop(f20,0.14)
for m_,a_ in [(72,0),(76,0.1),(79,0.2),(84,0.3)]: pluck(f21+0.4+a_,m_,0.16,0.6)
# punchline
for i in range(9): ping(m2+0.15+i*0.42,0.06,84+(i%4)*2)
pop(m2+0.1,0.15); pop(b1+0.05,0.15); pop(b1+0.3,0.12); kaching(b1+0.1,0.1)
scratch(b2-0.25,0.28); wind(b2-0.1,tip,0.07)
for i in range(4): shutter(b2+0.3+i*0.33,0.1)
for k2 in ['m3.0','m3.1','m3.3','m3.4']: blip(P(k2))
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
sduck=1-0.6*np.clip(e/0.05,0,1)
out=v+mus*0.45*duck+sfx*0.75*sduck
pk=np.percentile(np.abs(out),99.9); out=out*min(1.0,0.8/pk); out=np.tanh(out*1.1)/np.tanh(1.1)*0.95
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
if __name__=='__main__':
    import sys
    W=int(2*sr)
    for i in range(0,N,W):
        r=lambda x: 20*np.log10(np.sqrt((x[i:i+W]**2).mean())+1e-9)
        print(f'{i/sr:5.1f} voice {r(v):6.1f} mus {r(mus*0.45*duck):6.1f} sfx {r(sfx*0.75*sduck):6.1f}')
