"""Content-addressed blob storage with recoverable atomic writes."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BlobManifest:
    blob_hash: str
    relative_path: str
    size_bytes: int
    media_type: str
    deduplicated: bool = False


class ContentAddressedBlobStore:
    def __init__(self, data_root: str | Path):
        self.data_root = Path(data_root).resolve()
        self.blobs_root = self.data_root / "blobs" / "sha256"
        self.staging_root = self.data_root / "staging"
        self.quarantine_root = self.data_root / "quarantine"
        for path in (self.blobs_root, self.staging_root, self.quarantine_root):
            path.mkdir(parents=True, exist_ok=True)

    def destination(self, digest: str) -> Path:
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("invalid SHA-256 digest")
        return self.blobs_root / digest[:2] / digest[2:4] / digest

    def put_bytes(self, payload: bytes, media_type: str = "application/octet-stream") -> BlobManifest:
        fd, temporary = tempfile.mkstemp(prefix="blob-", suffix=".staging", dir=self.staging_root)
        temp_path = Path(temporary)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            digest = hashlib.sha256(payload).hexdigest()
            target = self.destination(digest)
            target.parent.mkdir(parents=True, exist_ok=True)
            deduplicated = target.exists()
            if deduplicated:
                if self.verify(digest) is False:
                    raise OSError(f"existing blob failed verification: {digest}")
                temp_path.unlink()
            else:
                os.replace(temp_path, target)
                self._fsync_directory(target.parent)
            relative = target.relative_to(self.data_root).as_posix()
            return BlobManifest(digest, relative, len(payload), media_type, deduplicated)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def put_file(self, source: str | Path, media_type: str = "application/octet-stream") -> BlobManifest:
        source_path = Path(source)
        fd, temporary = tempfile.mkstemp(prefix="blob-", suffix=".staging", dir=self.staging_root)
        temp_path = Path(temporary)
        digest = hashlib.sha256()
        size = 0
        try:
            with source_path.open("rb") as incoming, os.fdopen(fd, "wb") as outgoing:
                for block in iter(lambda: incoming.read(1 << 20), b""):
                    digest.update(block)
                    size += len(block)
                    outgoing.write(block)
                outgoing.flush()
                os.fsync(outgoing.fileno())
            value = digest.hexdigest()
            target = self.destination(value)
            target.parent.mkdir(parents=True, exist_ok=True)
            deduplicated = target.exists()
            if deduplicated:
                if not self.verify(value):
                    raise OSError(f"existing blob failed verification: {value}")
                temp_path.unlink()
            else:
                os.replace(temp_path, target)
                self._fsync_directory(target.parent)
            return BlobManifest(value, target.relative_to(self.data_root).as_posix(), size, media_type, deduplicated)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def verify(self, digest: str) -> bool:
        target = self.destination(digest)
        if not target.is_file():
            return False
        actual = hashlib.sha256()
        with target.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                actual.update(block)
        return actual.hexdigest() == digest

    def read(self, digest: str) -> bytes:
        if not self.verify(digest):
            raise FileNotFoundError(digest)
        return self.destination(digest).read_bytes()

    def recover_staging(self) -> tuple[Path, ...]:
        """Move incomplete writes to quarantine instead of destroying them."""
        recovered = []
        for path in sorted(self.staging_root.glob("*.staging")):
            target = self.quarantine_root / f"{path.name}.{uuid.uuid4().hex}.orphan"
            try:
                shutil.move(str(path), str(target))
            except FileNotFoundError:
                continue
            recovered.append(target)
        if recovered:
            self._fsync_directory(self.quarantine_root)
        return tuple(recovered)

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
