# Project Status & Roadmap

**VR-CESM Eiger.Alps Porting Project**  
**Last Updated:** November 2025

---

## Current Status: ✅ Production Runs Active

**Phase:** Production simulations in progress  
**Timeline:** Year 1 of multi-year climate modeling campaign

---

## Completed Milestones

### Phase 1: Initial Setup (Sept-Oct 2025) ✅
- [x] CESM3 beta06 installation on Eiger.Alps
- [x] Machine configuration file for Eiger
- [x] Compiler toolchain setup (Cray/GNU)
- [x] Library dependencies (NetCDF, PIO, ESMF)

### Phase 2: Grid Porting (Oct 2025) ✅
- [x] Transfer Kenya VR grid files (ne60x02) from Derecho
- [x] Convert SCRIP mesh to ESMF format
- [x] Register custom grid in CESM framework
- [x] Validate mesh file compatibility

### Phase 3: Test Case Development (Oct 2025) ✅
- [x] Create test case with Kenya grid
- [x] Configure PE layout for atm-land coupling
- [x] Resolve build issues (namelist defaults, mesh paths)
- [x] Successful 30-day test run

### Phase 4: Performance Benchmarking (Oct 2025) ✅
- [x] Standard grid scaling tests (4, 6, 8, 12 nodes)
- [x] Throughput analysis and efficiency calculations
- [x] PE layout optimization
- [x] I/O configuration tuning
- [x] **Result:** 82% efficiency at 12 nodes, 11.16 years/day

### Phase 5: Production Configuration (Oct-Nov 2025) ✅
- [x] VR grid production case setup
- [x] Spin-up protocol defined (70-year equilibration)
- [x] Diagnostic monitoring tools deployed
- [x] Initial production runs launched

---

## Current Work (Nov 2025)

### Active Tasks
- 🔄 Running first batch of 70-year spin-up simulations (3 scenarios)
- 🔄 Monitoring model stability and output quality
- 🔄 Validating land-atmosphere feedback representation
- 🔄 Adjusting I/O frequency based on data volume

### Near-Term Priorities
- Complete first 10 spin-up runs by end of November
- Analyze spin-up convergence criteria
- Optimize output file management strategy
- Document lessons learned from initial runs

---

## Upcoming Milestones

### Q4 2025 - Q1 2026: Spin-up Campaign
**Goal:** Complete 70-year equilibration for all 103 scenarios

**Tasks:**
- [ ] Batch 1: 10 scenarios (Nov-Dec 2025)
- [ ] Batch 2: 30 scenarios (Dec-Jan 2026)
- [ ] Batch 3: 30 scenarios (Jan-Feb 2026)
- [ ] Batch 4: 33 scenarios (Feb-Mar 2026)

**Resource Requirements:**
- ~7-10 days per scenario (70 years @ 8-12 nodes)
- ~98,000 node-hours total for Year 1
- Phased submission to manage queue limits

### Q2 2026: Analysis Period Runs
**Goal:** Run 30-year analysis periods for all scenarios

**Tasks:**
- [ ] Configure high-frequency output (daily/monthly)
- [ ] Submit analysis runs (shorter, more I/O intensive)
- [ ] Initial data QC and validation
- [ ] Archive to long-term storage

### Q3 2026: Data Analysis & Publications
**Goal:** Extract scientific insights, prepare manuscripts

**Tasks:**
- [ ] Land-atmosphere feedback quantification
- [ ] Regional climate change signals
- [ ] Socio-economic scenario comparison
- [ ] Manuscript preparation

---

## Technical Metrics

### Performance Achieved
| Metric | Value | Status |
|--------|-------|--------|
| Parallel Efficiency (12 nodes) | 82% | ✅ Excellent |
| Throughput (12 nodes) | 11.16 years/day | ✅ Production-ready |
| Resource Cost | 25.8 NH/year | ✅ Acceptable |
| Stability | No crashes in tests | ✅ Robust |

### Resource Usage (Projected)
| Phase | Node-Hours | Timeline |
|-------|------------|----------|
| Spin-up (103 scenarios) | ~70,000 | Q4 2025 - Q1 2026 |
| Analysis (103 scenarios) | ~28,000 | Q2 2026 |
| **Total Year 1** | **~98,000 NH** | **12 months** |

---

## Known Issues & Risks

### Technical Challenges (Resolved)
- ✅ Mesh format compatibility → Converted to ESMF
- ✅ PE layout optimization → Balanced atm/land
- ✅ Namelist configuration → Custom defaults added
- ✅ I/O performance → PIO settings tuned

### Active Monitoring
- ⚠️ **Queue wait times** - Eiger availability variable
- ⚠️ **Storage quotas** - Need to monitor/archive regularly  
- ⚠️ **Model drift** - Watch for climate drift in long runs

### Mitigation Strategies
- Staggered job submission to avoid queue congestion
- Automated data transfer to archive storage
- Regular checkpointing and restart capability
- Diagnostic monitoring for early drift detection

---

## Success Criteria

### Phase 5 Complete When:
- [x] Production configuration validated
- [x] First scenario successfully spun up
- [ ] Output data quality confirmed
- [ ] Storage and archival workflows operational

### Project Success Metrics:
- **Technical:** 100+ simulations completed with <5% failure rate
- **Performance:** Average >8 years/day throughput maintained
- **Science:** High-resolution climate data suitable for publication
- **Timeline:** All Year 1 runs complete by March 2026

---

## Lessons Learned

### What Worked Well
✅ Systematic benchmarking before production  
✅ Incremental testing (small → large scale)  
✅ Close collaboration with CSCS support  
✅ Comprehensive documentation throughout  

### What Could Improve
⚠️ Earlier validation of VR grid scaling  
⚠️ More aggressive I/O tuning from start  
⚠️ Better storage space planning  

### Recommendations for Future Ports
1. Always benchmark scaling before committing resources
2. Test full PE layout with target grid early
3. Validate output data volume projections
4. Build monitoring/diagnostic tools first
5. Document every configuration choice

---

## Team & Resources

**Lead:** Marie-Estelle Demory (Wyss Academy for Nature)  
**Institution:** University of Bern  
**HPC Facility:** CSCS Eiger.Alps  
**Allocation:** [Project allocation details]

**Support:**
- CSCS User Support (technical issues)
- CESM Forum (model-specific questions)
- Internal team (science/analysis)

---

## Repository Maintenance

**Update Frequency:** Monthly during active phases  
**Next Review:** December 2025 (after first batch complete)  
**Archive Plan:** Full documentation to Zenodo after completion

---

*Status reflects progress as of November 2025*  
*For questions or updates, contact: jan.goepel@unibe.ch*
