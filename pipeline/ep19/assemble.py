import json,subprocess,numpy as np,wave,sys
sys.path.insert(0,'.')
SEGS=json.load(open('segs_out.json'))
def segs(n): return SEGS[n]
P={
'n1':["Shoulder-deep.","In sand."],
'f1':["Deeper!","It's for the video!"],
'h1':["Okay.","One more meter."],
'n2':["The dry sand on top starts to slide.","Then the wall falls."],
'h2':["Whoa!","I can't move!"],
'n3':["Sand up to your chest.","Every breath gets harder.","Bad idea."],
'm1':["Pause.","This little box of sand weighs about 45 kilos.","Like a whole person.","Now a wall of it pushes on your chest, so your lungs can't open.","Let's rewind."],
'n4':["Same beach.","Same friends.","This time, the hole stops at your knees."],
'h3':["Knee-deep.","Done."],
'f2':["That's not a hole.","That's a bathtub!"],
'm2':["Under the sand?","That's my home.","Not yours."],
'm3':["Keep holes no deeper than your knees.","Never dig tunnels.","Fill the hole before you leave.","Someone stuck?","Call for help.","Don't jump in."],
'm4':["The hole can wait.","Your life can't."]}
import itertools
def split_lines(words,MAX=30):
    n=len(words); full=' '.join(words)
    if len(full)<=MAX: return [words]
    best=None
    for k in (2,3,4):
        for cuts in itertools.combinations(range(1,n),k-1):
            parts=[words[a:b] for a,b in zip((0,)+cuts,cuts+(n,))]
            ls=[len(' '.join(p)) for p in parts]
            if max(ls)>MAX+5: continue
            score=(max(ls)-min(ls))+k*12-sum(15 for p in parts[:-1] if p[-1][-1] in '.,:!?')+sum(12 for p in parts for w in p[:-1] if w[-1] in '.?!')
            if best is None or score<best[0]: best=(score,parts)
        if best: return best[1]
    return [words]
SPK={'n':'nar','m':'fine','h':'hero','f':'friend'}
order=[('n1',0.05),('f1',0.08),('h1',0.06),('n2',0.12),('h2',0.32),('n3',0.12),('m1',0.45),('n4',0.62),('h3',0.12),('f2',0.1),('m2',0.35),('m3',0.3),('m4',0.3)]
t=0;clips=[];caps=[];PH={}
for n,gap in order:
    s,d=segs(n); t+=gap
    sp=SPK[n[0]]
    assert len(s)==len(P[n]),(n,len(s),len(P[n]))
    for k,((a,b),txt) in enumerate(zip(s,P[n])):
        PH[f'{n}.{k}']=[round(t+a,3),round(t+b,3)]
        if txt is None: continue
        # split into display lines <=32 chars
        words=txt.split(); lines=split_lines(words)
        tot=sum(len(w)+1 for w in words); x=t+a; dur=b-a
        for L in lines:
            ws=[];
            for w in L:
                wd=dur*(len(w)+1)/tot; ws.append([w,round(x,3),round(x+wd,3)]); x+=wd
            caps.append({'spk':sp,'start':ws[0][1],'end':ws[-1][2],'words':ws})
    clips.append({'name':n,'start':round(t,3),'dur':d,'spk':sp}); t+=d
total=t+0.9
json.dump({'ph':PH,'clips':clips,'caps':caps,'total':round(total,2)},open('timeline.json','w'),indent=0)
# mix
inputs=[];flt=[]
for i,c in enumerate(clips):
    inputs+=['-i',f'audio/{c["name"]}.wav']; flt.append(f'[{i}:a]aresample=48000,adelay={int(c["start"]*1000)}|{int(c["start"]*1000)}[a{i}]')
mix=''.join(f'[a{i}]' for i in range(len(clips)))+f'amix=inputs={len(clips)}:normalize=0,apad,atrim=0:{total}[v]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(flt)+';'+mix,'-map','[v]','-ac','1','-ar','48000','voice.wav'],check=True)
for c in clips: print(c['name'],c['start'],round(c['start']+c['dur'],2))
print('total',total,'caps',len(caps))
