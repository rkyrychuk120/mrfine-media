import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["Could you jump off a stopped ski lift?","This one stopped twenty minutes ago."],
'h1':["My feet are freezing.","That snow looks soft.","I'm jumping."],
'n2':["You lift the safety bar.","You slide to the edge of the seat."],
'm1':["Pause.","Soft snow?","Only on top.","Under it: hard,","+icy ground.","This chair is ten metres up. That's like jumping off a three-floor building.","Let's rewind."],
'n4':["Same lift.","Same stop.","Bar down.","Sit back.","Stay calm.","If the lift can't start again, ski patrol will come and get you down."],
'h2':["Okay...","it's moving again.","I'm fine."],
'm2':["Twenty cold minutes.","Cold toes warm up.","Broken legs take months.","Gravity has no undo button."],
'm3':["Stuck on a lift?","Keep the bar down.","Stay seated and stay calm.","Wait for ski patrol.","Never jump."],
'm4':["The slope can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.05),('h1',0.15),('n2',0.1),('m1',0.45),('n4',0.6),('h2',0.2),('m2',0.3),('m3',0.35),('m4',0.45)]
t=0;clips=[];caps=[];PH={}
for n,gap in order:
    s,d=segs(n); t+=gap
    sp=SPK[n[0]]
    assert len(s)==len(P[n]),(n,len(s),len(P[n]))
    for k,((a,b),txt) in enumerate(zip(s,P[n])):
        PH[f'{n}.{k}']=[round(t+a,3),round(t+b,3)]
        if txt is None: continue
        merge=txt.startswith('+')
        if merge: txt=txt[1:]
        # split into display lines <=32 chars
        words=txt.split(); lines=[];cur=[]
        sents=[];sc_=[]
        for w in words:
            sc_.append(w)
            if w[-1] in '.!?' and len(' '.join(sc_))>=9: sents.append(sc_);sc_=[]
        if sc_: sents.append(sc_)
        for S_ in sents:
            Ls=len(' '.join(S_)); n_=max(1,-(-Ls//32)); tgt=Ls/n_; cur=[]
            for w in S_:
                if cur and len(' '.join(cur+[w]))>tgt+4 and len(lines)<99: lines.append(cur);cur=[]
                cur.append(w)
            lines.append(cur)
        tot=sum(len(w)+1 for w in words); x=t+a; dur=b-a
        for L in lines:
            ws=[];
            for w in L:
                wd=dur*(len(w)+1)/tot; ws.append([w,round(x,3),round(x+wd,3)]); x+=wd
            if merge and caps and len(' '.join(w[0] for w in caps[-1]['words']+ws))<=30:
                caps[-1]['words']+=ws; caps[-1]['end']=ws[-1][2]
            else: caps.append({'spk':sp,'start':ws[0][1],'end':ws[-1][2],'words':ws})
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
