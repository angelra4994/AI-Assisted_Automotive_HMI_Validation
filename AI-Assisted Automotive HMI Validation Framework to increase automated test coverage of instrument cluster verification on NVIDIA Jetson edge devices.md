## Overview

Modern automotive instrument clusters contain hundreds of visual indicators, telltales, gauges, and touch-based functionalities, similar to modern smartphones, where system-level interactions must be extensively verified throughout the software development lifecycle.

Traditionally, Computer Vision solutions based on OpenCV scripts have been developed to support validation activities and issue investigations. These solutions can help identify HMI malfunctions such as:

- Black Screen
- White Screen
- Missing Text


While effective for specific use cases, rule-based image-processing approaches often require significant engineering effort and are sensitive to environmental factors such as brightness variations, reflections, camera positioning, display design changes, and image quality. As a result, maintaining and extending these scripts across multiple projects and HMI variants can become time-consuming and difficult to scale.

This project investigates how AI-assisted Computer Vision and Edge AI can complement traditional validation methods by automatically detecting dashboard elements, recognizing visible symptoms of HMI issues, and correlating visual observations with expected system behavior. Beyond supporting automated validation, the framework aims to assist engineers during issue analysis by automatically identifying potential symptoms, recording timestamps, and generating visual evidence that accelerates root-cause investigation. 

High-Value HMI Issues Detectable by Computer Vision

- Partial Rendering Failure
- Flickering
- Screen Freeze
- Corrupted Graphics
- Tearing


The solution runs on an **NVIDIA Jetson Orin Nano Super** and leverages deep learning models to detect dashboard Regions of Interest (ROI), monitor visual states, correlate observations with CAN messages, and automatically generate validation results. The long-term vision is to increase automated test coverage, improve validation scalability, and provide a reusable AI-assisted analysis framework that integrates seamlessly into automotive CI/CD workflows.


![[HMI validation Man vs Aut.png]]



---
## Motivation

Automotive software validation traditionally relies on:

- Manual observation of dashboard behavior
- Human verification of visual indicators
- Manual generation of test evidence

As the number of cluster features increases, manual validation becomes:

- Time-consuming
- Difficult to scale
- Error-prone
- A bottleneck for continuous integration

---

## Problem Statement

Vehicle instrument clusters react to numerous signals that control:

- Warning telltales
- Vehicle status indicators
- ADAS notifications
- Gauge states
- Driver information displays
 
Validating these visual responses typically requires a tester to manually confirm that the dashboard behavior matches the expected vehicle state.

Currently, on MultiView project, the estimation to validate manually the Display Region Check safety feature is 8hours



---
## Objective

Develop an automated validation framework capable of:

1. Detecting dashboard Regions of Interest (ROI)
2. Identifying visual indicators and display elements
3. Processing CAN messages related to dashboard behavior
4. Correlating expected and observed states
5. Generating automated Pass/Fail verdicts
6. Producing validation artifacts for CI/CD pipelines

---

## Current Progress

### Phase 1 — [[Demo of Dashboard ROI Detection]] ✅

The first stage of the project focuses on present an open-weight framework to locate regions within the cluster that are relevant for validation.

Implemented features:

- NVIDIA Jetson Orin Nano Super deployment
- Real-time image processing using YOLO26n
- Dashboard pattern detection
- Region of Interest extraction

Example:

```text
Parking Break              -> Detected
Hazard                     -> Detected
Needle Pointer             -> Detected

```


---

## Next Development Phase

### Phase 2 — CAN-Aware State Validation 🚧

The next step is integrating visual detection with CAN communication.

Validation flow:

```text
CAN Signal
      |
      V
Expected Dashboard's telltale State
      |
      V
Computer Vision Detection
      |
      V
State Correlation
      |
      V
PASS / FAIL
```

### Example 1

```text
CAN:
Parking Break = ON

Expected:
Parking Break telltale visible

Observed:
Parking Break telltale detected

Result:
PASS
```

### Example 2

```text
CAN:
Hazard_Status = ON

Expected:
Hazard warning telltale visible

Observed:
Hazard warning telltale not detected

Result:
FAIL
```

---

## System Architecture

```text
                    +----------------------+
                    |   CI/CD Pipeline     |
                    +----------+-----------+
                               |
                               V

                    +----------------------+
                    | Automated Test Suite |
                    +----------+-----------+
                               |
                               V

                    +----------------------+
                    | CAN Simulation Layer |
                    +----------+-----------+
                               |
                               V

                    +----------------------+
                    | Vehicle Cluster DUT  |
                    +----------+-----------+
                               |
                               V

                    +----------------------+
                    | NVIDIA Jetson Orin   |
                    | Nano Super           |
                    +----------+-----------+
                               |
        +----------------------+----------------------+
        |                      |                      |
        V                      V                      V

   ROI Detection         CAN Listener        Validation Engine
        |                      |                      |
        +----------------------+----------------------+
                               |
                               V

                         Test Report
```

Note: CANoe-Vector is already used for "CAN Simulation layer"

---

## Technology Stack

### Hardware

- NVIDIA Jetson Orin Nano Super
- Automotive Instrument Cluster
- CAN Interface

### Software

- TensorRT
- YOLO
- DOCKERS 

### Planned Integrations

- Jenkins
- Weight and Bias(W&B)
- DeepStream SDK

---
## Roadmap

### Completed

- [x] Jetson Orin Nano Super setup
- [x] Dashboard image acquisition
- [x] ROI detection
- [x] Pattern recognition prototype

### In Progress

- [ ] CAN message processing
- [ ] DBC integration
- [ ] Telltales state correlation 
- [ ] Automated verdict generation

### Planned

- [ ] DeepStream deployment
- [ ] Automated regression testing
- [ ] CI/CD integration
- [ ] Automated validation reports

---

## Expected Benefits

### Validation

- Increased automated test coverage
- Earlier defect detection
- Reduced manual verification effort
- Improved repeatability
### Business

- Reduced validation costs
- Faster software release cycles
- Improved product quality
### MultiView project:

- Automate Display Region Check validation 

---
## Author

**Angel Alejandro Rivas Alfaro**

---
