import json,subprocess,wave,numpy as np
from segs import segs
T={
'a1':"*Click.* The back door *opens.*",
'a2':"Part ten: we found *oxygen* for the kid. And a *police* *officer,* *locked* *in* his own car. We decided to *let* *him* *out.*",
'a3':"He gets out *slowly.* *Hands* *up.* And he tells us: my *partner* was *bitten.* He *locked* *me* *in...* so he *couldn't* *hurt* *me.* Then he *walked* *away.*",
'a4':"*Rule* *number* *eleven:* at a checkpoint, keep your *hands* where they can *see* *them.*",
'a5':"The officer shows us the way. The *sun* is going *down.* And there it is: the *bridge.* *Lights,* *soldiers,* and a big green sign: *safe* *zone.*",
'a6':"We get out with our *hands* *up.* A soldier *checks* *our* *arms,* one by one. *Clean.* *Clean.* Then... the *kid* starts to *cough.*",
'a7':"The soldier *raises* his *gun.* That boy is *sick.* He *stays* *outside.*",
'a8':"On paper, we *made* *it:* the safe zone is *twenty* *meters* away. *One* *problem...* they *won't* let the *kid* in. And at *sunset,* the *gate* *closes.*",
'a9':"*Real* *fact:* asthma is *not* *contagious.* You *can't* catch it from someone's *cough.*",
'a10':"So, *what* *would* *you* *do?* Tell the truth, show his *empty* *inhaler,* and ask them to check him... or take the officer's *secret* *path* under the bridge? *Tell* *me* in the comments. Part twelve tomorrow: the *finale.*"}
SR=24000;GAP_MAX=0.32
def load(n):
    w=wave.open(f'audio/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;r=np.sqrt((x[np.abs(x)>0.01]**2).mean());x=x/r*(0.08 if n in('a1','a3','a6') else 0.1);return x,sr
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
    gap_before={'a2':0.5,'a3':0.4,'a4':0.5,'a5':0.4,'a6':0.5,'a7':0.5,'a8':0.5,'a9':0.5,'a10':0.4}.get(n,0.18)
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
