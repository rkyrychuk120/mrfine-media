import numpy as np, wave, json
from warp import old2new as W
sr=48000; tl=json.load(open('timeline.json')); D=tl['total']; N=int(D*sr)
mus=np.zeros(N); sfx=np.zeros(N)
rng=np.random.default_rng(1)
def add(buf,t,x,g=1.0):
    i=int(t*sr)
    if i>=N: return
    j=min(N,i+len(x)); buf[i:j]+=x[:j-i]*g
def env(n,a=0.005,r=0.2):
    t=np.arange(n)/sr; return np.minimum(1,t/a)*np.exp(-t/r)
bpm=96; beat=60/bpm
prog=[[60,64,67],[55,59,62],[57,60,64],[53,57,60]]
def note(m,dur,amp):
    n=int(dur*sr); t=np.arange(n)/sr; f=440*2**((m-69)/12)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t)+0.1*np.sin(6*np.pi*f*t))*env(n,0.004,0.35)*amp
t=0;bar=0
while t<D:
    ch=prog[bar%4]
    for b in range(4):
        tb=t+b*beat
        if b in (0,2): add(mus,tb,note(ch[0]-12,beat*0.95,0.35))
        arp=[ch[0],ch[1],ch[2],ch[1]]
        add(mus,tb,note(arp[b]+12,beat,0.18)); add(mus,tb+beat/2,note(ch[(b+1)%3]+12,beat/2,0.12))
        n=int(0.03*sr); add(mus,tb+beat/2,rng.standard_normal(n)*env(n,0.001,0.01)*0.05)
    t+=4*beat; bar+=1
lvl=np.ones(N)*0.9
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(W(29.3),W(38.4),0.45); seg(W(38.4),W(57.9),0.35); seg(W(57.9),W(59.4),0.0); seg(W(106.9),D,1.0)
k=int(0.25*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
def strike(t):
    n=int(0.35*sr); x=np.convolve(rng.standard_normal(n),np.ones(6)/6,'same')*env(n,0.01,0.08)*0.6; add(sfx,t,x)
    n2=int(0.5*sr); add(sfx,t+0.3,rng.standard_normal(n2)*env(n2,0.05,0.3)*0.15)
strike(W(7.62)); strike(W(9.47))
n=int(0.4*sr); add(sfx,W(9.0),np.convolve(rng.standard_normal(n),np.ones(30)/30,'same')*env(n,0.05,0.15)*0.8)
def whoosh(t,d,g):
    n=int(d*sr); x=np.convolve(rng.standard_normal(n),np.ones(40)/40,'same'); w=np.sin(np.pi*np.arange(n)/n)**2; add(sfx,t,x*w*g)
whoosh(W(14.0),0.8,0.8); whoosh(W(29.4),1.0,1.4); whoosh(W(22.5),0.6,0.7)
for tt in np.arange(W(29.6),W(35.6),0.07):
    if rng.random()<0.5: n=int(0.01*sr); add(sfx,tt+rng.random()*0.05,rng.standard_normal(n)*env(n,0.0005,0.004)*0.25)
for tt in np.arange(W(34.4),W(38.35),0.5):
    n=int(0.22*sr); t_=np.arange(n)/sr; add(sfx,tt,np.sign(np.sin(2*np.pi*3150*t_))*0.12*np.minimum(1,t_/0.005)*np.minimum(1,(0.22-t_)/0.005))
n=int(0.05*sr); add(sfx,W(38.38),rng.standard_normal(n)*env(n,0.001,0.01)*0.6)
n=int(0.12*sr); t_=np.arange(n)/sr; add(sfx,W(38.40),np.sin(2*np.pi*180*t_)*env(n,0.002,0.05)*0.5)
for tt in (40.65,56.95): add(sfx,W(tt),np.sin(2*np.pi*1200*np.arange(int(0.04*sr))/sr)*0.15)
n=int(1.5*sr); t_=np.arange(n)/sr; f=np.linspace(1800,300,n)
add(sfx,W(57.9),(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*t_/1.5))
for tt in [42.5,44.1,44.8,45.7,47.2,52.6,59.5,66.0,67.6,69.0,70.9,71.85,73.95,76.6,78.4,79.9,89.5,91.1,96.35,99.35,102.26,104.98,108.4]:
    n=int(0.08*sr); f=np.linspace(500,900,n); add(sfx,W(tt),np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.03)*0.18)
n=int(0.6*sr); t_=np.arange(n)/sr; add(sfx,W(94.8),(np.sin(2*np.pi*1320*t_)+0.5*np.sin(2*np.pi*1980*t_))*env(n,0.002,0.25)*0.12)
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
out=v+mus*0.11*duck+sfx*0.7
out/=max(1,np.abs(out).max()/0.95)
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
