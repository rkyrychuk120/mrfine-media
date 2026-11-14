import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["BANG! Your tyre just blew.","You are going 110."],
'h1':["No, no, no! I have to stop, now!"],
'n2':["You hit the brakes hard.","You pull the wheel. The car starts to spin."],
'm1':["Pause.","You wanted to stop fast.","The car picked spin instead.","A blown tyre already pulls the car to one side.","Hard braking makes it much worse.","Let's rewind."],
'n4':["Same road.","Same bang.","Both hands on the wheel.","Keep it straight. Slowly lift your foot off the gas."],
'h2':["Okay...","it's","slowing down.","I'm fine."],
'm2':["No spin.","Just a flat tyre and a boring afternoon.","Boring means you're still here."],
'm3':["If a tyre blows:","Hold the wheel straight.","Slowly lift off the gas.","No hard braking.","When the car is calm, pull off the road."],
'm4':["Stopping can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.05),('h1',0.15),('n2',0.1),('m1',0.6),('n4',0.75),('h2',0.25),('m2',0.3),('m3',0.35),('m4',0.45)]
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
            if cur and (len(' '.join(cur+[w]))>30 or (cur[-1][-1] in '.:!?' and len(' '.join(cur))>=9)): lines.append(cur);cur=[]
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
