import numpy as np, wave, sys
sr=44100; T=20.0; n=int(sr*T); t=np.arange(n)/sr
rng=np.random.default_rng(7); out=np.zeros(n)
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
# room tone
room=lp(rng.standard_normal(n),0.02); room/=np.abs(room).max(); out+=0.03*room
env=lambda a,b,fi,fo: np.clip((t-a)/fi,0,1)*np.clip((b-t)/fo,0,1)
# low drone D minor-ish
for f,amp in [(73.42,.10),(110.0,.06),(146.83,.035),(174.61,.025)]:
    out+=amp*env(0,17.5,2.5,0.6)*np.sin(2*np.pi*f*t+np.sin(2*np.pi*.13*t))*(1-0.35*((t>7)&(t<12)))
# vibration buzz + ringtone
for a,b in [(5.15,5.75),(6.05,6.6)]:
    m=env(a,b,.02,.03); out+=0.12*m*np.sign(np.sin(2*np.pi*165*t))*(0.6+0.4*np.sin(2*np.pi*30*t))*0.5
def note(at,f,amp,dec=1.6,h=(1,.45,.2,.08)):
    d=t-at; m=d>=0; d=np.clip(d,0,None)
    s=sum(w*np.sin(2*np.pi*f*(k+1)*d*(1+0.0008*k)) for k,w in enumerate(h))
    return m*amp*np.exp(-d*dec)*(1-np.exp(-d*200))*s
for at,f in [(5.15,659.25),(5.3,783.99),(5.45,987.77),(6.05,659.25),(6.2,783.99),(6.35,987.77)]:
    out+=note(at,f,0.05,dec=5)
out+=note(6.8,2400,0.04,dec=60)  # answer click
# sad piano in close-up
for at,f,a in [(12.3,110.0,.10),(12.3,220.0,.07),(12.3,329.63,.06),(13.4,523.25,.06),(14.4,493.88,.06),(15.5,440.0,.07),(15.5,164.81,.06),(16.6,329.63,.05)]:
    out+=note(at,f,a,dec=0.9)
out*=1-np.clip((t-17.3)/0.3,0,1)*(t<17.75)
# final chord under end card
for f,a in [(110.0,.09),(164.81,.06),(261.63,.05),(329.63,.04)]:
    out+=note(17.8,f,a,dec=0.55)
# reverb
y=out.copy()
for dly,g in [(0.061,.32),(0.113,.27),(0.173,.22),(0.257,.17),(0.371,.12),(0.523,.08)]:
    k=int(dly*sr); y[k:]+=g*out[:-k]
y*=np.clip((T-t)/0.6,0,1)*np.clip(t/0.3,0,1)
y=y/np.abs(y).max()*0.6
st=np.stack([y,np.roll(y,int(.009*sr))],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
