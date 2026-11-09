import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["This egg is a bomb.","And you just pressed start."],
'h1':["Two minutes.","Boiled egg.","No pan.","Genius."],
'n2':["Two a.m.","You're hungry,","and lazy.","Ding!","It looks fine.","You cut it open..."],
'n3':["Hot egg.","In your face."],
'h2':["Ow!","Ow!","Hot!"],
'm1':["Pause.","Inside the shell, the egg makes steam.","The steam has nowhere to go.","So the egg can burst, even after it leaves the microwave.","Let's rewind."],
'n4':["Same egg. Crack it into a bowl.","Poke the yolk.","Cover it,","and cook it in short steps."],
'h3':["Breakfast.","And I","still have a face."],
'm2':["Eggs don't explode in the microwave.","They wait for you."],
'm3':["Hot food on your skin?","Cool it under cool running water for twenty minutes."],
'm4':["Breakfast can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.15),('h1',0.15),('n2',0.15),('n3',0.75),('h2',0.05),('m1',0.5),("n4",1.15),('h3',0.25),('m2',0.35),('m3',0.35),('m4',0.4)]
t=0;clips=[];caps=[];PH={}
for n,gap in order:
    s,d=segs(n); t+=gap
    sp=SPK[n[0]]
    assert len(s)==len(P[n]),(n,len(s),len(P[n]))
    for k,((a,b),txt) in enumerate(zip(s,P[n])):
        PH[f'{n}.{k}']=[round(t+a,3),round(t+b,3)]
        if txt is None: continue
        # split into display lines <=32 chars
        words=txt.split(); lines=[];cur=[]
        for w in words:
            if cur and len(' '.join(cur+[w]))>30: lines.append(cur);cur=[]
            cur.append(w)
        lines.append(cur)
        tot=sum(len(w)+1 for w in words); x=t+a; dur=b-a
        for L in lines:
            ws=[];
            for w in L:
                wd=dur*(len(w)+1)/tot; ws.append([w,round(x,3),round(x+wd,3)]); x+=wd
            caps.append({'spk':sp,'start':ws[0][1],'end':ws[-1][2],'words':ws})
    clips.append({'name':n,'start':round(t,3),'dur':d,'spk':sp}); t+=d
total=t+2.1
json.dump({'ph':PH,'clips':clips,'caps':caps,'total':round(total,2)},open('timeline.json','w'),indent=0)
# mix
inputs=[];flt=[]
for i,c in enumerate(clips):
    inputs+=['-i',f'audio/{c["name"]}.wav']; flt.append(f'[{i}:a]aresample=48000,adelay={int(c["start"]*1000)}|{int(c["start"]*1000)}[a{i}]')
mix=''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{total}[v]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(flt)+';'+mix,'-map','[v]','-ac','1','-ar','48000','voice.wav'],check=True)
for c in clips: print(c['name'],c['start'],round(c['start']+c['dur'],2))
print('total',total,'caps',len(caps))
