import json,subprocess,wave,numpy as np
from segs import segs
T={
'a1':"He's *through* *the* *door.* *Run.*",
'a2':"Our train *died* in a tunnel. A zombie was *hitting* the door, and the lock was *broken.* The *comments* said: *run.* So we're *running.*",
'a3':"He *jumps* down onto the tracks after us. He's *faster* than us. So we do the only thing that works.",
'a4':"*Light* *off.* *Back* *to* *the* *wall.* *Don't* *breathe.*",
'a5':"He runs *right* *past* *us.* *Close* *enough* *to* *touch.*",
'a6':"*Rule* *number* *two:* light is life. There are *four* of us now. The *nurse* has a phone. *Twenty-three* *percent.* The guy in the *suit* has a *lighter.* And the *kid* has headphones... and *zero* *battery.*",
'a7':"The next station is *four* *hundred* *meters* away. In the dark, that feels like *four* *kilometers.* So we walk on the side, slowly, one step at a time.",
'a8':"And then... the *kid* *trips.*",
'a9':"His hand lands *ten* *centimeters* from the *third* *rail.* One touch, and you don't get a *second* one.",
'a10':"Then, for *three* *seconds,* one bar of *signal.* A message from *Mom.* Where are you? Don't go to the *stations.* They're *full* *of* *them.*",
'a11':"Okay. On paper, we're *fine.* Four hundred meters. Twenty-three percent. Four people. Just *one* *problem...*",
'a12':"It's not *twenty-three* *percent* anymore. And ahead of us, in the dark... *the* *one* *who* *ran* *past* *us* is *coming* *back.*",
'a13':"*Real* *fact:* many subway tunnels have small *service* *rooms* with heavy metal doors. Some of them *lock* from the inside.",
'a14':"So, *what* *would* *you* *do?* Turn off the light and walk in total darkness... or hide in the service room, and hope the door holds? *Tell* *me* in the comments. Part three tomorrow."}
SR=24000;GAP_MAX=0.32
def load(n):
    w=wave.open(f'audio/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;r=np.sqrt((x[np.abs(x)>0.01]**2).mean());x=x/r*(0.075 if n in('a4','a5','a9','a12') else 0.1);return x,sr
t=0;clips=[];chunks=[];full=[]
for n in ['a%d'%i for i in range(1,15)]:
    sg,d=segs(n);x,sr=load(n)
    # rebuild with capped gaps
    pieces=[];newseg=[];cur=0
    for i,(a,b) in enumerate(sg):
        a2=max(0,a-0.05);b2=min(len(x)/sr,b+0.08)
        if i>0:
            gap=min(GAP_MAX,max(0.12,a-sg[i-1][1]));pieces.append(np.zeros(int(gap*sr)));cur+=gap
        seg=x[int(a2*sr):int(b2*sr)];newseg.append((cur+(a-a2),cur+(a-a2)+(b-a)));pieces.append(seg);cur+=len(seg)/sr
    y=np.concatenate(pieces);dur=len(y)/sr
    gap_before={'a2':0.35,'a4':0.25,'a5':1.3,'a6':0.6,'a8':0.3,'a9':1.0,'a10':0.5,'a12':0.3,'a13':0.5}.get(n,0.18)
    t+=gap_before if n!='a1' else 0.25
    words=T[n].split();tot_sp=sum(b-a for a,b in newseg);tot_c=sum(len(w.strip('*'))+1 for w in words)
    def at(f):
        q=f*tot_sp
        for a,b in newseg:
            if q<=b-a:return a+q
            q-=b-a
        return newseg[-1][1]
    c=0;wt=[]
    for w in words:
        L=len(w.strip('*'))+1;wt.append((w,t+at(c/tot_c),t+at((c+L)/tot_c)));c+=L
    cur=[]
    for w in wt:
        cur.append(w);txt=' '.join(q[0].strip('*') for q in cur)
        if len(txt)>=12 or w[0].rstrip('*')[-1] in '.:?,' or len(cur)>=3:
            chunks.append({'s':cur[0][1],'e':cur[-1][2],'w':[[q[0].strip('*'),q[0].startswith('*'),q[1]] for q in cur]});cur=[]
    if cur:chunks.append({'s':cur[0][1],'e':cur[-1][2],'w':[[q[0].strip('*'),q[0].startswith('*'),q[1]] for q in cur]})
    clips.append({'n':n,'start':round(t,3),'dur':round(dur,3)});full.append((t,y));t+=dur
total=t+3.0
N=int(total*SR);v=np.zeros(N)
for st,y in full:i=int(st*SR);v[i:i+len(y)]+=y[:N-i]
wo=wave.open('voice_raw.wav','wb');wo.setnchannels(1);wo.setsampwidth(2);wo.setframerate(SR);wo.writeframes((np.clip(v,-1,1)*32767).astype(np.int16).tobytes());wo.close()
subprocess.run(['ffmpeg','-v','error','-y','-i','voice_raw.wav','-af','acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5','-ar','48000','voice.wav'],check=True)
open('tl.js','w').write('const TL='+json.dumps({'clips':clips,'chunks':chunks,'total':round(total,2)})+';')
for c in clips:print(c['n'],c['start'],round(c['start']+c['dur'],2))
print('total',round(total,2))
