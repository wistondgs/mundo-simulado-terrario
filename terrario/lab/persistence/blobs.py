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
        digest = hashlib.sha256(payload).hexdigest()
        target = self.destination(digest)
        # Fast path: a concurrent or prior writer may already have committed an
        # identical, verifiable blob. Never rewrite it.
        if target.is_file():
            if not self.verify(digest):
                raise OSError(f"existing blob failed verification: {digest}")
            relative = target.relative_to(self.data_root).as_posix()
            return BlobManifest(digest, relative, len(payload), media_type, True)
        fd, temporary = tempfile.mkstemp(prefix=f"blob-{os.getpid()}-", suffix=".staging", dir=self.staging_root)
        temp_path = Path(temporary)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                # Lost a concurrent race; the committed blob wins.
                if not self.verify(digest):
                    raise OSError(f"existing blob failed verification: {digest}")
                temp_path.unlink()
                deduplicated = True
            else:
                try:
                    os.replace(temp_path, target)
                except FileNotFoundError:
                    # Another process replaced the target between our check and
                    # rename; fall through to verify the committed blob.
                    if not target.exists() or not self.verify(digest):
                        raise
                self._fsync_directory(target.parent)
                deduplicated = False
            relative = target.relative_to(self.data_root).as_posix()
            return BlobManifest(digest, relative, len(payload), media_type, deduplicated)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def put_file(self, source: str | Path, media_type: str = "application/octet-stream") -> BlobManifest:
        source_path = Path(source)
        fd, temporary = tempfile.mkstemp(prefix=f"blob-{os.getpid()}-", suffix=".staging", dir=self.staging_root)
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
        """Move orphaned writes to quarantine instead of destroying them.

        Staging files are named ``blob-<pid>-*.staging``. A file is only
        recovered when its owning process is no longer alive, so an active
        concurrent writer is never moved out from under itself.
        """
        recovered = []
        for path in sorted(self.staging_root.glob("*.staging")):
            if self._owner_alive(path.name):
                continue
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
    def _owner_alive(name: str) -> bool:
        parts = name.split("-")
        if len(parts) < 3 or not parts[1].isdigit():
            return False
        try:
            os.kill(int(parts[1]), 0)
        except (ProcessLookupError, OverflowError, ValueError):
            return False
        except PermissionError:
            return True
        return True

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
