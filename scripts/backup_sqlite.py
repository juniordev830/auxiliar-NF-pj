"""Offline SQLite backup/recovery. Never overwrites an existing destination."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import stat
import tempfile
from contextlib import closing

from backup_crypto import KEY_SIZE, decrypt_member, encrypt_member, generate_key

NAMES = ("controlador-gastos.db", "auxiliar-pj.db")

def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()

def check(path, *, immutable=False):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Arquivo SQLite ausente ou inválido: {path}")
    uri = path.resolve().as_uri() + "?mode=ro"
    if immutable:
        uri += "&immutable=1"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError(f"Falha de integridade: {path}")

def copy_sqlite(src, dst):
    check(src)
    with closing(sqlite3.connect(src.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)) as source:
        with closing(sqlite3.connect(dst)) as target:
            source.backup(target)
    os.chmod(dst, 0o600)
    check(dst)

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

def backup(residential, pj, destination, *, key_file=None):
    sources = [Path(residential), Path(pj)]
    if sources[0].resolve() == sources[1].resolve():
        raise ValueError("Informe dois bancos distintos.")
    if all(p.exists() for p in sources) and sources[0].samefile(sources[1]):
        raise ValueError("Informe dois bancos distintos.")
    key = read_key(key_file) if key_file is not None else None
    destination, temp = prepare(destination)
    try:
        manifest = {"version": 2 if key else 1, "files": {}}
        for source, name in zip(sources, NAMES):
            copy_sqlite(source, temp / name)
            manifest["files"][name] = digest(temp / name)
        (temp / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        os.chmod(temp / "manifest.json", 0o600)
        if key:
            for name in (*NAMES, "manifest.json"):
                plain = temp / name
                encrypt_member(plain, temp / (name + ".enc"), key, name)
                plain.unlink()
        publish(temp, destination)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    return destination

def open_backup_member(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"Arquivo de backup não é regular: {path.name}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"Arquivo de backup não é regular: {path.name}")
        return os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise


def read_key(path):
    with open_backup_member(Path(path)) as stream:
        if os.name == "posix" and os.fstat(stream.fileno()).st_mode & 0o077:
            raise ValueError("O arquivo de chave deve ter permissão exclusiva do proprietário.")
        key = stream.read(KEY_SIZE + 1)
    if len(key) != KEY_SIZE:
        raise ValueError("A chave deve conter exatamente 32 bytes aleatórios.")
    return key


def parse_manifest(data, version):
    if len(data) > 4096:
        raise ValueError("Manifesto de backup excede 4 KiB.")
    manifest = json.loads(data)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if (not isinstance(files, dict) or manifest.get("version") != version or
            set(files) != set(NAMES) or any(not isinstance(value, str) or
                re.fullmatch(r"[0-9a-f]{64}", value) is None for value in files.values())):
        raise ValueError("Manifesto de backup inválido.")
    return files


def restore(source, destination, *, key_file=None):
    source = Path(source)
    if source.is_symlink() or not source.is_dir():
        raise ValueError("A origem deve ser um diretório de backup.")
    for name in NAMES:
        for suffix in ("-journal", "-wal", "-shm"):
            sidecar = source / (name + suffix)
            if sidecar.exists() or sidecar.is_symlink():
                raise ValueError(f"Arquivo auxiliar SQLite inesperado: {sidecar.name}")

    key = read_key(key_file) if key_file is not None else None
    encrypted_manifest = source / "manifest.json.enc"
    if not key and (encrypted_manifest.exists() or encrypted_manifest.is_symlink()):
        raise ValueError("Informe o arquivo de chave desta cópia criptografada.")
    destination, temp = prepare(destination)
    try:
        if key:
            manifest = temp / "manifest.json"
            with open_backup_member(encrypted_manifest) as stream:
                decrypt_member(stream, manifest, key, "manifest.json", max_size=4096)
            files = parse_manifest(manifest.read_bytes(), 2)
            manifest.unlink()
        else:
            with open_backup_member(source / "manifest.json") as stream:
                files = parse_manifest(stream.read(4097), 1)

        for name in NAMES:
            staged = temp / name
            if key:
                with open_backup_member(source / (name + ".enc")) as stream:
                    decrypt_member(stream, staged, key, name)
            else:
                with open_backup_member(source / name) as stream, staged.open("xb") as copy:
                    shutil.copyfileobj(stream, copy, length=1024 * 1024)
                os.chmod(staged, 0o600)
            if digest(staged) != files[name]:
                raise ValueError(f"Checksum inválido: {name}")
            check(staged, immutable=True)
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
    create.add_argument("--chave-arquivo", type=Path)
    recover = sub.add_parser("restore")
    recover.add_argument("--origem", required=True)
    recover.add_argument("--destino", required=True)
    recover.add_argument("--chave-arquivo", type=Path)
    key = sub.add_parser("gerar-chave")
    key.add_argument("--destino", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "backup":
            result = backup(args.residencial, args.pj, args.destino, key_file=args.chave_arquivo)
        elif args.command == "restore":
            result = restore(args.origem, args.destino, key_file=args.chave_arquivo)
        else:
            result = generate_key(args.destino)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))
    print(f"Concluído: {result}")

if __name__ == "__main__":
    main()
