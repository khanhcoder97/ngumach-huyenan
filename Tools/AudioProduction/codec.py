"""Bounded native codec calls avoid Windows libsndfile large-OGG stack overflow.

See https://github.com/bastibe/python-soundfile/issues/396 . No shared handles.
"""
import numpy as np
import soundfile as sf


def write_encoded(path,data,rate,*,format,subtype=None,**options):
    x=np.asarray(data)
    if x.ndim==1:x=x[:,None]
    with sf.SoundFile(path,mode='w',samplerate=rate,channels=x.shape[1],format=format,subtype=subtype,**options) as f:
        for start in range(0,len(x),4096):f.write(x[start:start+4096])


def decode(path):
    chunks=[]
    with sf.SoundFile(path) as f:
        rate=f.samplerate;channels=f.channels
        while True:
            part=f.read(8192,dtype='float32',always_2d=True)
            if not len(part):break
            chunks.append(part)
    return np.concatenate(chunks) if chunks else np.zeros((0,channels),np.float32),rate
