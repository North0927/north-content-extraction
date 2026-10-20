import importlib.util
from pathlib import Path
import tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('media_policy',ROOT/'scripts/media_policy.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
class PolicyTests(unittest.TestCase):
    def test_time_boundary(self):
        self.assertEqual(policy.decide('video',300,0)['analysis_mode'],'detailed')
        self.assertEqual(policy.decide('video',300,0)['baseline_frame_count'],21)
        result=policy.decide('video',301,0)
        self.assertEqual(result['analysis_mode'],'brief')
        self.assertEqual(result['baseline_frame_times_seconds'],[])
    def test_storage_overrides_detail(self):
        self.assertEqual(policy.decide('video',301,0,allow_long_detail=True)['baseline_frame_count'],22)
        self.assertEqual(policy.decide('video',301,300000001,allow_long_detail=True)['analysis_mode'],'brief')
        self.assertEqual(policy.decide('article',None,300000000)['analysis_mode'],'detailed')
        self.assertEqual(policy.decide('article',None,0,projected_additional_bytes=300000001)['analysis_mode'],'brief')
    def test_unknown_not_zero(self):
        self.assertEqual(policy.decide('video',None,0)['analysis_mode'],'brief')
        self.assertEqual(policy.decide('article',None,None)['analysis_mode'],'brief')
    def test_invalid_values(self):
        for value in [-1,True,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):policy.decide('video',value,0)
    def test_storage_readonly(self):
        temporary_root=ROOT/'output'/'test-temp'
        temporary_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(temporary_root.resolve()))
            file=Path(directory)/'素材.txt';file.write_text('实际证据',encoding='utf8')
            before=file.read_bytes();result=policy.inspect_folder(directory)
            self.assertEqual(result['logical_bytes'],len(before))
            self.assertTrue(result['complete']);self.assertEqual(file.read_bytes(),before)
if __name__=='__main__':unittest.main()
