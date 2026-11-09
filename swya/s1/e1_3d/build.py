import json,subprocess,wave,numpy as np
from segs import segs
T={
'a1':"He's been *hitting* that door for two minutes now. And the lock... is *broken.*",
'a2':"*Three* *minutes* *earlier.* Monday, *8:12.* You're on the subway, between two stations. Packed car. *Thirty-two* people. Nobody looks up from their phone. Then the train *stops.* Hard. The lights go out, and the *red* emergency light comes on. From the next car, a *scream.* Then nothing.",
'a3':"*No* *signal.* But one *video* loads in a group chat. People in the street, *biting* people. And now something in the next car is *hitting* the door between you.",
'a4':"*Rule* *number* *one:* don't panic. Panic is loud, and loud is what they *follow.* So you look around. Who's here? A guy in a *suit,* holding his briefcase like a shield. A *nurse,* coming back from a night shift. And a *kid* with headphones, who hasn't noticed anything yet.",
'a5':"You check what you have. *Water:* one bottle. *Light:* your phone, *23%.* *Next* *station:* 400 meters. *The* *door:* closed. On paper, it's not that bad. There was only *one* *problem.*",
'a6':"The lock on that door was *broken.* It was only holding because nobody had pulled the *handle* yet. And now, slowly... *someone* *was.*",
'a7':"*Real* *fact:* many modern subway tunnels have an *emergency* *exit* or a cross passage every few hundred meters. But *never* touch the *third* *rail.* It can still be *live.*",
'a8':"So, *what* *would* *you* *do?* Open the emergency door and run into the dark tunnel... or block it with everything you have, and wait for help? *Tell* *me* in the comments. Part two tomorrow."}
SR=24000;GAP_MAX=0.32
def load(n):
    w=wave.open(f'audio/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768;return x,sr
t=0;clips=[];chunks=[];full=[]
for n in ['a1','a2','a3','a4','a5','a6','a7','a8']:
    sg,d=segs(n);x,sr=load(n)
    # rebuild with capped gaps
    pieces=[];newseg=[];cur=0
    for i,(a,b) in enumerate(sg):
        a2=max(0,a-0.05);b2=min(len(x)/sr,b+0.08)
        if i>0:
            gap=min(GAP_MAX,max(0.12,a-sg[i-1][1]));pieces.append(np.zeros(int(gap*sr)));cur+=gap
        seg=x[int(a2*sr):int(b2*sr)];newseg.append((cur+(a-a2),cur+(a-a2)+(b-a)));pieces.append(seg);cur+=len(seg)/sr
    y=np.concatenate(pieces);dur=len(y)/sr
    gap_before=0.5 if n in('a2',) else 0.18
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
