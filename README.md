# LLVM-Based Data-Flow Duplication & Security Pass

## Project Overview

This project implements a **compiler-based fault injection countermeasure system** that detects and prevents fault injection attacks through data-flow duplication and statistical variable ranking. The system automatically identifies security-critical comparisons in compiled code and inserts redundant checks to detect when faults corrupt the program's behavior.

**Key Innovation**: Unlike naive duplication (which increases code size 3-4x), we use **Bayesian ranking** to protect only critical variables, reducing overhead to ~25%.

## Architecture

```
C Source Code
    ↓
[Go Parser] ← Recursive descent parser generating LLVM IR
    ↓
LLVM IR (Intermediate Representation)
    ↓
[Python Protector] ← Data-flow duplication + Bayesian ranking
    ↓
Protected IR (with verification checks)
    ↓
[Verification Engine] ← Proves protections survive -O2 optimization
    ↓
Fault-Detection Executable
```

## Problem Statement

**Fault injection attacks** corrupt program data/registers during execution using:
- Laser pulses
- Voltage glitches  
- Electromagnetic interference

A compromised comparison can bypass authentication:
```c
if (input == secret)  // Attack: flip this to always true
    return 1;         // Attacker gains access
```

## Solution: Data-Flow Duplication

Instead of protecting just one variable, we **duplicate the entire data flow**:

### Unprotected IR:
```llvm
%7 = icmp eq i32 %5, %6              ; Single comparison
br i1 %7, label %grant, label %deny  ; Direct branch
```

### Protected IR:
```llvm
%7 = icmp eq i32 %5, %6              ; Original
%dup_1000 = icmp eq i32 %5, %6       ; Duplicate shadow copy
%verify = icmp eq i1 %7, %dup_1000   ; Verify they match
br i1 %verify, label %safe, label %fault

safe:
  br i1 %7, label %grant, label %deny  ; Trusted branch

fault:
  call void @abort()                   ; Detection + response
```

**Why This Works:**
- Attacker must corrupt TWO values at precise timing (exponentially harder)
- Both duplicates must match for verification to pass
- Fault detection triggers abort() if tampering detected

## Components

### 1. Go Parser (`src/go-parser/`)
Parses a C subset and generates LLVM IR:
- Recursive descent parser
- AST generation
- LLVM IR code generation
- ✅ **Status**: COMPLETE

### 2. Python Protector (`src/python-tools/llvm_protector_ranked.py`)
Analyzes LLVM IR and inserts protective checks:
- Identifies all comparisons via IR parsing
- Bayesian ranking to score criticality
- Duplicates high-priority comparisons
- Inserts verification + abort() logic
- ✅ **Status**: COMPLETE

### 3. Verification Engine (`src/python-tools/verify_protection.py`)
Proves protections survive compiler optimizations:
- Counts abort() calls before/after -O2
- Tracks duplicate comparison survival
- Measures code size overhead
- Confirms robustness against optimization
- ✅ **Status**: COMPLETE

## Project Status

| Component | Status | Details |
|-----------|--------|---------|
| Go Parser | ✅ Complete | Generates LLVM IR from C |
| Ranked Protector | ✅ Complete | Bayesian ranking + duplication |
| Verification Engine | ✅ Complete | Proves optimization resilience |

## Quick Start

```bash
bash demo.sh
```

This runs the complete pipeline and shows results.

## Demonstration Results

**Protected IR survives -O2 optimization:**
```
[✓] VERIFICATION PASSED
    Abort calls:    1 → 1 ✓
    Duplicates:     2 → 2 ✓
    Code overhead:  +25% (vs 3-4x for naive duplication)
```

## File Structure
```
llvm-security-project/
├── src/
│   ├── go-parser/               # C parser → LLVM IR
│   └── python-tools/
│       ├── llvm_protector_ranked.py    # Bayesian protector
│       └── verify_protection.py         # Verification engine
├── tests/
│   ├── inputs/                  # Test C programs
│   └── outputs/                 # Generated IR + results
├── bin/
│   └── c2llvm                   # Compiled Go parser
├── demo.sh                      # End-to-end demonstration
└── README.md                    # This file
