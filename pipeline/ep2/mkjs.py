import json,wave,numpy as np
from warp import P
tl=json.load(open('timeline.json'))
fps=30;N=int(tl['total']*fps)+1
env={k:[0.0]*N for k in ['nar','fine','kid','mom']}
for c in tl['clips']:
    w=wave.open(f"audio/{c['name']}.wav");sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
    hop=sr//fps
    for i in range(0,len(x)//hop):
        r=np.sqrt((x[i*hop:(i+1)*hop]**2).mean()); f=int(round(c['start']*fps))+i
        if f<N: env[c['spk']][f]=max(env[c['spk']][f],r)
for k in env:
    a=np.array(env[k]); m=np.percentile(a[a>0],95) if (a>0).any() else 1
    env[k]=[round(min(1,v/m),2) for v in a]
tl['env']=env;tl['fps']=fps;tl['warp']=P
open('timeline.js','w').write('const TL='+json.dumps(tl)+';')
print('ok',N)
