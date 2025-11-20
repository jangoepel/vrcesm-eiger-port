# Technical Notes: Challenges & Solutions

**Detailed documentation of technical issues encountered during VR-CESM porting to Eiger.Alps**

---

## Overview

This document captures the key technical challenges faced when porting Variable-Resolution CESM3 from NCAR Derecho (Intel architecture) to CSCS Eiger.Alps (AMD Milan architecture), along with solutions and lessons learned.

---

## Challenge 1: Mesh File Format Compatibility

### Problem
CESM3 on Eiger expected ESMF-format mesh files, but Kenya VR grid was provided in SCRIP format from Derecho. Build failed with:
```
ERROR: Cannot find mesh file in ESMF format
```

### Root Cause
Different CESM versions and configurations use different mesh file formats. SCRIP (originally for regridding) vs ESMF (native CESM coupler format).

### Solution
Convert SCRIP to ESMF format using NCO tools:

```bash
module load NCO

# Rename coordinate variables
ncrename -v grid_center_lat,centerCoords \
         -v grid_center_lon,centerCoords \
         input_SCRIP.nc intermediate.nc

# Add required ESMF attributes
ncatted -a units,centerCoords,c,c,"degrees" intermediate.nc
ncatted -a coordinates,elementMask,c,c,"centerCoords" intermediate.nc

# Final output
mv intermediate.nc ne60x02_Kenya_EXODUS.nc
```

### Verification
```bash
ncdump -h ne60x02_Kenya_EXODUS.nc | grep -i "esmf\|exodus"
```

### Lessons Learned
- Always verify mesh format requirements for target system
- Keep both SCRIP and ESMF versions for portability
- Test mesh file before submitting production runs

---

## Challenge 2: PE Layout Optimization

### Problem
Initial runs with copied PE layout from Derecho showed poor scaling (< 60% efficiency at 12 nodes). Atmosphere component was load-imbalanced.

### Root Cause
Derecho's Intel architecture and Eiger's AMD Milan have different:
- Core counts per node (Derecho: 128, Eiger: 128) - same but different memory hierarchy
- MPI implementation (Intel MPI vs Cray MPICH)
- Optimal task-to-core mapping strategies

### Solution
Systematic PE layout tuning based on component timing:

**Before (Derecho layout):**
```
NTASKS_ATM=256
NTASKS_LND=128
```

**After (Optimized for Eiger 12-node):**
```
NTASKS_ATM=768   (3x increase)
NTASKS_LND=320   (2.5x increase)
NTASKS_ICE=128
NTASKS_CPL=128
```

### Key Insights
- Monitor `cesm_timing` output for component run times
- Balance load so no single component dominates
- Use full node (128 tasks/node) for efficiency
- ATM:LND ratio of ~2.4:1 worked best for atmosphere-land configuration

### Verification
```bash
grep "Run Time" run/cesm_timing.* | grep -E "ATM|LND"
```

Good balance when ATM and LND per-task times are similar.

---

## Challenge 3: Compiler Flag Differences

### Problem
Build failed with optimization-related errors:
```
ICE: internal compiler error: Segmentation fault
```

### Root Cause
Aggressive optimization flags from Derecho's Intel compiler (`-O3 -xHost`) don't translate directly to GNU/Cray compilers on Eiger.

### Solution
Conservative but safe compiler flags in `config_machines.xml`:

```xml
<compiler MACH="eiger">
  <FFLAGS>
    <base>-O2 -march=znver3</base>
    <DEBUG>-g -fbacktrace -fbounds-check</DEBUG>
  </FFLAGS>
  <CFLAGS>
    <base>-O2 -march=znver3</base>
  </CFLAGS>
</compiler>
```

### Performance Impact
- `-O2` vs `-O3`: ~5% slower but stable
- `-march=znver3`: AMD Zen3 (Milan) specific optimizations
- Worth the trade-off for reliability

### Lessons Learned
- Start conservative, optimize later
- Test with DEBUG flags first for new ports
- Document working flags for reproducibility

---

## Challenge 4: I/O Configuration & PIO Settings

### Problem
Slow I/O performance (>10% of total time) and occasional hangs during output writing. Large history files took excessive time to write.

### Root Cause
Default PIO (Parallel I/O) settings not optimized for Eiger's Lustre filesystem configuration. Too few I/O tasks caused bottlenecks.

### Solution
Tuned PIO settings in `env_run.xml`:

```bash
./xmlchange PIO_TYPENAME=pnetcdf       # Use parallel-netcdf
./xmlchange PIO_STRIDE=4               # I/O task spacing
./xmlchange PIO_NUMIOTASKS=32          # Number of I/O tasks
./xmlchange PIO_REARRANGER=box         # Rearrangement strategy
```

**Lustre Striping:**
```bash
# Set stripe count for output directory
lfs setstripe -c 8 /path/to/archive/atm/hist
```

### Results
- I/O time reduced from 10% to 3-4% of total
- No more hangs during output writing
- History files write 3x faster

### Verification
```bash
# Check PIO configuration
grep "PIO_" env_run.xml

# Monitor I/O during run
lfs df -h /path/to/output
```

---

## Challenge 5: Custom Grid Namelist Defaults

### Problem
Build failed when creating namelists for custom grid:
```
ERROR: No default value for 'drydep_srf_file' for grid ne60x02_Kenya
```

### Root Cause
CESM's `namelist_defaults_cam.xml` only has entries for standard grids. Custom VR grids need explicit defaults for all required parameters.

### Solution
Add entries to `${CESM_ROOT}/components/cam/bld/namelist_files/namelist_defaults_cam.xml`:

```xml
<!-- Kenya ne60x02 VR Grid -->
<se_mesh_file hgrid="ne60x02_Kenya">
  /users/jgpel/vrgrids/ne60x02_Kenya/ne60x02_Kenya_EXODUS.nc
</se_mesh_file>

<bnd_topo hgrid="ne60x02_Kenya">
  /users/jgpel/vrgrids/ne60x02_Kenya/ne60x02_Kenya_topography.nc
</bnd_topo>

<ncdata hgrid="ne60x02_Kenya">
  /users/jgpel/vrgrids/ne60x02_Kenya/ne60x02_Kenya_initial_conditions.nc
</ncdata>

<drydep_srf_file hgrid="ne60x02_Kenya">
  /users/jgpel/vrgrids/ne60x02_Kenya/ne60x02_Kenya_drydep.nc
</drydep_srf_file>
```

### Similar Changes Needed for CLM
Edit `components/clm/bld/namelist_files/namelist_defaults_clm.xml`:

```xml
<fsurdat hgrid="0.9x1.25" mask="ne60x02_Kenya">
  /users/jgpel/vrgrids/ne60x02_Kenya/ne60x02_Kenya_surface_data.nc
</fsurdat>
```

### Lessons Learned
- Document all required namelist variables for custom grids
- Use absolute paths (not relative) for reliability
- Test with `./preview_namelists` before building

---

## Challenge 6: Grid Registration in CESM Framework

### Problem
CESM didn't recognize custom grid name. Creating case failed:
```
ERROR: Grid ne60x02_Kenya is not supported
```

### Root Cause
New grids must be registered in multiple XML configuration files within CESM source.

### Solution
Update three key files:

**1. Grid Definition** (`config/cesm/config_grids.xml`):
```xml
<domain name="ne60x02_Kenya">
  <nx>69120</nx>
  <ny>1</ny>
  <desc>Variable-res ne60, 0.125 deg over Kenya</desc>
</domain>
```

**2. Model Grid** (`config/cesm/component_grids_nuopc.xml`):
```xml
<model_grid alias="ne60x02_Kenya">
  <grid name="atm">ne60x02_Kenya_np4</grid>
  <grid name="lnd">ne60x02_Kenya_np4</grid>
  <grid name="ocn">gx1v7</grid>
  <mesh atm="ne60x02_Kenya_EXODUS.nc" lnd="ne60x02_Kenya_EXODUS.nc" />
</model_grid>
```

**3. Grid Alias** (`config/cesm/modelgrid_aliases_nuopc.xml`):
```xml
<model_grid alias="ne60x02_Kenya_g17">
  ne60x02_Kenya_ne60x02_Kenya_gx1v7
</model_grid>
```

### Verification
```bash
cd cime/scripts
./query_config --grids | grep -i kenya
```

Should show registered grid with description.

---

## Additional Technical Notes

### Memory Requirements
- Standard resolution: ~4 GB/core
- VR ne60x02: ~6 GB/core (50% more due to higher resolution)
- Use `ulimit -s unlimited` for stack size

### Job Scheduling
- **Queue:** `normal` for <24hr, `long` for >24hr
- **Priority:** Smaller jobs (≤8 nodes) schedule faster
- **Timing:** Submit overnight for better queue position

### Data Management
- Output: ~50 GB per simulation year (monthly history)
- Archive frequently to project storage
- Use compression for long-term archive: `nccopy -d 3`

### Debugging Tips
```bash
# Enable detailed logging
./xmlchange DEBUG=TRUE
./xmlchange INFO_DBUG=2

# Check specific component
cd run
grep -i "error\|warning" atm.log.*
```

---

## Performance Summary

### What Works Well
- ✅ Atmosphere-land coupling scales efficiently
- ✅ AMD Milan performance comparable to Intel on Derecho
- ✅ Cray MPI stable and efficient
- ✅ PIO works well with tuned settings

### Known Limitations
- ⚠️ GPU acceleration not yet available (CAM6 is CPU-only)
- ⚠️ Ocean coupling would reduce efficiency significantly
- ⚠️ Very high resolution (>0.0625°) may hit memory limits

### Future Optimization Opportunities
1. **Hybrid MPI+OpenMP** - May improve cache utilization
2. **Advanced I/O** - ADIOS2 backend for PIO
3. **Load Balancing** - Dynamic adjustment mid-run
4. **CAM7 Migration** - When GPU support arrives

---

## Reproducibility Checklist

For others attempting similar ports:

- [ ] Document exact CESM version and tag
- [ ] Save all XML configuration files
- [ ] Record module versions (`module list`)
- [ ] Archive successful build logs
- [ ] Document PE layout and rationale
- [ ] Save working compiler flags
- [ ] Note any system-specific quirks
- [ ] Test on minimal case before production

---

## Contact & Support

**Questions about this port:**  
Jan Göpel (jan.goepel@unibe.ch)

**CSCS Support:**  
help@cscs.ch

**CESM Community:**  
https://bb.cgd.ucar.edu

---

*Last Updated: November 2025*  
*Document maintained alongside active development*
