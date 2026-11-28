# Cap internal pauses (Shorts pacing) and map phrase times; then tempo 1.05
import wave,numpy as np,subprocess,os,json
from segs import segs
TEMPO=1.08
# phrase intervals in ORIGINAL clip time; splits = extra silence inserted at a time (s)
PH={
'n1':[(0.0,1.27),(1.56,2.84)],
'f1':[(0.0,1.2),(1.5,2.72)],
'h1':[(0.15,1.0),(1.28,2.31)],
'n2':[(0.0,2.35),(2.6,3.96)],
'h2':[(0.0,1.15),(1.5,2.65)],
'n3':[(0.0,1.76),(2.39,4.23),(4.92,5.72)],
'm1':[(0.0,0.46),(1.15,4.74),(5.1,6.4),(7.25,10.72),(11.54,12.17)],
'n4':[(0.0,0.79),(0.99,1.91),(2.25,4.03)],
'h3':[(0.0,0.74),(1.51,1.96)],
'f2':[(0.0,1.42),(1.42,2.63)],
'm2':[(0.0,1.41),(1.71,2.69),(2.69,3.5)],
'm3':[(0.0,1.78),(1.98,3.21),(3.59,5.38),(5.89,6.56),(6.86,7.46),(7.72,8.44)],
'm4':[(0.0,1.28),(1.75,3.22)]}
CAP={'n1':0.3,'f1':0.3,'h1':0.3,'n2':0.32,'h2':0.35,'n3':0.28,'m1':0.22,'n4':0.32,'h3':0.4,'f2':0.3,'m2':0.45,'m3':0.21,'m4':0.4}
DROP={}
SPLIT={'f1':[(1.3,0.18)],'h1':[(1.2,0.2)],'h2':[(1.3,0.18)],'f2':[(1.42,0.14)],'m2':[(2.69,0.3)]}
SEG={}
for n,ph in PH.items():
    w=wave.open(f'audio_raw/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)
    s,d=segs(n); s=[(a,b) for a,b in s if b-a>0.08 and not any(x<=a and b<=y for x,y in DROP.get(n,[]))]
    # split segments at SPLIT points
    for (p,_) in SPLIT.get(n,[]):
        s2=[]
        for a,b in s:
            if a<p<b: s2+= [(a,p),(p,b)]
            else: s2.append((a,b))
        s=s2
    extra={p:g for p,g in SPLIT.get(n,[])}
    out=[np.zeros(int(0.03*sr),np.int16)];pos=0.03;M=[]  # map pieces (orig_a,orig_b,new_a)
    prev=None
    for i,(a,b) in enumerate(s):
        a0=max(0,a-0.04) if a not in extra else a; b0=min(d,b+0.06) if b not in extra else b
        if prev is not None:
            gap=a-prev; keep=max(0,min(CAP[n],gap)-0.1) if a not in extra else extra[a]
            z=int(keep*sr); out.append(np.zeros(z,np.int16)); pos+=z/sr
            if prev_b0>a0: a0=prev_b0
        seg=x[int(a0*sr):int(b0*sr)]; out.append(seg); M.append((a0,b0,pos)); pos+=len(seg)/sr
        prev=b; prev_b0=b0
    out.append(np.zeros(int(0.05*sr),np.int16))
    def mp(t,st=False):
        for a0,b0,p in M:
            if (t<b0 if st else t<=b0): return p+max(0,t-a0)
        a0,b0,p=M[-1]; return p+(b0-a0)
    y=np.concatenate(out); wo=wave.open(f'audio/{n}_t.wav','wb');wo.setnchannels(1);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes(y.tobytes());wo.close()
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'audio/{n}_t.wav','-af',f'atempo={TEMPO}',f'audio/{n}.wav'],check=True); os.remove(f'audio/{n}_t.wav')
    ss=[(round(mp(a,True)/TEMPO,3),round(mp(b)/TEMPO,3)) for a,b in ph]
    SEG[n]=[ss,round(len(y)/sr/TEMPO,3)]
    print(n,round(d,2),'->',SEG[n][1],ss)
json.dump(SEG,open('segs_out.json','w'))
