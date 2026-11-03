import wave,numpy as np,re,json
from scipy.signal import butter,lfilter,find_peaks
sil=[float(x) for x in open('sil.txt').read().split()]
w=wave.open('voice.wav');sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)/32768.;D=len(a)/sr
b,c=butter(3,[250/(sr/2),3200/(sr/2)],'band');x=lfilter(b,c,a)
env=np.abs(x);k=int(sr*0.03);env=np.convolve(env,np.ones(k)/k,'same')
b2,c2=butter(2,12/(sr/2));env=lfilter(b2,c2,env)
p,_=find_peaks(env,distance=int(sr*0.07),prominence=0.02*env.max());pk=p/sr
segs=[];t=0.0
for i in range(0,len(sil),2):
    s=sil[i]; e=sil[i+1] if i+1<len(sil) else D
    segs.append((t,s)); t=e
if t<D-0.05: segs.append((t,D))
segs=[(a_,b_) for a_,b_ in segs if b_-a_>0.06]
text=open('/tmp/claude-0/work/stylo2/out/texte-voix-off-enzo-episode-02-stylo-a-bille.txt').read()
words=[w_ for w_ in text.split() if re.search(r"\w",w_)]
def syl(w_):
    x=re.sub(r"[^a-zéèêàâîôûçù']","",w_.lower());x=x.replace("'","")
    return max(1,len(re.findall(r"[aeiouyéèêàâîôûù]+",x)))
wt=[syl(w_) for w_ in words]
cnt=[int(((pk>=a_-0.04)&(pk<=b_+0.04)).sum()) for a_,b_ in segs]
N=len(words);M=len(segs);cum=np.cumsum([0]+wt)
print(N,sum(wt),sum(cnt),M)
# DP : coût sur nb de syllabes (tolère mute e) + bonus coupure fin de phrase/ponctuation
punct=[1 if re.search(r"[.?!:,]$",w_) else 0 for w_ in words]
dp=np.full((M+1,N+1),1e9);bk={};dp[0][0]=0
for m in range(1,M+1):
    for j in range(N+1):
        for i in range(max(0,j-14),j+1):
            if dp[m-1][i]>=1e9: continue
            s=cum[j]-cum[i];nw=j-i
            exp=s-0.3*nw
            cost=(exp-cnt[m-1])**2*1.0 if nw>0 else 1.5
            if nw>0 and j<N and not punct[j-1]: cost+=2.0   # une pause sans ponctuation coûte
            c_=dp[m-1][i]+cost
            if c_<dp[m][j]: dp[m][j]=c_;bk[(m,j)]=i
j=N;cuts=[]
for m in range(M,0,-1): i=bk[(m,j)];cuts.append((m,i,j));j=i
cuts.reverse()
res=[]
for m,i,j in cuts:
    a_,b_=segs[m-1]
    print(f"{a_:.2f}-{b_:.2f} [{cnt[m-1]}] "+' '.join(words[i:j]))
    if j>i:
        pks=pk[(pk>=a_-0.04)&(pk<=b_+0.04)]
        ws=wt[i:j];tot=sum(ws);c_=0
        for kk in range(i,j):
            idx=min(max(len(pks)-1,0),int(round(c_*len(pks)/tot))) if len(pks) else 0
            st=float(max(a_,(pks[idx]-0.06) if len(pks) else a_))
            res.append([words[kk],round(st,3)]);c_+=wt[kk]
# fins de mots
out=[]
for n_,(wd,st) in enumerate(res):
    en=res[n_+1][1] if n_+1<len(res) else D
    out.append([wd,st,min(en,st+0.9)])
json.dump(out,open('words.json','w'),ensure_ascii=False)
