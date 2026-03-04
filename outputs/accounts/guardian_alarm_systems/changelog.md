# Changelog: Guardian Alarm Systems
**Account ID**: `guardian_alarm_systems`
**Generated**: 2026-03-04 10:50:36 UTC
**Transition**: v1 (Demo) → v2 (Onboarding)

---

## Summary
Total changes: **12** field(s) updated.

## ⏰ Business Hours

### `business_hours.holidays`
**Reason**: Holiday schedule specified during onboarding

**Before (v1)**:
```json
[
  "Monday through Friday, 8:30 AM to 5:30 PM Eastern. Closed weekends and federal holidays."
]
```

**After (v2)**:
```json
[
  "Business hours \u2014 Monday through Friday 8:30 AM to 5:30 PM Eastern, closed weekends and federal holidays. Correct?",
  "That's right. But I want to add \u2014 we observe these specific holidays: New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving, day after Thanksgiving, Christmas Eve, and Christmas Day. On those days treat everything as after-hours protocol.",
  "Got it, eight named holidays. Emergency definitions on the service side \u2014 access control completely down, alarm panel offline or comm failure, suspected tampering. Changes?"
]
```

---

## 🚨 Emergency Configuration

### `emergency_definition`
**Reason**: Emergency definitions refined during onboarding

**Before (v1)**:
```json
[
  "So there's a gap between true alarm emergencies that your monitoring station handles",
  "An emergency for us on the service side would be: access control system completely down",
  "Alarm panel offline or in communication failure",
  "A client reporting they think their system was tampered with"
]
```

**After (v2)**:
```json
[
  "So there's a gap between true alarm emergencies that your monitoring station handles",
  "An emergency for us on the service side would be: access control system completely down",
  "Alarm panel offline or in communication failure",
  "A client reporting they think their system was tampered with",
  "Emergency definitions on the service side \u2014 access control completely down",
  "Alarm panel offline or comm failure",
  "Suspected tampering",
  "Add one: CCTV system failure at a high-security client site",
  "If any of them call about CCTV being down",
  "Also I want to refine \"access control down\" \u2014 it's only emergency if it affects building entry"
]
```

---

### `emergency_routing_rules.chain`
**Reason**: Emergency routing chain updated during onboarding

**Before (v1)**:
```json
[
  {
    "role": "Field Supervisor",
    "phone": "404-555-0450",
    "timeout_seconds": 60
  },
  {
    "role": "Field Supervisor",
    "phone": "404-555-0460",
    "timeout_seconds": 60
  },
  {
    "role": "Field Supervisor",
    "phone": "404-555-0475",
    "timeout_seconds": 60
  }
]
```

**After (v2)**:
```json
[
  {
    "role": "Field Supervisor",
    "phone": "404-555-0450",
    "timeout_seconds": 60
  },
  {
    "role": "Field Supervisor",
    "phone": "404-555-0460",
    "timeout_seconds": 60
  },
  {
    "role": "Field Supervisor",
    "phone": "404-555-0475",
    "timeout_seconds": 60
  },
  {
    "role": "Contact",
    "phone": "404-555-0440",
    "timeout_seconds": 30
  }
]
```

---

### `emergency_routing_rules.fallback_message`
**Reason**: Fallback message specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: I

---

### `non_emergency_routing_rules.office_number`
**Reason**: office_number updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: 404-555-0440

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
  "company name and check against a client list"
]
```

**After (v2)**:
```json
[
  "company name and check against a client list",
  "type of business"
]
```

---

## 📞 Routing & Transfer

### `call_transfer_rules.office_timeout_seconds`
**Reason**: Transfer office_timeout_seconds updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: 30

---

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
  "access control",
  "alarm system",
  "cctv",
  "monitoring",
  "security"
]
```

**After (v2)**:
```json
[
  "ac",
  "access control",
  "alarm system",
  "cctv",
  "monitoring",
  "security"
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
  "residential security"
]
```

---

## 📝 Other Changes

### `custom_greeting`
**Reason**: Custom greeting specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: Thank you for calling Guardian Alarm Systems. This is Clara, your virtual assistant. How can I help you?

---
