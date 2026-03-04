"""
test_pipeline.py - Automated test suite for Clara Automation Pipeline.

Tests cover:
    - Transcript parsing and normalization
    - Account memo extraction
    - Agent spec generation
    - Onboarding update / diff logic
    - Changelog generation
    - End-to-end pipeline execution

Usage:
    python tests/test_pipeline.py
    python -m pytest tests/test_pipeline.py -v
"""

import os
import sys
import json
import unittest
import shutil

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.parse_transcript import parse_transcript, slugify, match_demo_to_onboarding, load_all_transcripts
from scripts.extract_memo import extract_account_memo
from scripts.generate_agent_spec import generate_agent_spec
from scripts.update_from_onboarding import update_from_onboarding
from scripts.generate_changelog import generate_changelog, generate_changes_json


# ============================================================================
# Test Data
# ============================================================================

DEMO_DIR = os.path.join(PROJECT_ROOT, 'data', 'transcripts', 'demo')
ONBOARDING_DIR = os.path.join(PROJECT_ROOT, 'data', 'transcripts', 'onboarding')
TEST_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'tests', 'test_outputs')


class TestSlugify(unittest.TestCase):
    """Tests for the slugify function."""

    def test_basic_name(self):
        self.assertEqual(slugify("Ben's Electric Solutions"), "bens_electric_solutions")

    def test_special_characters(self):
        self.assertEqual(slugify("AllStar Plumbing & Mechanical"), "allstar_plumbing_mechanical")

    def test_mixed_case(self):
        self.assertEqual(slugify("Comfort Zone HVAC"), "comfort_zone_hvac")

    def test_trailing_spaces(self):
        self.assertEqual(slugify("  Test Company  "), "test_company")


class TestTranscriptParsing(unittest.TestCase):
    """Tests for transcript parsing functionality."""

    def test_parse_demo_transcript(self):
        """Ensure demo transcript parsing returns expected fields."""
        demo_files = [f for f in os.listdir(DEMO_DIR) if f.endswith('.txt')]
        self.assertGreaterEqual(len(demo_files), 5, "Expected at least 5 demo transcripts")

        filepath = os.path.join(DEMO_DIR, demo_files[0])
        result = parse_transcript(filepath)

        # Check required fields
        self.assertIn('call_type', result)
        self.assertIn('company_name', result)
        self.assertIn('account_id', result)
        self.assertIn('turns', result)
        self.assertIn('full_text', result)
        self.assertEqual(result['call_type'], 'demo')
        self.assertTrue(len(result['company_name']) > 0, "Company name should not be empty")
        self.assertTrue(len(result['turns']) > 0, "Should have at least one turn")

    def test_parse_onboarding_transcript(self):
        """Ensure onboarding transcript parsing works."""
        onb_files = [f for f in os.listdir(ONBOARDING_DIR) if f.endswith('.txt')]
        self.assertGreaterEqual(len(onb_files), 5, "Expected at least 5 onboarding transcripts")

        filepath = os.path.join(ONBOARDING_DIR, onb_files[0])
        result = parse_transcript(filepath)
        self.assertEqual(result['call_type'], 'onboarding')

    def test_demo_onboarding_pairing(self):
        """Ensure demo and onboarding transcripts pair correctly."""
        demos = load_all_transcripts(DEMO_DIR)
        onboardings = load_all_transcripts(ONBOARDING_DIR)
        pairs = match_demo_to_onboarding(demos, onboardings)

        self.assertEqual(len(pairs), len(demos))
        paired_count = sum(1 for _, ob in pairs if ob is not None)
        self.assertEqual(paired_count, 5, "All 5 accounts should have a matching onboarding")


class TestMemoExtraction(unittest.TestCase):
    """Tests for account memo extraction."""

    def setUp(self):
        """Parse a demo transcript for testing."""
        filepath = os.path.join(DEMO_DIR, 'bens_electric_demo.txt')
        self.transcript = parse_transcript(filepath)
        self.memo = extract_account_memo(self.transcript)

    def test_required_fields(self):
        """Memo should contain all required fields."""
        required = [
            'account_id', 'company_name', 'business_hours',
            'services_supported', 'emergency_definition',
            'emergency_routing_rules', 'non_emergency_routing_rules',
            'call_transfer_rules', 'integration_constraints',
            'after_hours_flow_summary', 'office_hours_flow_summary',
            'excluded_services', 'questions_or_unknowns', 'notes',
        ]
        for field in required:
            self.assertIn(field, self.memo, f"Missing required field: {field}")

    def test_company_identification(self):
        """Should correctly identify the company."""
        self.assertIn('electric', self.memo['company_name'].lower())

    def test_business_hours_extracted(self):
        """Should extract business hours."""
        hours = self.memo['business_hours']
        self.assertIn('regular', hours)
        self.assertTrue(hours['regular'].get('start'), "Should have start time")
        self.assertTrue(hours['regular'].get('end'), "Should have end time")

    def test_emergency_definitions_exist(self):
        """Should extract at least one emergency definition."""
        self.assertTrue(len(self.memo['emergency_definition']) > 0,
                       "Should have at least one emergency definition")

    def test_routing_chain_exists(self):
        """Should extract routing chain with phone numbers."""
        chain = self.memo['emergency_routing_rules'].get('chain', [])
        self.assertTrue(len(chain) > 0, "Should have at least one routing entry")
        for entry in chain:
            self.assertIn('phone', entry)
            self.assertIn('role', entry)
            self.assertIn('timeout_seconds', entry)

    def test_services_extracted(self):
        """Should extract supported services."""
        self.assertTrue(len(self.memo['services_supported']) > 0,
                       "Should have at least one service")

    def test_excluded_services(self):
        """Should identify excluded services."""
        excluded = self.memo['excluded_services']
        # Ben's Electric doesn't do generators
        has_generator_exclusion = any('generator' in e.lower() for e in excluded)
        self.assertTrue(has_generator_exclusion, "Should exclude generator installations")


class TestAgentSpecGeneration(unittest.TestCase):
    """Tests for Retell agent spec generation."""

    def setUp(self):
        filepath = os.path.join(DEMO_DIR, 'bens_electric_demo.txt')
        transcript = parse_transcript(filepath)
        self.memo = extract_account_memo(transcript)
        self.spec = generate_agent_spec(self.memo, 'v1')

    def test_agent_name(self):
        """Agent spec should have a proper name."""
        self.assertTrue(self.spec['agent_name'].startswith('Clara'))

    def test_has_system_prompt(self):
        """Agent spec should include a system prompt."""
        prompt = self.spec['response_engine']['system_prompt']
        self.assertTrue(len(prompt) > 100, "System prompt should be substantial")

    def test_version_tag(self):
        """Agent spec should have correct version."""
        self.assertEqual(self.spec['version'], 'v1')

    def test_voice_config(self):
        """Agent spec should have voice configuration."""
        self.assertIn('voice_id', self.spec)
        self.assertIn('voice_speed', self.spec)

    def test_transfer_protocol(self):
        """Agent spec should have transfer protocol."""
        self.assertIn('call_transfer_protocol', self.spec)
        self.assertIn('fallback_protocol', self.spec)

    def test_tool_invocations(self):
        """Agent spec should have tool invocations defined."""
        tools = self.spec.get('tool_invocations', [])
        self.assertTrue(len(tools) > 0, "Should have at least one tool")
        for tool in tools:
            self.assertIn('note', tool)
            self.assertIn('INTERNAL', tool['note'])


class TestOnboardingUpdate(unittest.TestCase):
    """Tests for v1 -> v2 onboarding update."""

    def setUp(self):
        # Set up v1 memo
        demo_path = os.path.join(DEMO_DIR, 'bens_electric_demo.txt')
        demo = parse_transcript(demo_path)
        self.v1_memo = extract_account_memo(demo)

        # Parse onboarding transcript
        onb_path = os.path.join(ONBOARDING_DIR, 'bens_electric_onboarding.txt')
        self.onboarding = parse_transcript(onb_path)

    def test_produces_v2_memo(self):
        """Should produce a v2 memo."""
        v2_memo, changes = update_from_onboarding(self.v1_memo, self.onboarding)
        self.assertIsNotNone(v2_memo)
        self.assertIn('account_id', v2_memo)

    def test_produces_changes(self):
        """Should record changes between v1 and v2."""
        v2_memo, changes = update_from_onboarding(self.v1_memo, self.onboarding)
        self.assertTrue(len(changes) > 0, "Should have detected changes")

    def test_changes_have_required_fields(self):
        """Each change should have field, old_value, new_value, reason."""
        v2_memo, changes = update_from_onboarding(self.v1_memo, self.onboarding)
        for change in changes:
            self.assertIn('field', change)
            self.assertIn('old_value', change)
            self.assertIn('new_value', change)
            self.assertIn('reason', change)

    def test_v1_fields_preserved(self):
        """V1 data should be preserved where onboarding doesn't override."""
        v2_memo, changes = update_from_onboarding(self.v1_memo, self.onboarding)
        self.assertEqual(v2_memo['account_id'], self.v1_memo['account_id'])
        self.assertEqual(v2_memo['company_name'], self.v1_memo['company_name'])


class TestChangelogGeneration(unittest.TestCase):
    """Tests for changelog generation."""

    def test_empty_changelog(self):
        """Should handle empty changes list."""
        md = generate_changelog('test_account', 'Test Co', [])
        self.assertIn('No changes detected', md)

    def test_changelog_with_changes(self):
        """Should produce formatted markdown with changes."""
        changes = [
            {
                'field': 'business_hours.regular',
                'old_value': {'start': '7:00 AM'},
                'new_value': {'start': '7:30 AM'},
                'reason': 'Updated during onboarding',
            }
        ]
        md = generate_changelog('test_account', 'Test Co', changes)
        self.assertIn('business_hours.regular', md)
        self.assertIn('7:00 AM', md)
        self.assertIn('7:30 AM', md)

    def test_changes_json(self):
        """Should produce valid structured JSON."""
        changes = [{'field': 'test', 'old_value': 'a', 'new_value': 'b', 'reason': 'test'}]
        result = generate_changes_json('test', 'Test', changes)
        self.assertEqual(result['total_changes'], 1)
        self.assertEqual(len(result['changes']), 1)


class TestEndToEnd(unittest.TestCase):
    """End-to-end pipeline tests."""

    def test_all_accounts_produce_output(self):
        """Every demo transcript should produce a valid account memo."""
        demos = load_all_transcripts(DEMO_DIR)
        self.assertEqual(len(demos), 5)

        for demo in demos:
            memo = extract_account_memo(demo)
            spec = generate_agent_spec(memo, 'v1')
            self.assertTrue(len(memo['account_id']) > 0)
            self.assertTrue(len(spec['agent_name']) > 0)

    def test_full_pipeline_flow(self):
        """Full flow: demo -> v1 -> onboarding -> v2 -> changelog."""
        demos = load_all_transcripts(DEMO_DIR)
        onboardings = load_all_transcripts(ONBOARDING_DIR)
        pairs = match_demo_to_onboarding(demos, onboardings)

        for demo, onboarding in pairs:
            self.assertIsNotNone(onboarding, f"No onboarding for {demo['account_id']}")

            # Pipeline A
            v1_memo = extract_account_memo(demo)
            v1_spec = generate_agent_spec(v1_memo, 'v1')

            # Pipeline B
            v2_memo, changes = update_from_onboarding(v1_memo, onboarding)
            v2_spec = generate_agent_spec(v2_memo, 'v2')
            changelog_md = generate_changelog(demo['account_id'], demo['company_name'], changes)

            # Verify outputs
            self.assertEqual(v1_spec['version'], 'v1')
            self.assertEqual(v2_spec['version'], 'v2')
            self.assertTrue(len(changelog_md) > 0)
            self.assertTrue(len(changes) > 0,
                          f"No changes for {demo['account_id']} — unexpected")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Clara Automation Pipeline — Test Suite")
    print("=" * 60 + "\n")

    # Run tests
    unittest.main(verbosity=2)
