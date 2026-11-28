import json,sys,re,base64,subprocess,glob,os
f,name=sys.argv[1],sys.argv[2]
d=json.load(open(f)); txt=''.join(x.get('text','') for x in d if isinstance(x,dict))
m=re.search(r'(/root/\S+?mcp-Speko-blob-\S+?\.wav)',txt)
sid=re.search(r'synthesis_?[iI]d\W+([\w-]+)',txt)
if m: src=m.group(1)
else:
    j=json.loads(txt[txt.index('{'):txt.rindex('}')+1])
    def find(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if isinstance(v,str) and len(v)>1000: return v
                r=find(v)
                if r: return r
        return None
    b=find(j); src=f'/tmp/claude-0/{name}.bin'; open(src,'wb').write(base64.b64decode(b))
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-ac','1','-ar','48000',f'audio_raw/{name}.wav'],check=True)
print(name,sid.group(1) if sid else None,subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'audio_raw/{name}.wav'],capture_output=True,text=True).stdout.strip())
