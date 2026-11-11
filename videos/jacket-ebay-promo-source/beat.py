import numpy as np, wave, sys
sr=44100; T=20.0; n=int(sr*T); t=np.arange(n)/sr; out=np.zeros((n,2)); rng=np.random.default_rng(3)
def add(sig,at,g=1.0,pan=0.0):
    i=int(at*sr); m=min(len(sig),n-i)
    if m<=0: return
    out[i:i+m,0]+=sig[:m]*g*(1-pan); out[i:i+m,1]+=sig[:m]*g*(1+pan)
def kick(d=.35):
    tt=np.arange(int(d*sr))/sr; f=45+110*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/sr
    return np.tanh(2.2*np.sin(ph)*np.exp(-tt*7))
def snare():
    tt=np.arange(int(.22*sr))/sr; nz=rng.standard_normal(len(tt))
    nz=np.diff(np.concatenate([[0],nz]))  # brighter
    return (0.6*nz*np.exp(-tt*22)+0.5*np.sin(2*np.pi*190*tt)*np.exp(-tt*30))
def hat(d=.05):
    tt=np.arange(int(d*sr))/sr; nz=np.diff(np.concatenate([[0],rng.standard_normal(len(tt))]))
    return nz*np.exp(-tt*90)
def bass(f,d):
    tt=np.arange(int(d*sr))/sr; s=np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt)
    return np.tanh(1.5*s)*np.minimum(1,tt/.01)*np.exp(-tt*1.8)
def whoosh(d=.35,rev=False):
    tt=np.arange(int(d*sr))/sr; nz=rng.standard_normal(len(tt)); env=np.sin(np.pi*tt/d)**2
    y=np.convolve(nz,np.ones(12)/12,'same')*env; return y[::-1] if rev else y
def impact():
    tt=np.arange(int(1.2*sr))/sr; return 0.9*kick(1.2)[:len(tt)]+0.3*np.convolve(rng.standard_normal(len(tt)),np.ones(30)/30,'same')*np.exp(-tt*4)
B=0.5  # 120 bpm
# intro: hits on each word, riser into drop
for a in [.25,.75,1.25,1.75]: add(kick(),a,.8); add(hat(.08),a,.3)
tt=np.arange(int(1.0*sr))/sr; riser=np.convolve(rng.standard_normal(len(tt)),np.ones(6)/6,'same')*(tt/1.0)**2*0.5
riser+=0.15*np.sin(2*np.pi*(200+800*tt**2)*tt)*(tt/1.0)
add(riser,2.0,.7)
add(impact(),3.0,1.0)
# groove 3-15, and 15-19.5
roots=[55.0,55.0,49.0,43.65]   # A A G F
for k in range(int((19.5-3)/B)):
    at=3+k*B
    if abs(at-15)<1e-6: add(impact(),at,.9); continue
    add(kick(),at,.85)
    if k%2==1: add(snare(),at,.5)
    add(hat(),at+B/2,.22,.3); add(hat(.03),at+B/4,.12,-.3); add(hat(.03),at+3*B/4,.12,-.3)
    if k%2==0: add(bass(roots[(k//4)%4],0.95),at,.35)
# whooshes into cuts
for c in [5.5,8,9.75,11.5,13.25]: add(whoosh(),c-.3,.35)
add(whoosh(.5),14.6,.4)
y=out*np.clip((19.9-t)/0.5,0,1)[:,None]
y/=np.abs(y).max(); y*=0.85
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y*32767).astype('<i2').tobytes()); w.close()
