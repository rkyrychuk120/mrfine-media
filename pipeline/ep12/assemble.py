import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
SEGS=json.load(open('segs_out.json'))
def segs(n): return SEGS[n]
P={
'n1':["This moose is ten metres away.","And you want a selfie."],
'h1':["Look at him!","So cool.","Just one more step..."],
'n2':["Its ears go back. The hair on its back goes up. You keep filming.","Then it charges."],
'm1':["Pause.","In Alaska, moose hurt more people than bears","every year.","Ears back and hair up means one thing. You are way too close.","Let's rewind."],
'n4':["Same moose.","Same phone.","Stay far away.","Use the zoom.","Ears go back?","Walk away slowly."],
'h2':["Nice zoom.","He looks calm.","I'm fine."],
'm2':["You wanted the moose up close. The moose wanted you far away.","And the moose is bigger."],
'm3':["Remember.","A bear?","Don't run.","A moose?","Run!","Get behind a tree or a car.","Knocked down?","Curl up,","cover your head, and stay still."],
'm4':["The selfie can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.05),('h1',0.2),('n2',0.15),('m1',0.6),('n4',0.75),('h2',0.3),('m2',0.35),('m3',0.35),('m4',0.45)]
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
