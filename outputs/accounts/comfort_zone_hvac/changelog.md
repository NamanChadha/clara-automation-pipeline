# Changelog: Comfort Zone HVAC
**Account ID**: `comfort_zone_hvac`
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
  "start": "8:00 AM",
  "end": "6:00 PM"
}
```

**After (v2)**:
```json
{
  "days": "Monday-Friday",
  "start": "9:00 AM",
  "end": "1:00 PM"
}
```

---

### `business_hours.saturday`
**Reason**: Saturday hours confirmed/updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: {'start': '9:00 AM', 'end': '1:00 PM', 'note': 'maintenance contracts only'}

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
  "Mostly. I want to add that during peak summer months, June through August, we extend to 7 PM on weekdays because that's our busiest season for AC work. Also we now have a Saturday morning crew, 9 AM to 1 PM Mountain, for maintenance contract appointments only.",
  "Mostly. I want to add that during peak summer months, June through August, we extend to 7 PM on weekdays because that's our busiest season for AC work. Also we now have a Saturday morning crew, 9 AM to 1 PM Mountain, for maintenance contract appointments only."
]
```

---

## 🚨 Emergency Configuration

### `emergency_definition`
**Reason**: Emergency definitions refined during onboarding

**Before (v1)**:
```json
[
  "Our emergency definition is: complete heating failure when outside temp is below 32\u00b0F",
  "Gas leak or gas smell from HVAC equipment",
  "Carbon monoxide detector triggered related to furnace",
  "AC failure in a commercial building with servers or medical equipment"
]
```

**After (v2)**:
```json
[
  "Our emergency definition is: complete heating failure when outside temp is below 32\u00b0F",
  "Gas leak or gas smell from HVAC equipment",
  "Carbon monoxide detector triggered related to furnace",
  "AC failure in a commercial building with servers or medical equipment",
  "Emergency definitions \u2014 you had heating failure below 32\u00b0F",
  "Gas leak or smell from HVAC",
  "And AC failure in commercial buildings with servers or medical equipment",
  "Add one more: any HVAC failure in a building with elderly care or daycare facilities"
]
```

---

### `emergency_routing_rules.chain`
**Reason**: Emergency routing chain updated during onboarding

**Before (v1)**:
```json
[
  {
    "role": "On-call Technician",
    "phone": "303-555-0200",
    "timeout_seconds": 30
  },
  {
    "role": "On-call Technician",
    "phone": "303-555-0210",
    "timeout_seconds": 30
  }
]
```

**After (v2)**:
```json
[
  {
    "role": "On-call Technician",
    "phone": "303-555-0200",
    "timeout_seconds": 60
  },
  {
    "role": "On-call Technician",
    "phone": "303-555-0210",
    "timeout_seconds": 60
  },
  {
    "role": "Business Partner",
    "phone": "303-555-0225",
    "timeout_seconds": 40
  },
  {
    "role": "Contact",
    "phone": "303-555-0190",
    "timeout_seconds": 25
  }
]
```

---

### `emergency_routing_rules.fallback_message`
**Reason**: Fallback message specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: I

---

### `non_emergency_collection_fields`
**Reason**: Additional data collection fields added during onboarding

**Before (v1)**:
```json
[
  "info and the details about what they need"
]
```

**After (v2)**:
```json
[
  "info and the details about what they need",
  "info and we'll enter it manually"
]
```

---

## 📞 Routing & Transfer

### `call_transfer_rules.office_timeout_seconds`
**Reason**: Transfer office_timeout_seconds updated during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: 25

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
  "duct",
  "duct cleaning",
  "furnace",
  "heating",
  "hvac",
  "indoor air quality"
]
```

**After (v2)**:
```json
[
  "ac",
  "air conditioning",
  "duct",
  "duct cleaning",
  "furnace",
  "heating",
  "hvac",
  "indoor air quality",
  "ventilation"
]
```

---

### `integration_constraints`
**Reason**: Integration constraints updated during onboarding

**Before (v1)**:
```json
[]
```

**After (v2)**:
```json
[
  "We don't use ServiceTrade. We use Housecall Pro. For now, Clara shouldn't try to create any jobs in the system. Just collect info and we'll enter it manually. Maybe in phase two we'll integrate."
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
  "commercial refrigeration"
]
```

---

## 📝 Other Changes

### `custom_greeting`
**Reason**: Custom greeting specified during onboarding

- **Before (v1)**: (not set)
- **After (v2)**: Thanks for calling Comfort Zone HVAC, where your comfort is our priority. This is Clara, how can I help?

---
