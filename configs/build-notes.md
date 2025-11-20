# Build Configuration Notes

**Compiler settings, build system configuration, and optimization details for CESM3 on Eiger.Alps**

---

## System Environment

### Hardware
- **Machine:** CSCS Eiger.Alps
- **Architecture:** AMD Milan (Zen 3)
- **Processors:** AMD EPYC 7763 64-Core
- **Cores/Node:** 128 (2 sockets × 64 cores)
- **Memory/Node:** 256 GB DDR4
- **Interconnect:** Cray Slingshot

### Software Stack
- **OS:** SLES 15 SP3 (Linux)
- **Scheduler:** Slurm
- **MPI:** Cray MPICH 8.1.x
- **Compilers:** Cray/GNU (default)
- **Modules:** Lmod system

---

## Module Configuration

### Standard Build Environment

```bash
module purge
module load cray-netcdf-hdf5parallel
module load cray-parallel-netcdf
module load cmake
```

**Rationale:**
- `cray-netcdf-hdf5parallel`: NetCDF4 with HDF5 parallel I/O support
- `cray-parallel-netcdf`: PnetCDF for MPI-IO operations
- `cmake`: Required by CIME build system

### Module Versions (October 2025)
```
Currently Loaded Modules:
  1) cray-mpich/8.1.25
  2) cray-hdf5-parallel/1.12.2.1
  3) cray-netcdf-hdf5parallel/4.9.0.1
  4) cray-parallel-netcdf/1.12.3.1
  5) cmake/3.26.3
```

---

## Compiler Configuration

### Machine Definition File

Location: `${CESM_ROOT}/cime/config/cesm/machines/config_machines.xml`

Key entries for Eiger:

```xml
<machine MACH="eiger">
  <DESC>CSCS Eiger.Alps AMD Milan system</DESC>
  <NODENAME_REGEX>eiger</NODENAME_REGEX>
  <OS>LINUX</OS>
  <COMPILERS>gnu,cray</COMPILERS>
  <MPILIBS>mpich</MPILIBS>
  
  <RUNDIR>$CIME_OUTPUT_ROOT/$CASE/run</RUNDIR>
  <EXEROOT>$CIME_OUTPUT_ROOT/$CASE/bld</EXEROOT>
  <DIN_LOC_ROOT>/project/common/cesm_inputdata</DIN_LOC_ROOT>
  
  <MAX_TASKS_PER_NODE>128</MAX_TASKS_PER_NODE>
  <MAX_MPITASKS_PER_NODE>128</MAX_MPITASKS_PER_NODE>
  
  <BATCH_SYSTEM>slurm</BATCH_SYSTEM>
  <SUPPORTED_BY>cscs-help</SUPPORTED_BY>
</machine>
```

### Compiler Flags (GNU)

Location: `${CESM_ROOT}/cime/config/cesm/machines/config_compilers.xml`

**Fortran Flags:**
```xml
<compiler COMPILER="gnu" MACH="eiger">
  <FFLAGS>
    <base>-O2 -march=znver3 -fno-second-underscore</base>
    <DEBUG>-g -fbacktrace -fbounds-check -ffpe-trap=invalid,zero,overflow</DEBUG>
    <OPT>-O2 -march=znver3</OPT>
  </FFLAGS>
  
  <FFLAGS_NOOPT>-O0</FFLAGS_NOOPT>
  
  <FIXEDFLAGS>-ffixed-form</FIXEDFLAGS>
  <FREEFLAGS>-ffree-form</FREEFLAGS>
</compiler>
```

**C Flags:**
```xml
<CFLAGS>
  <base>-O2 -march=znver3</base>
  <DEBUG>-g</DEBUG>
</CFLAGS>
```

**C++ Flags:**
```xml
<CXXFLAGS>
  <base>-O2 -march=znver3</base>
  <DEBUG>-g</DEBUG>
</CXXFLAGS>
```

### Flag Explanations

**`-O2`**: Moderate optimization, balances speed vs compilation time  
**`-march=znver3`**: AMD Zen 3 (Milan) specific optimizations  
**`-fno-second-underscore`**: Fortran name mangling compatibility  
**`-fbacktrace`**: Debug mode backtraces  
**`-fbounds-check`**: Array bounds checking (debug only)  

### Why Not -O3?

Initial tests with `-O3` showed:
- ❌ Occasional segfaults in ICE component
- ❌ Numerical instabilities in CLM
- ✅ Only ~3% speed improvement over `-O2`

**Decision:** Use `-O2` for reliability

---

## Library Paths

### NetCDF
```bash
NETCDF_PATH=/opt/cray/pe/netcdf-hdf5parallel/4.9.0.1/gnu/9.1
NETCDF_C_PATH=$NETCDF_PATH
NETCDF_FORTRAN_PATH=$NETCDF_PATH
```

### PnetCDF
```bash
PNETCDF_PATH=/opt/cray/pe/parallel-netcdf/1.12.3.1/gnu/9.1
```

### ESMF (if custom build)
```bash
ESMF_ROOT=/path/to/custom/esmf
ESMFMKFILE=$ESMF_ROOT/lib/esmf.mk
```

---

## Build Process

### 1. Configure Build

```bash
cd $CASE_ROOT

# Set build options
./xmlchange EXEROOT=$CASE_ROOT/bld
./xmlchange BUILD_COMPLETE=FALSE

# Compiler choice
./xmlchange COMPILER=gnu
```

### 2. Clean Build

```bash
# Remove previous build artifacts
./case.build --clean-all

# Build from scratch
./case.build 2>&1 | tee build.log
```

### 3. Build Output

Successful build produces:
```
$EXEROOT/cesm.exe      # Main executable (~150 MB)
$EXEROOT/lib/           # Component libraries
$EXEROOT/*/obj/         # Object files
```

### 4. Build Time

- **Clean build:** ~25-30 minutes
- **Incremental:** ~5-10 minutes
- **Parallel:** Uses `gmake -j 8` by default

---

## Component-Specific Settings

### CAM (Atmosphere)

**Physics Package:**
```bash
./xmlchange --append CAM_CONFIG_OPTS="-phys cam6"
```

**Resolution-specific:**
```xml
<!-- For VR grids -->
<CAM_CONFIG_OPTS>-phys cam6 -clubb_sgs</CAM_CONFIG_OPTS>
```

### CLM (Land)

**Satellite Phenology:**
```bash
./xmlchange CLM_BLDNML_OPTS="-bgc sp"
```

**Custom Surface Data:**
Use `user_nl_clm` for non-standard datasets

### CICE (Ice)

**Prescribed Ice:**
```bash
./xmlchange CICE_CONFIG_OPTS="-phys prescribed"
```

### PIO (Parallel I/O)

**Build Configuration:**
```xml
<PIO_VERSION>2</PIO_VERSION>
<PIO_TYPENAME>pnetcdf</PIO_TYPENAME>
<PIO_IOFORMAT>64bit_offset</PIO_IOFORMAT>
```

**Runtime Configuration:**
Set in `env_run.xml` (see technical-notes.md)

---

## Optimization Strategies

### 1. Memory Layout

**Stack Size:**
```bash
ulimit -s unlimited
```

**Huge Pages:**
```bash
# Optional, for large memory jobs
module load craype-hugepages2M
```

### 2. MPI Tuning

**Cray MPICH Settings:**
```bash
export MPICH_GNI_NUM_BUFS=512
export MPICH_GNI_NDREG_MAXSIZE=16777216
```

### 3. Threading

**Hybrid MPI+OpenMP:**
```bash
./xmlchange NTHRDS_ATM=2   # 2 threads per MPI task
./xmlchange NTHRDS_LND=1   # Pure MPI for land
```

**Current Configuration:** Pure MPI (NTHRDS=1) for all components

---

## Troubleshooting Build Issues

### Common Problems

**1. Missing NetCDF**
```
Error: netcdf.mod not found
```
**Solution:** Load `cray-netcdf-hdf5parallel` module

**2. ESMF Errors**
```
Error: ESMF_Initialize failed
```
**Solution:** Check ESMFMKFILE points to valid esmf.mk

**3. Out of Memory**
```
Killed (signal 9)
```
**Solution:** Reduce parallel make jobs:
```bash
./xmlchange GMAKE_J=4
```

**4. Undefined References**
```
undefined reference to `__netcdf_MOD_nf90_open'
```
**Solution:** Link order issue, check SLIBS in config_compilers.xml

### Debug Build

For troubleshooting:
```bash
./xmlchange DEBUG=TRUE
./case.build --clean
./case.build
```

Produces executable with symbols for gdb/valgrind

---

## Verification

### Post-Build Checks

```bash
# Executable exists and is recent
ls -lh bld/cesm.exe

# Check library dependencies
ldd bld/cesm.exe | grep -i netcdf

# Test run (if possible)
./case.submit --test
```

### Build Log Analysis

```bash
# Check for warnings
grep -i "warning" build.log | wc -l

# Check compilation times
grep "Compiling" build.log | tail -20

# Verify all components built
grep "Successfully built" build.log
```

---

## Performance Considerations

### Compiler Optimization Levels

| Level | Compile Time | Runtime | Stability | Recommendation |
|-------|--------------|---------|-----------|----------------|
| `-O0` | Fast | Slowest | Best | Debug only |
| `-O1` | Fast | Slow | Good | Early testing |
| `-O2` | Medium | Fast | Good | ✅ **Production** |
| `-O3` | Slow | Fastest | Risk | Avoid |

### AMD Milan Specific

**Vectorization:**
- `-march=znver3` enables AVX2 instructions
- ~10-15% speedup over generic `-march=x86-64`

**Cache Optimization:**
- L3 cache: 256 MB per socket
- Consider `-mtune=znver3` for fine-tuning

---

## Build Configuration Summary

### Recommended Settings (Production)

```bash
# Compiler
COMPILER=gnu

# Optimization
FFLAGS: -O2 -march=znver3
CFLAGS: -O2 -march=znver3

# Modules
cray-netcdf-hdf5parallel
cray-parallel-netcdf

# Threading
NTHRDS=1 (pure MPI)

# Build Jobs
GMAKE_J=8
```

### Settings to Avoid

- ❌ `-O3` (instability risk)
- ❌ Hybrid MPI+OpenMP (unless well-tested)
- ❌ `-march=native` (not portable)
- ❌ Aggressive loop unrolling flags

---

## Maintenance Notes

### When to Rebuild

- **Full rebuild:** After CESM source changes
- **Partial rebuild:** After namelist/XML changes (not needed)
- **Clean build:** After module/compiler changes

### Build Artifacts Location

```
$EXEROOT/
├── cesm.exe          # Main executable
├── lib/              # Component libraries
│   ├── libatm.a
│   ├── liblnd.a
│   └── ...
└── */obj/            # Object files (can delete after build)
```

---

*Last Updated: November 2025*  
*Configuration validated for CESM3 beta06 on Eiger.Alps*
