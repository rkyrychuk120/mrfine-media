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
seg(0,a2,0.45);seg(a2,a3,0.45);seg(a3,a4,0.28);seg(a4,a5,0.5);seg(a5,a6,0.55);seg(a6,a7,0.25);seg(a7,a8,0.3);seg(a8,a9,0.5);seg(a9,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def thud(tt0,g=1,f0=90):
    n=int(.35*sr);tt=np.arange(n)/sr
    x=(np.sin(2*np.pi*f0*tt)*1.2+lp(rng.standard_normal(n),12)*2.5)*env(n,.001,.06)
    gl=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((820,1),(1900,.5),(3300,.3)))*env(n,.001,.05)*.3
    add(fx,tt0,verb(x*.6+gl,0.5),0.35*g)
for buf,seed in ((fxL,3),(fxR,4)):
    r=np.random.default_rng(seed);buf+=lp(r.standard_normal(N),120)*4*0.05
# door click + creak
tc=wT('a1','click');thud(tc,0.7,160)
n=int(.8*sr);tt=np.arange(n)/sr;add(fx,tc+0.1,np.sin(2*np.pi*(260+90*tt)*tt+2*np.sin(2*np.pi*9*tt))*np.sin(np.pi*tt/.8)*.04)
for k in np.arange(tc+0.7,tc+2.0,0.42):
    n=int(.12*sr);add(fx,k,lp(rng.standard_normal(n),10)*env(n,.002,.03)*.35)
def radio(t0,d=1.8,g=1):
    n=int(d*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);bp=lp(nz,2)-lp(nz,12)
    syl=(0.5+0.5*np.sign(np.sin(2*np.pi*3.3*tt+np.sin(2*np.pi*.7*tt)*3)))
    v=np.sin(2*np.pi*(380+60*np.sin(2*np.pi*5*tt))*tt)*syl*.4
    add(fx,t0,(bp*.5+v*.25)*np.sin(np.pi*tt/d)**.5*0.10*g)
radio(a2+0.4,2.0);radio(a4+1.0,1.6,0.8)
# whisper section: soft heartbeat during partner story
for k in np.arange(wT('a3','partner'),a4,0.85):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.6)
# van drive a5
tth=wT('a5','there')+0.6
ee=np.clip((t-a5)/0.4,0,1)*np.clip((tth+0.8-t)/0.8,0,1)
eng=lp(np.sign(np.sin(2*np.pi*(30+8*np.clip((t-a5)/2,0,1))*t))*0.5+lp(rng.standard_normal(N),30)*2,8);fx+=eng*0.05*ee
n=int(.4*sr);add(fx,tth-0.3,lp(rng.standard_normal(n),3)*np.sin(np.pi*np.arange(n)/n)*.04)
# river wind ambience at the bridge (noise, no tone)
wind=lp(rng.standard_normal(N),60)*6*(0.7+0.3*np.sin(2*np.pi*0.13*t));fx+=wind*0.05*np.clip((t-a5)/1.5,0,1)
# floodlights clunk
thud(wT('a5','lights')-0.1,0.9,70)
# heartbeat a6..a8
for k in np.arange(a6,a8,0.72):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
# soldier footsteps
for k in np.arange(wT('a6','checks'),wT('a6','kid')+1.4,0.45):
    n=int(.1*sr);add(fx,k,lp(rng.standard_normal(n),8)*env(n,.002,.025)*.25)
# kid coughs (match animation peaks)
tK=wT('a6','kid')
for i in range(40):
    k=tK+(np.pi/2+2*np.pi*i)/7-0.08
    if k>a8+2:g=0.4
    else:g=1
    if k>a9:break
    n=int(.22*sr);tt=np.arange(n)/sr;nz=rng.standard_normal(n);add(fx,k,(lp(nz,3)-lp(nz,25))*env(n,.004,.06)*.5*g)
# gun raise: metal clack
tr=wT('a7','raises')+0.35;n=int(.15*sr);tt=np.arange(n)/sr;add(fx,tr,(sum(np.sin(2*np.pi*f*tt)*a for f,a in ((1800,1),(3100,.6),(4700,.3)))*env(n,.001,.02))*.25)
add(fx,tr+0.12,(sum(np.sin(2*np.pi*f*tt)*a for f,a in ((1500,1),(2700,.6)))*env(n,.001,.02))*.2)
def boom(t0,g=.16,d=2.0):
    n=int(d*sr);tt=np.arange(n)/sr;add(fx,t0,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*g,8))
boom(wT('a7','that'),.15);boom(wT('a8','one'),.16)
# distant groans (short events)
for k in range(12):
    tk=rng.random()*D;n=int(1.3*sr);tt=np.arange(n)/sr;fq=rng.uniform(90,170)
    addS(tk,verb(np.sin(2*np.pi*(fq-20*tt)*tt+3*np.sin(2*np.pi*rng.uniform(15,30)*tt))*np.sin(np.pi*tt/1.3)**2*.022,1.2),1,rng.uniform(-.8,.8))
for w,nn in (('tell',0),('or',0)):
    n=int(.5*sr);add(fx,wT('a10',w,nn)-0.2,lp(rng.standard_normal(n),40)*np.sin(np.pi*np.arange(n)/n)**2*3)
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
