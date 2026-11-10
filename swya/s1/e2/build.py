import json,subprocess,wave,numpy as np
from segs import segs
T={
'a1':"He's *through* *the* *door.* *Run.*",
'a2':"Our train *died* in a tunnel. A zombie was *hitting* the door, and the lock was *broken.* The *comments* said: *run.* So we're *running.*",
'a3':"*Rule* *number* *two:* light is life. The *nurse* has a phone. *Twenty-three* *percent.* The guy in the *suit* has a *lighter.* And the *kid* has headphones... and *zero* *battery.*",
'a4':"The next station is *four* *hundred* *meters* away. In the dark, that feels like *four* *kilometers.* So we walk on the side, slowly, one step at a time.",
'a5':"And we *never* step on the *third* *rail.* One touch, and you don't get a *second* one.",
'a6':"Then, for *three* *seconds,* one bar of *signal.* A message from *Mom.* Where are you? Don't go to the *stations.* They're *full* *of* *them.*",
'a7':"Okay. On paper, we're *fine.* Four hundred meters. Twenty-three percent. Four people. Just *one* *problem...*",
'a8':"It's not *twenty-three* *percent* anymore. And behind us, in the dark... *something* *is* *following* our light.",
'a9':"*Real* *fact:* many subway tunnels have small *service* *rooms* with heavy metal doors. Some of them *lock* from the inside.",
'a10':"So, *what* *would* *you* *do?* Turn off the light and walk in total darkness... or hide in the service room, and hope the door holds? *Tell* *me* in the comments. Part three tomorrow."}
SR=24000;GAP_MAX=0.32
def load(n):
    w=wave.open(f'audio/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;return x,sr
t=0;clips=[];chunks=[];full=[]
for n in ['a%d'%i for i in range(1,11)]:
    sg,d=segs(n);x,sr=load(n)
    # rebuild with capped gaps
    pieces=[];newseg=[];cur=0
    for i,(a,b) in enumerate(sg):
        a2=max(0,a-0.05);b2=min(len(x)/sr,b+0.08)
        if i>0:
            gap=min(GAP_MAX,max(0.12,a-sg[i-1][1]));pieces.append(np.zeros(int(gap*sr)));cur+=gap
        seg=x[int(a2*sr):int(b2*sr)];newseg.append((cur+(a-a2),cur+(a-a2)+(b-a)));pieces.append(seg);cur+=len(seg)/sr
    y=np.concatenate(pieces);dur=len(y)/sr
    gap_before=0.35 if n in('a2','a6','a9') else 0.18
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
