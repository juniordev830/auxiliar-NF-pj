"""Offline SQLite backup/recovery. Never overwrites an existing destination."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import tempfile
from contextlib import closing

NAMES = ("controlador-gastos.db", "auxiliar-pj.db")
REQUIRED_TABLES = {NAMES[0]: {"Pessoas", "Transacoes"}, NAMES[1]: {"Lancamentos"}}
MAX_MANIFEST_BYTES = 16 * 1024

def read_manifest(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("Manifesto ausente ou inválido.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("Manifesto excede o limite permitido.")
    manifest = json.loads(raw)
    if not isinstance(manifest, dict) or type(manifest.get("version")) is not int or manifest["version"] != 1:
        raise ValueError("Versão do manifesto inválida.")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(NAMES):
        raise ValueError("Arquivos do manifesto inválidos.")
    if any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
           for value in files.values()):
        raise ValueError("Checksum inválido no manifesto.")
    return manifest

def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()

def check(path, expected=None, immutable=False):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Arquivo SQLite ausente ou inválido: {path}")
    uri = path.resolve().as_uri() + "?mode=ro" + ("&immutable=1" if immutable else "")
    with closing(sqlite3.connect(uri, uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError(f"Falha de integridade: {path}")
        if expected is not None:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            missing = REQUIRED_TABLES[expected] - tables
            if missing:
                raise ValueError(f"Esquema incompatível com {expected}: faltam {', '.join(sorted(missing))}.")
            if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise ValueError(f"Falha de integridade referencial: {path}")

def copy_sqlite(src, dst):
    check(src, dst.name)
    with closing(sqlite3.connect(src.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)) as source:
        with closing(sqlite3.connect(dst)) as target:
            source.backup(target)
    os.chmod(dst, 0o600)
    check(dst, dst.name)

def prepare(destination):
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("O destino já existe; escolha um diretório novo.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination, Path(tempfile.mkdtemp(prefix=".pj-temporario-", dir=destination.parent))

def publish(temp, destination):
    # Reserve the destination without overwriting an existing directory.
    destination.mkdir(mode=0o700, exist_ok=False)
    try:
        for item in temp.iterdir():
            item.rename(destination / item.name)
    except BaseException:
        # Only remove the newly reserved directory, never an existing backup.
        shutil.rmtree(destination)
        raise

def backup(residential, pj, destination):
    sources = [Path(residential), Path(pj)]
    if sources[0].resolve() == sources[1].resolve():
        raise ValueError("Informe dois bancos distintos.")
    if all(p.exists() for p in sources) and sources[0].samefile(sources[1]):
        raise ValueError("Informe dois bancos distintos.")
    destination, temp = prepare(destination)
    try:
        manifest = {"version": 1, "files": {}}
        for source, name in zip(sources, NAMES):
            copy_sqlite(source, temp / name)
            manifest["files"][name] = digest(temp / name)
        (temp / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        os.chmod(temp / "manifest.json", 0o600)
        publish(temp, destination)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    return destination

def verify(source):
    """Validate an existing offline backup without publishing or modifying it."""
    source = Path(source)
    manifest = read_manifest(source / "manifest.json")
    for name in NAMES:
        path = source / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Arquivo de backup ausente ou inválido: {name}")
        if digest(path) != manifest["files"][name]:
            raise ValueError(f"Checksum inválido: {name}")
        # A published backup must stand alone; do not accidentally read live WAL data.
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(path) + suffix)
            if sidecar.exists() or sidecar.is_symlink():
                raise ValueError(f"Backup contém arquivo auxiliar inesperado: {name}{suffix}")
        check(path, name, immutable=True)
    return source

def restore(source, destination):
    source = Path(source)
    manifest_path = source / "manifest.json"
    manifest = read_manifest(manifest_path)
    destination, temp = prepare(destination)
    try:
        for name in NAMES:
            src = source / name
            check(src, name)
            # Hash the copied bytes, not an earlier version of a mutable source.
            shutil.copyfile(src, temp / name)
            os.chmod(temp / name, 0o600)
            if digest(temp / name) != manifest["files"][name]:
                raise ValueError(f"Checksum inválido: {name}")
            check(temp / name, name)
        publish(temp, destination)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    return destination

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("backup")
    create.add_argument("--residencial", required=True)
    create.add_argument("--pj", required=True)
    create.add_argument("--destino", required=True)
    validate = sub.add_parser("verify")
    validate.add_argument("--origem", required=True)
    recover = sub.add_parser("restore")
    recover.add_argument("--origem", required=True)
    recover.add_argument("--destino", required=True)
    args = parser.parse_args()
    try:
        if args.command == "backup":
            result = backup(args.residencial, args.pj, args.destino)
        elif args.command == "verify":
            result = verify(args.origem)
        else:
            result = restore(args.origem, args.destino)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))
    print(f"Concluído: {result}")

if __name__ == "__main__":
    main()
