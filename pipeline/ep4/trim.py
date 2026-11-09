# tighten internal pauses (Shorts pacing): keep speech, cap gaps
import wave,numpy as np,sys
from segs import segs
CAP={'n1':0.3,'n2':0.32,'n3':0.3,'m1':0.35,'n4':0.3,'m2':0.25,'m3':0.3,'m4':0.4,'h1':0.28,'h2':0.2,'h3':0.25}
for n,cap in CAP.items():
    s,d=segs('../ep4/audio_raw/'+n if False else n)
    w=wave.open(f'audio_raw/{n}.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)
    s=[(a,b) for a,b in s if b-a>0.12]
    out=[np.zeros(int(0.03*sr),np.int16)]
    for i,(a,b) in enumerate(s):
        if i: out.append(np.zeros(int(min(cap,a-s[i-1][1])*sr),np.int16))
        out.append(x[max(0,int((a-0.04)*sr)):int((b+0.06)*sr)])
    out.append(np.zeros(int(0.05*sr),np.int16))
    y=np.concatenate(out); wo=wave.open(f'audio/{n}.wav','wb');wo.setnchannels(1);wo.setsampwidth(2);wo.setframerate(sr);wo.writeframes(y.tobytes());wo.close()
    print(n,round(d,2),'->',round(len(y)/sr,2))
