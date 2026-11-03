from PIL import Image, ImageDraw, ImageFont
CAV="/tmp/claude-0/work/fonts/caveat700.ttf"; PAT="/tmp/claude-0/work/fonts/patrick.ttf"
bg=Image.open('g44.5.png').convert('RGB')
# fond papier: effacer tout sauf stylo -> reprendre papier en haut/bas
paper=bg.copy()

import numpy as np
box=(440,590,640,1290)
crop=bg.crop(box); a=np.array(crop).astype(int)
mx=a.max(2); mn=a.min(2)
dark=(mn<175)
green=(a[:,:,1]-a[:,:,0]>45)
m=(dark|green)
yy0,xx0=np.mgrid[0:crop.height,0:crop.width]
m&=~(green&(yy0+box[1]>1220))
m&=(xx0+box[0]<630)
# retirer curseur
yy,xx=np.mgrid[0:crop.height,0:crop.width]
m&=~((xx+box[0]>582)&(yy+box[1]>1128)&(yy+box[1]<1200))
alpha=Image.fromarray((m*255).astype('uint8')).resize((int(crop.width*0.78*1.0),int(crop.height*0.78)),Image.LANCZOS)
penim=crop.resize(alpha.size,Image.LANCZOS)
clean=Image.new('RGB',(1080,1920))
strip=bg.crop((0,1500,1080,1900))
for y in range(0,1920,400): clean.paste(strip,(0,y))
im=clean; d=ImageDraw.Draw(im)
def ctext(t,y,size,fill,font=CAV):
    f=ImageFont.truetype(font,size); w=d.textlength(t,font=f); d.text(((1080-w)/2,y),t,font=f,fill=fill)
ink=(20,20,24); gr=(18,150,100); gy=(95,95,100)
ctext("POURQUOI C'EST CONÇU COMME ÇA ?",295,44,gy,PAT)
d.line([(150,360),(930,360)],fill=(150,160,190),width=4)
ctext("POURQUOI LE",440,125,ink)
ctext("STYLO",545,200,gr)
ctext("FAIT CLIC ?",770,125,ink)
im.paste(penim,((1080-penim.width)//2,985),alpha)
ctext("L'INGÉNIEUR MALIN EXPLIQUE",1530,44,gy,PAT)
im.save('image-miniature-episode-02-stylo-a-bille.png')
