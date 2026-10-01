# Master Plan: Bi-Tapp EMDR Generic Protocol Framework & Personal Treatment Application

This Master Plan defines the end-to-end clinical and software execution blueprint for acquiring and operating the **Bi-Tapp** bilateral tactile stimulation kit (`https://bi-tapp.com/`), comparing **Online Non-Human** vs. **Online Human** EMDR treatment pathways, and delivering a split **Generic Bilateral Protocol Framework (`framework/bls_protocol_engine/`)** and **Specific Personal EMDR Companion Application (`apps/bitapp_personal_emdr/`)** merged into the `main` branch on GitHub (`https://github.com/itayshemesh/bitapp-emdr-platform`).

---

## 1. Executive Summary & Core Objectives

1. **Clinical & Operational EMDR Treatment Roadmap**:
   Establish an evidence-based protocol using the **Bi-Tapp** Bluetooth tactile bilateral stimulation (BLS) kit (`https://bi-tapp.com/`) to address:
   - **Target Cluster 1 (Completed Past Event — 2.5 Years Ago)**: Persistent intrusive rumination ("looping thoughts" / relational attachment mini-trauma) following a breakup with a former partner 2.5 years ago.
   - **Target Cluster 2 (Ongoing Relational Stressor)**: Secondary attachment grief, role-loss, and emotional load from not living in the same household with 3 children.
2. **Online Non-Human vs. Online Human Option Synthesis**:
   Compare self-administered/AI-guided digital EMDR platforms against certified human telehealth EMDR clinicians (integrated with Bi-Tapp via `remotEMDR` 5-character provider control codes), detailing exact expectations, step-by-step protocols, hardware/session costs, and weekly frequency schedules.
3. **Two-Layer Software Architecture (Generic Framework + Specific Usage)**:
   - **Layer 1 — Generic Framework (`framework/bls_protocol_engine/`)**: A reusable, domain-agnostic state-machine engine for multi-modal bilateral stimulation protocols, Subjective Units of Disturbance ($\text{SUD} \in [0, 10]$) and Validity of Cognition ($\text{VOC} \in [1, 7]$) tracking, Window-of-Tolerance safety circuit breakers, and optional Google Workspace session journaling via OAuth 2.0 PKCE.
   - **Layer 2 — Specific Usage Application (`apps/bitapp_personal_emdr/`)**: A concrete instantiation configured specifically for the Bi-Tapp hardware profile, featuring a **Breakup Rumination Interrupter & R-TEP Protocol Pack**, a **Parental Separation Resourcing Pack (3 Children RDI)**, and a **Telehealth Clinician Handoff Exporter**.
4. **GitHub Main-Branch Delivery & Version-Controlled Master Plan**:
   Both the codebase and this Master Plan (`docs/MASTER_PLAN.md`) are version-controlled, audited for zero secret exposure, and merged into the `main` branch.

---

## 2. Clinical Landscape: Why a 2.5-Year Breakup Still Loops & How to Treat It

### 2.1 The Adaptive Information Processing (AIP) Explanation
Under Francine Shapiro's **Adaptive Information Processing (AIP)** model, painful relational rejections and sudden breakups function as "small-t" or attachment traumas when intense autonomic arousal prevents the hippocampus and prefrontal cortex from consolidating the experience into narrative long-term memory.
- **State-Specific Storage**: The breakup remains stored in raw limbic networks with its original emotional charge, visceral chest/gut sensations, and negative self-cognitions (e.g., *"I am replaceable"*, *"I lost my chance"*).
- **Why Rumination Loops Happen**: When a present cue (a quiet evening, returning home after seeing your children) activates that neural network, your conscious mind tries to "solve" or replay the 2.5-year-old breakup logically. Because verbal reasoning cannot rewrite a subcortical limbic memory trace, the thought loops endlessly.
- **How Bilateral Tactile Stimulation (Bi-Tapp) Breaks the Loop**: Alternating left-right tactile stimulation simultaneously (1) taxes working memory (degrading the vividness of the intrusive image), (2) triggers an orienting response that shifts autonomic balance from sympathetic arousal to parasympathetic vagal regulation, and (3) facilitates thalamocortical memory reconsolidation (analogous to REM sleep).

### 2.2 Separating the Two Clinical Clusters

| Clinical Cluster | Nature of Stressor | Primary EMDR Protocol | Recommended Delivery Mode |
| :--- | :--- | :--- | :--- |
| **Cluster 1: Ex-Girlfriend Breakup (2.5 Years Ago)** | Completed historical event ("mini-trauma") generating present looping thoughts | **Recent Traumatic Episode Protocol (R-TEP)** & **Standard 3-Pronged EMDR** (Past scenes $\rightarrow$ Present triggers $\rightarrow$ Future template) | **Hybrid**: Daily Bi-Tapp Mode A Loop Interrupter + Weekly Reprocessing (Self-guided for $\text{SUD} \le 6$; Human Telehealth for $\text{SUD} \ge 7$ touchstone scenes) |
| **Cluster 2: Not Living With Your 3 Children** | Ongoing present-day attachment separation & role transition | **Phase 2 Resource Development & Installation (RDI)** (Fatherhood Connection Anchor, Container) + Attachment-Focused EMDR | **Phase 2 RDI Daily (Non-Human)** + **Human Telehealth Clinician** for processing grief/guilt without emotional flooding |

---

## 3. Bi-Tapp Hardware Guide (`https://bi-tapp.com/`)

### 3.1 Device Specifications
* **Form Factor**: Two compact (`2.5" x 0.5"`), rechargeable Bluetooth Low Energy (BLE) tappers that pulse alternately left and right.
* **Hands-Free Versatility**: Hold in palms, wear inside **Bi-Tapp Wristbands**, or slip into pockets or socks while working, resting, or in therapy.
* **Mobile App Controls (iOS & Android)**:
  - **Rate of Speed (`1–10`)**: Controls oscillation frequency (slow calming cadence vs. fast reprocessing cadence).
  - **Rate of Intensity (`1–10`)**: Controls haptic vibration strength.
* **Remote Therapist Bridge (`remotEMDR`)**:
  In Bi-Tapp App $\rightarrow$ Settings $\rightarrow$ enable **"Allow Provider Control"** and **"Show Provider Setup Code"**. Share the **5-character setup code** with your online therapist using `remotEMDR.com`, enabling the clinician to control your tappers' speed, intensity, and pauses remotely in real time.

### 3.2 Hardware Pricing Breakdown

| Component | Price (USD) | Notes |
| :--- | :--- | :--- |
| **Bi-Tapp Base Kit** | **$277.00** | 2 Bluetooth tappers, dual 2-in-1 USB charging cable, protective carrying pouch, free iOS/Android app. |
| **Wristbands (Pair)** | **$20.00** | Recommended for hands-free rumination interruption during work or sleep preparation. |
| **Wall Charger / Extra Cable** | **$15.00** | Optional USB power adapter (`$297–$312` bundled kit range). |
| **Shipping** | **$10–$15** (US) / **$40–$60** (Intl) | Flat-rate international shipping outside the US. |

---

## 4. Online Non-Human vs. Online Human EMDR Options (Using Bi-Tapp)

| Dimension | Option 1: Online Non-Human (Self-Guided / AI / Custom Framework + Bi-Tapp) | Option 2: Online Human Telehealth Therapist + Bi-Tapp (via `remotEMDR`) | Option 3: Hybrid Stepped-Care Protocol [Recommended] |
| :--- | :--- | :--- | :--- |
| **Platforms & Tools** | • **Bi-Tapp App + This Repository (`bitapp-emdr-platform`)** ($0/mo)<br>• **VirtualEMDR** ($69–$79/mo)<br>• **Easy EMDR / Bilateralstimulation.io** ($0–$20/mo) | • **EMDRIA Directory** (`emdria.org`) Telehealth Clinicians<br>• **Employee EAP / Lyra Health** ($0 copay for eligible sessions)<br>• **Headway / Alma** In-Network ($20–$60 copay)<br>• **Private Attachment-EMDR / Intensives** ($150–$300/hr) | • **Daily Non-Human**: Bi-Tapp + `bitapp-emdr-platform` for daily resourcing, loop interruption, & $\text{SUD} \le 6$ targets<br>• **Weekly Human**: Telehealth EMDR clinician via `remotEMDR` for $\text{SUD} \ge 7$ attachment & children-separation grief |
| **Bi-Tapp Integration** | User sets Bi-Tapp app speed/intensity as prompted by `BiTappCompanionAdapter` (`Speed 2` for resourcing; `Speed 7` for 35s reprocessing sets). | Client shares 5-character Bi-Tapp Provider Setup Code with therapist on `remotEMDR.com`; therapist controls tappers live over video. | Local app control for daily self-regulation; 5-character `remotEMDR` code during weekly human telehealth sessions. |
| **Clinical Safety** | **Moderate-Low** if used unsupervised on high-SUD trauma; mitigated in our software by `SafetyCircuitBreaker`. | **High**: Clinician monitors affect, dissociation, and looping thoughts, providing live Cognitive Interweaves. | **Optimal**: Hard software safety gates ($\text{SUD} \ge 7 \implies \text{Container}$) + human co-regulation for deep layers. |
| **Monthly Cost** | **$0/mo** (Open-Source Framework) or **$69–$79/mo** (Commercial Web). | **$0/mo** (EAP/Lyra), **$80–$240/mo** (in-network weekly), or **$600–$1,200/mo** (private pay). | **$0–$240/mo** after one-time ~$309 hardware purchase. |

---

## 5. What to Expect, How to Do It, & Weekly Frequency Schedule

### 5.1 Step-by-Step Protocol & Exact Bi-Tapp Settings

| Mode | Clinical Purpose | Bi-Tapp Speed | Bi-Tapp Intensity | Set Duration | How to Execute |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode A: Acute Loop Interrupter** | Stop active looping thoughts about ex-girlfriend on demand | **Slow (`2/10`)** | **Gentle (`3/10`)** | **5–10 mins continuous** | 1. Turn on Bi-Tapp at Speed 2, Intensity 3.<br>2. Acknowledge: *"This is a 2.5-year-old memory trace firing, not a present emergency."*<br>3. Breathe 4s in / 6s out while feeling the left-right pulses until $\text{SUD} \le 2$. |
| **Mode B: Phase 2 RDI Resourcing** | Install Safe Place, Container, & Fatherhood Connection Anchor (3 kids) | **Slow (`3/10`)** | **Gentle (`3/10`)** | **4–6 sets of 15–20 sec** | 1. Bring up a vivid, warm memory of laughing/connecting with your 3 kids.<br>2. Locate the warmth in your body.<br>3. Run 20s slow tapping sets ONLY while the feeling remains positive. |
| **Mode C: Phase 4 Desensitization** | Reprocess discrete breakup scenes ($\text{SUD} \le 6$ self; $\text{SUD} \ge 7$ clinician) | **Fast (`7/10`)** | **Distinct (`6/10`)** | **Sets of 35 sec** (15–25 sets) | 1. **Phase 3**: Rate Worst Image, Negative Cognition (NC), Positive Cognition (PC, $\text{VOC } 1\text{–}7$), Emotion, $\text{SUD } (0\text{–}10)$, Body location.<br>2. **Phase 4**: Hold Image + NC + Body sensation; run Bi-Tapp at Speed 7 for 35s.<br>3. **Pause**: Stop tappers, take a breath, note *"What do you notice now?"* Repeat until $\text{SUD} \le 1$. |
| **Mode D: Phase 5–7 Installation & Closure** | Install Positive Cognition ($\text{VOC}=7$), clear body scan, and close safely | **Moderate (`4/10`)** then **Slow (`2/10`)** | **Gentle (`3–4/10`)** | **25s sets** (Phase 5) / **60s** (Phase 7) | 1. **Phase 5**: Pair memory with PC at Speed 4 until $\text{VOC} = 7$.<br>2. **Phase 6**: Scan body head-to-toe; tap out any residual tension.<br>3. **Phase 7 Closure**: Always end with 60s at Speed 2 (Container / Safe Place). |

### 5.2 What to Expect & Weekly Frequency Schedule
* **Daily Resourcing & Loop Interruption**: **10–15 minutes/day** (morning/bedtime at Speed 2–3) plus **on-demand (5–10 mins)** whenever an intrusive breakup loop starts.
* **Structured Reprocessing Frequency**: **Strictly 1x per week (60–90 minutes)**. Never exceed 2 reprocessing sessions per week—your brain requires **48–72 hours of post-session REM sleep and synaptic reconsolidation** (during which vivid dreams, brief emotional waves, or sudden insights are normal).
* **Expected Timeline**:
  - **Weeks 1–2**: Bi-Tapp arrival, Phase 2 Safe Place/Container/Fatherhood RDI installation, target mapping.
  - **Weeks 3–10 (6–8 Weekly Sessions)**: Reprocessing the 2.5-year ex-partner breakup target cluster ($\text{SUD } 7\text{–}8 \rightarrow 0\text{–}1$).
  - **Weeks 6–16+**: Ongoing human telehealth integration for attachment resilience and navigating life apart from your 3 children.

---

## 6. Software Architecture & Execution Tasks

```
bitapp-emdr-platform/
├── README.md
├── pyproject.toml
├── .gitignore
├── docs/
│   ├── MASTER_PLAN.md
│   └── ARCHITECTURE_RFC.md
├── framework/
│   └── bls_protocol_engine/
│       ├── __init__.py
│       ├── schemas.py
│       ├── safety.py
│       ├── engine.py
│       ├── adapters.py
│       └── workspace_sync.py
├── apps/
│   └── bitapp_personal_emdr/
│       ├── __init__.py
│       ├── bitapp_presets.py
│       ├── clinical_packs.py
│       ├── options_analyzer.py
│       └── cli.py
└── tests/
    ├── test_framework_engine.py
    └── test_bitapp_personal_app.py
```

| Task ID | Layer | Deliverable Summary | Verification Command |
| :--- | :--- | :--- | :--- |
| `TASK-101` | Documentation | Version-controlled `docs/MASTER_PLAN.md` and `docs/ARCHITECTURE_RFC.md`. | `python3 -m unittest discover -s tests` |
| `TASK-102` | Security & Setup | `pyproject.toml`, `README.md`, `.gitignore`, isolated `~/.config/bitapp-emdr/oauth_client.json`. | `git status` |
| `TASK-103` | Generic Framework | `schemas.py` and `safety.py` (`SafetyCircuitBreaker` with 3-set stagnation & $\text{SUD} \ge 8$ gates). | `python3 tests/test_framework_engine.py` |
| `TASK-104` | Generic Framework | `engine.py` (`ProtocolEngine`), `adapters.py`, and `workspace_sync.py`. | `python3 tests/test_framework_engine.py` |
| `TASK-105` | Specific App | `bitapp_presets.py`, `clinical_packs.py`, `options_analyzer.py`, and `cli.py`. | `python3 tests/test_bitapp_personal_app.py` |
| `TASK-106` | Verification | Full unit & integration test suite across generic and specific layers. | `python3 -m unittest discover -s tests -p "test_*.py" -v` |
| `TASK-107` | Security Gate | Pre-push secret & confidentiality scan (`0` leaked credentials or internal links). | Pre-push audit exit code 0 |
| `TASK-108` | GitHub Rollout | Push feature branch and merge into `main` on `https://github.com/itayshemesh/bitapp-emdr-platform`. | `git log -n 3 main` |
