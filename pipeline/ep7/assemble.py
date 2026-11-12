import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["Bear.","Twenty metres.","Your legs say:","run."],
'h1':["Nope. Nope. I'm out!"],
'n2':["You turn and run.","Now you look like food that runs away."],
'n3':["Twenty metres.","Ten.","Five."],
'm1':["Pause.","A bear can run about fifty kilometres an hour.","That's faster than a horse.","And when you run,","it can chase you.","Let's rewind."],
'n4':["Same trail.","Same bear.","This time, you don't run.","Stand tall.","Talk calmly.","Back away slowly."],
'h2':["Hey, bear.","Easy.","I'm just leaving.",None],
'm2':["The bear walked away.","You were too boring to chase. Congratulations."],
'm3':["If you see a bear:","don't run.","Stand tall.","Talk calmly.","Back away slowly.","Keep bear spray ready."],
'm4':["Your cardio can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.1),('h1',0.15),('n2',0.15),('n3',0.15),('m1',0.4),('n4',0.75),('h2',0.25),('m2',0.3),('m3',0.35),('m4',0.45)]
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
total=t+1.3
json.dump({'ph':PH,'clips':clips,'caps':caps,'total':round(total,2)},open('timeline.json','w'),indent=0)
# mix
inputs=[];flt=[]
for i,c in enumerate(clips):
    inputs+=['-i',f'audio/{c["name"]}.wav']; flt.append(f'[{i}:a]aresample=48000,adelay={int(c["start"]*1000)}|{int(c["start"]*1000)}[a{i}]')
mix=''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{total}[v]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(flt)+';'+mix,'-map','[v]','-ac','1','-ar','48000','voice.wav'],check=True)
for c in clips: print(c['name'],c['start'],round(c['start']+c['dur'],2))
print('total',total,'caps',len(caps))
