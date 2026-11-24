import json,sys,re,subprocess,shutil
f,name=sys.argv[1],sys.argv[2]
s=open(f).read()
m=re.search(r'(/root/\S+?mcp-Speko-blob-\S+?\.wav)',s)
src=m.group(1)
sid=re.search(r'synthesis_?[iI]d\W+([\w-]+)',s)
print('sid',sid.group(1) if sid else None)
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-ac','1','-ar','48000',f'audio_raw/{name}.wav'],check=True)
print(name,subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'audio_raw/{name}.wav'],capture_output=True,text=True).stdout.strip())
