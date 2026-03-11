# PhD Proposal: Cognitive Digital Twin Platform for Energy Communities

---

## 1. Research Goal

**The overarching goal of this PhD is to create a platform for Energy Community Digital Twin (ECDT).**

The platform will enable the integration of heterogeneous spatial and temporal data from buildings and distribution grids, enriched with a semantic layer, to support decision-making, optimization, and fault detection in energy communities. By addressing key research gaps—heterogeneous data integration from sparse sources, standardization through ontologies, and the "perfect data fallacy"—this work aims to deliver a **Cognitive Digital Twin** that can reason over real-world energy community data.

---

## 2. Key Concepts

### 2.1 Energy Communities (EC)

Energy Communities are locally and collectively organized energy systems that consist of:

- **Consumers, prosumers, and other local entities** (power plants, storage facilities, EV charging stations, public buildings)
- **Voluntary participation** with access to Local Electricity Markets (LEM)
- **Shared benefits** from local Renewable Energy Sources (RES), trading, and grid management

They are reconfiguring the energy sector toward decentralization, enabling members to consume, store, and sell electricity, and to offer flexibility to the power system. EC initiatives face barriers including fragmented digital infrastructures, lack of standardized models for appliances and energy systems, and limited interoperability across vendors and domains.

### 2.2 Digital Twin of Energy Communities (ECDT)

An Energy Community Digital Twin (ECDT) is a virtual representation of an energy community that:

- **Replicates** the EC and the operation of individual entities (consumers, prosumers, public assets)
- **Combines** a network model with measurements to support decision-making
- **Enables** real-time or near-real-time monitoring, optimization, and coordination
- **Supports** data assimilation (e.g., Distribution System State Estimation) and analysis phases

A **Cognitive Digital Twin** extends this by adding a **semantic layer** (ontology) that enables:

- Machine-interpretable meaning of data and models
- Interoperability across heterogeneous systems
- Reasoning and flexibility beyond rigid, vendor-specific implementations

### 2.3 Digital Shadow vs. Digital Twin vs. Simulator

| Concept | Description |
|---------|-------------|
| **Digital Shadow** | One-way data flow: physical system → digital representation. No feedback to the physical system. |
| **Digital Twin** | Two-way continuous exchange of data between physical and digital. Enables closed-loop control and adaptation. |
| **Simulator / Co-Simulator** | Computational model used to predict behavior. Can be coupled with real data for validation and fault detection. |

A semantic layer is needed to deal with digital shadows and digital twins consistently, enabling interoperability and reusability.

---

## 3. Research Gaps in ECDT

Three major research gaps motivate this PhD:

### Gap 1: Heterogeneous Platform for City Information Model from Sparse Data Sources

There is a need to develop a **heterogeneous platform** that can integrate:

- **Buildings** (geometry, thermal zones, envelope, energy systems, occupant behavior)
- **Distribution grid** (network topology, assets, connectivity)
- **Sparse and heterogeneous data sources** (cadastral data, LiDAR, OpenStreetMap, utility records, smart meters)

Most existing tools focus either on electricity networks or on local energy systems; the interaction between buildings and grids is not comprehensively addressed. Building a unified City Information Model (CIM) that hosts both building and grid data from sparse sources remains an open challenge.

### Gap 2: Standardization and Semantic Layer

**2.1 Standardization**

- Digital twins are often **tightly coupled** with their physical counterparts, hindering reusability and interoperability.
- There is an **absence of standardized models** for appliances and energy systems.
- Different vendors and domains use incompatible representations, limiting plug-and-produce scenarios.

**2.2 Semantic Layer by Ontology**

- A semantic layer (ontology) is needed for **ultimate flexibility** and interoperability.
- Ontology-based concepts enable high-level, vendor-neutral descriptions of capabilities and behaviors.
- This supports semantic contracts, dynamic integration, and reasoning over heterogeneous data.

### Gap 3: The "Perfect Data" Fallacy

Most academic case studies for Distribution System State Estimation (DSSE) and energy community modeling are based on **synthetic test cases** that fail to show the complexities of real networks and lack necessary power and voltage measurement data.

In reality:

- Raw data from power meters can be **stuck**, have **gross errors**, or present **missing values**
- Actual networks often have **unreported manual tap position changes** on transformers, making the baseline model inaccurate from the start
- Mismatches between real and digital line parameters can cause state estimators to flag normal measurements as gross errors
- Voltage measurements are typically not stored by utilities, yet errors in the network model can only be identified when voltage data are available

Working with **actual data** from an energy community is essential to validate and improve digital twin frameworks under real-world conditions.

---

## 4. Research Plan and Methodology

### Phase I: Urban Energy Model (UEM) — Foundation

**Objective:** Develop an urban energy model to host buildings and grid data (spatial data) with simulation results (time series data).

**Deliverables:**

- Integration of **3DCityDB** (or equivalent) for spatial building and grid data
- **TimeScaleDB** (or equivalent) for time series simulation results
- Support for **CityJSON** format for structured 3D city representation
- Bridging **CIM → BIM → BEM** for high-resolution urban energy modeling

**Technical path:** Extend CIM Wizard to use CityJSON instead of GeoJSON, and integrate with building energy simulation outputs.

### Phase II: Semantic Layer (Ontology)

**Objective:** Add an ontology layer to enable a Cognitive Digital Twin.

**Deliverables:**

- Integration of **web semantic** technologies (RDF, OWL, SPARQL)
- Ontology for energy community concepts (buildings, grid assets, appliances, energy flows)
- Standard & Semantic CIM paper (Paper 1)

**Outcome:** The platform becomes a **Cognitive Urban Energy Digital Twin** because it can reason over semantically enriched data.

### Phase III: AI Assistant (CIM Assist) — Side Project

**Objective:** Fine-tune an LLM to convert natural language to Spatio-Temporal SQL (txt2STSQL).

**Deliverables:**

- txt2STSQL benchmark dataset
- Fine-tuned model for domain-specific energy/spatial queries
- CIM Assist MVP for querying spatiotemporal datasets
- Paper on txt2STSQL (Paper II)

**Rationale:** Enables agentic engineering and natural language interfaces for energy community data exploration.

### Phase IV: Actual Data — Addressing the Perfect Data Fallacy

**Objective:** Use actual data from an energy community to validate and improve the platform.

**Deliverables:**

- Integration of real power meter data, network model, and (where available) voltage measurements
- Handling of stuck meters, gross errors, missing values, and unreported tap changes
- Validation of DSSE and digital twin outputs under real-world conditions

**Reference:** ECDT_UK.pdf demonstrates how measurement and network uncertainties substantially impact digital twin quality.

### Phase V: Edge Computing and Fault Detection

**Objective:** Deploy an embedded board for edge computing in the energy community to co-simulate with the COESI platform (digital shadow co-simulator).

**Deliverables:**

- Embedded board deployment for local data collection and processing
- Co-simulation with COESI platform
- **Fault detection** by comparing actual data from the embedded board with predicted data from COESI
- Quantification of residuals and anomalies

**Rationale:** Fault Detection and Diagnosis (FDD) at whole-building or community level is crucial for continuous commissioning. Comparing predicted vs. measured data enables identification of anomalies and operational faults.

---

## 5. Timeline & Milestones

| Phase | Milestone | Output |
|-------|-----------|--------|
| I | Milestone I | CIM Wizard MVP; CityJSON restructure; UEM foundation |
| II | Milestone II | CIM Wizard extension by web semantic; Cognitive Urban Digital Twin |
| III | Milestone III | CIM Assist development; txt2STSQL benchmark; Paper II |
| IV | — | Actual EC data integration; validation |
| V | — | Embedded board; COESI co-simulation; fault detection |

---

## 6. Papers for Review (SOTA)

The following papers in `paper/sota/` are recommended for your literature review and positioning:

### 6.1 Energy Community Digital Twin

| Paper | File | Summary |
|-------|------|---------|
| **Enabling coordination in energy communities: A Digital Twin model** | `energy_community_DT.pdf` | Proposes a DT with bi-level optimization for EC coordination, iEMS (member assistant) and eEMS (EC assistant). Includes LEM, LFM, value sharing, flexibility. Tested on EC case study with seasonal and annual results. |
| **Operation Orchestration of Local Energy Communities through Digital Twin** | `Operation_Orchestration_...pdf` | Review of modeling and simulation approaches for LEC DT. Presents DT framework with model library, twining services, physics-based and data-driven models. Focus on flexibility profiles for balancing reserves. |
| **Enabling Self-Adaptation of Renewable Energy Communities with a Capability-Based Digital Twin** | `ecdt.pdf` | AAS-based digital twin for RECs. Addresses standardization and interoperability via Asset Administration Shell. Capability-based semantics for plug-and-produce. Self-adaptive, autonomic computing. |

### 6.2 Real Data and Perfect Data Fallacy

| Paper | File | Summary |
|-------|------|---------|
| **Smart Energy Network Digital Twins: Findings from a UK-Based Demonstrator Project** | `ECDT_UK.pdf` | **Critical for Gap 3.** Real-world DT on SEND microgrid. Open-source network model and measurements. Demonstrates impact of measurement and network uncertainties. Discusses synthetic vs. real data for DSSE. |
| **The gap between predicted and measured energy performance of buildings** | `predicted vs measured data.pdf` | Framework for investigating performance gap. Root causes: design, construction, operation. Performance gap is a function of time and external conditions. |

### 6.3 Fault Detection and Anomaly Detection

| Paper | File | Summary |
|-------|------|---------|
| **A data analytics-based tool for the detection and diagnosis of anomalous daily energy patterns in buildings** | `capozzoli-anomaly1.pdf` | FDD at whole-building level. Multi-step clustering for anomalous load profiles. ANN + Regression Tree for fault-free predictive model. Continuous commissioning. |
| **Automated load pattern learning and anomaly detection for enhancing energy management in smart buildings** | `capozzoli-anomaly.pdf` | SAX-based methodology for energy time series. Characterisation of patterns, anomaly detection. Supports stakeholders in energy management. |
| **Anomaly detection on household appliances based on variational autoencoders** | `midiori_anomaly_detection.pdf` | VAE for appliance-level anomaly detection. Power signatures. Outperforms OC-SVM. Relevant for edge/appliance-level fault detection. |

### 6.4 Occupancy, HVAC, and Cost-Optimal Analysis

| Paper | File | Summary |
|-------|------|---------|
| **Data analytics for occupancy pattern learning to reduce the energy consumption of HVAC systems in office buildings** | `capozzoli_Ocupancy_HVAC.pdf` | Occupancy-based HVAC optimization. 14% savings for Zaanstad Town Hall. Calibrated with actual energy data. |
| **Assessment of cost-optimal energy performance requirements for the Italian residential building stock** | `Corrado_cost-optimal_residential.pdf` | Cost-optimal methodology per EPBD. Reference buildings, EEM packages. |
| **Cost-optimal analysis of Italian office buildings** | `corrado_cost-optimal_office.pdf` | Quasi-steady state vs. dynamic simulation for cost-optimal analysis. |

**Key insight:** Corrado et al. (2014) show that physical interventions are priority for individual units; at EC scale, Building Automation and data-driven smart agents become most economically viable.

### 6.5 NILM and Load Disaggregation

| Paper | File | Summary |
|-------|------|---------|
| **Simple Event Detection and Disaggregation Approach for Residential Energy Estimation** | `Simple_Event_Detection_and_Disaggregatio.pdf` | AWB-NILM, event-based disaggregation. Active/reactive power at 1 Hz. Relevant for substation-level or disaggregated load modeling. |
| **Non-intrusive Load Composition Estimation from Aggregate ZIP Load Models using Machine Learning** | `midiori1.pdf` | Load composition at substation level. ZIP load model, MLP-ANN, PSO, GA. NILM for substations. |

---

## 7. Relationship to Existing Work (CIM Wizard & COESI)

- **CIM Wizard** provides the building and urban data pipeline (calculators, PostGIS, vector/raster data). It will be extended with CityJSON, semantic layer, and time series integration.
- **COESI** is a co-simulation platform for energy modeling. The embedded board will co-simulate with COESI to enable fault detection by comparing predicted (COESI) vs. actual (embedded board) data.

---

## 8. Expected Contributions

1. **Heterogeneous ECDT platform** integrating buildings and grid from sparse data sources
2. **Semantic layer** for ECDT enabling cognitive capabilities and interoperability
3. **txt2STSQL** benchmark and fine-tuned LLM for natural language querying of spatiotemporal energy data
4. **Validation with actual EC data** addressing the perfect data fallacy
5. **Edge-based fault detection** via embedded board and COESI co-simulation

---


*Last updated: 11 March 2026*
