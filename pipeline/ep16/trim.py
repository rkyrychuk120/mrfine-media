# Cap internal pauses (Shorts pacing) and map phrase times; then tempo 1.05
import wave,numpy as np,subprocess,os,json
from segs import segs
TEMPO=1.05
# phrase intervals in ORIGINAL clip time; splits = extra silence inserted at a time (s)
PH={
'n1':[(0.24,1.44),(1.97,4.73),(5.41,6.01)],
'h1':[(0.23,2.32)],
'n2':[(0.31,1.34),(2.29,4.6),(4.93,6.57),(7.36,7.92)],
'm1':[(0.1,0.74),(1.07,4.4),(4.8,6.43),(6.66,8.79),(9.43,9.93)],
'n4':[(0.25,2.36),(2.73,4.2),(4.2,5.45),(6.02,7.61)],
'h2':[(0.21,1.88),(2.43,3.76)],
'm2':[(0.28,1.71),(2.08,3.44),(4.15,5.2)],
'm3':[(0.0,0.5),(0.5,2.87),(3.13,5.59),(5.96,7.86),(8.02,9.67)],
'm4':[(0.0,1.68),(2.11,3.19)]}
CAP={'n1':0.3,'h1':0.2,'n2':0.3,'m1':0.3,'n4':0.25,'h2':0.35,'m2':0.38,'m3':0.25,'m4':0.35}
SPLIT={'m3':[(0.5,0.16)]}
SEG={}
for n,ph in PH.items():
    w=wave.open(f'audio_raw/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)
    s,d=segs(n); s=[(a,b) for a,b in s if b-a>0.08]
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
