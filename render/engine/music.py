"""Musique synthétisée 104 bpm. Usage : python music.py durée_s music.wav"""
import numpy as np, wave
import sys
sr=44100; D=float(sys.argv[1]); OUT=sys.argv[2]; N=int(D*sr); bpm=104; beat=60/bpm
out=np.zeros(N)
def add(at,sig,g=1.0):
    a=int(at*sr); e=min(N,a+len(sig))
    if a<N: out[a:e]+=sig[:e-a]*g
def pluck(f,dur=0.35,dec=9):
    t=np.arange(int(dur*sr))/sr
    return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)+0.12*np.sin(2*np.pi*3*f*t))*np.exp(-t*dec)*np.minimum(1,t/0.004)
def bass(f,dur=0.5):
    t=np.arange(int(dur*sr))/sr
    return np.sin(2*np.pi*f*t)*np.exp(-t*4)*np.minimum(1,t/0.01)
def kick(dur=0.25):
    t=np.arange(int(dur*sr))/sr; f=45+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*14)
rng=np.random.default_rng(1)
def hat(dur=0.05):
    t=np.arange(int(dur*sr))/sr; n=rng.standard_normal(len(t)); n=n-np.convolve(n,np.ones(8)/8,mode='same')
    return n*np.exp(-t*80)
hz=lambda m:440*2**((m-69)/12)
chords=[(48,[60,64,67,72]),(45,[57,60,64,69]),(53,[65,69,72,77]),(43,[62,67,71,74])]
pat=[0,2,1,3,2,1,3,2]
nb=int(D/beat)+1
for b in range(nb):
    bar=b//4; root,notes=chords[bar%4]; t0=b*beat
    add(t0,bass(hz(root-12)),0.55)
    if b%2==0: add(t0,kick(),0.35)
    for h in range(2):
        tt=t0+h*beat/2
        add(tt,pluck(hz(notes[pat[(b*2+h)%8]]+(12 if (bar%4==3 and h==1) else 0))),0.22)
        if h==1: add(tt,hat(),0.10)
    if b%4==0: add(t0,pluck(hz(notes[0]-12),1.2,2.5),0.12)
t=np.arange(N)/sr
# arrivée progressive + fondu final
out*=np.clip(t/2.0,0,1)*np.clip((D-t)/2.5,0,1)
out/=np.abs(out).max()
with wave.open(OUT,"wb") as o:
    o.setnchannels(1);o.setsampwidth(2);o.setframerate(sr);o.writeframes((out*32767).astype(np.int16).tobytes())
