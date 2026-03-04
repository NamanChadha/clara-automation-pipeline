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

    # Services supported (merge lists)
    v1_services = set(v1_memo.get('services_supported', []))
    ob_services = set(onboarding_memo.get('services_supported', []))
    if ob_services and ob_services != v1_services:
        merged_services = list(v1_services | ob_services)
        changes.append({
            'field': 'services_supported',
            'old_value': sorted(list(v1_services)),
            'new_value': sorted(merged_services),
            'reason': 'Services list updated with onboarding data',
        })
        v2_memo['services_supported'] = sorted(merged_services)

    # Emergency definitions (merge and update)
    v1_emergencies = v1_memo.get('emergency_definition', [])
    ob_emergencies = onboarding_memo.get('emergency_definition', [])
    if ob_emergencies:
        merged_emergencies = _merge_lists_smart(v1_emergencies, ob_emergencies)
        if merged_emergencies != v1_emergencies:
            changes.append({
                'field': 'emergency_definition',
                'old_value': v1_emergencies,
                'new_value': merged_emergencies,
                'reason': 'Emergency definitions refined during onboarding',
            })
            v2_memo['emergency_definition'] = merged_emergencies

    # Emergency routing rules
    routing_changes = _merge_routing(
        v1_memo.get('emergency_routing_rules', {}),
        onboarding_memo.get('emergency_routing_rules', {}),
        v2_memo
    )
    changes.extend(routing_changes)

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

    # Integration constraints (merge lists)
    v1_constraints = v1_memo.get('integration_constraints', [])
    ob_constraints = onboarding_memo.get('integration_constraints', [])
    if ob_constraints:
        merged_constraints = _merge_lists_smart(v1_constraints, ob_constraints)
        if merged_constraints != v1_constraints:
            changes.append({
                'field': 'integration_constraints',
                'old_value': v1_constraints,
                'new_value': merged_constraints,
                'reason': 'Integration constraints updated during onboarding',
            })
            v2_memo['integration_constraints'] = merged_constraints

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

    # Custom greeting (onboarding overrides)
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

    # Re-evaluate unknowns (some may be resolved)
    v2_memo['questions_or_unknowns'] = _re_evaluate_unknowns(v2_memo, v1_memo)
    v2_memo['notes'] = (
        "Updated from onboarding call. Confirmed operational details "
        "override demo assumptions."
    )

    return v2_memo, changes


def _merge_business_hours(v1_hours: Dict, ob_hours: Dict, v2_memo: Dict) -> List[Dict]:
    """Merge business hours, onboarding overrides demo."""
    changes = []
    merged = copy.deepcopy(v1_hours)

    # Regular hours
    if ob_hours.get('regular') and ob_hours['regular'].get('start'):
        old = v1_hours.get('regular', {})
        new = ob_hours['regular']
        if old != new:
            changes.append({
                'field': 'business_hours.regular',
                'old_value': old,
                'new_value': new,
                'reason': 'Regular business hours confirmed/updated during onboarding',
            })
            merged['regular'] = new

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

    for key in ['office_number', 'callback_timeframe']:
        if ob.get(key) and ob[key] != v1.get(key, ''):
            changes.append({
                'field': f'non_emergency_routing_rules.{key}',
                'old_value': v1.get(key, '(not set)'),
                'new_value': ob[key],
                'reason': f'{key} updated during onboarding',
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
