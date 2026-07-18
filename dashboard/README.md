# TheraCare — AI-Powered Post-Discharge Follow-Up Agent

<p align="center">
  <img src="TheraCare_PostDischarge/assets/icon.png" alt="TheraCare Logo" width="80" />
</p>

<p align="center">
  <strong>Reducing preventable hospital readmissions through intelligent patient follow-up, risk scoring, and real-time clinical alerts.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React_Native-Expo-0D9488?style=flat-square&logo=expo" />
  <img src="https://img.shields.io/badge/Backend-Node.js_+_Express-339933?style=flat-square&logo=nodedotjs" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite" />
  <img src="https://img.shields.io/badge/AI-OpenRouter_GPT--4.1--mini-FF6B35?style=flat-square" />
  <img src="https://img.shields.io/badge/FHIR-R4_Ready-E91E8C?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" />
</p>

---

## The Problem

**1 in 5 Medicare patients** is readmitted to the hospital within 30 days of discharge — costing the US healthcare system **$26 billion annually**. Over **50% of these readmissions are preventable** with proper follow-up and patient education.

Root causes:
- Patients receive 10-page clinical documents written at a graduate reading level they cannot understand
- No structured follow-up after discharge — patients are on their own
- Warning signs go unrecognized because no one is asking the right questions
- Care teams have zero visibility into what happens at home

**TheraCare fixes all three.**

---

## What TheraCare Does

| Feature | Description |
|---|---|
| 📄 **AI Discharge Parsing** | Upload any hospital discharge PDF — AI extracts diagnoses, medications, appointments, and warning signs automatically |
| ✏️ **Plain-Language Rewriter** | One tap rewrites clinical text to 6th-grade reading level — studies show this reduces readmissions by up to 50% |
| 💬 **Daily Check-In** | Personalized questions generated from the patient's discharge data, including PHQ-2/GAD-2 mental health screening |
| 📷 **Medication Photo Verification** | Patient photos their pill — AI vision model confirms they took it |
| ⚡ **Risk Scoring Engine** | 0–100 readmission risk score computed from diagnosis, medications, age, and check-in responses |
| 🏥 **Clinician Dashboard** | Real-time web dashboard showing all patients sorted by risk, with active flags and full discharge detail |
| 📞 **Voice Call Pipeline** | Twilio + Vapi.ai architecture for AI-driven phone follow-up (elderly/low-tech patients) |
| 🩺 **FHIR R4 Integration** | Epic/Cerner-ready schema — swap credentials to connect to any EHR system |
| ⌚ **Wearable Vitals** | Apple Health/Fitbit alert engine with diagnosis-specific thresholds |

---

## Screenshots

| Patient App | Clinician Dashboard |
|---|---|
| Discharge Analysis · Plain Language Toggle · Check-In Flow | Patient List · Risk Scores · Clinical Flags |

---

## Tech Stack

### Frontend — Patient Mobile App
- **React Native** with **Expo** — cross-platform iOS, Android, and web
- **TypeScript** — fully typed codebase
- **React Navigation** — bottom tab and stack navigation
- **Expo Notifications** — push notification support
- **Expo Image Picker** — medication photo capture

### Backend — API Server
- **Node.js + Express v5**
- **SQLite** via `better-sqlite3` — persistent patient data
- **Multer** — discharge document file uploads
- **OpenRouter** — GPT-4.1-mini for all AI features including vision

### Database Schema
```
patients          — demographics, diagnosis, discharge info
discharge_data    — full parsed discharge JSON per patient
follow_ups        — scheduled check-in records
responses         — patient check-in answers with clinical flags
risk_scores       — daily risk score with transparent breakdown
```

---

## Quick Start

### Prerequisites
- Node.js v18+
- npm v9+
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai))

### 1. Clone & Install
```bash
git clone https://github.com/GauravAcharya511/AI-Powered-Post-Discharge-Follow-Up-Agent.git
cd AI-Powered-Post-Discharge-Follow-Up-Agent/TheraCare_PostDischarge
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_MODEL=openai/gpt-4.1-mini
PORT=3001
```

### 3. Start the API Server
```bash
npm run api
```
```
TheraCare API running on http://localhost:3001
  DB        → theracare.db
  Dashboard → http://localhost:3001/dashboard
```

### 4. Seed Sample Patients
```bash
curl -X POST http://localhost:3001/api/seed
curl -X POST http://localhost:3001/api/seed-extra
```

Loads 3 patients with different risk profiles:
- **Amanda Lee** — Pneumonia, medium risk (score: 40–70)
- **James Thornton** — CHF, high risk (score: 90+)
- **Sofia Reyes** — Appendectomy, low risk (score: 10)

### 5. Start the Patient App
```bash
npm start
# Press 'w' for web browser at localhost:8081
# Press 'i' for iOS simulator
# Scan QR code with Expo Go on your phone
```

### 6. Open the Clinician Dashboard
```
http://localhost:3001/dashboard
```

---

## API Reference

All endpoints available at `http://localhost:3001`

### Patient & Discharge
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze-discharge` | Upload and AI-analyze a discharge PDF |
| `POST` | `/api/simplify-discharge` | Rewrite clinical text to plain English |
| `GET` | `/api/patients` | All patients with risk scores (dashboard feed) |
| `GET` | `/api/patients/:mrn` | Full patient detail, responses, flags |

### Check-In
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/checkin/:mrn/questions` | Personalized check-in questions for patient |
| `POST` | `/api/checkin/:mrn/submit` | Submit responses, recompute risk score |
| `GET` | `/api/patients/:mrn/risk` | Latest risk score with breakdown |

### Advanced Features
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/medication/verify-photo` | AI vision medication photo verification |
| `POST` | `/api/voice/initiate-call` | Voice call pipeline (Twilio + Vapi architecture) |
| `GET` | `/api/fhir/patient/:mrn` | FHIR R4 patient resource (Epic/Cerner ready) |
| `POST` | `/api/vitals/ingest` | Wearable vitals with diagnosis-specific alerts |
| `POST` | `/api/notifications/register` | Register Expo push token |

### Development
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/seed` | Load Amanda Lee mock data |
| `POST` | `/api/seed-extra` | Load James Thornton + Sofia Reyes |
| `GET` | `/api/health` | Server health check |
| `GET` | `/dashboard` | Clinician dashboard web UI |

---

## Risk Scoring Engine

Every patient gets a transparent 0–100 readmission risk score. Each point has a documented clinical reason — fully auditable by clinicians.

| Risk Factor | Points | Clinical Basis |
|---|---|---|
| High-risk diagnosis (CHF, pneumonia, sepsis) | +20 | HOSPITAL score |
| 2+ secondary diagnoses | +10 | LACE index |
| 4+ discharge medications | +10 | Polypharmacy research |
| Age ≥ 65 | +10 | Medicare readmission data |
| Missed medications reported | +20 | Adherence literature |
| Fever ≥ 103°F reported | +15 | Clinical guidelines |
| Chest pain / breathing difficulty | +20 | Emergency protocols |
| PHQ-2/GAD-2 mental health flag | +15 | Validated screeners |

**Thresholds:** 0–39 = 🟢 Low · 40–69 = 🟡 Medium · 70–100 = 🔴 High

---

## Project Structure

```
AI-Powered-Post-Discharge-Follow-Up-Agent/
│
├── TheraCare_PostDischarge/          # Main application
│   ├── server/
│   │   ├── index.js                  # Express API — all 15 endpoints
│   │   ├── database.js               # SQLite schema + DB helpers
│   │   └── dashboard.html            # Clinician dashboard (single file)
│   │
│   ├── src/
│   │   ├── screens/
│   │   │   ├── discharge/
│   │   │   │   ├── DischargeHomeScreen.tsx
│   │   │   │   ├── DischargeAnalysisScreen.tsx  # Plain-language toggle
│   │   │   │   └── DischargeRemindersScreen.tsx
│   │   │   ├── CheckInScreen.tsx               # Daily check-in flow
│   │   │   ├── MedicationPhotoScreen.tsx        # AI photo verification
│   │   │   ├── TheraCareAIScreen.tsx            # AI chat assistant
│   │   │   ├── MedicationsScreen.tsx
│   │   │   ├── SchedulesScreen.tsx
│   │   │   └── InsuranceCardsScreen.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── checkinService.ts               # Check-in + plain-language API
│   │   │   ├── notificationService.ts           # Push notifications
│   │   │   └── dischargeAnalysis.ts             # Discharge upload service
│   │   │
│   │   ├── navigation/
│   │   │   └── AppNavigator.tsx                # Tab + stack navigation
│   │   │
│   │   ├── components/
│   │   │   ├── TheraCareHeader.tsx
│   │   │   └── MedicationCard.tsx
│   │   │
│   │   ├── data/
│   │   │   └── mockData.ts                     # Mock patients + AI responses
│   │   │
│   │   ├── theme/
│   │   │   └── colors.ts
│   │   │
│   │   └── config/
│   │       └── api.ts                          # API base URL config
│   │
│   ├── assets/                                 # App icons + splash screen
│   ├── .env.example                            # Environment template
│   ├── package.json
│   └── tsconfig.json
│
├── The Machiavellians/                         # Team docs + presentations
└── synthetic_us_discharge_papers/              # Sample discharge data
```

---

## Summer Roadmap

With funding, three phases are planned:

### Phase 1 — Voice-Based Follow-Up Calls
Twilio + Vapi.ai voice agent that conducts check-ins by phone. Critical for elderly and low-tech patients. Multilingual support (EN, ES, ZH, HI). Auto-escalates to nurse line on red-flag keywords.

**Impact: 10/10 · Complexity: 7/10**

### Phase 2 — Wearable Vitals Integration
Passive monitoring via Apple Health and Fitbit APIs. Auto-flags SpO2 drops, heart rate spikes, and weight gain for CHF patients — without the patient doing anything.

**Impact: 9/10 · Complexity: 6/10**

### Phase 3 — FHIR / EHR Integration
Connect directly to Epic and Cerner via FHIR R4 SMART on FHIR OAuth2. Schema already implemented. Federally mandated interoperability means hospitals must provide access.

**Impact: 9/10 · Complexity: 9/10**

---

## Demo Commands

Test the architecture integrations in your browser console at `http://localhost:3001/dashboard`:

```javascript
// Voice call — James Thornton (CHF, high risk)
fetch('http://localhost:3001/api/voice/initiate-call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mrn: 'MRN-10039271', phoneNumber: '+13125550100', language: 'en' })
}).then(r => r.json()).then(d => console.log(JSON.stringify(d, null, 2)));

// FHIR R4 patient resource
fetch('http://localhost:3001/api/fhir/patient/MRN-10039271')
  .then(r => r.json()).then(d => console.log(JSON.stringify(d, null, 2)));

// Wearable vitals — CHF alerts
fetch('http://localhost:3001/api/vitals/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mrn: 'MRN-10039271', vitals: { heartRate: 118, spO2: 91, weight: 189, previousWeight: 185 }})
}).then(r => r.json()).then(d => console.log(JSON.stringify(d, null, 2)));
```

---

## Team

**The Machiavellians** — Health Informatics, Spring 2026

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for better patient outcomes
</p>
