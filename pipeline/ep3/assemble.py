import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
from segs import segs
P={
'n1':["Winter.","The pond in the park is frozen.","Your friend pulls out her phone."],
'f1':["Walk to the middle!","This is going viral!"],
'n2':["The ice looks solid.","The ice","is lying.","First step.","Fine.","Second step.","Fine.","Third step..."],
'n3':["Crack.","You're in.","The water is so cold, it knocks the air right out of you.","You gasp. You splash. You grab the edge...","and it breaks."],
'f2':["Hold on!","Hold on!"],
'n4':["Ten seconds, you can't stop gasping.",None,"Thirty seconds, your arms get heavy."],
'm1':["Hi.","I'm Mr Fine,","and I just put you on pause.","Because this is real.","You can't tell how thin ice is just by looking.","And cold water hits you like a punch.","You gasp. You panic. You fight the water.","But that shock passes in about a minute,","if you stay calm.","So...","let's rewind."],
'n5':["Same pond.","Same friend.","Same phone.","But this time...","you stay on the shore.","Because ice is not a floor."],
'n6':["And if you ever do fall in:","keep calm and shout for help.","Float, and let your breathing settle. Spread your arms flat on the ice.","Kick your legs and slide out.","Then stay flat and crawl to the shore.","Never stand up."],
'f3':["So... no video?"],
'y1':["Sure.","You walk to the middle.","I'll film."],
'f4':["Nope."],
'm2':["The ice said it was fine.","I'm Mr Fine.","We are not the same."],
'm3':["Stay off frozen ponds and lakes.","Friend falls in? Don't go after them. Call for help, lie down, and reach out with a stick or a scarf from the shore."],
'm4':["Views can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','y':'kid','f':'friend'}
order=[('n1',0.3),('f1',0.2),('n2',0.3),('n3',0.9),('f2',0.1),('n4',0.2),('m1',1.6),('n5',1.6),('n6',0.6),('f3',0.8),('y1',0.3),('f4',0.8),('m2',0.4),('m3',0.5),('m4',0.5)]
t=0;clips=[];caps=[]
for n,gap in order:
    s,d=segs(n); t+=gap
    sp=SPK[n[0]]
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
