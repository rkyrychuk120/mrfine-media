# ===== ep17: dog + turkey bone. Music per scene: cozy folk pluck (Thanksgiving) -> 'aww' glide on the sad eyes -> sneaky pizzicato (trash)
# -> sad music box + whimpers (one hour later) -> sting + silence on the freeze -> thinking keys (pause) -> rewind sweep
# -> cozy folk again (right move) -> happy groove (good boy) -> comic minor plod + monitor beeps + printer + ka-ching (vet bill) -> calm tip -> chime
P_=P
n1b=P('n1.1'); n1c=P('n1.2'); h1=C['h1']['start']; h10=P('h1.0'); h11e=PE('h1.1')
n20=P('n2.0'); n20e=PE('n2.0'); n21=P('n2.1'); n22=P('n2.2'); n22e=PE('n2.2'); n23=P('n2.3'); n23e=PE('n2.3'); n24=P('n2.4')
DROP=h11e-0.1; CATCH=DROP+0.32; GULP=n20+0.35; TRASH=n21-0.15; HOUR=n23-0.3; FZ=PE('n2.4')+0.3
W0=TRASH; W1=TRASH+0.9; KNOCK=W1+0.15
pause=C['m1']['start']-0.15; rwE=C['n4']['start']-0.05; rwS=rwE-1.0
v1=P('m1.1'); v1e=PE('m1.1'); st=P('m1.2'); ste=PE('m1.2'); rw=P('m1.3')
a0=P('n4.0'); a1=P('n4.1'); a1e=PE('n4.1'); a2=P('n4.2'); a3=P('n4.3'); a4=P('n4.4'); a4e=PE('n4.4'); a5=P('n4.5'); a5e=PE('n4.5')
hS=C['h2']['start']; h21=P('h2.1'); CLOSE=a5+0.15; give=a4+(a4e-a4)*0.45; take=give+0.35
m2=C['m2']['start']; b1=P('m2.1'); b2=P('m2.2'); b2e=PE('m2.2'); tip=C['m3']['start']; end=C['m4']['start']-0.2
def folk(a,b,g=1.0,bpm=100):
    prog=[[55,59,62],[60,64,67],[57,60,64],[62,66,69]]; beat=60/bpm; t=a; i=0
    while t<b:
        ch=prog[(i//8)%4]
        if i%4==0: add(mus,t,note(ch[0]-12,beat*1.8,0.22*g,0.6))
        if i%4==2: add(mus,t,note(ch[0]-5,beat*1.2,0.12*g,0.6))
        pluck(t,ch[i%3]+12,0.13*g,0.45)
        if i%2==1: pluck(t,ch[(i+1)%3]+24,0.05*g,0.25)
        if i%8==7: n=int(0.03*sr); add(mus,t,rng.standard_normal(n)*env(n,0.001,0.012)*0.07*g)
        t+=beat/2; i+=1
def sneaky(a,b,g=1.0,bpm=126):
    seq=[45,None,48,None,50,None,48,51,45,None,48,None,52,51,50,None]; beat=60/bpm; t=a; i=0
    while t<b:
        m=seq[i%16]
        if m: pluck(t,m,0.24*g,0.22); pluck(t,m+12,0.06*g,0.15)
        if i%4==0: kick(t,0.25*g,70)
        t+=beat/2; i+=1
def sadbox(a,b,g=1.0):
    mel=[69,67,65,64,65,None,62,None,64,65,64,62,60,None,None,None]; beat=60/72; t=a; i=0
    while t<b:
        m=mel[i%16]
        if m: mbox(t,m,0.12*g,-0.3)
        if i%4==0: mbox(t,[50,46,48,45][(i//4)%4],0.09*g,-0.3)
        t+=beat/2; i+=1
def aww(t,g=0.12,f0=880,f1=620,d=0.7):
    n=int(d*sr); tt=np.arange(n)/sr; f=np.linspace(f0,f1,n)*(1+0.012*np.sin(2*np.pi*6*tt))
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.3*np.sin(4*np.pi*np.cumsum(f)/sr); add(mus,t,x*np.minimum(1,tt/0.08)*np.minimum(1,(d-tt)/0.25)*g)
def whimper(t,g=0.1,d=0.55):
    n=int(d*sr); tt=np.arange(n)/sr; f=980-380*(tt/d)+40*np.sin(2*np.pi*9*tt)
    x=np.sin(2*np.pi*np.cumsum(f)/sr)+0.25*np.sin(4*np.pi*np.cumsum(f)/sr)+np.convolve(rng.standard_normal(n),np.ones(6)/6,'same')*0.15
    add(sfx,t,x*np.sin(np.pi*tt/d)**1.5*g)
def chomp(t,g=0.2):
    n=int(0.07*sr); x=np.convolve(rng.standard_normal(n),np.ones(3)/3,'same')*env(n,0.001,0.02); add(sfx,t,x*g); add(sfx,t+0.02,note(50,0.08,0.3*g,0.2)[:int(0.06*sr)])
def crunch(a,b,g=0.18):
    t=a
    while t<b: chomp(t,g*(0.7+0.5*rng.random())); t+=0.13+rng.random()*0.06
def paws(a,b,g=0.08,stepd=0.2):
    t=a
    while t<b: tick(t,g); tick(t+0.05,g*0.7); t+=stepd
def snap(t,g=0.3):
    n=int(0.04*sr); add(sfx,t,rng.standard_normal(n)*env(n,0.0005,0.006)*g); clank(t+0.01,0.06)
def woof(t,g=0.18):
    n=int(0.16*sr); tt=np.arange(n)/sr; f=np.linspace(420,260,n)
    x=np.sign(np.sin(2*np.pi*np.cumsum(f)/sr))*0.4+np.convolve(rng.standard_normal(n),np.ones(10)/10,'same')*2
    x=np.convolve(x,np.ones(14)/14,'same'); add(sfx,t,x*np.minimum(1,tt/0.01)*np.exp(-tt/0.07)*g)
def printer(a,b,g=0.08):
    t=a
    while t<b: tick(t,g); n=int(0.03*sr); add(sfx,t+0.015,rng.standard_normal(n)*env(n,0.001,0.01)*g*0.6); t+=0.045
def kaching(t,g=0.2):
    for m_,o in [(84,0),(88,0.07),(91,0.14)]: add(sfx,t+o,note(m_,0.6,g,1.4))
    for k_ in range(6): n=int(0.03*sr); add(sfx,t+0.2+k_*0.05,np.sin(2*np.pi*(3000+rng.random()*1500)*np.arange(n)/sr)*env(n,0.001,0.02)*g*0.5)
def plod(a,b,g=1.0):
    seq=[45,None,40,None,45,None,40,None,44,None,40,None,45,47,48,None]; beat=60/92; t=a; i=0
    while t<b:
        m=seq[i%16]
        if m: add(mus,t,note(m,beat*0.5,0.24*g,1.1));
        if i%2==0: pluck(t+beat/2,[64,67,63,67][(i//4)%4],0.08*g,0.2)
        t+=beat/2; i+=1
# ---------------- MUSIC
folk(0.0,TRASH-0.1,1.0,100)
aww(n1b+0.25,0.1)
sneaky(TRASH,HOUR-0.1,1.25)
sadbox(HOUR+0.6,FZ,0.9)
heartbeat(n23+0.6,FZ,0.25)
sting(n24,0.7)
keys(pause+0.25,rwS,1.1)
folk(rwE+0.15,hS-0.1,0.75,100)
aww(a1+0.15,0.11,940,700,0.8)
groove(hS-0.1,m2,0.6,104)
plod(m2+0.05,tip-0.1,0.85)
pad(tip,end,[60,64,67,71],0.14); keys(tip+0.1,end,0.55); pad(end+0.2,D,[60,64,67,72],0.08)
for m_,a_ in [(72,0),(76,0.08),(79,0.16),(84,0.24)]: add(mus,end+0.4+a_,note(m_,1.4,0.18))
lvl=np.ones(N)
def seg(a,b,v): lvl[int(a*sr):int(b*sr)]=v
seg(rwS,rwE,0.2); seg(FZ,pause,0.0)
k=int(0.08*sr); lvl=np.convolve(lvl,np.ones(k)/k,mode='same'); mus*=lvl
# ---------------- SFX
pop(0.05,0.1)
whimper(n1c+0.15,0.06,0.4)
pop(n1c+0.05); ding(n1c+0.4,0.08)
rustle(h10,0.4,0.08)
whoosh(DROP,0.35,0.12); snap(CATCH,0.35)
crunch(CATCH+0.15,GULP-0.05,0.16)
gulp(GULP,0.35); gulp(GULP+0.18,0.25); pop(GULP+0.05,0.12)
for k_ in range(3): tick(n20+0.5+k_*0.62,0.1)
# trash
paws(W0,W1,0.07,0.18)
tapeRip(KNOCK,0.35,0.2); rustle(KNOCK+0.1,0.8,0.2); thunk(KNOCK+0.4,0.15)
crunch(W1+0.6,HOUR-0.3,0.12)
for i_,tt_ in enumerate([n22,n22+(n22e-n22)*0.33,n22+(n22e-n22)*0.62]): pop(tt_,0.14)
# one hour later
whoosh(HOUR,0.5,0.12)
t_=HOUR+0.05
while t_<n23+0.7: tick(t_,0.08); t_+=0.07
whimper(n23+1.0,0.09); whimper(n23e-0.3,0.08,0.7)
pop(n23+(n23e-n23)*0.52,0.12); click(n23+(n23e-n23)*0.52+0.15,0.15)
pop(n23+(n23e-n23)*0.8,0.12)
boom(n24,0.14)
n_=int(0.35*sr); tt=np.arange(n_)/sr; f=np.linspace(300,30,n_); add(sfx,FZ,np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt/0.2)*0.25)
n_=int(0.05*sr); add(sfx,pause,rng.standard_normal(n_)*env(n_,0.001,0.01)*0.6)
# pause diagram
whoosh(v1-0.4,0.6,0.14); pop(v1,0.14)
for k_ in range(5): pop(v1+(v1e-v1)*0.55+k_*0.06,0.06)
thr=st+(ste-st)*0.36; bel=st+(ste-st)*0.78
thunk(thr,0.22); pop(thr+0.02,0.14); thunk(bel,0.22); pop(bel+0.02,0.14)
pop(ste-0.3); click(ste-0.1,0.2); ding(ste+0.2,0.12)
n_=int(0.05*sr); add(sfx,rw+0.1,rng.standard_normal(n_)*env(n_,0.001,0.01)*0.5)
n_=int(1.0*sr); tt=np.arange(n_)/sr; f=np.linspace(1800,300,n_)
add(sfx,rwS,(np.sin(2*np.pi*np.cumsum(f)/sr)*0.08+np.convolve(rng.standard_normal(n_),np.ones(8)/8,'same')*0.05)*np.sin(np.pi*tt/1.0))
# right move
pop(a0+0.1,0.12)
for k_ in range(4): add(sfx,a1+0.4+k_*0.22,note(96-k_*2,0.3,0.05,0.4))
whoosh(a2-0.05,0.4,0.08); clank(a2+0.38,0.1)
pop(a2,0.12); pop(a3,0.12); whoosh(a3+0.45,0.6,0.1); thunk(a3+1.05,0.15)
pop(a4+0.3,0.12); snap(take-0.02,0.15); crunch(take+0.05,take+1.3,0.1)
whoosh(CLOSE,0.4,0.08); clank(CLOSE+0.75,0.3); click(CLOSE+0.75,0.3)
ding(CLOSE+0.8,0.1)
pop(hS+0.05,0.12)
pop(h21+0.05,0.15); ding(h21+0.1,0.12)
for m_,a_ in [(72,0),(76,0.1),(79,0.2),(84,0.3)]: pluck(h21+0.05+a_,m_,0.18,0.6)
# punchline: animal hospital
t_=m2+0.2
while t_<tip-0.2: beep(t_,0.035); t_+=0.85
pop(m2+0.05,0.15); pop(b1+0.4,0.15)
printer(b2+0.1,b2e-0.1,0.07)
kaching(b2e+0.05,0.18)
for k_ in ['m3.0','m3.1','m3.2','m3.3']: blip(P(k_))
pop(P('m3.4'),0.12)
