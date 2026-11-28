import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from backup_sqlite import backup, restore, NAMES

class BackupTest(unittest.TestCase):
    def test_backup_restore_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dbs = [root / name for name in NAMES]
            for i, path in enumerate(dbs):
                with closing(sqlite3.connect(path)) as db, db:
                    db.execute("CREATE TABLE sample (value INTEGER)")
                    db.execute("INSERT INTO sample VALUES (?)", (i,))
            saved = backup(*dbs, root / "saved")
            recovered = restore(saved, root / "recovered")
            for i, name in enumerate(NAMES):
                with closing(sqlite3.connect(recovered / name)) as db:
                    self.assertEqual(db.execute("SELECT value FROM sample").fetchone(), (i,))
            with self.assertRaises(FileExistsError):
                restore(saved, recovered)
            with self.assertRaises(FileExistsError):
                backup(*dbs, saved)
            with self.assertRaises(ValueError):
                backup(dbs[0], dbs[0], root / "same")
            sidecar = saved / (NAMES[0] + "-wal")
            sidecar.touch()
            with self.assertRaisesRegex(ValueError, "auxiliar SQLite inesperado"):
                restore(saved, root / "unexpected-sidecar")
            self.assertFalse((root / "unexpected-sidecar").exists())
            sidecar.unlink()
            manifest = saved / "manifest.json"
            manifest_bytes = manifest.read_bytes()
            manifest.write_bytes(b" " * 4097)
            with self.assertRaisesRegex(ValueError, "4 KiB"):
                restore(saved, root / "oversized-manifest")
            self.assertFalse((root / "oversized-manifest").exists())
            manifest.write_bytes(manifest_bytes)
            # Modify a valid SQLite database: integrity passes but checksum fails.
            with closing(sqlite3.connect(saved / NAMES[0])) as db, db:
                db.execute("UPDATE sample SET value=999")
            with self.assertRaises(ValueError):
                restore(saved, root / "tampered")
            self.assertFalse((root / "tampered").exists())

if __name__ == "__main__":
    unittest.main()
