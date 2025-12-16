# VR-CESM Eiger.Alps Porting Project

**Porting Variable-Resolution CESM3 from NCAR Derecho to CSCS Eiger.Alps**

This repository documents the technical work of porting and optimizing the Variable-Resolution Community Earth System Model (VR-CESM3) to run on the Swiss National Supercomputing Centre's Eiger.Alps system.

---

## Project Overview

**Objective:** Port Kenya-focused VR-CESM simulations (ne60x02 grid) from NCAR's Derecho to CSCS Eiger.Alps infrastructure, enabling high-resolution climate modeling for East African land-atmosphere feedback studies.

**System Details:**
- **Source System:** NCAR Derecho (CESM3 beta02)
- **Target System:** CSCS Eiger.Alps (AMD Milan CPUs)
- **Model:** CESM3 beta06 with CAM6, CLM5, coupled components
- **Grid:** Variable-resolution spectral element (ne60 globally, 0.125° over Kenya)

**Performance Results:**
- Successfully achieved **82% parallel efficiency** at 12 nodes
- Throughput: **11.16 simulation years/day** on 12 nodes
- Production-ready for multi-decade climate runs

---

## Key Achievements

### 1. **Successful Port & Optimization**
- ✅ Ported from Derecho (Intel) to Eiger (AMD Milan) architecture
- ✅ Optimized PE layout for atmosphere-land coupled configuration
- ✅ Achieved strong scaling efficiency: 99% (6 nodes) → 82% (12 nodes)
- ✅ Resolved mesh file compatibility and I/O configuration issues

### 2. **Performance Benchmarking**
Conducted systematic scaling tests on standard F2000climo compset:

| Nodes | Years/Day | NH/Year | Speedup | Efficiency |
|-------|-----------|---------|---------|-----------|
| 4     | 4.51      | 21.3    | 1.00x   | 100%      |
| 6     | 6.67      | 21.6    | 1.48x   | 99%       |
| 8     | 8.35      | 23.0    | 1.85x   | 93%       |
| 12    | 11.16     | 25.8    | 2.47x   | **82%**   |

*Strong scaling performance demonstrates excellent efficiency for atmosphere-land configuration*

### 3. **Technical Infrastructure**
- Custom Python diagnostic tools for automated spin-up monitoring
- Comprehensive documentation of technical challenges and solutions
- Reproducible build and configuration procedures

---

## Technical Challenges Solved

The porting process involved solving several key technical challenges:

1. **Mesh File Format Compatibility** - Converted SCRIP to ESMF format
2. **PE Layout Optimization** - Balanced CAM/CLM computational load
3. **Compiler Differences** - Adapted Intel flags for AMD environment
4. **I/O Configuration** - Optimized PIO settings for Eiger's Lustre filesystem
5. **Grid Registration** - Integrated custom VR grid into CESM framework
6. **Namelist Management** - Configured component-specific parameters

*Full technical details available in [`docs/technical-notes.md`](docs/technical-notes.md)*

---

## Repository Structure

```
vr-cesm-eiger-port/
├── README.md                    # This file
├── PROJECT_STATUS.md            # Current progress and roadmap
├── docs/
│   ├── setup.md                 # Complete setup guide
│   ├── benchmarks.md            # Detailed performance analysis
│   └── technical-notes.md       # Technical challenges & solutions
├── scripts/
│   ├── spinup_diagnostics.py   # Automated monitoring tool
│   └── analysis/
│       └── plot_benchmarks.py   # Performance visualization
├── benchmarks/
│   └── results/                 # Timing files from scaling tests
└── configs/
    └── build-notes.md           # Build configuration details
```

---

## Quick Start

**Prerequisites:**
- CSCS Eiger.Alps account
- CESM3 beta06 source code
- VR grid files (ne60x02 Kenya mesh)

**Setup:**
```bash
# See detailed instructions in docs/setup.md
source set_env.sh
cd cime/scripts
./create_newcase --case MY_CASE --compset F2000climo --res ne60x02 --machine eiger
```

---

## Current Status

**Phase:** Production runs in progress

**Project Scale (Year 1):**
- 103 simulations planned (70-year spinup + 30-year analysis per scenario)
- ~98,000 node-hours total on CSCS Eiger
- Expected completion: Q4 2025

**Latest Update:** October 2025 - Completed scaling benchmarks, initiated production runs

*See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for detailed roadmap*

---

## Scientific Context

This work supports climate modeling research at the Wyss Academy for Nature (University of Bern), focusing on:
- Land-atmosphere feedback mechanisms in East Africa
- High-resolution regional climate projections (0.125° over Kenya)
- Socio-economic scenario analysis under climate change

The Variable-Resolution approach enables computational efficiency by concentrating resolution where needed (Kenya region) while maintaining global context at coarser resolution.

---

## Tools & Technologies

- **Model:** CESM3 (beta06), CAM6, CLM5, CMEPS coupler
- **Languages:** Python 3.x, Bash, Fortran/C++ (model code)
- **HPC:** CSCS Eiger.Alps (Cray EX, AMD Milan), Slurm scheduler
- **Analysis:** xarray, matplotlib, pandas
- **Build System:** CMake, CIME framework

---

## Documentation

- **[Setup Guide](docs/setup.md)** - Complete porting instructions
- **[Performance Analysis](docs/benchmarks.md)** - Detailed scaling results
- **[Technical Notes](docs/technical-notes.md)** - Challenges & solutions
- **[Build Configuration](configs/build-notes.md)** - Compiler flags & settings

---

## Performance Highlights

**Excellent Strong Scaling:**
- Near-perfect efficiency up to 6 nodes (99%)
- Strong efficiency maintained at 12 nodes (82%)
- Production-ready performance: 11+ years/day

**Key Insight:** Atmosphere-land configuration scales significantly better than initially estimated, enabling efficient use of computational resources for multi-decade simulation campaigns.

---

## Contact

**Project Lead:** Jan Göpel  
**Institution:** Wyss Academy for Nature, University of Bern  
**System:** CSCS Eiger.Alps

---

## Acknowledgments

- CSCS for computational resources and technical support
- NCAR CESM development team
- Qing Sun (original Kenya grid development on Derecho)
- Wyss Academy for Nature

---

## License

This documentation is provided for reference. CESM3 model code is governed by CESM licensing terms.
