# Cap internal pauses (Shorts pacing) and map phrase times; then tempo 1.05
import wave,numpy as np,subprocess,os,json
from segs import segs
TEMPO=1.08
# phrase intervals in ORIGINAL clip time; splits = extra silence inserted at a time (s)
PH={
'n1':[(0.3,0.88),(1.19,2.89),(4.6,4.93)],
'h1':[(0.2,1.4),(1.8,2.53)],
'n2':[(0.1,2.1),(2.6,4.1),(4.6,6.45),(7.0,9.65),(10.3,11.06)],
'm1':[(0.2,0.63),(1.2,4.3),(4.4,6.65),(7.14,7.8)],
'n4':[(0.1,0.95),(1.24,2.73),(3.54,4.5),(5.3,6.1),(7.09,9.75),(10.95,12.4)],
'h2':[(0.0,1.2),(1.5,2.4)],
'm2':[(0.1,1.44),(1.48,4.46),(4.49,6.8)],
'm3':[(0.8,2.4),(2.5,5.0),(5.2,6.3),(6.7,8.36),(8.4,9.6)],
'm4':[(0.0,1.13),(1.68,3.23)]}
CAP={'n1':0.3,'h1':0.3,'n2':0.32,'m1':0.3,'n4':0.32,'h2':0.3,'m2':0.3,'m3':0.25,'m4':0.4}
DROP={'n1':[(3.1,4.3)],'m3':[(0.0,0.75)]}
SPLIT={'m2':[(1.46,0.14),(4.475,0.32)],'m3':[(8.37,0.12)]}
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
