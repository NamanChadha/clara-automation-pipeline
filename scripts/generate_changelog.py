"""
generate_changelog.py - Changelog generator for Clara Automation Pipeline.

Produces per-account changelog.md files showing field-by-field changes
between v1 (demo) and v2 (onboarding).
"""

import json
from typing import Dict, List
from datetime import datetime


def generate_changelog(
    account_id: str,
    company_name: str,
    changes: List[Dict]
) -> str:
    """
    Generate a markdown changelog from a list of changes.

    Args:
        account_id: The account identifier
        company_name: The company name
        changes: List of {field, old_value, new_value, reason} dicts

    Returns:
        Markdown string for the changelog
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# Changelog: {company_name}",
        f"**Account ID**: `{account_id}`",
        f"**Generated**: {now}",
        f"**Transition**: v1 (Demo) → v2 (Onboarding)",
        "",
        "---",
        "",
        "## Summary",
        f"Total changes: **{len(changes)}** field(s) updated.",
        "",
    ]

    if not changes:
        lines.append("_No changes detected between demo and onboarding data._")
        return '\n'.join(lines)

    # Categorize changes
    categories = _categorize_changes(changes)

    for category, category_changes in categories.items():
        lines.append(f"## {category}")
        lines.append("")

        for change in category_changes:
            field = change['field']
            old_val = change['old_value']
            new_val = change['new_value']
            reason = change.get('reason', 'Updated during onboarding')

            lines.append(f"### `{field}`")
            lines.append(f"**Reason**: {reason}")
            lines.append("")

            # Format the diff
            if isinstance(old_val, (list, dict)):
                lines.append("**Before (v1)**:")
                lines.append("```json")
                lines.append(json.dumps(old_val, indent=2))
                lines.append("```")
                lines.append("")
                lines.append("**After (v2)**:")
                lines.append("```json")
                lines.append(json.dumps(new_val, indent=2))
                lines.append("```")
            else:
                lines.append(f"- **Before (v1)**: {old_val or '_(not set)_'}")
                lines.append(f"- **After (v2)**: {new_val}")

            lines.append("")
            lines.append("---")
            lines.append("")

    return '\n'.join(lines)


def _categorize_changes(changes: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize changes into logical groups."""
    categories = {
        '⏰ Business Hours': [],
        '🚨 Emergency Configuration': [],
        '📞 Routing & Transfer': [],
        '💰 Pricing & Fees': [],
        '🔧 Integration & Constraints': [],
        '👤 Contact Info': [],
        '📝 Other Changes': [],
    }

    for change in changes:
        field = change['field']
        if 'business_hours' in field or 'holiday' in field or 'seasonal' in field:
            categories['⏰ Business Hours'].append(change)
        elif 'emergency' in field:
            categories['🚨 Emergency Configuration'].append(change)
        elif 'routing' in field or 'transfer' in field:
            categories['📞 Routing & Transfer'].append(change)
        elif 'fee' in field or 'price' in field or 'rate' in field or 'pricing' in field:
            categories['💰 Pricing & Fees'].append(change)
        elif 'integration' in field or 'constraint' in field:
            categories['🔧 Integration & Constraints'].append(change)
        elif 'contact' in field or 'email' in field or 'name' in field:
            categories['👤 Contact Info'].append(change)
        elif 'service' in field.lower():
             categories['🔧 Integration & Constraints'].append(change)
        else:
            categories['📝 Other Changes'].append(change)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def generate_changes_json(
    account_id: str,
    company_name: str,
    changes: List[Dict]
) -> Dict:
    """
    Generate a structured JSON changelog.

    Returns:
        Dict suitable for saving as changes.json
    """
    return {
        'account_id': account_id,
        'company_name': company_name,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'transition': 'v1 → v2',
        'total_changes': len(changes),
        'changes': changes,
    }
