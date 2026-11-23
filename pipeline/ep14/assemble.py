import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
SEGS=json.load(open('segs_out.json'))
def segs(n): return SEGS[n]
P={
'n1':["Oil on fire.","Water,","flour, or a lid?","Pick one."],
'h1':["Flour! Flour puts out fire, right?"],
'n2':["You throw a cup of flour on it.","The flour flies up in a cloud...","And the cloud catches fire!"],
'm1':["Pause.","Flour","can burn.","Thrown in a cloud, it makes the fire bigger,","fast.","Water?","Even worse.","Only the lid wins.","Let's rewind."],
'n4':["Same fire. Put the flour down.","Turn off the heat.","Slide the lid on.","And leave it closed."],
'h2':["Wait... that's it?","It's out!"],
'm2':["Fire is not a recipe.","Stop adding ingredients."],
'm3':["Remember.","Small fire in the pan?","Heat off.","Lid on.","Leave it.","Never water.","Never flour.","Never carry the pan.","Fire getting bigger?","Get everyone out,","and call the fire department."],
'm4':["Dinner can wait.","Your life can't."]}
SPK={'n':'nar','m':'fine','h':'hero'}
order=[('n1',0.05),('h1',0.15),('n2',0.12),('m1',0.75),('n4',0.8),('h2',0.3),('m2',0.35),('m3',0.4),('m4',0.45)]
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
            if cur and (len(' '.join(cur+[w]))>33 or (cur[-1][-1] in '.:!?' and len(' '.join(cur))>=9)): lines.append(cur);cur=[]
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
