import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
SEGS=json.load(open('segs_out.json'))
def segs(n): return SEGS[n]
P={
'n1':["The sea just ran away.","Fish are jumping on the wet sand."],
'h1':["No way! Look at all the fish!","I need a video of this!"],
'n2':["You walk out to film.","Then you hear a low roar.","A white line grows on the horizon."],
'm1':["Pause.","When the sea runs away fast, the water is coming back.","Near the beach, a tsunami still moves","faster than any person can run.","Let's rewind."],
'n4':["Same beach.","The sea runs away?","Don't look.","Go to high ground. Right now.","Don't wait for an alarm."],
'h2':["Okay, okay! I'm going! No video!"],
'm2':["The sea didn't leave.","It went to get its friends."],
'm3':["Remember.","The sea runs away? A loud roar?","A strong earthquake at the beach?","Go to high ground,","or far inland.","Stay there for hours.","The first wave is not always the biggest."],
'm4':["The video can wait.","Your life can't."]}
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
