# Changelog: AllStar Plumbing & Mechanical
**Account ID**: `allstar_plumbing_mechanical`
**Generated**: 2026-03-04 10:50:36 UTC
**Transition**: v1 (Demo) → v2 (Onboarding)

---

## Summary
Total changes: **11** field(s) updated.

## ⏰ Business Hours

### `business_hours.sunday`
**Reason**: Sunday hours updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: {'note': 'Emergency routing only'}

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
  "Yes, but we're extending Saturday hours to 2 PM starting January. Also, we've added Sunday emergency-only availability. We won't take regular calls on Sunday, but if it's an emergency, route it. Otherwise Sunday callers should hear that we're closed and will call back Monday."
]
```

---

## 🚨 Emergency Configuration

### `emergency_definition`
**Reason**: Emergency definitions refined during onboarding

**Before (v1)**:
```json
[
  "But plumbing emergencies don't wait \u2014 a burst pipe in a restaurant kitchen at midnight means they're losing thousands of dollars an hour.",
  "Active water leak or burst pipe",
  "Sewer backup or overflow",
  "Gas line damage or gas smell",
  "No hot water in a hotel or healthcare facility"
]
```

**After (v2)**:
```json
[
  "But plumbing emergencies don't wait \u2014 a burst pipe in a restaurant kitchen at midnight means they're losing thousands of dollars an hour.",
  "Active water leak or burst pipe",
  "Sewer backup or overflow",
  "Gas line damage or gas smell",
  "No hot water in a hotel or healthcare facility",
  "Emergency definitions \u2014 active water leak",
  "No hot water at hotels or healthcare",
  "Any plumbing issue at a restaurant during their operating hours is emergency priority \u2014 they have to shut down their kitchen if water isn't working",
  "Flooding from any source in a commercial building is emergency",
  "Oh and I want to be more specific about gas: any gas smell near a water heater or boiler should be treated as immediate emergency with a safety warning to leave the building.",
  "Water heater quotes",
  "And whether it's a restaurant or other facility type."
]
```

---

### `emergency_routing_rules.chain`
**Reason**: Emergency routing chain updated during onboarding

**Before (v1)**:
```json
[
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0500",
    "timeout_seconds": 45
  },
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0515",
    "timeout_seconds": 45
  },
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0525",
    "timeout_seconds": 45
  }
]
```

**After (v2)**:
```json
[
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0500",
    "timeout_seconds": 60
  },
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0515",
    "timeout_seconds": 60
  },
  {
    "role": "Plumbing Supervisor",
    "phone": "602-555-0525",
    "timeout_seconds": 60
  },
  {
    "role": "Contact",
    "phone": "602-555-0490",
    "timeout_seconds": 60
  }
]
```

---

### `emergency_routing_rules.fallback_message`
**Reason**: Fallback message specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: I

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
  "those questions for non-emergency grease trap scheduling",
  "size of the trap and when it was last serviced"
]
```

**After (v2)**:
```json
[
  "those questions for non-emergency grease trap scheduling",
  "size of the trap and when it was last serviced",
  "account number if they have it",
  "trap size in gallons"
]
```

---

## 📞 Routing & Transfer

### `call_transfer_rules.fallback_message`
**Reason**: Transfer fallback_message updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: I

---

## 🔧 Integration & Constraints

### `services_supported`
**Reason**: Services list updated with onboarding data

**Before (v1)**:
```json
[
  "ac",
  "backflow",
  "grease trap",
  "pipe",
  "plumbing",
  "sewer",
  "water heater",
  "water line"
]
```

**After (v2)**:
```json
[
  "ac",
  "backflow",
  "drain",
  "grease trap",
  "pipe",
  "plumbing",
  "sewer",
  "sprinkler",
  "water heater",
  "water line"
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
  "residential swimming pool plumbing",
  "irrigation or sprinkler systems \u2014 the lawn kind"
]
```

---

## 📝 Other Changes

### `custom_greeting`
**Reason**: Custom greeting specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: Thank you for calling AllStar Plumbing and Mechanical. This is Clara, how can I help you today?

---
