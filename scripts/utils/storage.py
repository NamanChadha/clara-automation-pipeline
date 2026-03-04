"""
storage.py - File-based JSON storage helpers for Clara Automation Pipeline.

Handles reading/writing account memos, agent specs, and changelogs
to the outputs/accounts/<account_id>/ directory structure.
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime


DEFAULT_OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'outputs'
))


def get_account_dir(account_id: str, version: str = "v1") -> str:
    """Get the output directory for an account version."""
    path = os.path.join(DEFAULT_OUTPUT_DIR, 'accounts', account_id, version)
    os.makedirs(path, exist_ok=True)
    return path


def save_json(data: Dict, filepath: str) -> str:
    """Save a dict as formatted JSON. Returns the filepath."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def load_json(filepath: str) -> Optional[Dict]:
    """Load a JSON file. Returns None if not found."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_account_memo(account_id: str, memo: Dict, version: str = "v1") -> str:
    """Save an account memo JSON."""
    dirpath = get_account_dir(account_id, version)
    filepath = os.path.join(dirpath, 'account_memo.json')
    memo['_metadata'] = {
        'version': version,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'account_id': account_id,
    }
    return save_json(memo, filepath)


def load_account_memo(account_id: str, version: str = "v1") -> Optional[Dict]:
    """Load an account memo JSON."""
    filepath = os.path.join(
        DEFAULT_OUTPUT_DIR, 'accounts', account_id, version, 'account_memo.json'
    )
    return load_json(filepath)


def save_agent_spec(account_id: str, spec: Dict, version: str = "v1") -> str:
    """Save an agent spec JSON."""
    dirpath = get_account_dir(account_id, version)
    filepath = os.path.join(dirpath, 'agent_spec.json')
    spec['_metadata'] = {
        'version': version,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'account_id': account_id,
    }
    return save_json(spec, filepath)


def load_agent_spec(account_id: str, version: str = "v1") -> Optional[Dict]:
    """Load an agent spec JSON."""
    filepath = os.path.join(
        DEFAULT_OUTPUT_DIR, 'accounts', account_id, version, 'agent_spec.json'
    )
    return load_json(filepath)


def save_changelog(account_id: str, changelog_md: str) -> str:
    """Save a changelog markdown file for an account."""
    dirpath = os.path.join(DEFAULT_OUTPUT_DIR, 'accounts', account_id)
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, 'changelog.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(changelog_md)
    return filepath


def load_changelog(account_id: str) -> Optional[str]:
    """Load an existing changelog."""
    filepath = os.path.join(DEFAULT_OUTPUT_DIR, 'accounts', account_id, 'changelog.md')
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def list_accounts() -> list:
    """List all account IDs that have output data."""
    accounts_dir = os.path.join(DEFAULT_OUTPUT_DIR, 'accounts')
    if not os.path.exists(accounts_dir):
        return []
    return [
        d for d in os.listdir(accounts_dir)
        if os.path.isdir(os.path.join(accounts_dir, d))
    ]


def account_has_version(account_id: str, version: str) -> bool:
    """Check if an account has a specific version's outputs."""
    dirpath = os.path.join(DEFAULT_OUTPUT_DIR, 'accounts', account_id, version)
    if not os.path.exists(dirpath):
        return False
    memo_path = os.path.join(dirpath, 'account_memo.json')
    return os.path.exists(memo_path)
