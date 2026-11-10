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
def addS(t0,x,g=1,pan=0.0):add(fxL,t0,x,g*(1-pan)/1);add(fxR,t0,x,g*(1+pan)/1)
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
seg(0,a2,0.75);seg(a2,a3,0.85);seg(a3,a5,0.5);seg(a5,a6,0.3);seg(a6,a7,0.25);seg(a7,a8,0.45);seg(a8,a9,0.15);seg(a9,a10,0.4);seg(a10,D,0.6)
lvl=np.convolve(lvl,np.ones(int(.25*sr))/(.25*sr),'same');mus*=lvl
def door_hit(tt0,g=1):
    n=int(.6*sr);tt=np.arange(n)/sr
    thud=(np.sin(2*np.pi*58*tt)*1.4+lp(rng.standard_normal(n),20)*4)*env(n,.001,.12)
    metal=sum(np.sin(2*np.pi*f*tt)*a for f,a in ((431,1),(1187,.6),(2273,.4),(3519,.25)))*env(n,.001,.35)*.5
    add(fx,tt0-.02,verb(thud*0.5+metal*0.6,0.8),0.28*g)
    n2=int(.8*sr);tt2=np.arange(n2)/sr;add(fx,tt0,sum(np.sin(2*np.pi*f*(1+.01*np.sin(2*np.pi*6*tt2))*tt2) for f in (1661,1760,1864))*env(n2,.005,.3)*.025*g)

# cold open: two hits then door burst
for b in (0.55,1.05): door_hit(b,0.9)
tth=wT('a1','through');door_hit(tth,1.3)
n=int(1.2*sr);tt=np.arange(n)/sr;add(fx,tth,verb(lp(rng.standard_normal(n),3)*env(n,.002,.25)*0.5,1.0),0.6)  # crash/splinter
n=int(.9*sr);tt=np.arange(n)/sr;add(fx,tth+0.15,np.sin(2*np.pi*(180-60*tt)*tt+4*np.sin(2*np.pi*31*tt))*env(n,.02,.4)*.35)  # growl
trun=wT('a1','run');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,trun+0.25,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((36.7,1),(55,.8),(73.4,.5)))*env(n,.01,.7)*.2,8))
# --- tunnel ambience (stereo, decorrelated) from a2
amb=(t>=a2-0.1)
for buf,seed in ((fxL,1),(fxR,2)):
    r=np.random.default_rng(seed);rum=lp(r.standard_normal(N),300)*9+lp(r.standard_normal(N),60)*1.2
    buf+=rum*0.07*amb*(1+0.3*np.sin(2*np.pi*0.07*t+seed))
# electrical hum near third rail, stronger in a5
hum=(np.sin(2*np.pi*50*t)+.5*np.sin(2*np.pi*100*t)+.25*np.sin(2*np.pi*150*t))
hl=np.where((t>=a5)&(t<a6),0.05,0.008)*amb;hl=np.convolve(hl,np.ones(int(.3*sr))/(.3*sr),'same')
fx+=hum*hl
# drips with reverb, random pan
for k in np.arange(a2+0.3,D-1,0.9):
    tk=k+rng.random()*0.6;n=int(.12*sr);tt=np.arange(n)/sr;x=verb(np.sin(2*np.pi*(1500-5000*tt)*tt)*env(n,.001,.025),0.9)
    addS(tk,x,0.25,rng.uniform(-.8,.8))
# distant metal screeches
for tk in (a3+3,a4+7,a7+2,a9+4):
    n=int(1.6*sr);tt=np.arange(n)/sr;x=verb(np.sin(2*np.pi*(900+200*np.sin(tt*3))*tt)*np.sin(np.pi*tt/1.6)**2*.05,1.6);addS(tk,x,0.6,rng.uniform(-.7,.7))
# footsteps on gravel: running in a2, walking after
def step(tk,g):n=int(.09*sr);x=lp(rng.standard_normal(n),3)*env(n,.002,.025)+lp(rng.standard_normal(n),12)*env(n,.001,.02)*2;addS(tk,x,g*0.22,rng.uniform(-.4,.4))
for tk in np.arange(a2,a3,np.pi/9): step(tk,1.0);step(tk+0.12,0.6)
for tk in np.arange(a3,a10+1,np.pi/3.6):
    if not(a9<=tk<a10): step(tk,0.55);step(tk+0.2,0.35)
# running breaths
for tk in np.arange(a2+0.2,a3,0.7):
    n=int(.35*sr);addS(tk,lp(rng.standard_normal(n),5)*np.sin(np.pi*np.arange(n)/n)*.06,1,0.1)
# lighter click+flame
tlt=a3+0.45;n=int(.05*sr);addS(tlt,lp(rng.standard_normal(n),2)*env(n,.001,.01)*.6,1,0.3)
n=int(1.5*sr);addS(tlt+0.05,lp(rng.standard_normal(n),20)*env(n,.05,.6)*.3,1,0.3)
# phone vibrate + pings for messages
tsg=wT('a6','signal');n=int(.5*sr);tt=np.arange(n)/sr;add(fx,tsg-0.2,np.sign(np.sin(2*np.pi*170*tt))*(np.sin(2*np.pi*12*tt)>0)*.08)
for w in ('where','dont','theyre'):
    tk=wT('a6',w)-0.15;n=int(.22*sr);add(fx,tk,(np.sin(2*np.pi*1318*np.arange(n)/sr)+np.sin(2*np.pi*1975*np.arange(n)/sr)*.5)*env(n,.002,.06)*.18)
tf=wT('a6','full');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tf,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.16,8))
# on-paper ticks + one problem hit
for w,nth in (('four',0),('twenty',0),('four',1)):
    n=int(.08*sr);add(fx,wT('a7',w,nth),np.sin(2*np.pi*2093*np.arange(n)/sr)*env(n,.001,.03)*.18)
tp=wT('a7','one');n=int(2.0*sr);tt=np.arange(n)/sr;add(fx,tp,lp(sum(np.sign(np.sin(2*np.pi*f*tt))*a for f,a in ((32.7,1),(49,.7)))*env(n,.01,.7)*.18,8))
# battery drop beeps + flicker buzz + heartbeat + footsteps behind
for k in range(3):
    n=int(.12*sr);add(fx,a8+0.2+k*0.35,np.sin(2*np.pi*(880-k*120)*np.arange(n)/sr)*env(n,.002,.05)*.16)
fl=((t>a8+0.3)&(t<a9))*(np.sin(2*np.pi*37/2/np.pi*t*2*np.pi/37*37)>0.2);fx+=np.sign(np.sin(2*np.pi*120*t))*0.008*((t>a8+0.3)&(t<a9))
for k in np.arange(a8,a9,0.8):
    for d,g in ((0,1),(.17,.7)):n=int(.16*sr);add(fx,k+d,np.sin(2*np.pi*48*np.arange(n)/sr)*env(n,.003,.05)*g*0.9)
tsth=wT('a8','something')
for i,tk in enumerate(np.arange(tsth-0.6,a9,0.62)):
    n=int(.1*sr);x=verb(lp(rng.standard_normal(n),6)*env(n,.002,.03),1.2);addS(tk,x,0.10+0.03*i,-0.2)
n=int(1.2*sr);tt=np.arange(n)/sr;addS(tsth+0.8,verb(np.sin(2*np.pi*(140-40*tt)*tt+3*np.sin(2*np.pi*27*tt))*env(n,.05,.5)*.12,1.5),1,-0.3)
# service door: metal creak
n=int(1.5*sr);tt=np.arange(n)/sr;add(fx,wT('a9','service'),np.sin(2*np.pi*(220+70*tt)*tt+3*np.sin(2*np.pi*19*tt))*np.sin(np.pi*tt/1.5)*.06)
n=int(.3*sr);add(fx,wT('a9','lock'),lp(rng.standard_normal(n),4)*env(n,.001,.05)*.4)
# choice whooshes + end hit
for w in ('turn','or'):
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
