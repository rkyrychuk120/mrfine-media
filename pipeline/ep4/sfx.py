import numpy as np, wave, json
sr=48000; tl=json.load(open('timeline.json')); D=tl['total']; N=int(D*sr); PH=tl['ph']
C={c['name']:c for c in tl['clips']}
P=lambda k:PH[k][0]
mus=np.zeros(N); sfx=np.zeros(N); rng=np.random.default_rng(4)
def add(buf,t,x,g=1.0):
    i=int(t*sr)
    if i>=N or i<0: return
    j=min(N,i+len(x)); buf[i:j]+=x[:j-i]*g
def env(n,a=0.005,r=0.2):
    t=np.arange(n)/sr; return np.minimum(1,t/a)*np.exp(-t/r)
def note(m,dur,amp,bright=1.0):
    n=int(dur*sr); t=np.arange(n)/sr; f=440*2**((m-69)/12)
    return (np.sin(2*np.pi*f*t)+0.3*bright*np.sin(4*np.pi*f*t)+0.1*bright*np.sin(6*np.pi*f*t))*env(n,0.004,0.35)*amp
POP=14.75; pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.1
tip=C['m3']['start']; end=C['m4']['start']-0.2
# section 1 (0..POP): tense minor pulse, getting faster/louder; 2 (pause): soft pad; 3 (after rewind): light major bounce; tip: calm pad; end: bright chord
def tense(a,b):
    t=a;i=0
    while t<b:
        k=(t-a)/(b-a); bt=0.42-0.16*k
        m=[45,45,48,44][(i//4)%4]
        add(mus,t,note(m,bt*0.9,0.4,0.6)); 
        if i%2==0: add(mus,t,note(m+12+[0,3,7,3][(i//2)%4],bt,0.12))
        n=int(0.02*sr); add(mus,t,rng.standard_normal(n)*env(n,0.001,0.006)*0.08)
        t+=bt;i+=1
def pad(a,b,ch,amp):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=sum(np.sin(2*np.pi*440*2**((m-69)/12)*t) for m in ch)/len(ch)
    w=np.minimum(1,t/0.6)*np.minimum(1,(n/sr-t)/0.6); add(mus,a,x*w*amp)
def bounce(a,b):
    beat=60/112; t=a; bar=0; prog=[[60,64,67],[65,69,72],[67,71,74],[60,64,67]]
    while t<b:
        ch=prog[bar%4]
        for k in range(4):
            tb=t+k*beat
            if tb>=b: break
            if k in (0,2): add(mus,tb,note(ch[0]-12,beat*0.9,0.32))
            add(mus,tb+beat/2,note(ch[(k+1)%3]+12,beat/2,0.14))
        t+=4*beat; bar+=1
tense(0,POP); pad(pause+0.2,rwS,[57,60,64],0.18); bounce(rwE,tip); pad(tip,end,[60,64,67,71],0.16)
for m,a in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: add(mus,end+0.4+a,note(m,1.4,0.18))
lvl=np.ones(N); 
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(POP-0.05,POP+1.0,0.0); seg(rwS,rwE,0.2)
k=int(0.1*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
# --- SFX
def hum(a,b,g):
    n=int((b-a)*sr); t=np.arange(n)/sr; x=(np.sin(2*np.pi*120*t)*0.5+np.sin(2*np.pi*240*t)*0.2)*np.minimum(1,t/0.1)*np.minimum(1,(n/sr-t)/0.05); add(sfx,a,x*g)
def ding(t,g=0.35):
    n=int(1.2*sr); tt=np.arange(n)/sr; add(sfx,t,(np.sin(2*np.pi*1568*tt)+0.5*np.sin(2*np.pi*3136*tt))*env(n,0.002,0.4)*g)
def whoosh(t,d,g):
    n=int(d*sr); x=np.convolve(rng.standard_normal(n),np.ones(40)/40,'same'); w=np.sin(np.pi*np.arange(n)/n)**2; add(sfx,t,x*w*g)
def boom(t,g):
    n=int(0.6*sr); tt=np.arange(n)/sr; f=np.linspace(140,40,n)
    add(sfx,t,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.9+rng.standard_normal(n)*0.5)*env(n,0.001,0.12)*g)
def tick(t,g=0.12):
    n=int(0.03*sr); add(sfx,t,np.sin(2*np.pi*2000*np.arange(n)/sr)*env(n,0.001,0.01)*g)
def blip(t):
    n=int(0.08*sr); f=np.linspace(500,900,n); add(sfx,t,np.sin(2*np.pi*np.cumsum(f)/sr)*env(n,0.002,0.03)*0.16)
hum(0,P('n2.3'),0.07); ding(P('n2.3'))
for tt in np.arange(0.3,P('n2.3'),0.5): tick(tt,0.06)
for tt in np.arange(P('n2.3')+0.4,POP,0.5): tick(tt,0.14)   # "out for" heartbeat ticks
n=int(0.15*sr); add(sfx,P('n2.3')+0.25,rng.standard_normal(n)*env(n,0.002,0.03)*0.3)  # door clack
boom(POP,1.1); whoosh(POP,0.4,0.6)
for tt in np.arange(POP+0.1,POP+0.6,0.07): n=int(0.05*sr); add(sfx,tt,np.convolve(rng.standard_normal(n),np.ones(6)/6,'same')*env(n,0.001,0.02)*0.25)  # splats
# pause click + rewind
n=int(0.05*sr); add(sfx,pause,rng.standard_normal(n)*env(n,0.001,0.01)*0.6)
n=int(1.1*sr); tt=np.arange(n)/sr; f=np.linspace(1800,300,n)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.1))
# crack / poke / lid / beep
n=int(0.06*sr); add(sfx,P('n4.0')+1.0,rng.standard_normal(n)*env(n,0.0005,0.012)*0.7)
for k in ['n4.1','n4.2']: blip(P(k))
ding(P('n4.3')+0.5,0.15)
for k in ['m1.1','m1.2','m1.3','m3.0','m3.1','h3.1']: blip(P(k))
w=wave.open('voice.wav'); v=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
v=np.pad(v,(0,max(0,N-len(v))))[:N]
e=np.convolve(np.abs(v),np.ones(int(0.15*sr))/(0.15*sr),'same'); duck=1-0.55*np.clip(e/0.05,0,1)
out=v+mus*0.12*duck+sfx*0.7
out/=max(1,np.abs(out).max()/0.95)
wo=wave.open('mix.wav','wb'); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((out*32767).astype(np.int16).tobytes()); wo.close()
print('ok',D)
