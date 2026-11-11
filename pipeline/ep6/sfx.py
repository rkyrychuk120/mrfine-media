import numpy as np, wave, json
sr=48000; tl=json.load(open('timeline.json')); D=tl['total']; N=int(D*sr); PH=tl['ph']
C={c['name']:c for c in tl['clips']}
P=lambda k:PH[k][0]
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
snap=PH['n3.2'][0]; spinEnd=PH['n3.2'][1]
pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.1
tip=C['m3']['start']; end=C['m4']['start']-0.2; eyes=P('n2.1')
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
# experiment: gym beat that slows and sags in pitch when the room spins
gymbeat(0,snap); gymbeat(snap,pause,warp=lambda t:1-0.35*min(1,(t-snap)/(spinEnd-snap)))
heartbeat(eyes,pause,0.8)
pad(pause+0.2,rwS,[57,60,64],0.18); bounce(rwE,tip); pad(tip,end,[60,64,67,71],0.16)
for m,a in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: add(mus,end+0.4+a,note(m,1.4,0.18))
lvl=np.ones(N)
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(rwS,rwE,0.2)
k=int(0.1*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
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
# bar clanks on each rep bottom (hook + squats)
h1=C['h1']['start']; n2=P('n2.0')
t_=0.55
while t_<h1: clank(t_,0.18); t_+=1/0.9
t_=n2+0.45
while t_<snap: clank(t_,0.18); t_+=1/1.1
whoosh(snap,1.2,0.4); whoosh(snap+1.0,1.2,0.35)
for q in range(3): blip(P('h1.2')+q*0.15)
blip(P('n1.0')+0.1); blip(P('n1.2'))
for k_ in ['n3.0','n3.1','n3.2']: tick(P(k_),0.3)
n=int(0.05*sr); add(sfx,pause,rng.standard_normal(n)*env(n,0.001,0.01)*0.6)
n=int(1.1*sr); tt=np.arange(n)/sr; f=np.linspace(1800,300,n)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.1))
boom(P('n4.2')+0.75,0.25)
for k_ in ['m1.1','n4.2','n4.3','n4.4','n4.5','m2.0','m3.0','m3.1','m3.2','m3.3','m3.4','m3.5']: blip(P(k_))
ding(C['h2']['start']+0.3,0.2)
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
out=v+mus*0.12*duck+sfx*0.7
out/=max(1,np.abs(out).max()/0.95)
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
