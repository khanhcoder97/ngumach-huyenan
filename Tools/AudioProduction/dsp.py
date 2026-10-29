"""Original modal/granular/instrument synthesis, 48 kHz. Never loads a sample."""
import hashlib
import math
import numpy as np

SR = 48000


def seed_for(key):
    return int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'little')


def rng_for(key):
    return np.random.Generator(np.random.PCG64(seed_for(key)))


def times(seconds):
    return np.arange(max(32, round(seconds*SR)), dtype=np.float64)/SR


def noise(n, rng, low=100, high=6000, slope=0):
    x = rng.standard_normal(n)
    f = np.fft.rfftfreq(n, 1/SR)
    shape = 1/(1+(f/high)**8)
    if low: shape *= (f/max(low,1))**2/(1+(f/max(low,1))**2)
    shape *= (np.maximum(f,20)/500)**(slope/2)
    y = np.fft.irfft(np.fft.rfft(x)*shape,n=n)
    return y/(np.std(y)+1e-12)


def env(t, duration, attack=.003, decay=5):
    return (1-np.exp(-t/max(attack,.0003)))*np.exp(-decay*t/max(duration,.001))


def glide(t, start, end, duration):
    rate=(end-start)/max(duration,.001)
    return np.sin(2*np.pi*(start*t+.5*rate*t*t))


def modal(t, frequency, ratios, duration, rng, damping=5):
    out=np.zeros(len(t))
    for i,r in enumerate(ratios):
        f=frequency*r*(1+rng.uniform(-.004,.004))
        if f>15000: continue
        out += np.sin(2*np.pi*f*t+rng.uniform(-.06,.06))*env(t,duration,.0015,damping+i*.8)/(1+i*.85)
    return out


def add_at(out, signal, when):
    start=round(when*SR)
    if start>=len(out): return
    n=min(len(signal),len(out)-start)
    if n>0: out[start:start+n]+=signal[:n]


def pluck(t, f, duration, bright=1):
    result=np.zeros(len(t))
    for h in range(1,9):
        if f*h>16000: break
        result+=np.sin(2*np.pi*f*h*t)*np.exp(-t*(3+1.5*h)/max(duration,.05))/(h**(1.4/bright))
    return result*(1-np.exp(-t/.0015))


def render_sfx(cue, variation):
    key=cue['cueKey'].lower(); family=cue['synthFamily']; rng=rng_for(key+f'/{variation}')
    slot=cue.get('skillSlot',0)
    duration=([.48,.30,.28,.72,.28,1.35][slot-1] if slot else .48)
    if '/step_' in key or 'mount_step' in key: duration=.21
    if family in ('ui','error','paper','coins'): duration=.18 if family=='ui' else .36
    if any(w in key for w in ('success','victory','legendary','level_up','reconnect')): duration=1.15
    if family.startswith('warning_'): duration=.86 if 'warning' in key or 'countdown' in key else 1.3
    if family.startswith('creature_'): duration=.32 if 'attack' in key else .25 if 'hurt' in key else .76
    if family=='horn': duration=1.7
    if family=='cinema': duration=3.1
    duration*=1+(variation-1)*.035
    t=times(duration); n=len(t); out=np.zeros(n); pitch=1+rng.uniform(-.035,.035)
    if family=='metal':
        f=(570+slot*83)*pitch
        if 'hammer' in key or 'repair' in key: f=340*pitch
        if slot==3: f*=([.9,1,1.14][variation]); duration_weight=[.75,1,1.35][variation]
        else: duration_weight=1
        out=modal(t,f,[1,1.43,2.16,3.12,4.53],duration,rng,5)*duration_weight
        out+=.27*noise(n,rng,900,6500)*env(t,duration,.002,13)
        if slot in (2,5): out+=.65*noise(n,rng,250,4400)*np.sin(np.pi*np.minimum(t/duration,1))**1.5
        if slot==6: out+=.55*glide(t,1400,270,duration)*env(t,duration,.006,3)
    elif family=='fire':
        flame=noise(n,rng,120,4800,-.6)
        out=flame*env(t,duration,.012,3)*(1+.2*np.sin(2*np.pi*(17+slot)*t))
        out+=.35*glide(t,210+70*slot,60+20*slot,duration)*env(t,duration,.003,5)
        for _ in range(4+slot):
            u=times(rng.uniform(.015,.05)); spark=noise(len(u),rng,2400,12000)*env(u,u[-1],.0005,6)
            add_at(out,spark*.17,rng.uniform(0,duration*.8))
    elif family=='water':
        out=.33*noise(n,rng,280,4600,-.4)*env(t,duration,.012,3)
        for i in range(3+slot):
            d=rng.uniform(.035,.095); u=times(d); f=rng.uniform(330,1500)*pitch
            drop=glide(u,f,f*(1.2+rng.uniform(0,.5)),d)*env(u,d,.0015,5)
            add_at(out,drop*(.4 if slot not in (4,6) else .2),rng.uniform(0,duration*.6))
        if slot in (3,4,6):
            for i,f in enumerate((420,630,840)):
                out+=.23*np.sin(2*np.pi*f*pitch*t)*env(t,duration,.028,2+i*.2)
    elif family=='stone':
        out=.9*noise(n,rng,45,1200,-1)*env(t,duration,.0015,7)
        out+=modal(t,(88+slot*17)*pitch,[1,1.71,2.9,5.1],duration,rng,7)*.8
        out+=.18*noise(n,rng,1200,6200)*env(t,duration,.015,3)
        for _ in range(5):
            u=times(.025); add_at(out,noise(len(u),rng,500,4000)*env(u,.025,.001,6)*.12,rng.uniform(.02,duration*.7))
    elif family=='wood':
        f=(185+slot*58)*pitch
        out=pluck(t,f,duration,1.1)*.75
        out+=noise(n,rng,900,5000)*env(t,duration,.006,7)*.4
        if slot in (2,4,6):
            out+=.25*pluck(t,f*1.5,duration*.8)
    elif family.startswith('creature_'):
        creature=family.removeprefix('creature_')
        roots={'aquatic':210,'roots':108,'beast':92,'insect':920,'raider':145,'construct':118,'engine':78,'rift':310}
        f=roots[creature]*pitch
        end=f*(.42 if 'death' in key else .86 if 'hurt' in key else 1.28)
        out=glide(t,f,end,duration)*env(t,duration,.012,3)
        out+=.35*glide(t,f*2.1,end*2.3,duration)*env(t,duration,.01,4)
        grit=noise(n,rng,180,2300,-.3)*env(t,duration,.005,4)
        out+=grit*(.8 if creature in ('roots','construct','engine') else .4)
        if creature=='insect': out*=.6+.4*np.sin(2*np.pi*45*t)**2
        if creature in ('aquatic','rift'): out+=.35*modal(t,f*3,[1,1.5,2.18],duration,rng,4)
        if creature=='raider': out+=noise(n,rng,700,3400)*env(t,duration,.018,5)*.28
    elif family.startswith('warning_'):
        base={'warning_water':320,'warning_wood':245,'warning_metal':410,'warning_rift':290}[family]*pitch
        pattern=[0,.22,.46]
        if 'emerge' in key: pattern=[0,.36]
        if 'bubble' in key: pattern=[0,.15,.32,.56]
        if 'success' in key: notes=[1.5,1.25,1]
        elif 'intro' in key: notes=[.75,1,1.12]
        else: notes=[1,1.19,1.5,1.66]
        for i,when in enumerate(pattern):
            u=times(min(.32,duration-when)); tone=modal(u,base*notes[i%len(notes)],[1,2,2.99],u[-1],rng,4)
            add_at(out,tone,when)
        out+=noise(n,rng,160,2200,-.8)*env(t,duration,.03,5)*.15
    elif family in ('reward','crystal','coins','ui','error','paper','horn','cinema'):
        if family=='paper':
            out=noise(n,rng,1300,8500)*env(t,duration,.008,5)*(0.4+.6*np.sin(np.pi*np.minimum(t/duration,1))**2)
            out+=.06*pluck(t,190*pitch,duration)
        elif family=='horn':
            f=147*pitch; shape=np.minimum(1,t/.1)*np.minimum(1,(duration-t)/.25)
            out=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2*t)+.14*np.sin(2*np.pi*f*3*t))*shape
            out+=.04*noise(n,rng,200,1600)*shape
        else:
            ratios=[1,1.25,1.5,2] if family in ('reward','cinema') else [1,1.334,2] if family=='error' else [1,1.5,2.5]
            f=(285 if family=='error' else 880 if family=='coins' else 610)*pitch
            if family=='cinema': f=220*pitch
            for i,r in enumerate(ratios):
                u=times(max(.03,duration-i*duration*.14)); b=modal(u,f*r,[1,2,3.98],u[-1],rng,4 if family!='cinema' else 2)
                add_at(out,b/(1+i*.4),i*duration*.14)
            if family=='error': out+=noise(n,rng,130,750)*env(t,duration,.008,7)*.15
    elif family in ('combat','rift'):
        out=noise(n,rng,180,6000)*env(t,duration,.008,5)
        out+=.5*glide(t,530*pitch,130*pitch,duration)*env(t,duration,.003,5)
    else:
        raise ValueError('Unimplemented synth family '+family)
    return out.astype(np.float32)


def instrument(kind, midi, seconds, rng):
    t=times(seconds); f=440*2**((midi-69)/12)
    if kind=='pluck': return pluck(t,f,seconds,1.05).astype(np.float32)
    if kind=='flute':
        phase=2*np.pi*f*t+.07*np.sin(2*np.pi*4.7*t)
        breath=noise(len(t),rng,1200,6500)*.035
        shape=np.sin(np.pi*np.minimum(t/max(seconds,.001),1))**.65
        return ((np.sin(phase)+.17*np.sin(2*phase)+.04*np.sin(3*phase)+breath)*shape).astype(np.float32)
    if kind=='bass': return ((np.sin(2*np.pi*f*t)+.2*np.sin(4*np.pi*f*t))*env(t,seconds,.012,2.5)).astype(np.float32)
    if kind=='drum': return (glide(t,145,49,seconds)*env(t,seconds,.001,8)+noise(len(t),rng,600,4000)*env(t,seconds,.001,14)*.09).astype(np.float32)
    if kind=='woodblock': return (modal(t,f,[1,2.76,4.5],seconds,rng,8)+noise(len(t),rng,1900,7000)*env(t,seconds,.001,15)*.12).astype(np.float32)
    if kind=='shaker': return (noise(len(t),rng,3500,13000)*env(t,seconds,.004,7)).astype(np.float32)
    raise ValueError(kind)


def circular_add(buf, signal, start, pan=0):
    start=int(start)%len(buf)
    angle=(max(-1,min(1,pan))+1)*np.pi/4
    stereo=signal[:,None]*np.array([np.cos(angle),np.sin(angle)],dtype=np.float32)
    first=min(len(stereo),len(buf)-start)
    buf[start:start+first]+=stereo[:first]
    if first<len(stereo): buf[:len(stereo)-first]+=stereo[first:]


def render_music(key, config):
    rng=rng_for('score/'+key); beat=60/config['bpm']; length=round(64*beat*SR)
    layers={k:np.zeros((length,2),np.float32) for k in ('melody','plucked','bass','percussion')}
    events=[]; scale=config['scale']; root=config['root']; motif=config['motif']; mood=config['mood']
    def note(kind, midi, start, beats, velocity, pan, layer):
        events.append(dict(instrument=kind,midi=midi,startBeat=round(start,4),durationBeats=beats,velocity=velocity,pan=pan,layer=layer))
        audio=instrument(kind,midi,max(.045,beats*beat),rng_for('music-note/'+key+'/'+str(len(events))))*velocity
        circular_add(layers[layer],audio,round(start*beat*SR),pan)
    for bar in range(16):
        section=bar//4; degree=[0,3,1,4][section]%len(scale)
        tonic=root+scale[degree]
        note('bass',tonic-12,bar*4,2.5,.24,0,'bass')
        if mood not in ('quiet','underwater'): note('bass',tonic-5,bar*4+2,1.6,.15,0,'bass')
        for step in range(8):
            if rng.random()>config['density']: continue
            d=(degree+[0,2,3,1,4,2,3,1][step]+section)%len(scale)
            note('pluck',root+12+scale[d],bar*4+step*.5,.9,.13 if mood!='boss' else .10,(-.4 if step%2 else .35),'plucked')
        if bar>=2:
            for j in range(2 if mood!='quiet' else 1):
                idx=(bar*2+j+section)%len(motif)
                d=motif[idx]%len(scale)
                # Three related phrases plus a bridge; no pre-existing melody is imported.
                if section==2: d=(d+2)%len(scale)
                octave=12 if section in (0,3) else 24
                note('flute',root+octave+scale[d],bar*4+j*2+(0.5 if bar%3==1 else 0),1.6,.16 if mood!='boss' else .12,.15,'melody')
        if mood not in ('quiet','underwater','rain') or section in (1,3):
            for b in (0,2): note('drum',48,bar*4+b,.55,.16 if mood in ('boss','frontier','finale') else .075,0,'percussion')
            note('woodblock',76 if mood!='desert' else 71,bar*4+1.5,.2,.07,-.25,'percussion')
            if mood in ('city','desert','boss','finale'):
                for b in (0.5,1.5,2.5,3.5): note('shaker',80,bar*4+b,.12,.035,.3,'percussion')
    score=dict(**config,bars=16,beatsPerBar=4,durationSamples=length,sampleRate=SR,events=events,
        authorship='Original motif, score and DSP; no third-party sample or existing tune loaded')
    return finish_music(layers,root),score


def finish_music(layers,root):
    mix=sum(layers.values()); length=len(mix)
    for delay,gain in ((.113,.12),(.227,.08),(.401,.05)):
        mix+=np.roll(mix,round(delay*SR),axis=0)*gain
    # Extremely quiet, exactly periodic drone; not a non-integer-cycle oscillator at the seam.
    t=np.arange(length,dtype=np.float64)/SR
    for midi in (root-12,root+7):
        hz=440*2**((midi-69)/12); cycles=round(hz*length/SR)
        drone=np.sin(2*np.pi*cycles*np.arange(length)/length)*.018*(.8+.2*np.cos(2*np.pi*2*t/(length/SR)))
        mix+=drone[:,None]
    return mix


def render_score(key,score):
    """Artist-edited score playback uses the same per-note seeds as composition."""
    beat=60/score['bpm']; length=score['durationSamples']
    layers={k:np.zeros((length,2),np.float32) for k in ('melody','plucked','bass','percussion')}
    for index,e in enumerate(score['events'],1):
        audio=instrument(e['instrument'],e['midi'],max(.045,e['durationBeats']*beat),rng_for('music-note/'+key+'/'+str(index)))*e['velocity']
        circular_add(layers[e['layer']],audio,round(e['startBeat']*beat*SR),e['pan'])
    return finish_music(layers,score['root'])


def render_ambience(key, seconds=16):
    rng=rng_for('ambience/'+key); t=times(seconds); n=len(t)
    low,high,slope=120,5000,-1
    if 'rain' in key: low,high,slope=650,10000,-.2
    elif 'underwater' in key: low,high,slope=25,950,-1.6
    elif 'rift' in key: low,high,slope=70,2800,-1
    elif 'forge' in key: low,high,slope=70,4200,-.7
    elif 'waterfall' in key: low,high,slope=60,7600,-.9
    elif 'crowd' in key or 'city' in key: low,high,slope=180,2200,-1
    mid=noise(n,rng,low,high,slope); side=noise(n,rng,low,high,slope)
    modulation=.8+.12*np.sin(2*np.pi*3*t/seconds)+.08*np.cos(2*np.pi*7*t/seconds)
    out=np.column_stack((mid*.83+side*.27,mid*.83-side*.27))*modulation[:,None]*.18
    if any(x in key for x in ('shore','drips','water','rain')):
        count=16 if 'rain' not in key else 38 if 'heavy' in key else 20
        for _ in range(count):
            u=times(rng.uniform(.025,.1)); f=rng.uniform(420,1900)
            drop=glide(u,f,f*1.4,u[-1])*env(u,u[-1],.001,5)*rng.uniform(.025,.07)
            circular_add(out,drop,round(rng.uniform(0,seconds)*SR),rng.uniform(-.8,.8))
    if 'crowd' in key or 'city' in key or 'forge' in key:
        for i in range(9 if 'forge' not in key else 13):
            kind='woodblock' if 'forge' not in key else 'pluck'
            strike=instrument(kind,49+rng.integers(0,24),.18,rng)*(.025 if 'forge' not in key else .045)
            circular_add(out,strike,round(rng.uniform(0,seconds)*SR),rng.uniform(-.7,.7))
    if 'rift' in key or 'mountain' in key or 'wind' in key:
        cycles=round((58 if 'rift' in key else 92)*seconds)
        drone=np.sin(2*np.pi*cycles*np.arange(n)/n+.4*np.sin(2*np.pi*2*t/seconds))
        out+=drone[:,None]*.022
    return out.astype(np.float32)


def master(data, *, loop=False, bus='SFX'):
    x=np.asarray(data,dtype=np.float64)
    if x.ndim==1: x=x[:,None]
    if not np.all(np.isfinite(x)): raise ValueError('Non-finite DSP output')
    x-=x.mean(axis=0,keepdims=True)
    if not loop:
        window=np.ones(len(x)); attack=min(round(.004*SR),len(x)//4); release=min(round(.035*SR),len(x)//3)
        window[:attack]=np.sin(np.linspace(0,np.pi/2,attack))**2
        window[-release:]=np.cos(np.linspace(0,np.pi/2,release))**2
        window[-1]=0
        x*=window[:,None]
        x-=window[:,None]*(x.mean(axis=0,keepdims=True)/(window.mean()+1e-12))
    target_db={'Music':-24,'Ambience':-33,'UI':-28}.get(bus,-25)
    rms=np.sqrt(np.mean(x*x)); peak=np.max(np.abs(x))
    if rms<1e-10: raise ValueError('Silent DSP output')
    x*=min(10**(target_db/20)/rms,.50/(peak+1e-12))
    return x.astype(np.float32)


def metrics(data):
    x=np.asarray(data,dtype=np.float64)
    if x.ndim==1:x=x[:,None]
    delta=np.abs(np.diff(x,axis=0))
    q=float(np.quantile(delta,.995)) if len(delta) else 1
    jump=float(np.max(np.abs(x[0]-x[-1])))
    return dict(peak=float(np.max(np.abs(x))),rmsDb=round(float(20*np.log10(np.sqrt(np.mean(x*x))+1e-12)),3),
        dc=float(np.max(np.abs(x.mean(axis=0)))),loopBoundaryJump=jump,
        seamRelativeToInterior995=round(jump/(q+1e-9),5),firstLastPeak=float(np.max(np.abs(x[[0,-1]]))))
