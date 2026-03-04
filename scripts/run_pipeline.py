"""
run_pipeline.py - CLI batch runner for Clara Automation Pipeline.

Usage:
    python scripts/run_pipeline.py --pipeline A      # Demo → v1 only
    python scripts/run_pipeline.py --pipeline B      # Onboarding → v2 only
    python scripts/run_pipeline.py --pipeline all    # Both pipelines

Features:
    - Batch processes all transcripts in data/transcripts/
    - Idempotent: re-running produces identical results
    - Logs all operations
    - Summary metrics at end
"""

import argparse
import os
import sys
import json
import time
from datetime import datetime

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.parse_transcript import (
    load_all_transcripts,
    match_demo_to_onboarding,
)
from scripts.extract_memo import extract_account_memo
from scripts.generate_agent_spec import generate_agent_spec
from scripts.update_from_onboarding import update_from_onboarding
from scripts.generate_changelog import generate_changelog, generate_changes_json
from scripts.utils.storage import (
    save_account_memo,
    save_agent_spec,
    save_changelog,
    save_json,
    load_account_memo,
    account_has_version,
    DEFAULT_OUTPUT_DIR,
)
from scripts.utils.task_tracker import TaskTracker


# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = os.environ.get('DATA_DIR', os.path.join(PROJECT_ROOT, 'data'))
DEMO_DIR = os.path.join(DATA_DIR, 'transcripts', 'demo')
ONBOARDING_DIR = os.path.join(DATA_DIR, 'transcripts', 'onboarding')


class PipelineRunner:
    """Orchestrates the full automation pipeline."""

    def __init__(self):
        self.tracker = TaskTracker()
        self.stats = {
            'pipeline_a': {'processed': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'pipeline_b': {'processed': 0, 'success': 0, 'failed': 0, 'skipped': 0},
        }
        self.start_time = time.time()

    def run_pipeline_a(self):
        """Pipeline A: Demo Call → Preliminary Agent (v1)."""
        print("\n" + "=" * 60)
        print("  PIPELINE A: Demo Call → Preliminary Agent (v1)")
        print("=" * 60)

        demo_transcripts = load_all_transcripts(DEMO_DIR)

        if not demo_transcripts:
            print(f"\n  ⚠ No demo transcripts found in {DEMO_DIR}")
            return

        print(f"\n  Found {len(demo_transcripts)} demo transcript(s)\n")

        for transcript in demo_transcripts:
            account_id = transcript['account_id']
            company = transcript['company_name']
            self.stats['pipeline_a']['processed'] += 1

            print(f"  ┌─ Processing: {company} ({account_id})")
            self.tracker.log_start(account_id, 'Pipeline A')

            try:
                # Step 1: Extract account memo
                print(f"  │  Extracting account memo...")
                memo = extract_account_memo(transcript)
                memo_path = save_account_memo(account_id, memo, 'v1')
                print(f"  │  ✓ Memo saved: {os.path.relpath(memo_path, PROJECT_ROOT)}")

                # Step 2: Generate agent spec
                print(f"  │  Generating agent spec...")
                spec = generate_agent_spec(memo, 'v1')
                spec_path = save_agent_spec(account_id, spec, 'v1')
                print(f"  │  ✓ Agent spec saved: {os.path.relpath(spec_path, PROJECT_ROOT)}")

                # Step 3: Log success
                self.tracker.log_success(
                    account_id, 'Pipeline A',
                    f'v1 created: {len(memo.get("services_supported", []))} services, '
                    f'{len(memo.get("emergency_definition", []))} emergencies defined'
                )
                self.stats['pipeline_a']['success'] += 1
                print(f"  └─ ✅ Complete\n")

            except Exception as e:
                self.tracker.log_failure(account_id, 'Pipeline A', str(e))
                self.stats['pipeline_a']['failed'] += 1
                print(f"  └─ ❌ Failed: {e}\n")

    def run_pipeline_b(self):
        """Pipeline B: Onboarding → Agent Modification (v2)."""
        print("\n" + "=" * 60)
        print("  PIPELINE B: Onboarding → Agent Modification (v2)")
        print("=" * 60)

        # Load all transcripts
        demo_transcripts = load_all_transcripts(DEMO_DIR)
        onboarding_transcripts = load_all_transcripts(ONBOARDING_DIR)

        if not onboarding_transcripts:
            print(f"\n  ⚠ No onboarding transcripts found in {ONBOARDING_DIR}")
            return

        print(f"\n  Found {len(onboarding_transcripts)} onboarding transcript(s)\n")

        # Match demo to onboarding
        pairs = match_demo_to_onboarding(demo_transcripts, onboarding_transcripts)

        for demo, onboarding in pairs:
            if not onboarding:
                continue

            account_id = demo['account_id']
            company = demo['company_name']
            self.stats['pipeline_b']['processed'] += 1

            print(f"  ┌─ Processing: {company} ({account_id})")
            self.tracker.log_start(account_id, 'Pipeline B')

            try:
                # Step 1: Load v1 memo
                v1_memo = load_account_memo(account_id, 'v1')
                if not v1_memo:
                    print(f"  │  ⚠ No v1 memo found. Running Pipeline A first...")
                    # Auto-run Pipeline A for this account
                    memo = extract_account_memo(demo)
                    save_account_memo(account_id, memo, 'v1')
                    v1_memo = memo

                # Step 2: Update from onboarding
                print(f"  │  Applying onboarding updates...")
                v2_memo, changes = update_from_onboarding(v1_memo, onboarding)
                memo_path = save_account_memo(account_id, v2_memo, 'v2')
                print(f"  │  ✓ v2 Memo saved: {os.path.relpath(memo_path, PROJECT_ROOT)}")
                print(f"  │    {len(changes)} field(s) changed")

                # Step 3: Generate v2 agent spec
                print(f"  │  Generating v2 agent spec...")
                v2_spec = generate_agent_spec(v2_memo, 'v2')
                spec_path = save_agent_spec(account_id, v2_spec, 'v2')
                print(f"  │  ✓ v2 Agent spec saved: {os.path.relpath(spec_path, PROJECT_ROOT)}")

                # Step 4: Generate changelog
                print(f"  │  Generating changelog...")
                changelog_md = generate_changelog(account_id, company, changes)
                cl_path = save_changelog(account_id, changelog_md)
                print(f"  │  ✓ Changelog saved: {os.path.relpath(cl_path, PROJECT_ROOT)}")

                # Also save structured changes JSON
                changes_json = generate_changes_json(account_id, company, changes)
                changes_path = os.path.join(
                    DEFAULT_OUTPUT_DIR, 'accounts', account_id, 'changes.json'
                )
                save_json(changes_json, changes_path)

                # Step 5: Log success
                self.tracker.log_success(
                    account_id, 'Pipeline B',
                    f'v2 created: {len(changes)} changes applied'
                )
                self.stats['pipeline_b']['success'] += 1
                print(f"  └─ ✅ Complete\n")

            except Exception as e:
                self.tracker.log_failure(account_id, 'Pipeline B', str(e))
                self.stats['pipeline_b']['failed'] += 1
                print(f"  └─ ❌ Failed: {e}\n")
                import traceback
                traceback.print_exc()

    def print_summary(self):
        """Print execution summary with metrics."""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("  PIPELINE EXECUTION SUMMARY")
        print("=" * 60)

        for pipeline_name, stats in self.stats.items():
            if stats['processed'] > 0:
                label = 'Pipeline A (Demo → v1)' if pipeline_name == 'pipeline_a' else 'Pipeline B (Onboarding → v2)'
                print(f"\n  {label}:")
                print(f"    Processed: {stats['processed']}")
                print(f"    Success:   {stats['success']}")
                print(f"    Failed:    {stats['failed']}")
                print(f"    Skipped:   {stats['skipped']}")

        print(f"\n  Total time: {elapsed:.2f}s")
        print(f"  Outputs:    {os.path.relpath(DEFAULT_OUTPUT_DIR, PROJECT_ROOT)}/")
        print(f"  Tracker:    {os.path.relpath(self.tracker.filepath, PROJECT_ROOT)}")
        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Clara Automation Pipeline - Batch Runner',
        epilog='Run on all transcripts in data/transcripts/'
    )
    parser.add_argument(
        '--pipeline', '-p',
        choices=['A', 'B', 'all'],
        default='all',
        help='Which pipeline to run: A (demo→v1), B (onboarding→v2), or all'
    )
    args = parser.parse_args()

    print("\n╔════════════════════════════════════════════════╗")
    print("║   Clara Automation Pipeline - Batch Runner     ║")
    print(f"║   Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}          ║")
    print("╚════════════════════════════════════════════════╝")

    runner = PipelineRunner()

    if args.pipeline in ('A', 'all'):
        runner.run_pipeline_a()

    if args.pipeline in ('B', 'all'):
        runner.run_pipeline_b()

    runner.print_summary()


if __name__ == '__main__':
    main()
