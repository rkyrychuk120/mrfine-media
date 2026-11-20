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
seg(0,a2,0.55);seg(a2,a3,0.45);seg(a3,a4,0.3);seg(a4,a5,0.5);seg(a5,a6,0.4);seg(a6,a7,0.25);seg(a7,a8,0.35);seg(a8,a9,0.5);seg(a9,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def thud(tt0,g=1,f0=90):
    n=int(.35*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f0*tt)*1.2+lp(rng.standard_normal(n),12)*2.5)*env(n,.001,.06)
    gl=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((820,1),(1900,.5),(3300,.3)))*env(n,.001,.05)*.3
    add(fx,tt0,verb(x*.6+gl,0.5),0.35*g)
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.05
# van arrival: engine + tire squeal + brake, idle until a3
eng=lp(np.sign(np.sin(2*np.pi*np.where(t<1.2,38-10*t/1.2,24)*t))*0.5+lp(rng.standard_normal(N),30)*2,8)
fx+=eng*0.045*np.clip((a3+0.5-t)/1.0,0,1)
n=int(1.3*sr);tt=np.arange(n)/sr;add(fx,0.35,lp(rng.standard_normal(n),2)*np.sin(2*np.pi*(1700+250*np.sin(tt*25))*tt)*np.sin(np.pi*tt/1.3)*.05)
n=int(.3*sr);add(fx,1.65,lp(rng.standard_normal(n),15)*env(n,.002,.08)*.5)
# soft van door + police door
for tt0 in (a2+0.6,a3+0.15):
    n=int(.25*sr);add(fx,tt0,lp(rng.standard_normal(n),6)*env(n,.001,.04)*.35)
# radio chatter bursts
def radio(t0,d=1.8,g=1):
    n=int(d*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);bp=lp(nz,2)-lp(nz,12)
    syl=(0.5+0.5*np.sign(np.sin(2*np.pi*3.3*tt+np.sin(2*np.pi*.7*tt)*3)))
    v=np.sin(2*np.pi*(380+60*np.sin(2*np.pi*5*tt))*tt)*syl*.4
    add(fx,t0,(bp*.5+v*.25)*np.sin(np.pi*tt/d)**.5*0.12*g)
radio(wT('a3','radio')-0.1,2.2);radio(wT('a5','radio')-0.1,2.6,1.2)
# wheezing until mask
tM=wT('a5','puts')
for k in np.arange(a2+0.8,tM+0.6,1.7):
    n=int(.9*sr);tt=np.arange(n)/sr;add(fx,k,lp(rng.standard_normal(n),3)*(0.5+0.5*np.sin(2*np.pi*480*tt))*np.sin(np.pi*tt/0.9)**2*.045)
for k in np.arange(tM+0.8,a6,2.6):
    n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,k,lp(rng.standard_normal(n),6)*np.sin(np.pi*tt/1.2)**2*.02)
# trunk creak + oxygen hiss
tTr=a5+0.4;n=int(.9*sr);tt=np.arange(n)/sr;add(fx,tTr,np.sin(2*np.pi*(300+120*tt)*tt+2*np.sin(2*np.pi*11*tt))*np.sin(np.pi*tt/.9)*.05)
n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tM+0.3,(lp(rng.standard_normal(n),1)-lp(rng.standard_normal(n),4))*env(n,.05,1.2)*.12)
# heartbeat a6
for k in np.arange(a6,a7,0.75):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
# knocks on glass
for i in range(2):thud(wT('a6','knock',i),1.6)
tw=wT('a6','police');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tw,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.14,8))
# distant groans (short events)
for k in range(14):
    tk=rng.random()*D;n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170)
    addS(tk,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.025,1.2),1,rng.uniform(-.8,.8))
tw=wT('a8','one');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tw,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.16,8))
for w in ('let','or'):
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
