import numpy as np,wave,json
tl=json.loads(open('tl.js').read()[9:-1]);sr=48000;D=tl['total'];N=int(D*sr);t=np.arange(N)/sr;rng=np.random.default_rng(11)
C={c['n']:c for c in tl['clips']};END=lambda n:C[n]['start']+C[n]['dur']
def wT(clip,word,nth=0):
    k=0
    for ch in tl['chunks']:
        if ch['s']<C[clip]['start']-0.01 or ch['s']>END(clip)+0.01: continue
        for w in ch['w']:
            ww=''.join(c for c in w[0].lower() if c.isalnum() or c in ':%')
            if ww.startswith(word):
                if k==nth: return w[2]
                k+=1
    return C[clip]['start']
mus=np.zeros(N);fx=np.zeros(N)
def add(buf,t0,x,g=1):
    i=int(t0*sr)
    if i>=N or i<0: return
    j=min(N,i+len(x));buf[i:j]+=x[:j-i]*g
def env(n,a,r):tt=np.arange(n)/sr;return np.minimum(1,tt/a)*np.exp(-tt/r)
def lp(x,k):return np.convolve(x,np.ones(k)/k,'same')
def verb(x,d=1.2):
    ir=rng.standard_normal(int(d*sr))*np.exp(-np.arange(int(d*sr))/sr*4/d)*0.04;return np.convolve(x,ir)
a2,a4,a5,a6,a7,a8=[C[n]['start'] for n in ('a2','a4','a5','a6','a7','a8')]
tStop=wT('a2','stops');tLights=wT('a2','lights');tScream=wT('a2','scream');tHit3=wT('a3','hitting');tEar=wT('a2','earlier')
# --- music: tense pulse bed (low synth ostinato + pad), level by section ---
bpm=84;beat=60/bpm
notes=[36,36,39,36,41,36,39,34]
for k,tb in enumerate(np.arange(0,D,beat/2)):
    m=notes[k%len(notes)];f=440*2**((m-69)/12);n=int(beat/2*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f*tt)+0.5*np.sign(np.sin(2*np.pi*f*tt))*0.3)*env(n,0.004,0.12);add(mus,tb,lp(x,6),0.5)
pad=sum(np.sin(2*np.pi*f*t+p) for f,p in ((65.4,0),(77.8,1),(98,2),(116.5,.5)))*0.25*(0.7+0.3*np.sin(2*np.pi*0.05*t))
mus+=pad
# section levels
lvl=np.full(N,0.55)
def seg(a,b,v):lvl[int(a*sr):int(b*sr)]=v
seg(0,a2,0.7);seg(a2,tEar+0.3,0.0);seg(tEar+0.3,tStop,0.35);seg(tStop,tLights,0.15);seg(tLights,a4,0.6);seg(a4,a5,0.5);seg(a5,a6,0.4);seg(a6,a7,0.75);seg(a7,a8,0.4);seg(a8,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.2*sr))/(.2*sr),'same');mus*=lvl
# --- FX ---
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)
for b in [wT('a1','hitting'),wT('a1','minutes')+0.1,wT('a1','broken'),tHit3,tHit3+0.9,tHit3+1.7]: door_hit(b)
# heartbeat cold open + twist
for a,b in ((0.3,a2),(a6,a7)):
    for k in np.arange(a,b,0.78):
        for d,g in ((0,1),(.17,.7)):
            n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.8)
# riser + braam into "3 minutes earlier"
n=int(1.0*sr);tt=np.arange(n)/sr;f=np.linspace(200,1800,n);add(fx,a2-1.0,(np.sin(2*np.pi*np.cumsum(f)/sr)*.12+lp(rng.standard_normal(n),3)*.2)*(tt/1)**2)
n=int(2.5*sr);tt=np.arange(n)/sr;add(fx,a2+0.02,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.8),(73.4,.5)))*env(n,.01,.8)*.18,8))
for k in np.arange(a2+0.6,tEar+0.4,0.5):
    n=int(.05*sr);add(fx,k,np.sin(2*np.pi*2400*np.arange(n)/sr)*env(n,.001,.01)*.12)
# train rumble + clacks while moving, brakes at stop
mv=(t>tEar+0.3)&(t<tStop+0.6);rum=(lp(rng.standard_normal(N),180)*10+np.sin(2*np.pi*42*t)*.4)*mv*np.clip((tStop+0.6-t)/0.6,0,1)
fx+=rum*0.12
for k in np.arange(tEar+0.5,tStop,0.62):
    for d in (0,.09):n=int(.06*sr);add(fx,k+d,lp(rng.standard_normal(n),6)*env(n,.001,.02)*.4)
n=int(1.4*sr);tt=np.arange(n)/sr;add(fx,tStop-0.3,np.sin(2*np.pi*(2300+250*np.sin(tt*28))*tt)*env(n,.05,.5)*.12)
n=int(.7*sr);tt=np.arange(n)/sr;add(fx,tStop,(np.sin(2*np.pi*45*tt)*1.5+lp(rng.standard_normal(n),40)*5)*env(n,.002,.25)*.4)
# lights out clunk + alarm hum
n=int(.35*sr);add(fx,tLights,np.sin(2*np.pi*70*np.arange(n)/sr)*env(n,.002,.1)*.9)
alarmz=(t>tLights)&(t<a7);fx+=np.sign(np.sin(2*np.pi*120*t))*0.012*alarmz
# scream (distant)
n=int(1.0*sr);tt=np.arange(n)/sr;add(fx,tScream,np.sin(2*np.pi*(850+380*np.sin(tt*8))*tt)*lp(rng.standard_normal(n),4)*env(n,.05,.35)*.2)
# phone notification ping
add(fx,wT('a3','video')-0.2,np.sin(2*np.pi*1568*np.arange(int(.25*sr))/sr)*env(int(.25*sr),.002,.08)*.25)
# paper sounds + pen ticks
n=int(.5*sr);add(fx,a5,lp(rng.standard_normal(n),3)*env(n,.02,.15)*.3)
for w in ['water','light','next','the']:
    n=int(.12*sr);add(fx,wT('a5',w)+.1,lp(rng.standard_normal(n),3)*env(n,.002,.03)*.3)
# "only one problem" hit
tp=wT('a5','one');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tp,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.18,8))
# handle creak
tsl=wT('a6','slowly');n=int(2.2*sr);tt=np.arange(n)/sr;add(fx,tsl,np.sin(2*np.pi*(180+60*tt)*tt+3*np.sin(2*np.pi*23*tt))*np.sin(np.pi*tt/2.2)*.1)
tb=wT('a6','broken');door_hit(tb,0.6)
# tunnel: drips + wind
fx+=lp(rng.standard_normal(N),400)*6*((t>a7))*0.08
for k in np.arange(a7+0.5,D,1.37):
    n=int(.12*sr);tt=np.arange(n)/sr;add(fx,k+rng.random()*0.4,np.sin(2*np.pi*(1200-4000*tt)*tt)*env(n,.001,.03)*.12)
th=wT('a7','third');n=int(4*sr);tt=np.arange(n)/sr;add(fx,th-0.2,np.sign(np.sin(2*np.pi*100*tt))*0.05*np.sin(np.pi*tt/4))
# choices whoosh + end hit
for w in ['open','or']:
    n=int(.5*sr);add(fx,wT('a8',w)-0.2,lp(rng.standard_normal(n),40)*np.sin(np.pi*np.arange(n)/n)**2*3)
n=int(3*sr);tt=np.arange(n)/sr;add(fx,END('a8')+0.05,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.8)))*env(n,.01,1.0)*.18,8))
# voice
w=wave.open('voice.wav');v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(.2*sr))/(.2*sr),'same');duck=1-0.5*np.clip(e/0.04,0,1)
out=v*1.0+mus*0.16*duck+fx*0.75

out/=max(1,np.abs(out).max()/0.97)
wo=wave.open('mix.wav','wb');wo.setnchannels(1);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes((out*32767).astype(np.int16).tobytes());wo.close();print('ok')
