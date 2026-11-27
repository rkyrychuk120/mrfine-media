# Cap internal pauses (Shorts pacing) and map phrase times; then tempo 1.05
import wave,numpy as np,subprocess,os,json
from segs import segs
TEMPO=1.08
# phrase intervals in ORIGINAL clip time; splits = extra silence inserted at a time (s)
PH={
'n1':[(0.0,1.31),(1.73,2.51)],
'f1':[(0.0,1.71),(1.95,2.64)],
'h1':[(0.0,0.5),(0.82,1.41)],
'n2':[(0.0,1.45),(1.91,2.68),(2.94,3.51)],
'h2':[(0.0,1.14),(1.53,2.66)],
'n3':[(0.05,1.2),(1.22,2.05),(2.38,3.31),(3.65,4.49),(4.96,5.97)],
'm1':[(0.0,0.45),(0.84,4.5),(4.75,6.76),(7.38,9.28),(9.92,10.66)],
'n4':[(0.0,0.78),(0.95,1.81),(2.26,4.38)],
'h3':[(0.0,0.43),(0.91,1.51)],
'f2':[(0.0,1.19),(1.62,2.39)],
'm2':[(0.0,1.4),(2.01,3.4),(4.2,5.14)],
'm3':[(0.0,2.15),(2.49,3.16),(3.37,3.93),(4.34,6.79),(7.15,8.07),(8.33,9.07)],
'm4':[(0.0,1.18),(1.4,2.4)]}
CAP={'n1':0.32,'f1':0.25,'h1':0.3,'n2':0.34,'h2':0.25,'n3':0.3,'m1':0.3,'n4':0.32,'h3':0.3,'f2':0.3,'m2':0.7,'m3':0.25,'m4':0.4}
DROP={'n1':[(2.6,4.6)],'h2':[(2.9,4.1)]}
SPLIT={'n3':[(1.21,0.16)],'n4':[(0.86,0.2)]}
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
