import json,subprocess,wave,numpy as np,re
from segs import segs
T={
's1':"Monday. 8:12 in the morning. You are on the subway. And the train just *stopped* in the middle of the tunnel.",
's2':"The lights go out. *Red* emergency light. Then a *scream* from the next car. Then silence. *No* *signal.* No news. Only one strange video in a group chat: people in the street... *biting* people.",
's3':"*Bang.* The door to the next car shakes. Someone really wants to come in. And he does not *knock* like a normal person.",
's4':"You check what you have. Water: one bottle. Light: your phone, *23%.* The door between the cars: closed. The next station: 400 meters. On paper, everything was *not* *so* *bad.*",
's5':"But there was *one* *thing* you did not know. The lock on that door... was *broken.*",
's6':"Real fact: in many modern subway tunnels, there is an *emergency* *passage* about every 250 meters. But *never* touch the *third* *rail.* It can still be live.",
's7':"So what do you do? *A:* open the emergency door and run into the tunnel. Or *B:* block the door with your bag and wait. Write *A* or *B* in the comments. Tomorrow you will see if you *survived.*"}
order=[('s1',0.6),('s2',0.5),('s3',0.4),('s4',0.6),('s5',0.6),('s6',0.8),('s7',0.6)]
t=0;clips=[];chunks=[]
for n,gap in order:
    sg,d=segs(n); t+=gap
    words=T[n].split(); tot_speech=sum(b-a for a,b in sg); tot_chars=sum(len(w.strip('*'))+1 for w in words)
    # map cumulative char fraction to time inside speech segments
    def at(frac):
        x=frac*tot_speech
        for a,b in sg:
            if x<=b-a: return a+x
            x-=b-a
        return sg[-1][1]
    c=0; wt=[]
    for w in words:
        L=len(w.strip('*'))+1; wt.append((w, t+at(c/tot_chars), t+at((c+L)/tot_chars))); c+=L
    # chunk: up to 3 words / 16 chars, break after punctuation
    cur=[]
    for w in wt:
        cur.append(w)
        txt=' '.join(x[0].strip('*') for x in cur)
        if len(txt)>=13 or w[0].rstrip('*')[-1] in '.:?,' or len(cur)>=3:
            chunks.append({'s':cur[0][1],'e':cur[-1][2],'w':[[x[0].strip('*'),x[0].startswith('*'),x[1]] for x in cur]}); cur=[]
    if cur: chunks.append({'s':cur[0][1],'e':cur[-1][2],'w':[[x[0].strip('*'),x[0].startswith('*'),x[1]] for x in cur]})
    clips.append({'n':n,'start':round(t,3),'dur':d}); t+=d
total=t+1.5
inputs=[];flt=[]
for i,c in enumerate(clips):
    inputs+=['-i',f'audio/{c["n"]}.wav']; ms=int(c['start']*1000); flt.append(f'[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]')
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(flt)+';'+''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{total}[v]','-map','[v]','-ac','1','-ar','48000','voice.wav'],check=True)
open('tl.js','w').write('const TL='+json.dumps({'clips':clips,'chunks':chunks,'total':round(total,2)})+';')
for c in clips: print(c['n'],c['start'],round(c['start']+c['dur'],2))
print('total',total,len(chunks))
