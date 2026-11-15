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
seg(0,a2,0.25);seg(a2,a3,0.5);seg(a3,a6,0.4);seg(a6,a7,0.3);seg(a7,a8,0.1);seg(a8,a10,0.45);seg(a10,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)





tk=[wT('a1','knock',k) for k in range(3)];tTurn=wT('a1','turns');tGet=wT('a5','get');tOpen=wT('a8','opened');tSo=wT('a2','so')
street=(t>=a2)&(t<tSo)
# ambience: room tone inside, outdoor wind in recap street shot
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.06*np.where(street,1,0.3)
# knocks (knuckles on metal door)
def knock(t0,g=1):
    n=int(.35*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*95*tt)*1.2+lp(rng.standard_normal(n),6)*1.5)*env(n,.001,.035)+sum(np.sin(2*np.pi*f*tt)*a for f,a in ((520,1),(1310,.5)))*env(n,.001,.09)*.25
    add(fx,t0,verb(x,0.6),0.5*g)
for q in tk: knock(q-0.03)
# lock turning
for d,f in ((0,2400),(0.12,1800),(0.3,3000)):
    n=int(.05*sr);add(fx,tTurn+d,np.sin(2*np.pi*f*np.arange(n)/sr)*env(n,.001,.01)*.25+lp(rng.standard_normal(n),2)*env(n,.001,.01)*.2)
# door creak at a3 and wider at get
def creak(t0,dur,g):
    n=int(dur*sr);tt=np.arange(n)/sr;f=380+120*np.sin(2*np.pi*1.3*tt)+60*rng.standard_normal(n).cumsum()/np.sqrt(n)*0
    x=np.sign(np.sin(np.cumsum(2*np.pi*f/sr)))*(0.5+0.5*np.sin(2*np.pi*23*tt)>0.6)*np.sin(np.pi*tt/dur)
    add(fx,t0,lp(x,8)*.05*g)
creak(a3-0.1,1.1,1);creak(tGet,0.7,0.7)
# footsteps
def step(tk_,g):n=int(.08*sr);addS(tk_,lp(rng.standard_normal(n),4)*env(n,.002,.02),g*0.18,rng.uniform(-.3,.3))
for q in np.arange(tGet+0.3,tGet+3.0,0.33): step(q,0.8)
for q in np.arange(a9,a9+2.4,0.5): step(q,0.5)
# item pickups a6
for w in ('water','food','radio','keys'):
    n=int(.2*sr);add(fx,wT('a6',w),lp(rng.standard_normal(n),3)*env(n,.005,.05)*.22)
# short radio static burst (<3s) on 'radio'
tr=wT('a6','radio');n=int(1.6*sr);tt=np.arange(n)/sr;add(fx,tr,rng.standard_normal(n)*np.sin(np.pi*tt/1.6)**2*(0.6+0.4*(np.sin(2*np.pi*7*tt)>0))*.03)
# keys jingle
tkk=wT('a6','keys');n=int(.5*sr);tt=np.arange(n)/sr
for d in (0,.07,.15,.22):add(fx,tkk+d,sum(np.sin(2*np.pi*f*tt)*a for f,a in ((3200,1),(4700,.6),(6100,.4)))*env(n,.001,.05)*.05)
# brother's breathing (raspy) during a6-a8
for q in np.arange(wT('a6','man'),a9,2.6):
    n=int(1.1*sr);tt=np.arange(n)/sr;add(fx,q,lp(rng.standard_normal(n),12)*np.sin(np.pi*tt/1.1)**2*.35)
# heartbeat a7-a8
for q in np.arange(a7,tOpen,0.78):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,q+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
# stinger when he opens his eyes + a short groan
n=int(2.2*sr);tt=np.arange(n)/sr;add(fx,tOpen-0.03,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.8)*.22,8))
n=int(1.4*sr);tt=np.arange(n)/sr;add(fx,tOpen+0.5,verb(np.sin(2*np.pi*(110-25*tt)*tt+3*np.sin(2*np.pi*22*tt))*np.sin(np.pi*tt/1.4)**2*.06,0.6))
# distant groans of the returning crowd (outside), more toward the end
for k in range(26):
    tk_=rng.random()*(D-2);n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170);g=0.5+0.9*(tk_/D)
    addS(tk_,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.035*g,1.2),1,rng.uniform(-.8,.8))
# hands on the glass (a9-a10)
for k in range(10):
    tk_=a9+rng.random()*(END('a10')-a9);n=int(.15*sr);addS(tk_,verb(lp(rng.standard_normal(n),10)*env(n,.002,.04),0.7),0.12,rng.uniform(-.6,.6))
for w in ('leave','or'):
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
