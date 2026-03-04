# Changelog: Prestige Fire Protection
**Account ID**: `prestige_fire_protection`
**Generated**: 2026-03-04 10:50:36 UTC
**Transition**: v1 (Demo) → v2 (Onboarding)

---

## Summary
Total changes: **10** field(s) updated.

## ⏰ Business Hours

### `business_hours.regular`
**Reason**: Regular business hours confirmed/updated during onboarding

**Before (v1)**:
```json
{
  "days": "Monday-Friday",
  "start": "8:00 AM",
  "end": "5:00 PM"
}
```

**After (v2)**:
```json
{
  "days": "Monday-Friday",
  "start": "8:00 AM",
  "end": "6:00 PM"
}
```

---

### `business_hours.saturday`
**Reason**: Saturday hours confirmed/updated during onboarding

**Before (v1)**:
```json
{
  "start": "8:00 AM",
  "end": "5:00 PM",
  "note": "inspections only"
}
```

**After (v2)**:
```json
{
  "start": "8:00 AM",
  "end": "6:00 PM",
  "note": ""
}
```

---

### `business_hours.seasonal_adjustments`
**Reason**: Seasonal hour adjustments specified during onboarding

**Before (v1)**:
```json
[]
```

**After (v2)**:
```json
[
  "Almost. Saturdays we're actually extending to 2 PM now because we're booking more weekend inspections. And I want to add that from November through March, we extend weekday hours to 6 PM because of freeze season \u2014 that's when we get the most emergency sprinkler calls from frozen pipes.",
  "Almost. Saturdays we're actually extending to 2 PM now because we're booking more weekend inspections. And I want to add that from November through March, we extend weekday hours to 6 PM because of freeze season \u2014 that's when we get the most emergency sprinkler calls from frozen pipes.",
  "Smart \u2014 seasonal hours. So November through March weekdays are 8 AM to 6 PM, April through October weekdays 8 to 5, Saturdays always 8 to 2. Correct?",
  "Smart \u2014 seasonal hours. So November through March weekdays are 8 AM to 6 PM, April through October weekdays 8 to 5, Saturdays always 8 to 2. Correct?"
]
```

---

## 🚨 Emergency Configuration

### `emergency_definition`
**Reason**: Emergency definitions refined during onboarding

**Before (v1)**:
```json
[
  "If a sprinkler head is leaking or a fire alarm panel goes into fault",
  "Active sprinkler discharge",
  "Fire alarm system in active alarm or fault condition",
  "Any fire suppression system that's been compromised \u2014 like if a valve was shut accidentally and there's no fire protection for a building",
  "Also if a sprinkler pipe bursts from freezing"
]
```

**After (v2)**:
```json
[
  "If a sprinkler head is leaking or a fire alarm panel goes into fault",
  "Active sprinkler discharge",
  "Fire alarm system in active alarm or fault condition",
  "Any fire suppression system that's been compromised \u2014 like if a valve was shut accidentally and there's no fire protection for a building",
  "Also if a sprinkler pipe bursts from freezing",
  "Fire alarm in fault or alarm",
  "Compromised suppression systems",
  "And burst pipes from freezing",
  "If a client says they have a fire department inspection within 24 hours and their system is down",
  "Any active kitchen hood suppression issue is always emergency because that's a real fire hazard."
]
```

---

### `emergency_routing_rules.chain`
**Reason**: Emergency routing chain updated during onboarding

**Before (v1)**:
```json
[
  {
    "role": "Supervisor",
    "phone": "704-555-0300",
    "timeout_seconds": 45
  },
  {
    "role": "Supervisor",
    "phone": "704-555-0315",
    "timeout_seconds": 45
  },
  {
    "role": "Supervisor",
    "phone": "704-555-0320",
    "timeout_seconds": 45
  }
]
```

**After (v2)**:
```json
[
  {
    "role": "Supervisor",
    "phone": "704-555-0300",
    "timeout_seconds": 60
  },
  {
    "role": "Supervisor",
    "phone": "704-555-0315",
    "timeout_seconds": 60
  },
  {
    "role": "Supervisor",
    "phone": "704-555-0320",
    "timeout_seconds": 60
  }
]
```

---

### `non_emergency_routing_rules.callback_timeframe`
**Reason**: callback_timeframe updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: next business day

---

### `non_emergency_collection_fields`
**Reason**: Additional data collection fields added during onboarding

**Before (v1)**:
```json
[
  "info"
]
```

**After (v2)**:
```json
[
  "info",
  "type of inspection \u2014 annual",
  "name",
  "if they want to leave an email for us to send a confirmation"
]
```

---

## 🔧 Integration & Constraints

### `services_supported`
**Reason**: Services list updated with onboarding data

**Before (v1)**:
```json
[
  "ac",
  "alarm system",
  "fire alarm",
  "fire protection",
  "fire suppression",
  "monitoring",
  "pipe",
  "sprinkler"
]
```

**After (v2)**:
```json
[
  "ac",
  "alarm system",
  "backflow",
  "fire alarm",
  "fire protection",
  "fire suppression",
  "monitoring",
  "pipe",
  "plumbing",
  "sprinkler"
]
```

---

### `excluded_services`
**Reason**: Service exclusions updated during onboarding

**Before (v1)**:
```json
[]
```

**After (v2)**:
```json
[
  "that"
]
```

---

## 📝 Other Changes

### `custom_greeting`
**Reason**: Custom greeting specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: Thank you for calling Prestige Fire Protection. This is Clara, how may I assist you today?

---
