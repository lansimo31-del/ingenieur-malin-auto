import numpy as np, wave, subprocess
sr=44100; D=53.4
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","../a/voice.wav","-ar",str(sr),"-ac","1","-af","apad=whole_dur=53.4","-t","53.4","vo.wav"])
w=wave.open("vo.wav"); v=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; v=np.pad(v,(0,int(D*sr)-len(v)))[:int(D*sr)]
rng=np.random.default_rng(3); n=rng.standard_normal(int(D*sr))
# bruit rose doux, filtré
k=np.ones(400)/400; amb=np.convolve(n,k,mode='same'); amb=np.convolve(amb,np.ones(60)/60,mode='same')
amb=amb/np.abs(amb).max()*0.05
t=np.arange(len(v))/sr
amb*=np.clip(t/1.5,0,1)*np.clip((D-t)/1.5,0,1)
# ducking
env=np.convolve(np.abs(v),np.ones(2205)/2205,mode='same'); duck=1-0.6*np.clip(env*8,0,1)
bed=amb*duck
def tick(at,f=880,g=0.05):
    a=int(at*sr); m=int(0.09*sr); tt=np.arange(m)/sr
    bed[a:a+m]+=g*np.sin(2*np.pi*f*tt)*np.exp(-tt*45)
for i,tm in enumerate([7.44,25.65,30.38,32.6,35.9]): tick(tm+0.05,660+80*i)
tick(50.52,990,0.06)
out=np.clip(v+bed,-1,1)
with wave.open("mix.wav","wb") as o:
    o.setnchannels(1);o.setsampwidth(2);o.setframerate(sr);o.writeframes((out*32767).astype(np.int16).tobytes())
