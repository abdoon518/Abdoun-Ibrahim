import numpy as np, wave, sys
sr=44100; T=15.0; t=np.arange(int(sr*T))/sr
def tone(f,amp,start,end,att=1.2,rel=1.5):
    env=np.clip((t-start)/att,0,1)*np.clip((end-t)/rel,0,1)
    return amp*env*(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)+0.12*np.sin(2*np.pi*3*f*t))
chords=[(0,4,[220.0,277.18,329.63,415.30]),(3.6,8,[185.0,233.08,277.18,369.99]),
        (7.4,11.8,[146.83,220.0,277.18,329.63]),(11.4,15,[164.81,207.65,246.94,329.63])]
x=np.zeros_like(t)
for s,e,fs in chords:
    for i,f in enumerate(fs): x+=tone(f,0.05 if i else 0.07,s,e,1.5,1.8)
x*=1+0.08*np.sin(2*np.pi*0.25*t)
def chime(at,f):
    d=np.clip(t-at,0,None); m=t>=at
    return m*0.12*np.exp(-d*2.2)*(np.sin(2*np.pi*f*d)+0.4*np.sin(2*np.pi*f*2.01*d)+0.2*np.sin(2*np.pi*f*3.02*d))
for at,f in [(4.6,1318.5),(4.75,1760.0),(12.2,1318.5),(12.35,1661.2),(13.4,2217.5)]: x+=chime(at,f)
# simple reverb via delays
y=x.copy()
for dly,g in [(0.083,0.35),(0.131,0.28),(0.197,0.22),(0.29,0.15)]:
    n=int(dly*sr); y[n:]+=g*x[:-n]
y*=np.clip((T-t)/1.0,0,1)
y=y/np.max(np.abs(y))*0.5
st=np.stack([y,np.roll(y,int(0.012*sr))],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
