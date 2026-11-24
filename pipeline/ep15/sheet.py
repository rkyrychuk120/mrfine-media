import sys,glob
from PIL import Image,ImageDraw
fs=sorted(glob.glob('st_*.png')); out=sys.argv[1]; cols=3
ims=[Image.open(f).resize((540,490)) for f in fs]
rows=(len(ims)+cols-1)//cols
for part in range(0,rows,4):
    sheet=Image.new('RGB',(540*cols,490*4),'black'); d=ImageDraw.Draw(sheet)
    for i in range(part*cols,min(len(ims),(part+4)*cols)):
        r=(i//cols)-part; c=i%cols; sheet.paste(ims[i],(c*540,r*490)); d.text((c*540+8,r*490+8),fs[i],fill='yellow')
    sheet.save(f'{out}_{part//4}.png')
