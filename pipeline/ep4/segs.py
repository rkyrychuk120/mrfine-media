import subprocess,re,json,sys
AUD='audio'
def segs(n):
    out=subprocess.run(['ffmpeg','-hide_banner','-i',f'{AUD}/{n}.wav','-af','silencedetect=noise=-38dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{AUD}/{n}.wav'],capture_output=True,text=True).stdout)
    ev=[(m.group(1),float(m.group(2))) for m in re.finditer(r'silence_(start|end): ([0-9.]+)',out)]
    s=[];cur=0.0;inside=False
    # speech intervals = complement of silence
    sil=[];st=None
    for k,v in ev:
        if k=='start': st=v
        else: sil.append((st,v))
    if st is not None and (not sil or sil[-1][0]!=st): sil.append((st,dur))
    t=0.0
    for a,b in sil:
        if a-t>0.05: s.append((round(t,2),round(a,2)))
        t=b
    if dur-t>0.05: s.append((round(t,2),round(dur,2)))
    return s,dur
if __name__=='__main__':
    for n in sys.argv[1:]:
        s,d=segs(n); print(n,len(s),s)
