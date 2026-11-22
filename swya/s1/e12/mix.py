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

A_=[0]+[C['a%d'%i]['start'] for i in range(1,12)];a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11=A_[1:];E11=END('a11')
fxL=np.zeros(N);fxR=np.zeros(N)
def addS(t0,x,g=1,pan=0.0):add(fxL,t0,x,g*(1-pan));add(fxR,t0,x,g*(1+pan))
camp=wT('a6','medic')-0.25
# --- music A: tense pulse until the barrier goes up
bpm=84;beat=60/bpm
notes=[36,36,39,36,41,36,39,34]
tense_end=wT('a5','barrier')
for k,tb in enumerate(np.arange(0,tense_end,beat/2)):
    m=notes[k%len(notes)];f=440*2**((m-69)/12);n=int(beat/2*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f*tt)+0.5*np.sign(np.sin(2*np.pi*f*tt))*0.3)*env(n,0.004,0.12);add(mus,tb,lp(x,6),0.5)
# --- music B: warm soft chords (piano-like plucks) after the barrier, dark again for the twist
chords=[[48,52,55,60],[45,48,52,57],[41,45,48,53],[43,47,50,55]]
cb=60/70*2
for k,tb in enumerate(np.arange(tense_end,a9,cb)):
    for j,m in enumerate(chords[k%4]):
        f=440*2**((m-69)/12);n=int(cb*1.5*sr);tt=np.arange(n)/sr
        x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*env(n,0.01,0.9);add(mus,tb+j*0.12,x,0.22)
for k,tb in enumerate(np.arange(a9,a10,beat)):
    f=440*2**((34-69)/12);n=int(beat*sr);tt=np.arange(n)/sr;add(mus,tb,lp(np.sign(np.sin(2*np.pi*f*tt))*env(n,0.01,0.35),10),0.35)
for k,tb in enumerate(np.arange(a10,D,cb)):
    for j,m in enumerate(chords[k%4]):
        f=440*2**((m-69)/12);n=int(cb*1.5*sr);tt=np.arange(n)/sr
        x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*env(n,0.01,0.9);add(mus,tb+j*0.12,x,0.22)
padT=sum(np.sin(2*np.pi*f*t+p) for f,p in ((65.4,0),(77.8,1),(98,2),(116.5,.5)))*0.25*(0.7+0.3*np.sin(2*np.pi*0.05*t))
padW=sum(np.sin(2*np.pi*f*t+p) for f,p in ((65.4,0),(82.4,1),(98,2),(130.8,.5)))*0.2
wk=np.clip((t-tense_end)/1.5,0,1)*(1-np.clip((t-a9)/0.5,0,1)*np.clip((a10+0.5-t)/0.5,0,1))
mus+=padT*(1-wk)+padW*wk
lvl=np.full(N,0.5)
def seg(a,b,v):lvl[int(a*sr):int(b*sr)]=v
seg(0,a2,0.4);seg(a2,a3,0.45);seg(a3,a4,0.28);seg(a4,a5,0.45);seg(a5,a6,0.3);seg(a6,a8,0.55);seg(a8,a9,0.5);seg(a9,a10,0.4);seg(a10,a11,0.5);seg(a11,D,0.65)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def thud(tt0,g=1,f0=90):
    n=int(.35*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f0*tt)*1.2+lp(rng.standard_normal(n),12)*2.5)*env(n,.001,.06)
    gl=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((820,1),(1900,.5),(3300,.3)))*env(n,.001,.05)*.3
    add(fx,tt0,verb(x*.6+gl,0.5),0.35*g)
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.05
# river wind on the bridge, then quieter camp air
wind=lp(rng.standard_normal(N),60)*6*(0.7+0.3*np.sin(2*np.pi*0.13*t));fx+=wind*0.05*np.where(t<camp,1.0,0.45)
def boom(t0,g=.16,d=2.0):
    n=int(d*sr);tt=np.arange(n)/sr;add(fx,t0,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*g,8))
boom(0.2,.15)
def clack(t0,g=.25):
    n=int(.15*sr);tt=np.arange(n)/sr;add(fx,t0,(sum(np.sin(2*np.pi*f*tt)*a for f,a in ((1800,1),(3100,.6),(4700,.3)))*env(n,.001,.02))*g)
clack(0.35)
# kid coughs at the start
for k in np.arange(0.2,a3,2*np.pi/6):
    n=int(.22*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);add(fx,k+np.pi/12,(lp(nz,3)-lp(nz,25))*env(n,.004,.06)*.4)
# heartbeat in tense whisper parts
for (x0,x1,g) in ((a1,a2,0.8),(a3,a4,0.6),(a5,wT('a5','lowers'),0.9)):
    for k in np.arange(x0,x1,0.75):
        for d,gg in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*gg*g)
# soldier footsteps
for k in np.arange(wT('a5','checks')-0.2,wT('a5','checks')+0.6,0.4):
    n=int(.1*sr);add(fx,k,lp(rng.standard_normal(n),8)*env(n,.002,.025)*.25)
clack(wT('a5','lowers')+0.3,.2)
# barrier going up: creak + clunk
tb=wT('a5','barrier');n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,tb,np.sin(2*np.pi*(180+60*tt)*tt+2*np.sin(2*np.pi*7*tt))*np.sin(np.pi*tt/1.2)*.035);thud(tb+1.2,0.8,80)
# walking
for k in np.arange(a6-0.1,camp,0.32):
    n=int(.1*sr);add(fx,k,lp(rng.standard_normal(n),8)*env(n,.002,.025)*.18)
# fire crackle in the camp (short random pops, no constant tone)
for k in range(140):
    tk=camp+rng.random()*(D-camp);n=int(.04*sr);add(fx,tk,lp(rng.standard_normal(n),2)*env(n,.001,.008)*rng.uniform(.05,.18))
fx+=lp(rng.standard_normal(N),20)*0.8*0.03*(t>camp)*(t<a9)
# inhaler puffs
for w in ('breath','two'):
    n=int(.45*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);add(fx,wT('a6',w)-0.35,(nz-lp(nz,6))*env(n,.01,.12)*.12)
n=int(.45*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);add(fx,a10+0.2,(nz-lp(nz,6))*env(n,.01,.12)*.1)
# twist: low boom on 'eyes', distant groans in the camp (short)
boom(wT('a9','eyes'),.18,2.5);boom(wT('a8','one'),.14)
for k in range(5):
    tk=a9+rng.random()*(a10-a9);n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,150)
    addS(tk,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.02,1.2),1,rng.uniform(-.8,.8))
# end card: soft swell
n=int(4*sr);tt=np.arange(n)/sr;add(fx,E11,lp(rng.standard_normal(n),60)*np.sin(np.pi*tt/4)**2*2.0)
# --- voice + mix
w=wave.open('voice.wav');v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(.2*sr))/(.2*sr),'same');duck=1-0.45*np.clip(e/0.04,0,1)
base=v*1.0+mus*0.22*duck+fx*0.75
L=base+fxL*0.75*duck**0.5;Rr=base+fxR*0.75*duck**0.5
m=max(1,max(np.abs(L).max(),np.abs(Rr).max())/0.97);L/=m;Rr/=m
st=np.stack([L,Rr],1)
wo=wave.open('mix_raw.wav','wb');wo.setnchannels(2);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes((st*32767).astype(np.int16).tobytes());wo.close()
import subprocess;subprocess.run(['ffmpeg','-v','error','-y','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mix.wav'],check=True);print('ok')
