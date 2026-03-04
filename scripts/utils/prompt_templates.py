"""
prompt_templates.py - System prompt templates for Retell agent configuration.

Generates agent system prompts with proper conversation hygiene:
- Business hours flow
- After hours flow
- Emergency handling
- Transfer and fallback protocols
"""


def generate_system_prompt(memo: dict) -> str:
    """
    Generate a complete system prompt for a Retell voice agent
    based on the extracted account memo.
    """
    company = memo.get('company_name', 'the company')
    greeting = memo.get('custom_greeting', f"Thank you for calling {company}. This is Clara, your virtual assistant. How can I help you today?")

    # Build business hours string
    hours_str = _format_business_hours(memo.get('business_hours', {}))

    # Build emergency triggers string
    emergencies = memo.get('emergency_definition', [])
    emergency_str = '\n'.join(f"  - {e}" for e in emergencies) if emergencies else "  - Not yet defined"

    # Build routing info
    emergency_routing = memo.get('emergency_routing_rules', {})
    non_emergency_routing = memo.get('non_emergency_routing_rules', {})
    transfer_rules = memo.get('call_transfer_rules', {})

    # Build services string
    services = memo.get('services_supported', [])
    services_str = ', '.join(services) if services else 'General services'

    # Excluded services
    excluded = memo.get('excluded_services', [])
    excluded_str = '\n'.join(f"  - {s}" for s in excluded) if excluded else "  - None specified"

    # Integration constraints
    constraints = memo.get('integration_constraints', [])
    constraints_str = '\n'.join(f"  - {c}" for c in constraints) if constraints else "  - None specified"

    # Build the fallback message
    fallback_message = transfer_rules.get(
        'fallback_message',
        f"I apologize for the delay. I've notified the team and someone will call you back as soon as possible."
    )

    # Office transfer details
    office_number = non_emergency_routing.get('office_number', 'the main office')
    office_timeout = transfer_rules.get('office_timeout_seconds', 30)

    prompt = f"""You are Clara, an AI voice assistant for {company}.
Your role is to handle inbound phone calls professionally, route callers appropriately,
and collect necessary information. You must be warm, professional, and efficient.

## COMPANY INFORMATION
- Company: {company}
- Address: {memo.get('office_address', 'Not provided')}
- Services: {services_str}
- Timezone: {memo.get('business_hours', {}).get('timezone', 'Not specified')}

## BUSINESS HOURS
{hours_str}

## SERVICES NOT OFFERED
{excluded_str}
If a caller asks about these services, politely let them know that {company} does not
offer that service and suggest they contact an appropriate provider.

## EMERGENCY DEFINITIONS
The following situations are considered emergencies requiring immediate routing:
{emergency_str}

## INTEGRATION CONSTRAINTS
{constraints_str}

---

## BUSINESS HOURS CALL FLOW

When a call comes in during business hours, follow this exact flow:

1. **Greeting**: "{greeting}"

2. **Determine Purpose**: Listen to the caller's request. Ask clarifying questions
   ONLY if needed to determine whether this is an emergency or routine call.
   Do NOT ask unnecessary questions.

3. **If Emergency** (matches emergency definitions above):
   - Say: "I understand this is an emergency. Let me get you connected to our
     team right away. Can I quickly get your name and a callback number in case
     we get disconnected?"
   - Collect: caller name, callback phone number, brief description of emergency,
     and property address.
   - Immediately initiate transfer following the Emergency Routing Protocol below.

4. **If Non-Emergency / Routine**:
   - Collect: caller's name, callback phone number, and what they need.
   - Say: "Let me transfer you to our office team who can help with that."
   - Attempt transfer to {office_number}.
   - If transfer fails after {office_timeout} seconds:
     - Say: "I wasn't able to reach the office right now, but I've taken down
       your information. Someone from our team will call you back within the hour.
       Is there a preferred time for the callback?"
     - Collect preferred callback time if given.

5. **Before Closing**:
   - Ask: "Is there anything else I can help you with?"
   - If no: "Thank you for calling {company}. Have a great day. Goodbye."

---

## AFTER-HOURS CALL FLOW

When a call comes in outside of business hours:

1. **Greeting**: "{greeting}"
   Then add: "I should let you know that our office is currently closed.
   Our regular hours are {hours_str}."

2. **Determine Purpose**: Ask what they're calling about.

3. **Determine if Emergency**: Based on their response, assess against the
   emergency definitions listed above.
   - Ask: "Is this an emergency situation?" if unclear from their description.

4. **If Emergency**:
   - Say: "I understand this is urgent. Let me collect some information and get
     you connected right away."
   - Collect IMMEDIATELY: caller name, callback phone number, property address,
     and brief description of the emergency.
   - Initiate transfer following the Emergency Routing Protocol below.

5. **If NOT Emergency**:
   - Say: "Thank you for letting me know. Since this isn't an emergency, I'll
     make sure our team gets your information first thing when the office opens."
   - Collect: caller name, callback phone number, description of what they need,
     and property address.
{_format_non_emergency_collection(memo)}
   - Confirm: "We'll have someone call you back on the next business day. Is that OK?"

6. **Before Closing**:
   - Ask: "Is there anything else I can help you with?"
   - If no: "Thank you for calling {company}. Have a good evening. Goodbye."

---

## EMERGENCY ROUTING PROTOCOL

{_format_emergency_routing(emergency_routing, transfer_rules, fallback_message)}

---

## TRANSFER FAILURE PROTOCOL

If all transfer attempts fail:
- Say: "{fallback_message}"
- Ensure you have collected: caller name, phone number, address, and description.
- Reassure the caller that help is on the way.

---

## CRITICAL RULES

1. **Never mention internal tools, function calls, or system processes to the caller.**
   The caller should only experience a natural conversation.
2. **Never invent or guess information.** If you don't know something, say so.
3. **Keep calls efficient.** Only collect information needed for routing and dispatch.
4. **Be empathetic but professional**, especially during emergencies.
5. **Safety first**: If the caller mentions gas leaks, fire, or life-threatening
   situations, advise them to call 911 if they haven't already.
6. **Always confirm information** by reading it back to the caller.
"""
    return prompt.strip()


def _format_business_hours(hours: dict) -> str:
    """Format business hours for the prompt."""
    if not hours:
        return "Not yet confirmed"

    parts = []
    regular = hours.get('regular', {})
    if regular:
        days = regular.get('days', 'Monday-Friday')
        if isinstance(days, list):
            days = ', '.join(days)
        start = regular.get('start', '?')
        end = regular.get('end', '?')
        parts.append(f"  - {days}: {start} to {end}")

    saturday = hours.get('saturday', {})
    if saturday:
        start = saturday.get('start', '?')
        end = saturday.get('end', '?')
        note = saturday.get('note', '')
        sat_str = f"  - Saturday: {start} to {end}"
        if note:
            sat_str += f" ({note})"
        parts.append(sat_str)

    sunday = hours.get('sunday', {})
    if sunday:
        note = sunday.get('note', 'closed')
        parts.append(f"  - Sunday: {note}")
    else:
        parts.append("  - Sunday: Closed")

    tz = hours.get('timezone', '')
    if tz:
        parts.append(f"  - Timezone: {tz}")

    seasonal = hours.get('seasonal_adjustments', [])
    for adj in seasonal:
        parts.append(f"  - Seasonal: {adj}")

    return '\n'.join(parts) if parts else "Not yet confirmed"


def _format_emergency_routing(routing: dict, transfer_rules: dict, fallback_message: str) -> str:
    """Format emergency routing chain for the prompt."""
    if not routing:
        return "Emergency routing not yet configured."

    chain = routing.get('chain', [])
    if not chain:
        return "Emergency routing not yet configured."

    parts = ["Follow this escalation chain in order:"]
    for i, entry in enumerate(chain, 1):
        role = entry.get('role', 'Contact')
        phone = entry.get('phone', 'TBD')
        timeout = entry.get('timeout_seconds', 60)
        parts.append(
            f"  {i}. **{role.title()}**: Transfer to {phone}. "
            f"Wait {timeout} seconds for an answer."
        )
        if i < len(chain):
            parts.append(f"     If no answer after {timeout} seconds, proceed to next contact.")

    parts.append(f"\nIf all contacts fail: \"{fallback_message}\"")

    return '\n'.join(parts)


def _format_non_emergency_collection(memo: dict) -> str:
    """Format additional non-emergency data collection fields."""
    extra_fields = memo.get('non_emergency_collection_fields', [])
    if not extra_fields:
        return ""

    lines = []
    for field in extra_fields:
        lines.append(f"   - Also ask: {field}")
    return '\n'.join(lines)
