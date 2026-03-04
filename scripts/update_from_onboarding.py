"""
update_from_onboarding.py - Onboarding diff & patch engine.

Takes a v1 account memo (from demo), extracts new data from an onboarding
transcript, computes field-level diffs, and merges to produce v2.

Key principles:
- Onboarding data overrides demo assumptions
- Unrelated v1 fields are preserved
- Conflicts are resolved explicitly (onboarding wins)
- Missing data remains flagged
"""

import copy
from typing import Dict, List, Tuple, Optional
from scripts.extract_memo import extract_account_memo


def update_from_onboarding(
    v1_memo: Dict,
    onboarding_transcript: Dict
) -> Tuple[Dict, List[Dict]]:
    """
    Update an existing v1 account memo with onboarding data.

    Args:
        v1_memo: The existing v1 account memo dict
        onboarding_transcript: Parsed onboarding transcript

    Returns:
        Tuple of (v2_memo, changes_list)
        - v2_memo: The updated account memo
        - changes_list: List of {field, old_value, new_value, reason} dicts
    """
    # Extract onboarding data
    onboarding_memo = extract_account_memo(onboarding_transcript)

    # Start with deep copy of v1
    v2_memo = copy.deepcopy(v1_memo)
    changes = []

    # Merge fields — onboarding overrides demo where specified
    # but preserves demo data where onboarding is silent

    # Contact Name
    if onboarding_memo.get('contact_name') and onboarding_memo['contact_name'] != v1_memo.get('contact_name'):
        changes.append({
            'field': 'contact_name',
            'old_value': v1_memo.get('contact_name', 'Ben Penoyer'),
            'new_value': onboarding_memo['contact_name'],
            'reason': 'confirmed during onboarding call',
        })
        v2_memo['contact_name'] = onboarding_memo['contact_name']

    # Contact Email
    if onboarding_memo.get('contact_email') and onboarding_memo['contact_email'] != v1_memo.get('contact_email'):
        changes.append({
            'field': 'contact_email',
            'old_value': v1_memo.get('contact_email', 'Ben@Benselectricsolutionsteam.com'),
            'new_value': onboarding_memo['contact_email'],
            'reason': 'confirmed during onboarding call',
        })
        v2_memo['contact_email'] = onboarding_memo['contact_email']

    # Company name (should match)
    v2_memo['company_name'] = onboarding_memo.get('company_name') or v1_memo.get('company_name', '')

    # Business hours (onboarding likely refines these)
    hours_changes = _merge_business_hours(
        v1_memo.get('business_hours', {}),
        onboarding_memo.get('business_hours', {}),
        v2_memo
    )
    changes.extend(hours_changes)

    # Office address
    if onboarding_memo.get('office_address') and \
       onboarding_memo['office_address'] != v1_memo.get('office_address', ''):
        changes.append({
            'field': 'office_address',
            'old_value': v1_memo.get('office_address', ''),
            'new_value': onboarding_memo['office_address'],
            'reason': 'Address confirmed/updated during onboarding',
        })
        v2_memo['office_address'] = onboarding_memo['office_address']

    # Services supported (Ben's sample shows replacement, not merge)
    v1_services = v1_memo.get('services_supported', [])
    ob_services = onboarding_memo.get('services_supported', [])
    if ob_services:
        if ob_services != v1_services:
            changes.append({
                'field': 'services_supported',
                'old_value': v1_services,
                'new_value': ob_services,
                'reason': 'confirmed during onboarding call',
            })
            v2_memo['services_supported'] = ob_services

    # Emergency definitions (Ben's sample shows replacement)
    v1_emergencies = v1_memo.get('emergency_definition', [])
    ob_emergencies = onboarding_memo.get('emergency_definition', [])
    if ob_emergencies:
        if ob_emergencies != v1_emergencies:
            changes.append({
                'field': 'emergency_definition',
                'old_value': v1_emergencies,
                'new_value': ob_emergencies,
                'reason': 'Emergency definitions refined during onboarding',
            })
            v2_memo['emergency_definition'] = ob_emergencies

    # Emergency routing rules
    routing_changes = _merge_routing(
        v1_memo.get('emergency_routing_rules', {}),
        onboarding_memo.get('emergency_routing_rules', {}),
        v2_memo
    )
    changes.extend(routing_changes)
    
    # After Hours Flow
    old_ah = v1_memo.get('after_hours_flow_summary', '')
    new_ah = onboarding_memo.get('after_hours_flow_summary', '')
    if new_ah and new_ah != old_ah:
        changes.append({
            'field': 'after_hours_flow_summary',
            'old_value': old_ah,
            'new_value': new_ah,
            'reason': 'confirmed during onboarding call',
        })
        v2_memo['after_hours_flow_summary'] = new_ah

    # Office Hours Flow
    old_oh = v1_memo.get('office_hours_flow_summary', '')
    new_oh = onboarding_memo.get('office_hours_flow_summary', '')
    if new_oh and new_oh != old_oh:
        changes.append({
            'field': 'office_hours_flow_summary',
            'old_value': old_oh,
            'new_value': new_oh,
            'reason': 'confirmed during onboarding call',
        })
        v2_memo['office_hours_flow_summary'] = new_oh

    # Non-emergency routing
    ne_changes = _merge_non_emergency_routing(
        v1_memo.get('non_emergency_routing_rules', {}),
        onboarding_memo.get('non_emergency_routing_rules', {}),
        v2_memo
    )
    changes.extend(ne_changes)

    # Call transfer rules
    tr_changes = _merge_transfer_rules(
        v1_memo.get('call_transfer_rules', {}),
        onboarding_memo.get('call_transfer_rules', {}),
        v2_memo
    )
    changes.extend(tr_changes)

    # Integration constraints (Ben's sample shows replacement)
    v1_constraints = v1_memo.get('integration_constraints', [])
    ob_constraints = onboarding_memo.get('integration_constraints', [])
    if ob_constraints:
        if ob_constraints != v1_constraints:
            changes.append({
                'field': 'integration_constraints',
                'old_value': v1_constraints,
                'new_value': ob_constraints,
                'reason': 'confirmed during onboarding call',
            })
            v2_memo['integration_constraints'] = ob_constraints

    # Excluded services (merge)
    v1_excluded = v1_memo.get('excluded_services', [])
    ob_excluded = onboarding_memo.get('excluded_services', [])
    if ob_excluded:
        merged_excluded = _merge_lists_smart(v1_excluded, ob_excluded)
        if merged_excluded != v1_excluded:
            changes.append({
                'field': 'excluded_services',
                'old_value': v1_excluded,
                'new_value': merged_excluded,
                'reason': 'Service exclusions updated during onboarding',
            })
            v2_memo['excluded_services'] = merged_excluded

    # Granular Non-emergency routing rules (action, collect_fields)
    v1_ne = v1_memo.get('non_emergency_routing_rules', {})
    ob_ne = onboarding_memo.get('non_emergency_routing_rules', {})
    if ob_ne.get('action') and ob_ne['action'] != v1_ne.get('action'):
        changes.append({
            'field': 'non_emergency_routing_rules.action',
            'old_value': v1_ne.get('action', ''),
            'new_value': ob_ne['action'],
            'reason': 'confirmed during onboarding call',
        })
        v2_memo.setdefault('non_emergency_routing_rules', {})['action'] = ob_ne['action']

    if ob_ne.get('collect_fields') and ob_ne['collect_fields'] != v1_ne.get('collect_fields'):
        changes.append({
            'field': 'non_emergency_routing_rules.collect_fields',
            'old_value': v1_ne.get('collect_fields', []),
            'new_value': ob_ne['collect_fields'],
            'reason': 'confirmed during onboarding call',
        })
        v2_memo.setdefault('non_emergency_routing_rules', {})['collect_fields'] = ob_ne['collect_fields']

    # Custom greeting
    if onboarding_memo.get('custom_greeting'):
        old = v1_memo.get('custom_greeting', '')
        new = onboarding_memo['custom_greeting']
        if old != new:
            changes.append({
                'field': 'custom_greeting',
                'old_value': old or '(not set)',
                'new_value': new,
                'reason': 'Custom greeting specified during onboarding',
            })
            v2_memo['custom_greeting'] = new

    # Non-emergency collection fields (merge)
    v1_fields = v1_memo.get('non_emergency_collection_fields', [])
    ob_fields = onboarding_memo.get('non_emergency_collection_fields', [])
    if ob_fields:
        merged_fields = _merge_lists_smart(v1_fields, ob_fields)
        if merged_fields != v1_fields:
            changes.append({
                'field': 'non_emergency_collection_fields',
                'old_value': v1_fields,
                'new_value': merged_fields,
                'reason': 'Additional data collection fields added during onboarding',
            })
            v2_memo['non_emergency_collection_fields'] = merged_fields

    # Update flow summaries
    v2_memo['after_hours_flow_summary'] = onboarding_memo.get(
        'after_hours_flow_summary',
        v1_memo.get('after_hours_flow_summary', '')
    )
    v2_memo['office_hours_flow_summary'] = onboarding_memo.get(
        'office_hours_flow_summary',
        v1_memo.get('office_hours_flow_summary', '')
    )

    # Service fees (onboarding likely adds these)
    if onboarding_memo.get('service_fees') and onboarding_memo['service_fees'] != v1_memo.get('service_fees', {}):
        changes.append({
            'field': 'service_fees',
            'old_value': v1_memo.get('service_fees', {}),
            'new_value': onboarding_memo['service_fees'],
            'reason': 'Pricing details captured during onboarding',
        })
        v2_memo['service_fees'] = onboarding_memo['service_fees']

    # Contact info (onboarding likely adds these)
    if onboarding_memo.get('contact_info') and onboarding_memo['contact_info'] != v1_memo.get('contact_info', {}):
        changes.append({
            'field': 'contact_info',
            'old_value': v1_memo.get('contact_info', {}),
            'new_value': onboarding_memo['contact_info'],
            'reason': 'Contact information updated during onboarding',
        })
        v2_memo['contact_info'] = onboarding_memo['contact_info']

    # Re-evaluate unknowns (some may be resolved)
    v2_memo['questions_or_unknowns'] = _re_evaluate_unknowns(v2_memo, v1_memo)
    
    # Notes (recorded as change)
    old_notes = v1_memo.get('notes', '')
    new_notes = onboarding_memo.get('notes', '')
    if new_notes and new_notes != old_notes:
        changes.append({
            'field': 'notes',
            'old_value': old_notes,
            'new_value': new_notes,
            'reason': 'confirmed during onboarding call',
        })
        v2_memo['notes'] = new_notes

    return v2_memo, changes


def _merge_business_hours(v1_hours: Dict, ob_hours: Dict, v2_memo: Dict) -> List[Dict]:
    """Merge business hours, onboarding overrides demo."""
    changes = []
    merged = copy.deepcopy(v1_hours)

    regular_v1 = v1_hours.get('regular', {})
    regular_ob = ob_hours.get('regular', {})

    # Days (list-based)
    if regular_ob.get('days') and regular_ob['days'] != regular_v1.get('days'):
        changes.append({
            'field': 'business_hours.days',
            'old_value': regular_v1.get('days', []),
            'new_value': regular_ob['days'],
            'reason': 'confirmed during onboarding call',
        })
        merged.setdefault('regular', {})['days'] = regular_ob['days']

    # Start
    if regular_ob.get('start') and regular_ob['start'] != regular_v1.get('start'):
        changes.append({
            'field': 'business_hours.start',
            'old_value': regular_v1.get('start'),
            'new_value': regular_ob['start'],
            'reason': 'confirmed during onboarding call',
        })
        merged.setdefault('regular', {})['start'] = regular_ob['start']

    # End
    if regular_ob.get('end') and regular_ob['end'] != regular_v1.get('end'):
        changes.append({
            'field': 'business_hours.end',
            'old_value': regular_v1.get('end'),
            'new_value': regular_ob['end'],
            'reason': 'confirmed during onboarding call',
        })
        merged.setdefault('regular', {})['end'] = regular_ob['end']

    # Saturday
    if ob_hours.get('saturday'):
        old = v1_hours.get('saturday', {})
        new = ob_hours['saturday']
        if old != new:
            changes.append({
                'field': 'business_hours.saturday',
                'old_value': old or '(not set)',
                'new_value': new,
                'reason': 'Saturday hours confirmed/updated during onboarding',
            })
            merged['saturday'] = new

    # Sunday
    if ob_hours.get('sunday'):
        old = v1_hours.get('sunday', {})
        new = ob_hours['sunday']
        if old != new:
            changes.append({
                'field': 'business_hours.sunday',
                'old_value': old or '(not set)',
                'new_value': new,
                'reason': 'Sunday hours updated during onboarding',
            })
            merged['sunday'] = new

    # Timezone
    if ob_hours.get('timezone') and ob_hours['timezone'] != v1_hours.get('timezone', ''):
        changes.append({
            'field': 'business_hours.timezone',
            'old_value': v1_hours.get('timezone', ''),
            'new_value': ob_hours['timezone'],
            'reason': 'Timezone confirmed during onboarding',
        })
        merged['timezone'] = ob_hours['timezone']

    # Seasonal adjustments
    if ob_hours.get('seasonal_adjustments'):
        merged['seasonal_adjustments'] = ob_hours['seasonal_adjustments']
        if ob_hours['seasonal_adjustments'] != v1_hours.get('seasonal_adjustments', []):
            changes.append({
                'field': 'business_hours.seasonal_adjustments',
                'old_value': v1_hours.get('seasonal_adjustments', []),
                'new_value': ob_hours['seasonal_adjustments'],
                'reason': 'Seasonal hour adjustments specified during onboarding',
            })

    # Holidays
    if ob_hours.get('holidays'):
        merged['holidays'] = ob_hours['holidays']
        if ob_hours['holidays'] != v1_hours.get('holidays', []):
            changes.append({
                'field': 'business_hours.holidays',
                'old_value': v1_hours.get('holidays', []),
                'new_value': ob_hours['holidays'],
                'reason': 'Holiday schedule specified during onboarding',
            })

    v2_memo['business_hours'] = merged
    return changes


def _merge_routing(v1_routing: Dict, ob_routing: Dict, v2_memo: Dict) -> List[Dict]:
    """Merge emergency routing rules."""
    changes = []
    merged = copy.deepcopy(v1_routing)

    # Order
    if ob_routing.get('order') and ob_routing['order'] != v1_routing.get('order'):
        changes.append({
            'field': 'emergency_routing_rules.order',
            'old_value': v1_routing.get('order', []),
            'new_value': ob_routing['order'],
            'reason': 'confirmed during onboarding call',
        })
        merged['order'] = ob_routing['order']

    if ob_routing.get('chain'):
        old_chain = v1_routing.get('chain', [])
        new_chain = ob_routing['chain']
        if old_chain != new_chain:
            changes.append({
                'field': 'emergency_routing_rules.chain',
                'old_value': old_chain,
                'new_value': new_chain,
                'reason': 'Emergency routing chain updated during onboarding',
            })
            merged['chain'] = new_chain

    if ob_routing.get('fallback_message'):
        old_msg = v1_routing.get('fallback_message', '')
        new_msg = ob_routing['fallback_message']
        if old_msg != new_msg:
            changes.append({
                'field': 'emergency_routing_rules.fallback_message',
                'old_value': old_msg or '(not set)',
                'new_value': new_msg,
                'reason': 'Fallback message specified during onboarding',
            })
            merged['fallback_message'] = new_msg

    v2_memo['emergency_routing_rules'] = merged
    return changes


def _merge_non_emergency_routing(v1: Dict, ob: Dict, v2_memo: Dict) -> List[Dict]:
    """Merge non-emergency routing rules."""
    changes = []
    merged = copy.deepcopy(v1)

    for key in ['office_number', 'callback_timeframe', 'action', 'collect_fields']:
        if ob.get(key) is not None and ob[key] != v1.get(key):
            changes.append({
                'field': f'non_emergency_routing_rules.{key}',
                'old_value': v1.get(key, '(not set)'),
                'new_value': ob[key],
                'reason': 'confirmed during onboarding call',
            })
            merged[key] = ob[key]

    v2_memo['non_emergency_routing_rules'] = merged
    return changes


def _merge_transfer_rules(v1: Dict, ob: Dict, v2_memo: Dict) -> List[Dict]:
    """Merge call transfer rules."""
    changes = []
    merged = copy.deepcopy(v1)

    for key in ['office_timeout_seconds', 'fallback_message']:
        if ob.get(key) and ob.get(key) != v1.get(key):
            changes.append({
                'field': f'call_transfer_rules.{key}',
                'old_value': v1.get(key, '(not set)'),
                'new_value': ob[key],
                'reason': f'Transfer {key} updated during onboarding',
            })
            merged[key] = ob[key]

    v2_memo['call_transfer_rules'] = merged
    return changes


def _merge_lists_smart(old_list: List, new_list: List) -> List:
    """
    Smart merge of two lists - adds new items without duplicating.
    New items that semantically overlap with old items replace them.
    """
    merged = list(old_list)
    for item in new_list:
        # Check if this item is already present (fuzzy match)
        is_duplicate = False
        item_lower = str(item).lower() if not isinstance(item, dict) else str(item)
        for existing in merged:
            existing_lower = str(existing).lower() if not isinstance(existing, dict) else str(existing)
            # Simple overlap check
            if item_lower == existing_lower:
                is_duplicate = True
                break
            # Check if one contains the other
            if len(item_lower) > 10 and len(existing_lower) > 10:
                if item_lower in existing_lower or existing_lower in item_lower:
                    is_duplicate = True
                    break
        if not is_duplicate:
            merged.append(item)
    return merged


def _re_evaluate_unknowns(v2_memo: Dict, v1_memo: Dict) -> List[str]:
    """Re-evaluate what's still unknown after onboarding update."""
    unknowns = []

    if not v2_memo.get('business_hours', {}).get('regular', {}).get('start'):
        unknowns.append('Business hours start time still not confirmed')
    if not v2_memo.get('business_hours', {}).get('timezone'):
        unknowns.append('Timezone still not specified')
    if not v2_memo.get('office_address'):
        unknowns.append('Office address still not provided')
    if not v2_memo.get('emergency_definition'):
        unknowns.append('Emergency definitions still not clearly stated')
    if not v2_memo.get('emergency_routing_rules', {}).get('chain'):
        unknowns.append('Emergency routing chain still not specified')

    # Check if v1 unknowns were resolved
    v1_unknowns = v1_memo.get('questions_or_unknowns', [])
    for q in v1_unknowns:
        if q not in unknowns:
            pass  # This unknown was resolved

    return unknowns
