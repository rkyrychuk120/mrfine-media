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
