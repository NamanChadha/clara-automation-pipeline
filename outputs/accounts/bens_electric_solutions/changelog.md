# Changelog: Ben's Electric Solutions
**Account ID**: `bens_electric_solutions`
**Generated**: 2026-03-04 10:50:36 UTC
**Transition**: v1 (Demo) → v2 (Onboarding)

---

## Summary
Total changes: **13** field(s) updated.

## ⏰ Business Hours

### `business_hours.regular`
**Reason**: Regular business hours confirmed/updated during onboarding

**Before (v1)**:
```json
{
  "days": "Monday-Friday",
  "start": "7:00 AM",
  "end": "5:00 PM"
}
```

**After (v2)**:
```json
{
  "days": "Monday-Friday",
  "start": "7:00 AM",
  "end": "5:30 PM"
}
```

---

### `business_hours.saturday`
**Reason**: Saturday hours confirmed/updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: {'start': '7:00 AM', 'end': '5:30 PM', 'note': 'emergency callbacks'}

---

### `business_hours.sunday`
**Reason**: Sunday hours updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: {'note': 'Closed'}

---

## 🚨 Emergency Configuration

### `emergency_definition`
**Reason**: Emergency definitions refined during onboarding

**Before (v1)**:
```json
[
  "Exposed live wiring",
  "Sparking panels",
  "Complete power loss at a commercial property",
  "Any situation where there's a fire risk from electrical issues"
]
```

**After (v2)**:
```json
[
  "Exposed live wiring",
  "Sparking panels",
  "Complete power loss at a commercial property",
  "Any situation where there's a fire risk from electrical issues",
  "Complete power loss at commercial properties",
  "I want to add one more: any electrical issue at a healthcare facility regardless of the specific problem",
  "If a hospital or medical office calls with any electrical issue",
  "Healthcare gets automatic emergency priority"
]
```

---

### `emergency_routing_rules.chain`
**Reason**: Emergency routing chain updated during onboarding

**Before (v1)**:
```json
[
  {
    "role": "Backup Technician",
    "phone": "813-555-0142",
    "timeout_seconds": 60
  },
  {
    "role": "Backup Technician",
    "phone": "813-555-0198",
    "timeout_seconds": 60
  },
  {
    "role": "Backup Technician",
    "phone": "813-555-0101",
    "timeout_seconds": 60
  }
]
```

**After (v2)**:
```json
[
  {
    "role": "Backup Technician",
    "phone": "813-555-0142",
    "timeout_seconds": 60
  },
  {
    "role": "Backup Technician",
    "phone": "813-555-0198",
    "timeout_seconds": 60
  },
  {
    "role": "Backup Technician",
    "phone": "813-555-0101",
    "timeout_seconds": 60
  },
  {
    "role": "Contact",
    "phone": "813-555-0100",
    "timeout_seconds": 30
  }
]
```

---

### `non_emergency_routing_rules.office_number`
**Reason**: office_number updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: 813-555-0100

---

### `non_emergency_routing_rules.callback_timeframe`
**Reason**: callback_timeframe updated during onboarding

- **Before (v1)**: within 30 minutes
- **After (v2)**: within 1 hour

---

### `non_emergency_collection_fields`
**Reason**: Additional data collection fields added during onboarding

**Before (v1)**:
```json
[
  "name and callback number",
  "information for?",
  "they need"
]
```

**After (v2)**:
```json
[
  "name and callback number",
  "information for?",
  "they need",
  "name"
]
```

---

## 📞 Routing & Transfer

### `call_transfer_rules.office_timeout_seconds`
**Reason**: Transfer office_timeout_seconds updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: 30

---

## 🔧 Integration & Constraints

### `services_supported`
**Reason**: Services list updated with onboarding data

**Before (v1)**:
```json
[
  "ac",
  "electrical work",
  "lighting",
  "panel upgrade",
  "rewiring",
  "wiring"
]
```

**After (v2)**:
```json
[
  "ac",
  "electrical work",
  "lighting",
  "panel upgrade",
  "rewiring",
  "wiring"
]
```

---

### `integration_constraints`
**Reason**: Integration constraints updated during onboarding

**Before (v1)**:
```json
[
  "For non-emergency stuff, Clara can create the service request in ServiceTrade. But for emergency calls, don't create anything \u2014 just route the call and let the technician handle the paperwork after. Oh and one more thing \u2014 we do NOT do generator installations. If someone calls about generators, just let them know we don't offer that service and recommend they call someone else."
]
```

**After (v2)**:
```json
[
  "For non-emergency stuff, Clara can create the service request in ServiceTrade. But for emergency calls, don't create anything \u2014 just route the call and let the technician handle the paperwork after. Oh and one more thing \u2014 we do NOT do generator installations. If someone calls about generators, just let them know we don't offer that service and recommend they call someone else.",
  "Here's the updated rule: Clara can create service requests in ServiceTrade for panel upgrades, lighting installations, and general maintenance requests. Do NOT create tickets for emergency calls \u2014 those just get routed. And do NOT create tickets for anything involving permits or inspections \u2014 those need to go through our permitting team first. Oh, and we still don't do generators \u2014 politely decline those."
]
```

---

### `excluded_services`
**Reason**: Service exclusions updated during onboarding

**Before (v1)**:
```json
[
  "generator installations",
  "that service and recommend they call someone else"
]
```

**After (v2)**:
```json
[
  "generator installations",
  "that service and recommend they call someone else",
  "generators \u2014 politely decline those"
]
```

---

## 📝 Other Changes

### `custom_greeting`
**Reason**: Custom greeting specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: Thank you for calling Ben

---
