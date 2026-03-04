"""
parse_transcript.py - Transcript normalizer for Clara Automation Pipeline.

Reads raw transcript .txt files, normalizes speaker labels,
detects call type (demo/onboarding), and extracts company name
to auto-assign an account_id.
"""

import os
import re
from typing import Dict, List, Optional, Tuple


# Patterns for detecting transcript metadata
HEADER_PATTERN = re.compile(
    r'Clara\s+(Demo|Onboarding)\s+Call\s*[-–]\s*(.+)',
    re.IGNORECASE
)

DATE_PATTERN = re.compile(
    r'Date:\s*(.+)',
    re.IGNORECASE
)

PARTICIPANTS_PATTERN = re.compile(
    r'Participants?:\s*(.+)',
    re.IGNORECASE
)

# Timestamp at start of a speaker turn
TURN_PATTERN = re.compile(
    r'\[(\d{2}:\d{2}:\d{2})\]\s*([^:]+?):\s*(.*)',
)

# Stage markers (demo agent playing, etc.)
STAGE_MARKER_PATTERN = re.compile(
    r'\[.*?(?:Demo|Agent|Clara)\s+(?:plays?|Demo).*?\]',
    re.IGNORECASE
)


def slugify(name: str) -> str:
    """Convert a company name to a URL/file-safe slug."""
    # Remove common suffixes for cleaner IDs
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    slug = re.sub(r'\s+', '_', slug)
    slug = slug.strip('_')
    return slug


def parse_transcript(filepath: str) -> Dict:
    """
    Parse a transcript file and return structured data.

    Returns:
        {
            'filepath': str,
            'filename': str,
            'call_type': 'demo' | 'onboarding',
            'company_name': str,
            'account_id': str,
            'date': str,
            'participants': str,
            'turns': [{'timestamp': str, 'speaker': str, 'text': str}, ...],
            'full_text': str,  # all speaker turns concatenated
            'client_text': str,  # only client speaker turns
            'clara_text': str,  # only Clara rep turns
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'call_type': detect_call_type(filepath, content),
        'company_name': '',
        'account_id': '',
        'date': '',
        'participants': '',
        'turns': [],
        'full_text': '',
        'client_text': '',
        'clara_text': '',
    }

    # Extract header info
    header_match = HEADER_PATTERN.search(content)
    if header_match:
        result['call_type'] = header_match.group(1).lower()
        result['company_name'] = header_match.group(2).strip()

    date_match = DATE_PATTERN.search(content)
    if date_match:
        result['date'] = date_match.group(1).strip()

    part_match = PARTICIPANTS_PATTERN.search(content)
    if part_match:
        result['participants'] = part_match.group(1).strip()

    # Parse speaker turns
    turns = []
    
    old_matches = list(TURN_PATTERN.finditer(content))
    if old_matches:
        for match in old_matches:
            timestamp = match.group(1)
            speaker = match.group(2).strip()
            text = match.group(3).strip()

            if STAGE_MARKER_PATTERN.match(text):
                continue

            turns.append({
                'timestamp': timestamp,
                'speaker': speaker,
                'text': text,
            })
    else:
        # Format: Speaker: 00:00 \n Text
        NEW_TURN_PATTERN = re.compile(r'^([^\n:]+?):\s*(\d{2}:\d{2}(?::\d{2})?)\s*\n(.*?)(?=^[^\n:]+?:\s*\d{2}:\d{2}|\Z)', re.MULTILINE | re.DOTALL)
        new_matches = list(NEW_TURN_PATTERN.finditer(content))
        if new_matches:
            for match in new_matches:
                speaker = match.group(1).strip()
                timestamp = match.group(2).strip()
                text = match.group(3).strip()
                
                if STAGE_MARKER_PATTERN.match(text):
                    continue

                turns.append({
                    'timestamp': timestamp,
                    'speaker': speaker,
                    'text': text,
                })
        else:
            # Fallback for raw text (Whisper output without labels)
            clean_content = re.sub(STAGE_MARKER_PATTERN, '', content).strip()
            if clean_content:
                turns.append({
                    'timestamp': '00:00:00',
                    'speaker': 'Unknown',
                    'text': clean_content,
                })

    result['turns'] = turns

    # Build concatenated text
    result['full_text'] = '\n'.join(t['text'] for t in turns)

    # Identify Clara rep vs client speakers
    clara_speakers = _identify_clara_speakers(turns, result['participants'])
    client_turns = [t for t in turns if t['speaker'] not in clara_speakers]
    clara_turns = [t for t in turns if t['speaker'] in clara_speakers]

    result['client_text'] = '\n'.join(t['text'] for t in client_turns)
    result['clara_text'] = '\n'.join(t['text'] for t in clara_turns)

    # If no client/clara text but we have full text, treat full text as client text for extraction
    if not result['client_text'] and result['full_text']:
        result['client_text'] = result['full_text']

    # Generate account_id from company name or filename
    if not result['company_name']:
        # Infer from filename: real_bens_electric_demo.txt -> Ben's Electric
        base = os.path.basename(filepath).lower()
        base = re.sub(r'_(demo|onboarding)\.txt$', '', base)
        base = base.replace('_', ' ').title()
        result['company_name'] = base

    if result['company_name']:
        result['account_id'] = slugify(result['company_name'])

    return result


def detect_call_type(filepath: str, content: str) -> str:
    """Detect if this is a demo or onboarding call."""
    filename = os.path.basename(filepath).lower()
    if 'onboarding' in filename:
        return 'onboarding'
    if 'demo' in filename:
        return 'demo'

    # Check content
    content_lower = content.lower()
    if 'onboarding' in content_lower:
        return 'onboarding'
    return 'demo'


def _identify_clara_speakers(turns: List[Dict], participants_str: str) -> set:
    """Identify which speakers are Clara representatives."""
    clara_names = {'alex', 'jordan', 'sam', 'clara'}
    # Also check participant list for Clara-side indicators
    clara_indicators = ['clara sales', 'clara onboarding', 'clara rep']

    speakers = set()

    # Check against known Clara rep names
    for turn in turns:
        speaker_lower = turn['speaker'].lower()
        if any(name in speaker_lower for name in clara_names):
            speakers.add(turn['speaker'])

    # Check participants string
    if participants_str:
        parts_lower = participants_str.lower()
        for indicator in clara_indicators:
            if indicator in parts_lower:
                # Find the speaker name before the indicator
                for turn in turns:
                    if turn['speaker'].lower() in parts_lower:
                        speakers.add(turn['speaker'])

    # If we found nothing, assume the first speaker is Clara rep
    if not speakers and turns:
        speakers.add(turns[0]['speaker'])

    return speakers


def load_all_transcripts(directory: str) -> List[Dict]:
    """Load and parse all .txt transcript files in a directory."""
    transcripts = []
    if not os.path.exists(directory):
        return transcripts

    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            try:
                parsed = parse_transcript(filepath)
                transcripts.append(parsed)
            except Exception as e:
                print(f"  ⚠ Error parsing {filename}: {e}")

    return transcripts


def match_demo_to_onboarding(
    demo_transcripts: List[Dict],
    onboarding_transcripts: List[Dict]
) -> List[Tuple[Dict, Optional[Dict]]]:
    """
    Match demo transcripts to their corresponding onboarding transcripts
    by account_id (company name slug).

    Returns list of (demo, onboarding_or_None) tuples.
    """
    onboarding_map = {t['account_id']: t for t in onboarding_transcripts}

    pairs = []
    for demo in demo_transcripts:
        onboarding = onboarding_map.get(demo['account_id'])
        pairs.append((demo, onboarding))

    return pairs
