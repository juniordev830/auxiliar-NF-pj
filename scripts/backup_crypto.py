"""Authenticated streaming encryption for SQLite backup members."""
from pathlib import Path
import os

MAGIC = b"GASTOS-PJ-AESGCM-1\0"
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32
CHUNK_SIZE = 1024 * 1024
MAX_MEMBER_SIZE = (1 << 36) - 32


def generate_key(path):
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(os.urandom(KEY_SIZE))
    return path


def _cipher(key, nonce, tag=None):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError as error:
        raise ValueError("Instale scripts/requirements-backup.txt para usar cópias criptografadas.") from error
    return Cipher(algorithms.AES(key), modes.GCM(nonce, tag))


def encrypt_member(source, target, key, name):
    if source.stat().st_size > MAX_MEMBER_SIZE:
        raise ValueError("Arquivo grande demais para o formato de backup criptografado.")
    nonce = os.urandom(NONCE_SIZE)
    cipher = _cipher(key, nonce).encryptor()
    cipher.authenticate_additional_data(MAGIC + name.encode("ascii"))
    with source.open("rb") as data, target.open("xb") as output:
        os.chmod(target, 0o600)
        output.write(MAGIC + nonce)
        for chunk in iter(lambda: data.read(CHUNK_SIZE), b""):
            output.write(cipher.update(chunk))
        output.write(cipher.finalize())
        output.write(cipher.tag)


def decrypt_member(source, target, key, name, max_size=MAX_MEMBER_SIZE):
    header = source.read(len(MAGIC) + NONCE_SIZE)
    if len(header) != len(MAGIC) + NONCE_SIZE or not header.startswith(MAGIC):
        raise ValueError(f"Formato criptografado inválido: {name}")
    payload_start = source.tell()
    payload_size = source.seek(0, os.SEEK_END) - payload_start - TAG_SIZE
    if not 0 <= payload_size <= max_size:
        raise ValueError(f"Tamanho inválido: {name}")
    source.seek(payload_start + payload_size)
    tag = source.read(TAG_SIZE)
    if len(tag) != TAG_SIZE:
        raise ValueError(f"Backup criptografado truncado: {name}")
    source.seek(payload_start)
    cipher = _cipher(key, header[-NONCE_SIZE:], tag).decryptor()
    from cryptography.exceptions import InvalidTag
    cipher.authenticate_additional_data(MAGIC + name.encode("ascii"))
    with target.open("xb") as output:
        os.chmod(target, 0o600)
        remaining = payload_size
        while remaining:
            chunk = source.read(min(CHUNK_SIZE, remaining))
            if not chunk:
                raise ValueError(f"Backup criptografado truncado: {name}")
            output.write(cipher.update(chunk))
            remaining -= len(chunk)
        try:
            output.write(cipher.finalize())
        except InvalidTag as error:
            raise ValueError(f"Autenticação criptográfica falhou: {name}") from error
