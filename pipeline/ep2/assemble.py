import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["Saturday.","Parents are out.","You're bored.","In the kitchen drawer, you find a box of matches.","Strike one.","Cool.","Another. Cooler.","You wave it around like a magic wand...","and it touches the curtain."],
'n2':["Tiny flame.","You panic. And your brain says: if Mom finds out, you're grounded till graduation.","So you throw a blanket on it, shut the door... and hide in your closet."],
'n3':["It doesn't.","Thirty seconds, the fire hits the ceiling.","One minute,","the room is full of black smoke."],
'm1':["Hi.","I'm Mr Fine, and I just put you on pause.","Because this is real.","One match. One curtain.","That's all it takes.","A small flame can turn into a major fire in less than thirty seconds.","And hiding?","It doesn't work.","Smoke finds every closet.","So...","let's rewind."],
'n4':[None,"Same Saturday. Same boredom. Same box of matches.","But this time...","you put it back.","Because fire doesn't play.","It spreads.","And if a fire ever does start:","don't hide,","don't fight it.","Yell fire!"],
'n5':["Get low under the smoke,","get out, and call the fire department from outside."],
'm2':["Boring Saturday?","Yes.","House still standing?","Also yes.","Good trade."],
'm3':["Matches and lighters aren't toys.","Find them?","Give them to an adult.","And if there's a fire:","get low,","get out, stay out,","and call the fire department."],
'm4':["Boredom passes.","Fire doesn't."],
'y1':["It'll go out.","It'll go out..."],'y2':["Fire!","FIRE!"],'y3':["I learned something today."],
'mom':["Why","are the matches","on the top shelf?"]}
SPK={'n':'nar','m':'fine','y':'kid','mo':'mom'}
order=[('n1',0.3),('n2',0.3),('y1',0.15),('n3',0.3),('m1',2.4),('n4',1.6),('y2',0.15),('n5',0.2),('mom',0.7),('y3',0.2),('m2',0.3),('m3',0.4),('m4',0.4)]
t=0;clips=[];caps=[]
for n,gap in order:
    s,d=segs(n); t+=gap
    sp='mom' if n=='mom' else SPK[n[0]]
    assert len(s)==len(P[n]),(n,len(s),len(P[n]))
    for (a,b),txt in zip(s,P[n]):
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
total=t+3.2
json.dump({'clips':clips,'caps':caps,'total':round(total,2)},open('timeline.json','w'),indent=0)
# mix
inputs=[];flt=[]
for i,c in enumerate(clips):
    inputs+=['-i',f'audio/{c["name"]}.wav']; flt.append(f'[{i}:a]aresample=48000,adelay={int(c["start"]*1000)}|{int(c["start"]*1000)}[a{i}]')
mix=''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{total}[v]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(flt)+';'+mix,'-map','[v]','-ac','1','-ar','48000','voice.wav'],check=True)
for c in clips: print(c['name'],c['start'],round(c['start']+c['dur'],2))
print('total',total,'caps',len(caps))
