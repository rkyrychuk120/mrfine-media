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

A_=[0]+[C['a%d'%i]['start'] for i in range(1,10)];a1,a2,a3,a4,a5,a6,a7,a8,a9=A_[1:]
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
seg(0,a3,0.45);seg(a3,a5,0.12);seg(a5,a6,0.5);seg(a6,a7,0.7);seg(a7,a8,0.45);seg(a8,a9,0.4);seg(a9,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)




tlook=wT('a3','look')
# ladder rungs clank while climbing
for tk in np.arange(0.3,tlook-0.3,0.6):
    n=int(.2*sr);tt=np.arange(n)/sr;x=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((420,1),(1100,.4)))*env(n,.002,.05);addS(tk,verb(x,0.8),0.12,rng.uniform(-.3,.3))
for tk in np.arange(0.4,tlook,1.6):
    n=int(.7*sr);addS(tk,lp(rng.standard_normal(n),6)*np.sin(np.pi*np.arange(n)/n)*.05,1,0)
# grate scrape on lift
tlf=wT('a3','lifts');n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,tlf,lp(rng.standard_normal(n),3)*(0.5+0.5*np.sin(2*np.pi*9*tt))*np.sin(np.pi*tt/1.2)*.25)
# outdoor ambience from look: wind + distant city, birds absent; crows
amb=(t>=tlook)
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.06*amb*(1+0.4*np.sin(2*np.pi*0.1*t+seed))
for tk in (a4+1.5,a4+5.5):
    n=int(.5*sr);tt=np.arange(n)/sr;addS(tk,verb(np.sin(2*np.pi*(700-300*tt)*tt)*lp(rng.standard_normal(n),2)*env(n,.01,.15)*.25,1.5),1,rng.uniform(-.7,.7))
# car alarm (classic multi-tone) from tAl to end, distant (lowpassed), louder in a8
tAl=wT('a5','car');al=np.zeros(N);ii=t>=tAl
f=np.where(((t-tAl)%4)<2,700+500*((t*6)%1>0.5),900+400*np.sin(2*np.pi*3*t))
ph=np.cumsum(2*np.pi*f/sr);al=np.sign(np.sin(ph))*ii
al=lp(al,6)*np.where((t>=a8)&(t<a9),0.05,0.028)
fxL+=al*0.8;fxR+=al*1.2
# zombie groans after come
tCome=wT('a5','come')
for k in range(24):
    tk=tCome+rng.random()*(a9-tCome);n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170)
    addS(tk,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.05,1.2),1,rng.uniform(-.8,.8))
for k in np.arange(tCome,a6,0.75):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
# 10-second ticks
tten=wT('a6','ten')
for k in range(10):
    n=int(.06*sr);add(fx,tten+k,np.sin(2*np.pi*1800*np.arange(n)/sr)*env(n,.001,.02)*.15)
# driver reveal hit
tdr=wT('a7','driver');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tdr,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.18,8))
n=int(1.0*sr);tt=np.arange(n)/sr;add(fx,tdr+0.4,np.sin(2*np.pi*(150-50*tt)*tt+4*np.sin(2*np.pi*29*tt))*env(n,.02,.4)*.2)
for w in ('run','or'):
    n=int(.5*sr);add(fx,wT('a9',w)-0.2,lp(rng.standard_normal(n),40)*np.sin(np.pi*np.arange(n)/n)**2*3)
n=int(3*sr);tt=np.arange(n)/sr;add(fx,END('a9')+0.05,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.8)))*env(n,.01,1.0)*.18,8))
# --- voice + mix
w=wave.open('voice.wav');v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(.2*sr))/(.2*sr),'same');duck=1-0.45*np.clip(e/0.04,0,1)
base=v*1.0+mus*0.22*duck+fx*0.75
L=base+fxL*0.75*duck**0.5;Rr=base+fxR*0.75*duck**0.5
m=max(1,max(np.abs(L).max(),np.abs(Rr).max())/0.97);L/=m;Rr/=m
st=np.stack([L,Rr],1)
wo=wave.open('mix_raw.wav','wb');wo.setnchannels(2);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes((st*32767).astype(np.int16).tobytes());wo.close()
import subprocess;subprocess.run(['ffmpeg','-v','error','-y','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mix.wav'],check=True);print('ok')
