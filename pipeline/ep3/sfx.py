import numpy as np, wave, json
W=lambda t:t
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
seg(19.3,40.1,0.45); seg(40.1,58.3,0.35); seg(58.3,59.8,0.0); seg(106.5,D,1.0)
k=int(0.25*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
def whoosh(t,d,g):
    n=int(d*sr); x=np.convolve(rng.standard_normal(n),np.ones(40)/40,'same'); w=np.sin(np.pi*np.arange(n)/n)**2; add(sfx,t,x*w*g)
# wind ambience on the pond
n=int(40*sr); wind=np.convolve(rng.standard_normal(n),np.ones(200)/200,'same')*(0.6+0.4*np.sin(np.arange(n)/sr*0.7)); add(sfx,0,wind*1.2)
def crack(t,g=1.0):
    for i in range(5):
        n=int(0.06*sr); add(sfx,t+i*0.045+rng.random()*0.02,rng.standard_normal(n)*env(n,0.0005,0.012)*0.9*g)
    n=int(0.25*sr); t_=np.arange(n)/sr; add(sfx,t,np.sin(2*np.pi*90*t_)*env(n,0.002,0.08)*0.6*g)
def splash(t,g=1.0,d=0.8):
    n=int(d*sr); x=np.convolve(rng.standard_normal(n),np.ones(5)/5,'same')*env(n,0.005,d/3); add(sfx,t,x*0.7*g)
for tt in (11.2,12.0): crack(tt,0.25)
for tt in (13.45,15.15,18.0):
    n=int(0.12*sr); add(sfx,tt,np.convolve(rng.standard_normal(n),np.ones(20)/20,'same')*env(n,0.005,0.04)*0.8)
crack(18.1,0.5); crack(19.4,1.3); splash(19.5,1.3,1.0); whoosh(19.3,0.6,0.8)
for tt in np.arange(26.0,27.4,0.25): splash(tt,0.5,0.3)
crack(29.4,1.0); splash(29.5,0.8,0.7)
for tt in np.arange(22.5,25.5,0.9):
    n=int(0.35*sr); add(sfx,tt,np.convolve(rng.standard_normal(n),np.ones(60)/60,'same')*np.sin(np.pi*np.arange(n)/n)*0.5)
for tt in (33.3,36.0):
    n=int(0.05*sr); add(sfx,tt,np.sin(2*np.pi*1500*np.arange(n)/sr)*env(n,0.001,0.03)*0.3)
for tt in np.arange(33.3,40.1,1.0):
    n=int(0.03*sr); add(sfx,tt,np.sin(2*np.pi*900*np.arange(n)/sr)*env(n,0.001,0.01)*0.15)
n=int(0.05*sr); add(sfx,40.12,rng.standard_normal(n)*env(n,0.001,0.01)*0.6)
n=int(0.12*sr); t_=np.arange(n)/sr; add(sfx,40.14,np.sin(2*np.pi*180*t_)*env(n,0.002,0.05)*0.5)
add(sfx,57.5,np.sin(2*np.pi*1200*np.arange(int(0.04*sr))/sr)*0.15)
n=int(1.5*sr); t_=np.arange(n)/sr; f=np.linspace(1800,300,n)
add(sfx,58.3,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*t_/1.5))
for tt in [11.05,13.41,14.33,15.11,16.34,17.96,43.9,45.35,48.1,50.4,51.25,52.1,53.3,55.34,60.06,61.08,62.05,64.31,65.63,68.6,70.6,72.65,74.8,77.19,79.16,81.58,92.8,94.45,98.08,100.15,102.5,103.6]:
    n=int(0.08*sr); f=np.linspace(500,900,n); add(sfx,tt,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.03)*0.18)
for tt in np.arange(77.3,78.6,0.4): whoosh(tt,0.35,0.25)
n=int(0.6*sr); t_=np.arange(n)/sr; add(sfx,96.4,(np.sin(2*np.pi*1320*t_)+0.5*np.sin(2*np.pi*1980*t_))*env(n,0.002,0.25)*0.12)
n=int(0.8*sr); t_=np.arange(n)/sr; add(sfx,108.5,(np.sin(2*np.pi*1046*t_)+0.6*np.sin(2*np.pi*1568*t_))*env(n,0.002,0.35)*0.12)
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
out=v+mus*0.11*duck+sfx*0.7
out/=max(1,np.abs(out).max()/0.95)
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
