"""
patterns.py - Rule-based extraction patterns for Clara Automation Pipeline.

Contains regex patterns and keyword dictionaries for extracting structured
data from call transcripts without using any paid LLM.
"""

import re
from typing import List, Dict, Optional, Tuple


# ============================================================================
# TIME / HOURS PATTERNS
# ============================================================================

TIME_PATTERN = re.compile(
    r'(\d{1,2})\s*(?::(\d{2}))?\s*(AM|PM|am|pm|a\.m\.|p\.m\.)',
    re.IGNORECASE
)

HOURS_RANGE_PATTERN = re.compile(
    r'(\d{1,2})\s*(?::(\d{2}))?\s*(AM|PM|am|pm|a\.m\.|p\.m\.)?'
    r'\s*(?:to|through|-|–|until)\s*'
    r'(\d{1,2})\s*(?::(\d{2}))?\s*(AM|PM|am|pm|a\.m\.|p\.m\.)',
    re.IGNORECASE
)

DAY_PATTERNS = {
    'monday': re.compile(r'\bmonday\b', re.IGNORECASE),
    'tuesday': re.compile(r'\btuesday\b', re.IGNORECASE),
    'wednesday': re.compile(r'\bwednesday\b', re.IGNORECASE),
    'thursday': re.compile(r'\bthursday\b', re.IGNORECASE),
    'friday': re.compile(r'\bfriday\b', re.IGNORECASE),
    'saturday': re.compile(r'\bsaturday\b', re.IGNORECASE),
    'sunday': re.compile(r'\bsunday\b', re.IGNORECASE),
}

DAY_RANGE_PATTERN = re.compile(
    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
    r'\s*(?:to|through|-|–)\s*'
    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
    re.IGNORECASE
)

TIMEZONE_PATTERNS = {
    'Eastern': re.compile(r'\b(?:eastern|EST|EDT|ET)\b', re.IGNORECASE),
    'Central': re.compile(r'\b(?:central|CST|CDT|CT)\b', re.IGNORECASE),
    'Mountain': re.compile(r'\b(?:mountain|MST|MDT|MT)\b', re.IGNORECASE),
    'Pacific': re.compile(r'\b(?:pacific|PST|PDT|PT)\b', re.IGNORECASE),
    'Arizona': re.compile(r'\b(?:arizona\s+time|mountain\s+standard)\b', re.IGNORECASE),
}

# ============================================================================
# PHONE NUMBER PATTERNS
# ============================================================================

PHONE_PATTERN = re.compile(
    r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})'
)

# ============================================================================
# ADDRESS PATTERNS
# ============================================================================

ADDRESS_PATTERN = re.compile(
    r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct)\.?'
    r'(?:\s*,?\s*(?:Suite|Ste|Apt|Unit|#)\s*\d+[A-Za-z]?)?'
    r'\s*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)',
    re.IGNORECASE
)

STATE_ABBREVS = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC'
}

# ============================================================================
# EMERGENCY KEYWORD PATTERNS
# ============================================================================

EMERGENCY_KEYWORDS = [
    # Electrical
    'exposed live wir', 'sparking panel', 'power loss', 'power outage',
    'fire risk', 'electrical fire', 'live wire',
    # Fire protection
    'sprinkler discharge', 'active sprinkler', 'fire alarm', 'alarm fault',
    'suppression system', 'compromised', 'sprinkler pipe burst', 'frozen pipe',
    'kitchen hood', 'fire department inspection',
    # HVAC
    'heating failure', 'gas leak', 'gas smell', 'carbon monoxide', 'co detector',
    'furnace', 'no heat',
    # Plumbing
    'water leak', 'burst pipe', 'sewer backup', 'sewer overflow',
    'gas line damage', 'no hot water', 'main water line', 'flooding',
    # Security
    'access control down', 'alarm panel offline', 'communication failure',
    'tampered', 'cctv failure', 'security threat',
    # General
    'emergency', 'urgent', 'immediate', 'life safety', 'dangerous',
]

EMERGENCY_SECTION_PATTERN = re.compile(
    r'(?:emergency|emergencies|urgent|critical)\s*(?:is|are|definition|would be|for us|calls?)[:,]?\s*(.+?)(?:\.|$)',
    re.IGNORECASE | re.DOTALL
)

# ============================================================================
# SERVICE TYPE KEYWORDS
# ============================================================================

SERVICE_KEYWORDS = {
    'electrical': [
        'panel upgrade', 'lighting', 'rewiring', 'electrical work',
        'wiring', 'circuit', 'outlet', 'switch', 'transformer',
    ],
    'fire_protection': [
        'sprinkler', 'fire alarm', 'fire suppression', 'extinguisher',
        'fire inspection', 'backflow', 'standpipe', 'hood system',
        'fire protection',
    ],
    'hvac': [
        'hvac', 'heating', 'cooling', 'air conditioning', 'ac',
        'furnace', 'heat pump', 'duct', 'ventilation', 'thermostat',
        'indoor air quality', 'duct cleaning',
    ],
    'plumbing': [
        'plumbing', 'pipe', 'water heater', 'drain', 'sewer',
        'backflow', 'grease trap', 'faucet', 'toilet', 'water line',
    ],
    'security': [
        'alarm system', 'access control', 'cctv', 'surveillance',
        'security', 'monitoring', 'camera', 'badge reader',
    ],
}

# ============================================================================
# ROUTING PATTERNS
# ============================================================================

TIMEOUT_PATTERN = re.compile(
    r'(\d+)\s*(?:second|sec)s?',
    re.IGNORECASE
)

TRANSFER_FAIL_PATTERNS = [
    re.compile(r'if\s+(?:the\s+)?transfer\s+(?:doesn\'t|does not|fails)', re.IGNORECASE),
    re.compile(r'if\s+(?:no one|nobody|they don\'t)\s+(?:answers?|picks?\s+up)', re.IGNORECASE),
    re.compile(r'if\s+(?:all\s+(?:three|fail|calls?\s+fail))', re.IGNORECASE),
    re.compile(r'(?:busy|doesn\'t\s+answer|no\s+answer)', re.IGNORECASE),
]

ROUTING_ROLE_KEYWORDS = [
    'on-call', 'oncall', 'on call', 'tech', 'technician',
    'backup', 'supervisor', 'manager', 'dispatcher', 'dispatch',
    'owner', 'me', 'myself', 'field supervisor', 'partner',
]

# ============================================================================
# INTEGRATION CONSTRAINT PATTERNS
# ============================================================================

SERVICETRADE_PATTERN = re.compile(
    r'service\s*trade', re.IGNORECASE
)

NEVER_CREATE_PATTERN = re.compile(
    r'(?:never|do\s+not|don\'t|should\s+not)\s+'
    r'(?:create|make|enter|put|add)\s+'
    r'(?:.*?)(?:in|into|to)\s+'
    r'(?:service\s*trade|the\s+system)',
    re.IGNORECASE
)

DO_NOT_DO_PATTERN = re.compile(
    r'(?:we\s+)?(?:don\'t|do\s+not|never|doesn\'t)\s+(?:do|offer|provide|handle|service)\s+(.+?)(?:\.|,|$)',
    re.IGNORECASE
)

# ============================================================================
# COMPANY NAME EXTRACTION
# ============================================================================

COMPANY_NAME_PATTERNS = [
    re.compile(r"(?:we're|we are|this is|I'm with|company is|company called)\s+([A-Z][A-Za-z\s&']+?)(?:\s*[,.]|\s+(?:we|based|out|here|in|and))", re.IGNORECASE),
    re.compile(r"(?:Clara (?:Demo|Onboarding) Call)\s*[-–]\s*(.+?)$", re.MULTILINE),
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_time(hour: str, minute: str, ampm: str) -> str:
    """Convert time components to HH:MM AM/PM format."""
    h = int(hour)
    m = minute if minute else "00"
    ap = ampm.upper().replace('.', '')
    return f"{h}:{m} {ap}"


def extract_phone_numbers(text: str) -> List[str]:
    """Extract all phone numbers from text."""
    matches = PHONE_PATTERN.findall(text)
    return [f"{m[0]}-{m[1]}-{m[2]}" for m in matches]


def extract_address(text: str) -> Optional[str]:
    """Extract first address from text."""
    match = ADDRESS_PATTERN.search(text)
    return match.group(0).strip() if match else None


def extract_timezone(text: str) -> Optional[str]:
    """Detect timezone from text."""
    for tz_name, pattern in TIMEZONE_PATTERNS.items():
        if pattern.search(text):
            return tz_name
    return None


def extract_hours_range(text: str) -> Optional[Dict]:
    """Extract a time range from text (e.g., '7 AM to 5 PM')."""
    match = HOURS_RANGE_PATTERN.search(text)
    if match:
        start_h, start_m, start_ap, end_h, end_m, end_ap = match.groups()
        # If start has no AM/PM, infer from context
        if not start_ap:
            start_ap = 'AM'  # default assumption for start times
        return {
            'start': normalize_time(start_h, start_m, start_ap),
            'end': normalize_time(end_h, end_m, end_ap),
        }
    return None


def extract_days_range(text: str) -> Optional[List[str]]:
    """Extract day range like 'Monday through Friday'."""
    day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    match = DAY_RANGE_PATTERN.search(text)
    if match:
        start = match.group(1).lower()
        end = match.group(2).lower()
        start_idx = day_order.index(start)
        end_idx = day_order.index(end)
        if end_idx >= start_idx:
            return [d.capitalize() for d in day_order[start_idx:end_idx + 1]]
    return None


def find_emergency_triggers(text: str) -> List[str]:
    """Find emergency-related phrases in text."""
    found = []
    text_lower = text.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            # Get the surrounding context
            idx = text_lower.index(keyword)
            start = max(0, idx - 20)
            end = min(len(text), idx + len(keyword) + 50)
            context = text[start:end].strip()
            # Clean up and add
            found.append(keyword.strip())
    return list(set(found))


def find_services(text: str) -> Dict[str, List[str]]:
    """Identify supported services by category."""
    found = {}
    text_lower = text.lower()
    for category, keywords in SERVICE_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            found[category] = matches
    return found


def find_excluded_services(text: str) -> List[str]:
    """Find services the company does NOT offer."""
    excluded = []
    for match in DO_NOT_DO_PATTERN.finditer(text):
        service = match.group(1).strip()
        if len(service) < 80:  # reasonable length
            excluded.append(service)
    return excluded


def extract_timeout(text: str) -> Optional[int]:
    """Extract a timeout in seconds from text."""
    match = TIMEOUT_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return None


def extract_routing_entries(text: str) -> List[Dict]:
    """Extract phone routing entries with roles and numbers."""
    entries = []
    lines = text.split('\n')
    for line in lines:
        phones = extract_phone_numbers(line)
        if phones:
            # Try to identify the role
            line_lower = line.lower()
            role = "unknown"
            for keyword in ROUTING_ROLE_KEYWORDS:
                if keyword in line_lower:
                    role = keyword
                    break
            timeout = extract_timeout(line)
            for phone in phones:
                entries.append({
                    'phone': phone,
                    'role': role,
                    'timeout_seconds': timeout,
                })
    return entries
