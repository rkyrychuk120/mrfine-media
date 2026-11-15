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

A_=[0]+[C['a%d'%i]['start'] for i in range(1,11)];a1,a2,a3,a4,a5,a6,a7,a8,a9,a10=A_[1:]
fxL=np.zeros(N);fxR=np.zeros(N)
def addS(t0,x,g=1,pan=0.0):add(fxL,t0,x,g*(1-pan));add(fxR,t0,x,g*(1+pan))
# --- music: tense pulse bed (low synth ostinato + pad), level by section ---
bpm=84;beat=60/bpm
notes=[36,36,39,36,41,36,39,34]
for k,tb in enumerate(np.arange(0,D,beat/2)):
    m=notes[k%len(notes)];f=440*2**((m-69)/12);n=int(beat/2*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f*tt)+0.5*np.sign(np.sin(2*np.pi*f*tt))*0.3)*env(n,0.004,0.12);add(mus,tb,lp(x,6),0.5)
pad=sum(np.sin(2*np.pi*f*t+p) for f,p in ((65.4,0),(77.8,1),(98,2),(116.5,.5)))*0.25*(0.7+0.3*np.sin(2*np.pi*0.05*t))
mus+=pad

lvl=np.full(N,0.5)
def seg(a,b,v):lvl[int(a*sr):int(b*sr)]=v
seg(0,a3,0.5);seg(a3,a6,0.4);seg(a6,a8,0.1);seg(a8,a10,0.45);seg(a10,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)





tStop=wT('a8','stopped')
# outdoor ambience (less inside)
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.06*np.where(t<a3,1,0.35)
# alarm until stop
f=np.where((t%4)<2,700+500*((t*6)%1>0.5),900+400*np.sin(2*np.pi*3*t));al=np.sign(np.sin(np.cumsum(2*np.pi*f/sr)))*(t<tStop)
al=lp(al,6)*0.02*np.clip((3.0-t)/1.5,0,1);fxL+=al*0.8;fxR+=al*1.2
# footsteps on street + inside
def step(tk,g):n=int(.08*sr);addS(tk,lp(rng.standard_normal(n),4)*env(n,.002,.02),g*0.18,rng.uniform(-.3,.3))
for tk in np.arange(0.3,a3,0.42): step(tk,1)
for tk in np.arange(a3,a5,0.55): step(tk,0.7)
# 10s ticks a1
for k in range(10):
    n=int(.06*sr);add(fx,0.5+k*0.6,np.sin(2*np.pi*1800*np.arange(n)/sr)*env(n,.001,.02)*.12)
# glass door creak + bell
n=int(.6*sr);tt=np.arange(n)/sr;add(fx,a3-0.2,sum(np.sin(2*np.pi*f*tt)*a for f,a in ((1568,1),(2093,.6)))*env(n,.005,.25)*.12)
# item rustle picks
for w in ('bandages','painkillers','antiseptic','inhaler'):
    n=int(.25*sr);add(fx,wT('a5',w),lp(rng.standard_normal(n),3)*env(n,.005,.06)*.3)
# heartbeat a6-a8
for k in np.arange(a6,a8,0.78):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
tly=wT('a7','they');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tly,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.2,8))
# faint knock from behind back door in a7
for k in (a7+2.0,a7+2.4):
    n=int(.2*sr);add(fx,k,verb((np.sin(2*np.pi*90*np.arange(n)/sr)+lp(rng.standard_normal(n),20)*2)*env(n,.002,.05),0.8),0.25)
# silence after alarm stops + groans approaching
n=int(1.5*sr);tt=np.arange(n)/sr;add(fx,tStop,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.7)))*env(n,.01,.6)*.16,8))
for k in range(18):
    tk=tStop+0.8+rng.random()*(D-tStop-2);n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170)
    addS(tk,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.045,1.2),1,rng.uniform(-.8,.8))
for w in ('knock','or'):
    n=int(.5*sr);add(fx,wT('a10',w)-0.2,lp(rng.standard_normal(n),40)*np.sin(np.pi*np.arange(n)/n)**2*3)
n=int(3*sr);tt=np.arange(n)/sr;add(fx,END('a10')+0.05,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.8)))*env(n,.01,1.0)*.18,8))
# --- voice + mix
w=wave.open('voice.wav');v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(.2*sr))/(.2*sr),'same');duck=1-0.45*np.clip(e/0.04,0,1)
base=v*1.0+mus*0.22*duck+fx*0.75
L=base+fxL*0.75*duck**0.5;Rr=base+fxR*0.75*duck**0.5
m=max(1,max(np.abs(L).max(),np.abs(Rr).max())/0.97);L/=m;Rr/=m
st=np.stack([L,Rr],1)
wo=wave.open('mix_raw.wav','wb');wo.setnchannels(2);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes((st*32767).astype(np.int16).tobytes());wo.close()
import subprocess;subprocess.run(['ffmpeg','-v','error','-y','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mix.wav'],check=True);print('ok')
