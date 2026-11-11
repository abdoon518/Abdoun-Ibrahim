import numpy as np, wave, sys
sr=44100; T=20.0; n=int(sr*T); t=np.arange(n)/sr; out=np.zeros((n,2)); rng=np.random.default_rng(5)
B=60/100  # 100 bpm
def add(sig,at,g=1.0,pan=0.0):
    i=int(at*sr); m=min(len(sig),n-i)
    if m>0: out[i:i+m,0]+=sig[:m]*g*(1-pan); out[i:i+m,1]+=sig[:m]*g*(1+pan)
def tt(d): return np.arange(int(d*sr))/sr
def kick():
    x=tt(.3); f=50+70*np.exp(-x*30); return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-x*9)
def snap():
    x=tt(.18); nz=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); return nz*np.exp(-x*35)*.6
def shaker():
    x=tt(.06); nz=np.diff(np.concatenate([[0],rng.standard_normal(len(x))])); return nz*np.sin(np.pi*x/.06)**2*.25
def pluck(f,d=1.2,b=0.5):
    x=tt(d); s=sum(a*np.sin(2*np.pi*f*k*x) for k,a in [(1,1),(2,.35),(3,.12),(4,.05)])
    return s*np.exp(-x*(2.5+b))*np.minimum(1,x/.004)
def pad(fs,d):
    x=tt(d); env=np.minimum(1,x/.4)*np.minimum(1,(d-x)/.4)
    return env*sum(np.sin(2*np.pi*f*x)+.2*np.sin(2*np.pi*2.003*f*x) for f in fs)/len(fs)
def bell(f):
    x=tt(1.5); return (np.sin(2*np.pi*f*x)+.4*np.sin(2*np.pi*f*2.76*x)*np.exp(-x*6))*np.exp(-x*3)*np.minimum(1,x/.002)
mid=lambda m:440*2**((m-69)/12)
# Fmaj7 - Em7 - Dm7 - Cmaj7 (two beats... one bar each = 4 beats)
chords=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]
bassn=[41,40,38,36]
bar=4*B; nb=int(T/bar)+1
for b in range(nb):
    at=b*bar; ch=chords[b%4]
    add(pad([mid(m) for m in ch],bar+.3),at,.10)
    for k in range(8):  # eighth-note plucked arpeggio
        m=ch[[0,2,1,3,2,1,3,2][k]]+12
        add(pluck(mid(m),.9),at+k*B/2,.10,(-.3 if k%2 else .3))
    if at>=2.9:  # drums after the intro
        add(pluck(mid(bassn[b%4]),bar,-1.6),at,.28)
        add(pluck(mid(bassn[b%4]),B,-1),at+2.5*B,.18)
        for k in range(4):
            add(kick(),at+k*B,.45 if k in(0,2) else .0)
            if k in(1,3): add(snap(),at+k*B,.35)
            for s in range(2): add(shaker(),at+k*B+s*B/2+B/4,.5,.2)
# little bell melody accents
mel=[(3.0,76),(3.6,79),(4.2,81),(8.0,77),(8.6,76),(9.2,72),(14.0,76),(14.6,79),(15.2,84),(17.4,83),(18.0,79),(18.6,76)]
for at,m in mel: add(bell(mid(m)),at,.12,.2)
add(bell(mid(88)),2.95,.10,-.3)
y=out.copy()
for dly,g in [(.09,.3),(.15,.25),(.23,.18),(.34,.12),(.5,.08)]:
    k=int(dly*sr); y[k:,0]+=g*out[:-k,1]; y[k:,1]+=g*out[:-k,0]
y*=(np.clip(t/.6,0,1)*np.clip((T-t)/1.2,0,1))[:,None]
y/=np.abs(y).max(); y*=.8
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y*32767).astype('<i2').tobytes()); w.close()
