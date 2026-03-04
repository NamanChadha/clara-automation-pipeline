"""
generate_agent_spec.py - Retell agent draft specification generator.

Produces a Retell-compatible agent configuration JSON
based on an extracted account memo.
"""

from typing import Dict
from scripts.utils.prompt_templates import generate_system_prompt


def generate_agent_spec(memo: Dict, version: str = "v1") -> Dict:
    """
    Generate a Retell agent draft specification from an account memo.

    Args:
        memo: Account memo dict from extract_memo()
        version: Version string ("v1" for demo, "v2" for onboarding)

    Returns:
        Retell-compatible agent spec dict.
    """
    company_name = memo.get('company_name', 'Unknown Company')
    system_prompt = generate_system_prompt(memo)

    spec = {
        # Agent identity
        'agent_name': f"Clara - {company_name}",
        'version': version,
        'version_description': _version_description(version),

        # Voice configuration
        'voice_id': 'retell-Cimo',
        'voice_model': 'eleven_turbo_v2',
        'voice_speed': 1.0,
        'voice_temperature': 0.7,
        'voice_emotion': 'friendly',
        'volume': 1.0,

        # Response engine
        'response_engine': {
            'type': 'retell-llm',
            'llm_id': 'PLACEHOLDER_LLM_ID',
            'system_prompt': system_prompt,
        },

        # Language
        'language': 'en-US',

        # Behavior settings
        'responsiveness': 0.8,
        'interruption_sensitivity': 0.6,
        'enable_backchannel': True,
        'backchannel_frequency': 0.8,
        'backchannel_words': ['yeah', 'uh-huh', 'got it', 'I see'],

        # Timing
        'reminder_trigger_ms': 15000,
        'reminder_max_count': 2,
        'end_call_after_silence_ms': 30000,
        'max_call_duration_ms': 600000,  # 10 minutes

        # Key variables (extracted from memo)
        'key_variables': {
            'company_name': company_name,
            'timezone': memo.get('business_hours', {}).get('timezone', ''),
            'business_hours': memo.get('business_hours', {}),
            'office_address': memo.get('office_address', ''),
            'emergency_routing_chain': memo.get('emergency_routing_rules', {}).get('chain', []),
            'office_number': memo.get('non_emergency_routing_rules', {}).get('office_number', ''),
        },

        # Tool invocation placeholders (internal - not shown to caller)
        'tool_invocations': [
            {
                'name': 'transfer_call',
                'description': 'Transfer the call to a specified phone number',
                'parameters': {
                    'phone_number': {'type': 'string', 'description': 'Number to transfer to'},
                    'timeout_seconds': {'type': 'integer', 'description': 'Seconds to wait'},
                },
                'note': 'INTERNAL ONLY - never mention to caller',
            },
            {
                'name': 'create_service_request',
                'description': 'Create a service request in the job management system',
                'parameters': {
                    'caller_name': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'service_type': {'type': 'string'},
                    'description': {'type': 'string'},
                    'address': {'type': 'string'},
                    'priority': {'type': 'string', 'enum': ['normal', 'urgent']},
                },
                'note': 'INTERNAL ONLY - never mention to caller',
            },
            {
                'name': 'send_notification',
                'description': 'Send an alert notification to the team',
                'parameters': {
                    'message': {'type': 'string'},
                    'urgency': {'type': 'string', 'enum': ['normal', 'high', 'critical']},
                },
                'note': 'INTERNAL ONLY - never mention to caller',
            },
        ],

        # Call transfer protocol
        'call_transfer_protocol': _build_transfer_protocol(memo),

        # Fallback protocol
        'fallback_protocol': _build_fallback_protocol(memo),

        # Voicemail detection
        'enable_voicemail_detection': True,
        'voicemail_message': f"Hi, this is Clara calling from {company_name}. "
                            f"We received your call and will be reaching out again shortly. "
                            f"Thank you.",

        # Post-call analysis
        'post_call_analysis_data': [
            {
                'type': 'string',
                'name': 'caller_name',
                'description': 'Name of the caller',
            },
            {
                'type': 'string',
                'name': 'call_purpose',
                'description': 'What the caller needed',
            },
            {
                'type': 'string',
                'name': 'call_type',
                'description': 'Emergency or non-emergency',
            },
            {
                'type': 'string',
                'name': 'action_taken',
                'description': 'What action was taken (transferred, message taken, etc.)',
            },
        ],
    }

    return spec


def _version_description(version: str) -> str:
    """Generate version description."""
    if version == "v1":
        return "Preliminary agent configuration based on demo call. Subject to refinement during onboarding."
    elif version == "v2":
        return "Updated agent configuration based on onboarding call. Confirmed operational details."
    return f"Agent configuration {version}"


def _build_transfer_protocol(memo: Dict) -> Dict:
    """Build the call transfer protocol configuration."""
    routing = memo.get('emergency_routing_rules', {})
    chain = routing.get('chain', [])
    transfer_rules = memo.get('call_transfer_rules', {})

    protocol = {
        'emergency_chain': [],
        'office_transfer': {
            'number': memo.get('non_emergency_routing_rules', {}).get('office_number', ''),
            'timeout_seconds': transfer_rules.get('office_timeout_seconds', 30),
        },
    }

    for entry in chain:
        protocol['emergency_chain'].append({
            'role': entry.get('role', 'Contact'),
            'number': entry.get('phone', ''),
            'timeout_seconds': entry.get('timeout_seconds', 60),
        })

    return protocol


def _build_fallback_protocol(memo: Dict) -> Dict:
    """Build the fallback protocol when transfers fail."""
    transfer_rules = memo.get('call_transfer_rules', {})
    routing = memo.get('emergency_routing_rules', {})

    return {
        'emergency_fallback_message': routing.get(
            'fallback_message',
            "I apologize for the inconvenience. I've notified our team and "
            "someone will call you back as soon as possible. If this is a "
            "life-threatening emergency, please call 911."
        ),
        'non_emergency_fallback_message': (
            "I wasn't able to reach anyone at the office right now. "
            "I've taken down all your information and someone from our team "
            "will call you back shortly."
        ),
        'callback_timeframe': memo.get('non_emergency_routing_rules', {}).get(
            'callback_timeframe', 'within 1 hour'
        ),
    }
