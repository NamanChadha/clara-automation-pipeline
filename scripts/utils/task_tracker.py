"""
task_tracker.py - Local markdown-based task tracking for Clara Automation Pipeline.

Creates and updates tasks/tracker.md to track processing status per account.
"""

import os
from datetime import datetime
from typing import Optional


DEFAULT_TASKS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'tasks'
)


class TaskTracker:
    """Tracks pipeline processing status in a markdown file."""

    def __init__(self, tasks_dir: str = None):
        self.tasks_dir = tasks_dir or DEFAULT_TASKS_DIR
        os.makedirs(self.tasks_dir, exist_ok=True)
        self.filepath = os.path.join(self.tasks_dir, 'tracker.md')
        self.entries = []
        self._load()

    def _load(self):
        """Load existing tracker entries."""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Parse existing entries from table
            self.entries = []
            for line in content.split('\n'):
                if line.startswith('|') and not line.startswith('| Account') and not line.startswith('|---'):
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 4:
                        self.entries.append({
                            'account_id': parts[0],
                            'pipeline': parts[1],
                            'status': parts[2],
                            'timestamp': parts[3],
                            'notes': parts[4] if len(parts) > 4 else '',
                        })

    def _save(self):
        """Write tracker to markdown file."""
        lines = [
            '# Clara Automation Pipeline - Task Tracker',
            '',
            f'_Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}_',
            '',
            '| Account ID | Pipeline | Status | Timestamp | Notes |',
            '|------------|----------|--------|-----------|-------|',
        ]
        for entry in self.entries:
            lines.append(
                f"| {entry['account_id']} | {entry['pipeline']} | {entry['status']} "
                f"| {entry['timestamp']} | {entry.get('notes', '')} |"
            )

        # Add summary
        total = len(self.entries)
        completed = sum(1 for e in self.entries if e['status'] == '✅ Complete')
        failed = sum(1 for e in self.entries if e['status'] == '❌ Failed')
        lines.extend([
            '',
            '## Summary',
            f'- **Total tasks**: {total}',
            f'- **Completed**: {completed}',
            f'- **Failed**: {failed}',
            f'- **Pending**: {total - completed - failed}',
        ])

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def log(self, account_id: str, pipeline: str, status: str, notes: str = ''):
        """Log a task status update."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Update existing entry or add new
        updated = False
        for entry in self.entries:
            if entry['account_id'] == account_id and entry['pipeline'] == pipeline:
                entry['status'] = status
                entry['timestamp'] = timestamp
                entry['notes'] = notes
                updated = True
                break

        if not updated:
            self.entries.append({
                'account_id': account_id,
                'pipeline': pipeline,
                'status': status,
                'timestamp': timestamp,
                'notes': notes,
            })

        self._save()

    def log_start(self, account_id: str, pipeline: str):
        """Log that processing has started."""
        self.log(account_id, pipeline, '🔄 Processing', 'Started')

    def log_success(self, account_id: str, pipeline: str, notes: str = ''):
        """Log successful processing."""
        self.log(account_id, pipeline, '✅ Complete', notes)

    def log_failure(self, account_id: str, pipeline: str, error: str):
        """Log a processing failure."""
        self.log(account_id, pipeline, '❌ Failed', error)
