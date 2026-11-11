import json,subprocess,wave,numpy as np
from segs import segs
T={
'a1':"The lock *clicks.* One second later... *something* *hits* *the* *door* from the other side.",
'a2':"Part two: we ran into the tunnel. He ran right past us in the dark, and came back. The *comments* said: *hide.* So we *hid.*",
'a3':"*Rule* *number* *three:* a locked room is safe... *only* *if* *you're* *the* *only* *ones* *inside.*",
'a4':"Shelves. *Water.* A *first-aid* *kit.* A *radio* with no signal. A *map* of the tunnels. On paper, we just found a *bunker.*",
'a5':"*One* *problem.* In the corner... *someone* *is* *breathing.*",
'a6':"A metro *worker.* *Alive.* He has the *keys* to every exit on this line. And a *bite* on his arm.",
'a7':"The nurse looks at the *bite.* Then at us. She doesn't say anything. She doesn't *have* *to.*",
'a8':"*Real* *fact:* metro workers carry *keys* and *radios,* and they know every *emergency* *exit* on their line.",
'a9':"So, *what* *would* *you* *do?* Trust him, and let him lead us out with his keys... or leave him here, and crawl into the dark ventilation shaft? *Tell* *me* in the comments. Part four tomorrow."}
SR=24000;GAP_MAX=0.32
def load(n):
    w=wave.open(f'audio/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;r=np.sqrt((x[np.abs(x)>0.01]**2).mean());x=x/r*(0.075 if n in('a1','a5') else 0.1);return x,sr
t=0;clips=[];chunks=[];full=[]
for n in ['a%d'%i for i in range(1,10)]:
    sg,d=segs(n);x,sr=load(n)
    # rebuild with capped gaps
    pieces=[];newseg=[];cur=0
    for i,(a,b) in enumerate(sg):
        a2=max(0,a-0.05);b2=min(len(x)/sr,b+0.08)
        if i>0:
            gap=min(GAP_MAX,max(0.12,a-sg[i-1][1]));pieces.append(np.zeros(int(gap*sr)));cur+=gap
        seg=x[int(a2*sr):int(b2*sr)];newseg.append((cur+(a-a2),cur+(a-a2)+(b-a)));pieces.append(seg);cur+=len(seg)/sr
    y=np.concatenate(pieces);dur=len(y)/sr
    gap_before={'a2':0.6,'a3':0.3,'a5':0.4,'a6':0.8,'a7':0.4,'a8':0.6,'a9':0.4}.get(n,0.18)
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
