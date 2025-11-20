# Performance Benchmarks: VR-CESM on Eiger.Alps

**Comprehensive scaling analysis for atmosphere-land coupled configuration**

---

## Benchmark Configuration

**Test Setup:**
- **Model:** CESM3 beta06
- **Compset:** F2000climo (2000_CAM60_CLM50%SP_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV_SESP)
- **Grid:** 0.9x1.25 (standard resolution for scaling tests)
- **Run Length:** 30 simulation days per test
- **System:** CSCS Eiger.Alps (AMD Milan, 128 cores/node)
- **Date:** October 16-20, 2025

**Rationale:**  
Standard-resolution benchmarks establish baseline scaling characteristics before deploying expensive VR-grid (ne60x02) production runs.

---

## Performance Summary

### Overall Metrics

| Configuration | Years/Day | Sec/Day | NH/Year | Speedup | Efficiency |
|--------------|-----------|---------|---------|---------|-----------|
| 4 nodes      | 4.51      | 52.5    | 21.3    | 1.00x   | 100%      |
| 6 nodes      | 6.67      | 35.5    | 21.6    | 1.48x   | **99%**   |
| 8 nodes      | 8.35      | 28.4    | 23.0    | 1.85x   | **93%**   |
| 12 nodes     | 11.16     | 21.2    | 25.8    | 2.47x   | **82%**   |

**Key Finding:** Atmosphere-land configuration achieves **strong scaling** with 82% efficiency at 12 nodes, significantly better than typical weak scaling expectations.

---

## Detailed Performance Analysis

### 1. Throughput Scaling

**Model Throughput (simulated years/day):**
- 4 nodes:  4.51 years/day (baseline)
- 6 nodes:  6.67 years/day (+48% improvement)
- 8 nodes:  8.35 years/day (+85% improvement)
- 12 nodes: 11.16 years/day (+147% improvement)

**Interpretation:** Nearly linear scaling from 4→6 nodes, with diminishing but acceptable returns at 12 nodes.

### 2. Parallel Efficiency

**Strong Scaling Efficiency:**
```
Efficiency = (Speedup / Node_Ratio) × 100%

6 nodes:  (1.48 / 1.5)  = 99%  ← Excellent
8 nodes:  (1.85 / 2.0)  = 93%  ← Very Good  
12 nodes: (2.47 / 3.0)  = 82%  ← Good
```

**What This Means:**
- At 6 nodes, we achieve near-perfect scaling (99% efficient)
- At 12 nodes, we still use 82% of additional resources effectively
- This is **strong scaling** behavior (fixed problem size, increasing resources)

### 3. Resource Consumption

**Node-Hours per Simulation Year:**
```
NH/year = (24 hours/day) / (years/day) × nodes

4 nodes:  24 / 4.51  × 4  = 21.3 NH/year
6 nodes:  24 / 6.67  × 6  = 21.6 NH/year
8 nodes:  24 / 8.35  × 8  = 23.0 NH/year
12 nodes: 24 / 11.16 × 12 = 25.8 NH/year
```

**Cost-Efficiency Trade-off:**
- 6 nodes: Only +1.4% overhead, 48% faster (best efficiency)
- 8 nodes: +8% overhead, 85% faster
- 12 nodes: +21% overhead, 147% faster (best throughput)

**Recommendation:** For long runs, 6-8 nodes optimal. For urgent results, 12 nodes justified.

---

## Component Timing Breakdown

### 4-Node Baseline

| Component | Time (s/day) | % Total | Throughput |
|-----------|--------------|---------|------------|
| ATM (CAM) | 46.3         | 88.2%   | 5.1 years/day |
| LND (CLM) | 4.2          | 8.0%    | 56.8 years/day |
| CPL       | 1.6          | 3.1%    | 145.9 years/day |
| Other     | 0.4          | 0.8%    | - |

**Bottleneck:** Atmosphere (CAM) dominates computational cost (~88%)

### 12-Node Optimized

| Component | Time (s/day) | % Total | Throughput |
|-----------|--------------|---------|------------|
| ATM (CAM) | ~18.7*       | ~88%    | ~12.6 years/day |
| LND (CLM) | ~1.9*        | ~9%     | ~126 years/day |
| CPL       | ~1.3         | ~6%     | 176.5 years/day |

*Estimated from total timing and baseline proportions*

**Scaling Behavior:** CAM scales well (2.5x faster), but communication overhead increases slightly (CPL % increases).

---

## PE Layout Analysis

**Task Distribution:**

| Nodes | Total PEs | ATM PEs | LND PEs | Other | Tasks/Node |
|-------|-----------|---------|---------|-------|------------|
| 4     | 478       | 256     | 96      | 126   | 128        |
| 6     | 717       | 384     | 144     | 189   | 128        |
| 8     | 956       | 512     | 192     | 252   | 128        |
| 12    | 1488      | 768     | 320     | 400   | 128        |

**Layout Strategy:**
- Consistent 128 tasks/node (full node utilization)
- ATM:LND ratio maintained at ~2.5:1 (reflects computational imbalance)
- Linear increase in PE counts maintains load balance

**Why This Works:**
- CAM atmosphere component scales efficiently with more PEs
- CLM land component is less compute-intensive, doesn't bottleneck
- Communication costs remain manageable up to 12 nodes

---

## Technical Insights

### What Drives Good Scaling?

1. **Atmosphere-Dominated Workload**
   - CAM (88% of runtime) parallelizes well
   - More PEs → each handles smaller spatial domain
   - Communication-to-computation ratio stays favorable

2. **Optimized PE Layout**
   - Tasks allocated proportionally to component costs
   - Full node utilization (128 tasks/node)
   - Minimized idle time

3. **Efficient Coupler**
   - CPL overhead remains low (~3-6% of total time)
   - Data exchange between components well-optimized

### Comparison to Expectations

**Initial Estimate (Wrong):**
- Predicted 69% efficiency at 12 nodes
- Assumed weak scaling behavior

**Actual Result (Better):**
- Achieved 82% efficiency at 12 nodes  
- Strong scaling behavior observed

**Lesson:** Atmosphere-land configuration scales significantly better than fully-coupled ocean models due to:
- No expensive ocean dynamics
- Prescribed SSTs (DOCN data ocean)
- Simpler component coupling

---

## Production Implications

### Optimal Configuration for Different Scenarios

**Long Multi-Decade Runs (70+ years):**
- **Best Choice:** 6-8 nodes
- **Rationale:** Excellent efficiency (93-99%), minimal cost overhead
- **Example:** 70-year run completes in ~10-11 days

**Urgent Short Runs (1-30 years):**
- **Best Choice:** 12 nodes
- **Rationale:** Maximum throughput despite 21% overhead
- **Example:** 30-year run completes in ~2.7 days

**Resource-Constrained:**
- **Fallback:** 4 nodes
- **Rationale:** Still reasonable (4.5 years/day), most efficient per-node

### VR-Grid Expectations

**Kenya ne60x02 Grid:**
- Higher resolution → more computation per timestep
- Expect ~30-40% slower than standard grid (based on cell count)
- Scaling characteristics should remain similar
- Likely optimal range: 8-12 nodes for production

**Estimated VR Throughput:**
- 12 nodes: ~7-8 years/day (vs 11.16 for standard grid)
- 8 nodes: ~5-6 years/day (vs 8.35 for standard grid)

---

## Validation & Quality Checks

**Test Validity:**
- ✅ All runs completed successfully (30 simulation days each)
- ✅ Consistent initialization and forcing
- ✅ Timing files show stable performance (no anomalies)
- ✅ Component load balance appropriate

**Reproducibility:**
- Same compset (F2000climo) across all tests
- Same grid (0.9x1.25) for apple-to-apples comparison
- Timing extracted from CESM built-in diagnostics

---

## Recommendations

### For This Project

1. **Standard Production:** Use 8 nodes (good balance of speed and efficiency)
2. **Time-Critical Runs:** Use 12 nodes when deadline-driven
3. **Spin-up Phase:** Consider 6 nodes (highest efficiency for long runs)

### For Future Work

1. **Test VR Grid Scaling:** Confirm ne60x02 grid exhibits similar behavior
2. **Optimize I/O:** Current tests use default PIO settings; further tuning possible
3. **Thread vs MPI:** Consider hybrid MPI+OpenMP for NUMA architecture
4. **GPU Acceleration:** Eiger has GPU nodes; CAM7 may benefit in future

---

## Raw Data

**Timing Files Available in `benchmarks/results/`:**
- `cesm_timing_clm_climo_4node_*.txt`
- `cesm_timing_clm_climo_6node_*.txt`
- `cesm_timing_clm_climo_8node_*.txt`
- `cesm_timing_clm_climo_12node_*.txt`

**Key Metrics Extracted:**
- Model Cost (pe-hrs/simulated_year)
- Model Throughput (simulated_years/day)
- Component timings (seconds/model-day)
- Init/Run/Final times

---

## Conclusions

**Key Takeaways:**

1. ✅ **Strong scaling achieved** - 82% efficiency at 12 nodes
2. ✅ **Production-ready** - 11+ years/day enables multi-decade campaigns  
3. ✅ **Cost-efficient** - Minimal overhead up to 8 nodes
4. ✅ **Better than expected** - Original estimates significantly pessimistic

**Impact on Project:**
- Enables 70-year spin-up runs in ~6-10 days (vs weeks on smaller allocations)
- 103-simulation campaign feasible within Year 1 timeline
- Confidence in scaling behavior for VR grid deployment

**Technical Validation:**
- Proper PE layout design confirmed
- Communication overhead manageable at scale
- AMD Milan architecture performs well for CESM workloads

---

## Appendix: Calculation Details

### Speedup
```
Speedup = Throughput(N nodes) / Throughput(4 nodes)

6 nodes:  6.67 / 4.51 = 1.48x
8 nodes:  8.35 / 4.51 = 1.85x
12 nodes: 11.16 / 4.51 = 2.47x
```

### Parallel Efficiency
```
Efficiency = Speedup / (N_nodes / N_baseline)

6 nodes:  1.48 / (6/4)  = 1.48 / 1.5  = 0.987 = 99%
8 nodes:  1.85 / (8/4)  = 1.85 / 2.0  = 0.925 = 93%
12 nodes: 2.47 / (12/4) = 2.47 / 3.0  = 0.823 = 82%
```

### Node-Hours per Year
```
NH/year = (Hours per day) / (Years per day) × Number of nodes

4 nodes:  24 / 4.51  × 4  = 21.29 NH/year
6 nodes:  24 / 6.67  × 6  = 21.59 NH/year  
8 nodes:  24 / 8.35  × 8  = 22.99 NH/year
12 nodes: 24 / 11.16 × 12 = 25.81 NH/year
```

---

*Last Updated: October 2025*  
*Analysis by: Jan Göpel, Wyss Academy for Nature*
