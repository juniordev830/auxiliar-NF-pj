import sqlite3
import json
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from backup_sqlite import backup, restore, verify, NAMES

class BackupTest(unittest.TestCase):
    def test_backup_restore_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dbs = [root / name for name in NAMES]
            for i, path in enumerate(dbs):
                with closing(sqlite3.connect(path)) as db, db:
                    for table in (("Pessoas", "Transacoes") if i == 0 else ("Lancamentos",)):
                        db.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
                    db.execute("CREATE TABLE sample (value INTEGER)")
                    db.execute("INSERT INTO sample VALUES (?)", (i,))
            saved = backup(*dbs, root / "saved")
            before = {p.name: p.read_bytes() for p in saved.iterdir()}
            self.assertEqual(verify(saved), saved)
            self.assertEqual({p.name: p.read_bytes() for p in saved.iterdir()}, before)
            sidecar = Path(str(saved / NAMES[0]) + "-wal")
            sidecar.write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "arquivo auxiliar"):
                verify(saved)
            sidecar.unlink()
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
            with self.assertRaisesRegex(ValueError, "Esquema incompatível"):
                backup(dbs[1], dbs[0], root / "swapped")
            self.assertFalse((root / "swapped").exists())
            manifest = saved / "manifest.json"
            original = manifest.read_text(encoding="utf-8")
            for invalid in ([], {"version": 1, "files": None}, {"version": 1, "files": {name: 12 for name in NAMES}}):
                manifest.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaises(ValueError):
                    restore(saved, root / "invalid")
                self.assertFalse((root / "invalid").exists())
            manifest.write_text(original, encoding="utf-8")
            # Modify a valid SQLite database: integrity passes but checksum fails.
            with closing(sqlite3.connect(saved / NAMES[0])) as db, db:
                db.execute("UPDATE sample SET value=999")
            with self.assertRaisesRegex(ValueError, "Checksum inválido"):
                verify(saved)
            with self.assertRaises(ValueError):
                restore(saved, root / "tampered")
            self.assertFalse((root / "tampered").exists())

if __name__ == "__main__":
    unittest.main()
