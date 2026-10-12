# FedHealth Architecture & System Design Documentation

This document provides a technical overview of the **FedHealth: Privacy-Preserving Federated Learning Platform for Multi-Hospital Disease Prediction**.

## 1. System Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT PRESENTATION TIER                        │
│                                                                        │
│   ┌───────────────────┐    ┌──────────────────┐    ┌───────────────┐   │
│   │   Admin Portal    │    │ Clinical Portal  │    │  Researcher   │   │
│   │ (Silo Governance) │    │  (Risk Inference)│    │  (Analytics)  │   │
│   └─────────┬─────────┘    └────────┬─────────┘    └───────┬───────┘   │
└─────────────┼───────────────────────┼──────────────────────┼───────────┘
              │                       │                      │
              └───────────────────────┼──────────────────────┘
                                      │ HTTPS / REST (JWT)
┌─────────────────────────────────────▼──────────────────────────────────┐
│                         APPLICATION API GATEWAY                        │
│                         FastAPI Service (Python)                       │
│                                                                        │
│   ┌────────────────────┐  ┌───────────────────┐  ┌─────────────────┐   │
│   │ Authentication     │  │ Hospital Silo     │  │ Anonymized EHR  │   │
│   │ & RBAC Middleware  │  │ Node Registry     │  │ Record Manager  │   │
│   └────────────────────┘  └───────────────────┘  └─────────────────┘   │
│   ┌────────────────────┐  ┌───────────────────┐  ┌─────────────────┐   │
│   │ Federated Round    │  │ Analytics Engine  │  │ Immutable Audit │   │
│   │ Task Coordinator   │  │ & Aggregations    │  │ Security Ledger │   │
│   └────────────────────┘  └───────────────────┘  └─────────────────┘   │
└─────────────────────────────────────▲──────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼──────────────────────────────────┐
│                   FEDERATED MACHINE LEARNING ENGINE                    │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │               Federated Server (FedAvg Coordinator)            │   │
│   │   • Sample-weighted parameter aggregation                      │   │
│   │   • Communication round synchronization                        │   │
│   │   • Global neural network checkpointing                        │   │
│   └────────────────────────────────┬───────────────────────────────┘   │
│                                    │                                   │
│   ┌────────────────────────────────▼───────────────────────────────┐   │
│   │                 Differential Privacy Engine                    │   │
│   │   • Global L2 gradient clipping: ||g||_2 <= C                  │   │
│   │   • Calibrated Gaussian mechanism: N(0, sigma^2 * C^2 * I)     │   │
│   │   • Rényi Moments Accountant: Cumulative (epsilon, delta)      │   │
│   └────────────────────────────────┬───────────────────────────────┘   │
│                                    │                                   │
│   ┌────────────────────────────────▼───────────────────────────────┐   │
│   │                  Clinical Prediction Models                    │   │
│   │   • DiseasePredictor (Deep MLP: 9 -> 64 -> 32 -> 3)            │   │
│   │   • Multi-label Sigmoid output: Diabetes, CVD, CKD             │   │
│   │   • Gradient-based Sensitivity Feature Attribution             │   │
│   └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────▲──────────────────────────────────┘
                                      │
┌─────────────────────────────────────▼──────────────────────────────────┐
│                         PERSISTENCE LAYER (SQL)                        │
│                                                                        │
│     [Users]  ───  [Hospitals]  ───  [PatientRecords (De-identified)]    │
│     [FederatedRounds]  ───  [LocalModelUpdates]  ───  [AuditLogs]      │
└────────────────────────────────────────────────────────────────────────┘
```

## 2. Federated Training Lifecycle Sequence

```
Hospital Node A              FedHealth Server              Hospital Node B
      │                              │                            │
      │   1. Fetch Global Model (θ)  │                            │
      │◄─────────────────────────────┤                            │
      │                              ├───────────────────────────►│
      │                              │   1. Fetch Global Model    │
      │                              │                            │
      │ 2. Local Training (E epochs) │                            │
      │    L_A(θ; D_A)               │ 2. Local Training          │
      │                              │    L_B(θ; D_B)             │
      │ 3. Compute Δθ_A              │                            │
      │    Apply L2 clip (C)         │ 3. Compute Δθ_B            │
      │                              │    Apply L2 clip (C)       │
      │ 4. Send Clipped Update       │                            │
      ├─────────────────────────────►│                            │
      │                              │ 4. Send Clipped Update     │
      │                              │◄───────────────────────────┤
      │                              │                            │
      │                              │ 5. Federated Averaging:    │
      │                              │    θ_new = Σ (n_k/N) Δθ_k  │
      │                              │                            │
      │                              │ 6. Inject DP Noise:        │
      │                              │    θ_new += N(0, σ² C² I)  │
      │                              │                            │
      │                              │ 7. Advance Accountant:     │
      │                              │    ε_spent += RDP_step()   │
      │                              │                            │
      │ 8. Broadcast Updated θ_new   │                            │
      │◄─────────────────────────────┤                            │
      │                              ├───────────────────────────►│
```

## 3. Security and HIPAA Compliance

1. **De-Identification Protocol:** No Patient Health Information (PHI) such as names, social security numbers, medical record numbers, or birthdates are ingested.
2. **K-Anonymity & Minimum Cell Counts:** Cohort statistics enforce minimum subgroup counts ($k \ge 5$) before reporting demographics.
3. **Differential Privacy Guarantee:** Bounded Gaussian noise ensures the inclusion or exclusion of any single patient record yields an indistinguishable global model update within $(\epsilon = 1.0, \delta = 10^{-5})$.
4. **Auditability:** Every administrative modification, round execution, and patient addition is hashed into a tamper-evident audit ledger.
