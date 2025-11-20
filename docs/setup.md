# VR-CESM Setup Guide for Eiger.Alps

**Complete instructions for porting and running Variable-Resolution CESM3 on CSCS Eiger**

---

## Prerequisites

### System Requirements
- **Account:** Active CSCS Eiger.Alps allocation
- **Access:** SSH access to Eiger login nodes
- **Storage:** ~500 GB for model, input data, and outputs
- **Queue:** Access to normal or long queue

### Knowledge Requirements
- Familiarity with Linux/Unix command line
- Basic understanding of CESM workflow
- Experience with HPC job submission (Slurm)

---

## Part 1: Initial Setup

### 1. Clone CESM3

```bash
# On Eiger login node
cd /users/YOUR_USERNAME
git clone -b cesm3.0.0-beta06 https://github.com/ESCOMP/CESM.git cesm_sandbox
cd cesm_sandbox
./manage_externals/checkout_externals
```

### 2. Configure Machine File

Check if Eiger is already configured:
```bash
cd cime/config/cesm/machines
ls config_machines.xml
grep "eiger" config_machines.xml
```

If not present, add Eiger configuration (see `configs/build-notes.md` for details).

### 3. Set Environment Variables

Create environment file:
```bash
cat > ~/set_env_cesm.sh << 'EOF'
#!/bin/bash
# CESM3 Environment for Eiger.Alps

# Module setup
module purge
module load cray-netcdf-hdf5parallel
module load cray-parallel-netcdf

# CESM paths
export CESM_ROOT=/users/YOUR_USERNAME/cesm_sandbox
export CIME_MODEL=cesm

# Grid files (if using custom VR grid)
export VRM_GRID_PATH=/path/to/your/vrgrids

echo "✓ CESM environment loaded"
EOF

chmod +x ~/set_env_cesm.sh
source ~/set_env_cesm.sh
```

---

## Part 2: Grid Setup (VR Configuration)

### Option A: Standard Grid (skip to Part 3)

If using standard CESM grids (e.g., ne30, f09), no additional setup needed.

### Option B: Custom VR Grid (Kenya ne60x02)

#### 1. Transfer Grid Files

```bash
# Create directory structure
mkdir -p /users/YOUR_USERNAME/vrgrids/ne60x02_Kenya

# Transfer from source system (Derecho)
# Files needed:
# - Mesh file (EXODUS.nc or SCRIP.nc)
# - Topography (USGS)
# - Surface data (CLM)
# - Initial conditions (CAM)
# - Land use timeseries (CLM)
```

#### 2. Convert Mesh Format (if needed)

If you have SCRIP format, convert to ESMF:
```bash
module load NCO
ncrename -v grid_center_lat,centerCoords \
         -v grid_center_lon,centerCoords \
         input_scrip.nc output_esmf.nc
# Additional NCO commands may be needed
```

#### 3. Register Grid

Edit `${CESM_ROOT}/cime/config/cesm/config_grids.xml`:
```xml
<domain name="ne60x02_Kenya">
  <nx>69120</nx>
  <ny>1</ny>
  <mesh>ne60x02_Kenya_EXODUS.nc</mesh>
  <desc>Variable-res ne60, 0.125 deg over Kenya</desc>
</domain>
```

Edit `${CESM_ROOT}/components/cam/bld/namelist_files/namelist_defaults_cam.xml`:
```xml
<se_mesh_file hgrid="ne60x02_Kenya">
  /path/to/your/vrgrids/ne60x02_Kenya/ne60x02_Kenya_EXODUS.nc
</se_mesh_file>
```

Verify registration:
```bash
cd ${CESM_ROOT}/cime/scripts
./query_config --grids | grep ne60x02
```

---

## Part 3: Create Test Case

### Standard Resolution Example

```bash
cd ${CESM_ROOT}/cime/scripts

./create_newcase \
  --case /users/YOUR_USERNAME/cases/test_f09 \
  --compset F2000climo \
  --res f09_g17 \
  --machine eiger \
  --run-unsupported

cd /users/YOUR_USERNAME/cases/test_f09
./case.setup
```

### VR Grid Example

```bash
./create_newcase \
  --case /users/YOUR_USERNAME/cases/test_kenya \
  --compset F2000climo \
  --res ne60x02_Kenya_g17 \
  --machine eiger \
  --run-unsupported

cd /users/YOUR_USERNAME/cases/test_kenya
```

---

## Part 4: Configure Case

### 1. Set PE Layout

Optimize based on node count and components:
```bash
# For 8-node configuration
./xmlchange NTASKS_ATM=512
./xmlchange NTASKS_LND=192
./xmlchange NTASKS_ICE=64
./xmlchange NTASKS_OCN=16
./xmlchange NTASKS_ROF=32
./xmlchange NTASKS_CPL=128
./xmlchange NTASKS_WAV=4
./xmlchange NTASKS_GLC=4

# Verify
./pelayout
```

### 2. Configure Run Parameters

```bash
# Run length
./xmlchange STOP_OPTION=ndays
./xmlchange STOP_N=30

# Output frequency
./xmlchange --append CAM_CONFIG_OPTS="-phys cam6"

# Job scheduling
./xmlchange JOB_WALLCLOCK_TIME=24:00:00
./xmlchange JOB_QUEUE=normal
```

### 3. Custom Namelists (VR Grid)

Create `user_nl_cam`:
```fortran
&cam_inparm
 se_mesh_file = '/path/to/ne60x02_Kenya_EXODUS.nc'
 bnd_topo = '/path/to/ne60x02_Kenya_topography.nc'
 ncdata = '/path/to/ne60x02_Kenya_initial_conditions.nc'
/
```

Create `user_nl_clm`:
```fortran
&clm_inparm
 fsurdat = '/path/to/ne60x02_Kenya_surface_data.nc'
 flanduse_timeseries = '/path/to/ne60x02_Kenya_landuse.nc'
/
```

### 4. Setup Case

```bash
./case.setup

# Check configuration
./case.st_archive --test
./check_input_data --download
```

---

## Part 5: Build Model

### 1. Clean Build (first time)

```bash
./case.build --clean-all
./case.build 2>&1 | tee build.log
```

Build takes ~20-30 minutes. Watch for errors in `build.log`.

### 2. Verify Build

```bash
ls -lh bld/cesm.exe
# Should see executable of ~100-200 MB
```

---

## Part 6: Submit Run

### 1. Check Job Script

```bash
cat case.run
# Verify Slurm directives look correct
```

### 2. Submit Job

```bash
./case.submit

# Monitor job
squeue -u $USER

# Check logs
tail -f run/cesm.log.* 
```

### 3. Monitor Progress

```bash
# Check timing
grep "simulated_years/day" run/cesm.log.*

# Check for errors
grep -i "error" run/*.log

# View latest output
ls -lht run/
```

---

## Part 7: Post-Processing

### 1. Check Outputs

```bash
cd archive
ls -lh atm/hist/
ls -lh lnd/hist/

# Verify netCDF files
ncdump -h atm/hist/CASE.cam.h0.2000-01.nc
```

### 2. Quick Diagnostics

```python
import xarray as xr
ds = xr.open_dataset('archive/atm/hist/CASE.cam.h0.2000-01.nc')
print(ds)
# Check for expected variables
```

### 3. Archive Data

```bash
# Transfer to project storage
cp -r archive/* /project/YOUR_PROJECT/data/
```

---

## Troubleshooting

### Build Fails

**Symptom:** Compilation errors  
**Solution:** 
- Check compiler modules loaded
- Verify library paths in config_machines.xml
- Look for specific error in build log

### Run Fails Immediately

**Symptom:** Job exits after seconds  
**Solution:**
- Check case.run Slurm directives match system
- Verify input data files exist
- Check cesm.log for error messages

### Poor Performance

**Symptom:** < 2 years/day on 12 nodes  
**Solution:**
- Check PE layout matches node count
- Verify I/O settings (PIO stride, aggregation)
- Monitor load balance: `./timing/*/cesm_timing_stats`

### Custom Grid Not Found

**Symptom:** "Grid not recognized" error  
**Solution:**
- Verify grid registration in config_grids.xml
- Check mesh file path absolute, not relative
- Ensure namelist defaults updated

---

## Optimization Tips

### 1. PE Layout Tuning

Monitor component costs:
```bash
grep "Run Time" run/cesm_timing.*
```

Adjust NTASKS to balance load:
- Increase NTASKS for slow components
- Keep total PEs ≤ 128 × number of nodes

### 2. I/O Configuration

Edit `env_run.xml`:
```bash
./xmlchange PIO_TYPENAME=pnetcdf
./xmlchange PIO_STRIDE=4
./xmlchange PIO_NUMIOTASKS=32
```

### 3. Restart Frequency

For long runs:
```bash
./xmlchange REST_N=365
./xmlchange REST_OPTION=ndays
```

---

## Production Workflow

### Batch Job Template

```bash
#!/bin/bash
#SBATCH --job-name=cesm_prod
#SBATCH --nodes=12
#SBATCH --time=48:00:00
#SBATCH --account=YOUR_ACCOUNT

cd /users/YOUR_USERNAME/cases/production_case
./case.submit
```

### Monitoring Script

```bash
#!/bin/bash
# monitor_runs.sh
while true; do
  squeue -u $USER
  tail -3 run/cesm.log.*
  sleep 300
done
```

---

## Additional Resources

- **CESM Documentation:** https://escomp.github.io/cesm/
- **CSCS User Portal:** https://user.cscs.ch
- **CESM Forum:** https://bb.cgd.ucar.edu
- **This Project:** See technical-notes.md for specific issues encountered

---

*Last Updated: November 2025*  
*Questions? Contact: jan.goepel@unibe.ch*
