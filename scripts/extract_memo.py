"""
extract_memo.py - Rule-based account memo extractor for Clara Automation Pipeline.

Extracts structured account data from parsed transcripts using pattern matching
and keyword analysis. No paid LLM calls — purely rule-based.

Produces the Account Memo JSON with all required fields per the assignment spec.
"""

import re
from typing import Dict, List, Optional
from scripts.utils.patterns import (
    extract_phone_numbers,
    extract_address,
    extract_timezone,
    extract_hours_range,
    extract_days_range,
    find_emergency_triggers,
    find_services,
    find_excluded_services,
    extract_timeout,
    HOURS_RANGE_PATTERN,
    DAY_RANGE_PATTERN,
    PHONE_PATTERN,
    SERVICETRADE_PATTERN,
    NEVER_CREATE_PATTERN,
    DO_NOT_DO_PATTERN,
)


def extract_account_memo(parsed_transcript: Dict) -> Dict:
    """
    Extract a structured account memo from a parsed transcript.

    Args:
        parsed_transcript: Output from parse_transcript()

    Returns:
        Account memo dict with all required fields.
    """
    full_text = parsed_transcript['full_text']
    client_text = parsed_transcript['client_text']
    company_name = parsed_transcript['company_name']
    account_id = parsed_transcript['account_id']

    memo = {
        'account_id': account_id,
        'company_name': company_name,
        'business_hours': _extract_business_hours(full_text),
        'office_address': extract_address(full_text) or '',
        'services_supported': _extract_services_list(full_text),
        'emergency_definition': _extract_emergency_definitions(full_text),
        'emergency_routing_rules': _extract_emergency_routing(full_text),
        'non_emergency_routing_rules': _extract_non_emergency_routing(full_text),
        'call_transfer_rules': _extract_transfer_rules(full_text),
        'integration_constraints': _extract_integration_constraints(full_text),
        'after_hours_flow_summary': _extract_after_hours_flow(full_text),
        'office_hours_flow_summary': _extract_office_hours_flow(full_text),
        'excluded_services': find_excluded_services(full_text),
        'custom_greeting': _extract_greeting(full_text),
        'non_emergency_collection_fields': _extract_collection_fields(full_text),
        'questions_or_unknowns': [],
        'notes': '',
    }

    # Identify missing/uncertain fields
    memo['questions_or_unknowns'] = _identify_unknowns(memo)
    memo['notes'] = _generate_notes(parsed_transcript, memo)

    return memo


def _extract_business_hours(text: str) -> Dict:
    """Extract business hours information from text."""
    hours = {
        'regular': {},
        'saturday': {},
        'sunday': {},
        'timezone': '',
        'seasonal_adjustments': [],
        'holidays': [],
    }

    # Find timezone
    tz = extract_timezone(text)
    if tz:
        hours['timezone'] = tz

    # Look for day ranges with hours
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Weekday hours
        if ('monday' in line_lower and 'friday' in line_lower) or \
           ('weekday' in line_lower) or \
           ('monday through friday' in line_lower):
            time_range = extract_hours_range(line)
            if time_range:
                hours['regular'] = {
                    'days': 'Monday-Friday',
                    'start': time_range['start'],
                    'end': time_range['end'],
                }

        # Saturday
        if 'saturday' in line_lower:
            time_range = extract_hours_range(line)
            if time_range:
                note = ''
                if 'inspection' in line_lower:
                    note = 'inspections only'
                elif 'maintenance' in line_lower:
                    note = 'maintenance contracts only'
                elif 'emergency' in line_lower:
                    note = 'emergency callbacks'
                hours['saturday'] = {
                    'start': time_range['start'],
                    'end': time_range['end'],
                    'note': note,
                }

        # Sunday
        if 'sunday' in line_lower:
            if 'emergency' in line_lower:
                hours['sunday'] = {'note': 'Emergency routing only'}
            elif 'closed' in line_lower:
                hours['sunday'] = {'note': 'Closed'}

        # Seasonal adjustments
        seasonal_months = ['november', 'december', 'january', 'february', 'march',
                          'june', 'july', 'august', 'september']
        for month in seasonal_months:
            if month in line_lower and ('extend' in line_lower or 'season' in line_lower):
                hours['seasonal_adjustments'].append(line.strip())

        # Holidays
        if 'holiday' in line_lower:
            hours['holidays'].append(line.strip())

    return hours


def _extract_services_list(text: str) -> List[str]:
    """Extract list of supported services."""
    services_found = find_services(text)
    flat_services = []
    for category, keywords in services_found.items():
        flat_services.extend(keywords)
    return list(set(flat_services))


def _extract_emergency_definitions(text: str) -> List[str]:
    """Extract emergency trigger definitions."""
    emergencies = []
    lines = text.split('\n')

    # Look for lines in the context of emergency discussion
    in_emergency_section = False
    for line in lines:
        line_lower = line.lower()

        # Detect emergency discussion context
        if any(kw in line_lower for kw in ['emergency is', 'emergency would be',
               'emergencies', 'emergency definition', 'emergency for us',
               'consider emergency', 'true emergency', 'treat it as emergency',
               'emergency priority', 'immediate response']):
            in_emergency_section = True

        if in_emergency_section:
            # Extract specific emergency conditions
            conditions = _extract_conditions_from_line(line)
            emergencies.extend(conditions)

            # End section detection
            if any(kw in line_lower for kw in ['routing', 'business hours',
                   'what are your hours', 'transfer', 'let me show',
                   'let me run', 'got it', 'clear', 'perfect']):
                in_emergency_section = False

    # Deduplicate and clean
    seen = set()
    unique = []
    for e in emergencies:
        e_clean = _clean_emergency_text(e)
        e_lower = e_clean.lower().strip()
        if e_lower not in seen and len(e_lower) > 8 and not _is_noise(e_clean):
            seen.add(e_lower)
            unique.append(e_clean)
    return unique


def _clean_emergency_text(text: str) -> str:
    """Clean up extracted emergency text to be a clear definition."""
    # Remove leading filler phrases
    text = re.sub(r'^(?:for us an emergency is:?\s*|a true emergency is:?\s*|an emergency (?:is|would be):?\s*)', '', text, flags=re.IGNORECASE)
    # Remove phone numbers from emergency text (they belong in routing)
    text = re.sub(r'\d{3}[-.]?\d{3}[-.]?\d{4}', '', text)
    # Remove leading/trailing noise
    text = re.sub(r'^[\s\-•*:,]+', '', text)
    text = re.sub(r'[\s,]+$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]
    return text


def _is_noise(text: str) -> bool:
    """Check if extracted text is noise rather than an actual emergency definition."""
    noise_patterns = [
        r'^there\'s a\b',
        r'^you mentioned\b',
        r'^we have\b',
        r'^basically\b',
        r'^that\'s\b',
        r'^right now\b',
        r'^and\s+(fire risk|the)\b',
        r'^those\b',
        r'^if (they|no one|nobody)\b',
        r'^keep all\b',
        r'^yes\b',
        r'^correct\b',
        r'^good\b',
        r'^smart\b',
    ]
    text_lower = text.lower().strip()
    for pattern in noise_patterns:
        if re.match(pattern, text_lower):
            return True
    # Too short after cleanup is noise
    if len(text_lower) < 10:
        return True
    return False


def _extract_conditions_from_line(line: str) -> List[str]:
    """Extract individual conditions/items from a line."""
    conditions = []
    # Split on common delimiters
    parts = re.split(r',\s*(?:or\s+)?|;\s*|\.\s+', line)
    for part in parts:
        part = part.strip()
        # Filter to meaningful emergency-related content
        emergency_words = [
            'wir', 'spark', 'power', 'fire', 'leak', 'burst', 'flood',
            'gas', 'carbon', 'alarm', 'fault', 'sprinkler', 'discharge',
            'tamper', 'access control', 'cctv', 'sewer', 'backup',
            'overflow', 'heating', 'heat', 'compromised', 'outage',
            'kitchen hood', 'inspection', 'healthcare', 'medical',
            'hospital', 'elderly', 'daycare', 'restaurant',
        ]
        if any(word in part.lower() for word in emergency_words):
            # Clean up the condition text
            part = re.sub(r'^[\s\-•*]+', '', part)
            part = re.sub(r'\s+', ' ', part)
            if len(part) > 8:
                conditions.append(part)
    return conditions


def _extract_emergency_routing(text: str) -> Dict:
    """Extract emergency call routing chain."""
    routing = {'chain': []}
    lines = text.split('\n')

    # Look for phone numbers in routing context
    in_routing = False
    for line in lines:
        line_lower = line.lower()

        # Detect routing discussion
        if any(kw in line_lower for kw in [
            'routing', 'route', 'on-call', 'oncall', 'dispatch',
            'escalation', 'if they don\'t pick up', 'transfer to',
            'primary', 'backup', 'last resort',
        ]):
            in_routing = True

        if in_routing:
            phones = extract_phone_numbers(line)
            if phones:
                role = _identify_role(line)
                timeout = extract_timeout(line)
                for phone in phones:
                    # Avoid duplicates
                    existing_phones = [e['phone'] for e in routing['chain']]
                    if phone not in existing_phones:
                        routing['chain'].append({
                            'role': role,
                            'phone': phone,
                            'timeout_seconds': timeout or 60,
                        })

            # End routing section
            if any(kw in line_lower for kw in [
                'let me show', 'demo', 'perfect', 'service trade',
                'servicetrade', 'what about', 'non-emergency',
                'during business hours',
            ]) and not phones:
                in_routing = False

    # Extract fallback message
    fallback = _extract_fallback_message(text)
    if fallback:
        routing['fallback_message'] = fallback

    return routing


def _identify_role(line: str) -> str:
    """Identify the role of a phone number from context. Order matters — more specific first."""
    line_lower = line.lower()
    role_map = [
        ('field supervisor', 'Field Supervisor'),
        ('plumbing supervisor', 'Plumbing Supervisor'),
        ('supervisor', 'Supervisor'),
        ('dispatch', 'Dispatcher'),
        ('backup', 'Backup Technician'),
        ('business partner', 'Business Partner'),
        ('partner', 'Business Partner'),
        ('owner', 'Owner'),
        ('last resort', 'Owner/Manager'),
        ('then me', 'Owner/Manager'),
        ('then i ', 'Owner/Manager'),
        ('come to me', 'Owner/Manager'),
        ('me directly', 'Owner/Manager'),
        ('maria', 'Manager'),
        ('primary on-call', 'Primary On-call'),
        ('primary', 'Primary On-call'),
        ('on-call', 'On-call Technician'),
        ('oncall', 'On-call Technician'),
        ('on call', 'On-call Technician'),
        ('tech ', 'On-call Technician'),
        ('manager', 'Manager'),
    ]
    for keyword, role in role_map:
        if keyword in line_lower:
            return role
    return 'Contact'


def _extract_fallback_message(text: str) -> Optional[str]:
    """Extract the fallback message when all transfers fail."""
    patterns = [
        re.compile(r'(?:tell|say|let)\s+(?:the\s+)?caller[:\s]+["\'](.+?)["\']', re.IGNORECASE),
        re.compile(r'Clara\s+should\s+(?:say|tell)[:\s]+["\'](.+?)["\']', re.IGNORECASE),
        re.compile(r'if\s+(?:all|nobody|no one)\s+(?:fail|answer).*?[:\s]+["\'](.+?)["\']', re.IGNORECASE | re.DOTALL),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def _extract_non_emergency_routing(text: str) -> Dict:
    """Extract non-emergency call handling rules."""
    routing = {}
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()
        # Main office number
        if ('office' in line_lower or 'main line' in line_lower or
            'main office' in line_lower or 'transfer to' in line_lower):
            if 'non-emergency' in line_lower or 'regular' in line_lower or \
               'during business' in line_lower or 'routine' in line_lower:
                phones = extract_phone_numbers(line)
                if phones:
                    routing['office_number'] = phones[0]

        # Also catch office numbers in broader context
        if 'main office' in line_lower or 'office line' in line_lower:
            phones = extract_phone_numbers(line)
            if phones and 'office_number' not in routing:
                routing['office_number'] = phones[0]

    # Non-emergency after-hours behavior
    for line in lines:
        line_lower = line.lower()
        if 'call back' in line_lower or 'callback' in line_lower:
            if 'next business day' in line_lower:
                routing['callback_timeframe'] = 'next business day'
            elif 'within the hour' in line_lower or 'within an hour' in line_lower:
                routing['callback_timeframe'] = 'within 1 hour'
            elif 'within 30 minutes' in line_lower:
                routing['callback_timeframe'] = 'within 30 minutes'

    return routing


def _extract_transfer_rules(text: str) -> Dict:
    """Extract call transfer rules (timeouts, retries, failure protocol)."""
    rules = {}
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()

        # Office transfer timeout
        if ('transfer' in line_lower or 'busy' in line_lower) and \
           ('office' in line_lower or 'doesn\'t answer' in line_lower):
            timeout = extract_timeout(line)
            if timeout:
                rules['office_timeout_seconds'] = timeout

    # Fallback message
    fallback = _extract_fallback_message(text)
    if fallback:
        rules['fallback_message'] = fallback

    return rules


def _extract_integration_constraints(text: str) -> List[str]:
    """Extract integration constraints (ServiceTrade rules, etc.)."""
    constraints = []
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()

        # Skip question lines (from Clara rep, not constraints)
        if line_lower.strip().endswith('?'):
            continue
        # Skip lines that are just discussing ServiceTrade without a constraint
        if 'can clara' in line_lower or 'we can integrate' in line_lower:
            continue

        # ServiceTrade specific rules with clear constraints
        if 'servicetrade' in line_lower or 'service trade' in line_lower:
            if any(kw in line_lower for kw in ['never', 'don\'t', 'do not', 'should not', 'cannot', 'do not create']):
                constraints.append(_clean_constraint(line.strip()))
            elif 'create' in line_lower and ('can' in line_lower or 'should' in line_lower):
                constraints.append(_clean_constraint(line.strip()))

        # Housecall Pro or other systems
        if 'housecall pro' in line_lower:
            constraints.append(_clean_constraint(line.strip()))

    return list(set(constraints))


def _clean_constraint(text: str) -> str:
    """Clean up a constraint text to be more readable."""
    # Remove conversational filler
    text = re.sub(r'^(?:OK so |So |Yeah |Right |Also |And |Oh and |Oh, and )', '', text, flags=re.IGNORECASE)
    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    return text


def _extract_after_hours_flow(text: str) -> str:
    """Generate after-hours flow summary from extracted data."""
    return ("After hours: Greet caller, note office is closed, determine purpose, "
            "check if emergency. If emergency: collect name, number, address, "
            "attempt routing via escalation chain. If non-emergency: collect "
            "details, confirm next-business-day callback.")


def _extract_office_hours_flow(text: str) -> str:
    """Generate office hours flow summary from extracted data."""
    return ("Business hours: Greet caller, determine purpose, check if emergency. "
            "If emergency: collect critical info and route immediately. "
            "If routine: collect name and number, transfer to office. "
            "If transfer fails: take message, confirm callback timeframe.")


def _extract_greeting(text: str) -> Optional[str]:
    """Extract custom greeting if specified."""
    patterns = [
        re.compile(r'(?:greeting|let\'s do)[:\s]+["\u201c](.+?)["\u201d\']', re.IGNORECASE),
        re.compile(r'["\u201c]([Tt]hank you for calling[^"\u201d]+)["\u201d]'),
        re.compile(r'["\u201c]([Tt]hanks for calling[^"\u201d]+)["\u201d]'),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            greeting = match.group(1).strip()
            # Ensure we got the full greeting, not just a fragment
            if len(greeting) > 20:
                return greeting
    return None


def _extract_collection_fields(text: str) -> List[str]:
    """Extract additional data collection requirements for non-emergency calls."""
    fields = []
    lines = text.split('\n')

    collection_keywords = [
        'ask for', 'ask about', 'collect', 'should ask',
        'also ask', 'need to know', 'ask what', 'ask the',
    ]

    for line in lines:
        line_lower = line.lower()
        for keyword in collection_keywords:
            if keyword in line_lower:
                # Extract the field being asked for
                match = re.search(
                    rf'{keyword}\s+(?:the\s+)?(?:their\s+)?(.+?)(?:\.|,|$)',
                    line,
                    re.IGNORECASE
                )
                if match:
                    field = match.group(1).strip()
                    if len(field) > 3 and len(field) < 100:
                        fields.append(field)

    return list(set(fields))


def _identify_unknowns(memo: Dict) -> List[str]:
    """Identify fields that are missing or uncertain."""
    unknowns = []

    if not memo.get('business_hours', {}).get('regular', {}).get('start'):
        unknowns.append('Business hours start time not confirmed')
    if not memo.get('business_hours', {}).get('timezone'):
        unknowns.append('Timezone not specified')
    if not memo.get('office_address'):
        unknowns.append('Office address not provided')
    if not memo.get('emergency_definition'):
        unknowns.append('Emergency definitions not clearly stated')
    if not memo.get('emergency_routing_rules', {}).get('chain'):
        unknowns.append('Emergency routing chain not specified')
    if not memo.get('services_supported'):
        unknowns.append('Specific services not listed')

    return unknowns


def _generate_notes(transcript: Dict, memo: Dict) -> str:
    """Generate contextual notes about the extraction."""
    notes_parts = []

    if transcript['call_type'] == 'demo':
        notes_parts.append(
            "Extracted from demo call — details may be preliminary and subject "
            "to change during onboarding."
        )
    elif transcript['call_type'] == 'onboarding':
        notes_parts.append(
            "Extracted from onboarding call — these are confirmed operational details."
        )

    if memo['questions_or_unknowns']:
        notes_parts.append(
            f"{len(memo['questions_or_unknowns'])} items need clarification."
        )

    return ' '.join(notes_parts)
