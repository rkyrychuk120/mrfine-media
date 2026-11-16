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
seg(0,a2,0.55);seg(a2,a3,0.45);seg(a3,a5,0.35);seg(a5,a6,0.55);seg(a6,a7,0.12);seg(a7,a8,0.4);seg(a8,a9,0.3);seg(a9,a10,0.35);seg(a10,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)






tCrash=wT('a1','crashes');tSide=wT('a5','sidewalk');tHands=wT('a5','hands');tBreath=wT('a6','breathing');tPull=wT('a6','pulling');tBroke=wT('a8','broke');tSafe=wT('a7','safe');tCheck=wT('a8','soldiers')
# engine rumble: filtered noise with slow modulation (not a tone), louder on exterior, fades as van stops at end
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);eng=lp(r.standard_normal(N),60)*3.0*(0.7+0.3*np.sin(2*np.pi*0.37*t+seed))
    g=np.where(t<0.3,0,0.11)*np.clip((D-t-4)/3,0.25,1);buf+=eng*g
    buf+=lp(r.standard_normal(N),8)*0.012  # road hiss / wind
# rev at start
n=int(2.5*sr);tt=np.arange(n)/sr;add(fx,0.25,lp(rng.standard_normal(n),30)*np.minimum(1,tt/0.3)*np.exp(-tt/1.6)*1.2)
# gate crash
n=int(1.2*sr);tt=np.arange(n)/sr
crash=(np.sin(2*np.pi*55*tt)*1.5+lp(rng.standard_normal(n),3)*2.5)*env(n,.001,.18)+sum(np.sin(2*np.pi*f*tt)*a for f,a in ((520,1),(910,.7),(1630,.5),(2870,.3)))*env(n,.001,.5)*.6
add(fx,tCrash-0.02,verb(crash,1.0),0.4)
for d in (0.25,0.45,0.7):n=int(.3*sr);add(fx,tCrash+d,sum(np.sin(2*np.pi*f*np.arange(n)/sr) for f in (1900,2700))*env(n,.001,.06)*.08)
# bumps on the sidewalk + zombie hits (thuds)
for q in np.arange(tSide-0.5,C['a6']['start'],0.55+0.0):
    n=int(.25*sr);addS(q+rng.uniform(0,.2),lp(rng.standard_normal(n),12)*env(n,.002,.06)*3,0.35,rng.uniform(-.5,.5))
# hands slapping glass
for q in np.arange(tHands-0.1,C['a6']['start']-0.3,0.32):
    n=int(.12*sr);addS(q+rng.uniform(0,.08),verb(lp(rng.standard_normal(n),5)*env(n,.001,.025),0.4),0.45,-0.6)
# groans outside during streets
for k in range(18):
    tk_=rng.uniform(C['a2']['start'],C['a7']['start']);n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170)
    addS(tk_,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.04,1.0),1,rng.uniform(-.8,.8))
# brother's wet breathing a6..end of a8
for q in np.arange(tBreath-0.3,C['a9']['start'],2.1):
    n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,q,lp(rng.standard_normal(n),10)*np.sin(np.pi*tt/1.2)**2*.45)
# tape stretching (creak) and snap
n=int(1.5*sr);tt=np.arange(n)/sr;add(fx,tPull,lp(rng.standard_normal(n),3)*(0.5+0.5*np.sin(2*np.pi*13*tt))*np.sin(np.pi*tt/1.5)*.08)
n=int(.4*sr);tt=np.arange(n)/sr;add(fx,tBroke-0.02,(lp(rng.standard_normal(n),2)*1.5)*env(n,.001,.05)*.5)
# heartbeat in a8 after 'one problem'
for q in np.arange(wT('a8','one'),C['a9']['start'],0.78):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,q+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
# stinger on broke
n=int(2.2*sr);tt=np.arange(n)/sr;add(fx,tBroke-0.03,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.8)*.22,8))
# short soldier radio chirp at checkpoint (<2s)
for q in (tSafe+0.2,tCheck):
    n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,q,rng.standard_normal(n)*np.sin(np.pi*tt/1.2)**2*(np.sin(2*np.pi*9*tt)>0)*.02)
    n2=int(.12*sr);add(fx,q,np.sin(2*np.pi*1800*np.arange(n2)/sr)*env(n2,.002,.04)*.05)
for w in ('stop','or'):
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
