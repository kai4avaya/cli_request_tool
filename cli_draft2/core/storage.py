"""Simple secure JSON credentials storage for TinyTorch CLI.

This module uses the values specified in `config.py` for the
credentials directory and filename so these aren't hardcoded in the codebase.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

import config


def _credentials_dir() -> Path:
	return Path(os.path.expanduser(config.CREDENTIALS_DIR))


def _credentials_path() -> Path:
	return _credentials_dir() / config.CREDENTIALS_FILE_NAME


def _ensure_dir() -> None:
	d = _credentials_dir()
	d.mkdir(parents=True, exist_ok=True)
	try:
		os.chmod(d, 0o700)
	except OSError:
		# Best-effort; on some platforms or filesystems it may fail
		pass


def save_credentials(data: Dict[str, str]) -> None:
	"""Persist credentials to disk safely and atomically.

	Notes:
	- We use an atomic replace via os.replace.
	- File permissions are set to user read/write only (0o600) when possible.
	"""
	_ensure_dir()
	p = _credentials_path()
	tmp = p.with_suffix(".tmp")
	with tmp.open("w", encoding="utf-8") as f:
		json.dump(data, f, indent=2)
		f.flush()
		os.fsync(f.fileno())
	os.replace(str(tmp), str(p))
	try:
		os.chmod(p, 0o600)
	except OSError:
		pass


def load_credentials() -> Optional[Dict[str, str]]:
	p = _credentials_path()
	if not p.exists():
		return None
	try:
		with p.open("r", encoding="utf-8") as f:
			return json.load(f)
	except (OSError, json.JSONDecodeError):
		return None


def delete_credentials() -> None:
	p = _credentials_path()
	try:
		p.unlink()
	except OSError:
		pass

