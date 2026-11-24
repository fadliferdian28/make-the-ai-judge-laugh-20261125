#!/usr/bin/env python3
"""Validate and publish the make.fun bounty entry."""

import hashlib
import os
import shutil
import sys
from pathlib import Path


EXPECTED_SHA256 = "f53286184b287e440f1e3837c88e0db3cf477322716f652b3ec8f87d83c5b9d8"


def fail(message: str) -> "None":
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    entry_path = Path(__file__).resolve().parent / "entry.txt"

    try:
        raw = entry_path.read_bytes()
    except OSError as exc:
        fail(f"cannot read {entry_path}: {exc}")

    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        fail(
            f"sha256 mismatch for {entry_path}: "
            f"expected {EXPECTED_SHA256}, got {digest}"
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"entry is not valid UTF-8: {exc}")

    line = text[:-1] if text.endswith("\n") else text
    char_count = len(line)
    if not 1 <= char_count <= 200:
        fail(f"entry must be 1-200 characters, got {char_count}")
    if not line.strip():
        fail("entry must not be whitespace-only")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination = output_dir / "entry.txt"

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            fail(f"output directory is not writable: {output_dir}")
        try:
            shutil.copyfile(entry_path, destination)
        except shutil.SameFileError:
            pass
    except OSError as exc:
        fail(f"cannot write {destination}: {exc}")

    print(line)
    print(f"characters: {char_count}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
