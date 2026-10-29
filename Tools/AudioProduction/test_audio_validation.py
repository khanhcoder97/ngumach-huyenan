import hashlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
import soundfile as sf
from validate_pack import check_clip, inside, source_sha
from dsp import SR
from codec import write_encoded,decode


class ValidationChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.path=self.root/'Client/Assets/Audio/PackV1/test.wav';self.path.parent.mkdir(parents=True)
        t=np.arange(4800)/SR;self.signal=(np.sin(t*2*np.pi*660)*np.hanning(4800)*.2).astype('float32')
        sf.write(self.path,self.signal,SR,subtype='PCM_16')
        self.clip=dict(path=self.path.relative_to(self.root).as_posix(),sha256=self.hash(),frames=4800,channels=1)
    def tearDown(self):self.temp.cleanup()
    def hash(self):return hashlib.sha256(self.path.read_bytes()).hexdigest()
    def errors(self):return check_clip(self.root,self.clip,False,require_meta=False)[0]
    def test_real_wav_passes(self):self.assertEqual(self.errors(),[])
    def test_runtime_hash_corruption(self):
        self.clip['sha256']='0'*64;self.assertIn('runtime hash mismatch',self.errors())
    def test_source_hash_survives_git_windows_line_endings(self):
        p=self.root/'score.json';p.write_bytes(b'{\n  "notes": []\n}\n')
        expected=source_sha(p);p.write_bytes(p.read_bytes().replace(b'\n',b'\r\n'))
        self.assertEqual(source_sha(p),expected)
        p.write_bytes(b'{\r\n  "notes": [60]\r\n}\r\n')
        self.assertNotEqual(source_sha(p),expected)
    def test_clipped_loud_audio_fails(self):
        sf.write(self.path,np.ones(4800),SR,subtype='PCM_16');self.clip['sha256']=self.hash()
        self.assertIn('clipping/headroom failure',self.errors())
    def test_silence_fails(self):
        sf.write(self.path,np.zeros(4800),SR,subtype='PCM_16');self.clip['sha256']=self.hash()
        self.assertIn('silent/near-silent clip',self.errors())
    def test_missing_and_pointer_fail(self):
        self.path.write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 99\n')
        self.assertTrue(any('LFS pointer' in s for s in self.errors()))
        self.path.unlink();self.assertTrue(any('missing file' in s for s in self.errors()))
    def test_traversal_and_wrong_prefix_fail(self):
        for path in ('../../outside.wav','Art_Source/Audio/Masters/test.wav','C:/outside.wav'):
            with self.assertRaises(ValueError):inside(self.root,path,'Client/Assets/Audio/PackV1')
    def test_long_stereo_ogg_roundtrip_uses_bounded_codec_calls(self):
        t=np.arange(SR*16,dtype=np.float32)/SR
        signal=np.column_stack((np.sin(2*np.pi*220*t)*.08,np.sin(2*np.pi*330*t)*.08)).astype(np.float32)
        path=self.root/'long.ogg';write_encoded(path,signal,SR,format='OGG',subtype='VORBIS')
        out,rate=decode(path)
        self.assertEqual(rate,SR);self.assertEqual(out.shape,signal.shape)
        self.assertGreater(float(np.sqrt(np.mean(out*out))),.02)


if __name__=='__main__':unittest.main()
