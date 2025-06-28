import unittest, tempfile, time, os
from pathlib import Path
from collectory.collector import rotate_backups
class TestBackupRotation(unittest.TestCase):
    def test_rotate_backups(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            prefix = "testcol"
            paths = []
            for i in range(5):
                p = d / f"{prefix}_{i}_backup.json"
                p.write_text("data")
                stamp  = time.time() + i
                os.utime(p, (stamp, stamp))
                paths.append(p)
                time.sleep(0.01)
            rotate_backups(d, prefix, keep=3)
            remaining = sorted(p.name for p in d.iterdir())
            
            self.assertCountEqual(
                remaining,
                [paths[4].name, paths[3].name, paths[2].name]
            )
        
if __name__ == "__main__":
    unittest.main()