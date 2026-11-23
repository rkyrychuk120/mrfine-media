# tighten internal pauses (Shorts pacing): keep speech, cap gaps, then speed up 5%
import wave,numpy as np,subprocess,os
from segs import segs
CAP={'n1':0.2,'h1':0.18,'n2':0.22,'m1':0.22,'n4':0.2,'h2':0.3,'m2':0.3,'m3':0.18,'m4':0.3}
TEMPO=1.05
import json
SEG={}
for n,cap in CAP.items():
    s,d=segs(n)
    w=wave.open(f'audio_raw/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)
    s=[(a,b) for a,b in s if b-a>0.2]
    out=[np.zeros(int(0.03*sr),np.int16)];pos=0.03;ss=[]
    for i,(a,b) in enumerate(s):
        if i: z=int(max(0,min(cap,a-s[i-1][1])-0.1)*sr); out.append(np.zeros(z,np.int16)); pos+=z/sr
        seg=x[max(0,int((a-0.04)*sr)):int((b+0.06)*sr)]; out.append(seg); ss.append((round((pos+0.04)/TEMPO,3),round((pos+len(seg)/sr-0.06)/TEMPO,3))); pos+=len(seg)/sr
    out.append(np.zeros(int(0.05*sr),np.int16))
    y=np.concatenate(out); wo=wave.open(f'audio/{n}_t.wav','wb');wo.setnchannels(1);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes(y.tobytes());wo.close()
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'audio/{n}_t.wav','-af',f'atempo={TEMPO}',f'audio/{n}.wav'],check=True); os.remove(f'audio/{n}_t.wav')
    SEG[n]=[ss,round(len(y)/sr/TEMPO,3)]
    print(n,round(d,2),'->',round(len(y)/sr/TEMPO,2))
json.dump(SEG,open('segs_out.json','w'))
