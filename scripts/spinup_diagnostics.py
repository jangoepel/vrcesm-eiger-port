#!/usr/bin/env python3
"""
spinup_diagnostics.py
Automated monitoring and diagnostics for CESM spin-up runs

Monitors key climate variables during long spin-up simulations to detect:
- Equilibration progress
- Model drift
- Outliers or instabilities

Usage:
    python spinup_diagnostics.py --case /path/to/case --years 10
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import sys

def check_equilibration(ds, var_name, threshold=0.01):
    """
    Check if variable has reached equilibrium based on trend analysis.
    
    Args:
        ds: xarray Dataset
        var_name: Variable name to check
        threshold: Max acceptable trend (units/year)
    
    Returns:
        bool: True if equilibrated, False otherwise
    """
    if var_name not in ds.variables:
        print(f"Warning: Variable {var_name} not found")
        return None
    
    var = ds[var_name]
    
    # Calculate annual means
    annual_mean = var.resample(time='1Y').mean()
    
    # Linear trend
    years = np.arange(len(annual_mean))
    trend = np.polyfit(years, annual_mean.values, 1)[0]
    
    equilibrated = abs(trend) < threshold
    
    return equilibrated, trend, annual_mean

def plot_timeseries(annual_data, var_name, output_dir):
    """Plot time series of variable with trend line."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    years = np.arange(len(annual_data))
    ax.plot(years, annual_data.values, 'o-', label='Annual Mean')
    
    # Trend line
    z = np.polyfit(years, annual_data.values, 1)
    p = np.poly1d(z)
    ax.plot(years, p(years), '--', label=f'Trend: {z[0]:.4f}/year', color='red')
    
    ax.set_xlabel('Year')
    ax.set_ylabel(f'{var_name}')
    ax.set_title(f'{var_name} - Spin-up Progress')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'{var_name}_spinup.png', dpi=150)
    plt.close()
    
    print(f"  → Saved plot: {var_name}_spinup.png")

def main():
    parser = argparse.ArgumentParser(description='CESM spin-up diagnostics')
    parser.add_argument('--case', required=True, help='Path to case directory')
    parser.add_argument('--years', type=int, default=10, 
                       help='Number of years to analyze')
    parser.add_argument('--output', default='.', 
                       help='Output directory for plots')
    args = parser.parse_args()
    
    case_dir = Path(args.case)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Find history files
    atm_hist = case_dir / 'archive' / 'atm' / 'hist'
    lnd_hist = case_dir / 'archive' / 'lnd' / 'hist'
    
    if not atm_hist.exists():
        print(f"Error: Cannot find atmosphere history files in {atm_hist}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("CESM Spin-up Diagnostics")
    print("="*60)
    print(f"Case: {case_dir}")
    print(f"Years: {args.years}")
    print("-"*60)
    
    # Key variables to monitor
    atm_vars = ['TS', 'PRECT', 'FLNT']  # Surface temp, precip, outgoing LW
    lnd_vars = ['TSA', 'GPP', 'TLAI']   # 2m temp, GPP, LAI
    
    # Analyze atmosphere
    print("\nAnalyzing atmosphere variables...")
    atm_files = sorted(atm_hist.glob('*.cam.h0.*.nc'))[:args.years*12]
    if atm_files:
        ds_atm = xr.open_mfdataset(atm_files, combine='by_coords')
        
        for var in atm_vars:
            if var in ds_atm:
                equilibrated, trend, annual = check_equilibration(ds_atm, var)
                status = "✓ Equilibrated" if equilibrated else "⚠ Still trending"
                print(f"  {var}: {status} (trend: {trend:.6f}/year)")
                plot_timeseries(annual, var, output_dir)
    else:
        print("  No atmosphere files found")
    
    # Analyze land
    print("\nAnalyzing land variables...")
    lnd_files = sorted(lnd_hist.glob('*.clm2.h0.*.nc'))[:args.years*12]
    if lnd_files:
        ds_lnd = xr.open_mfdataset(lnd_files, combine='by_coords')
        
        for var in lnd_vars:
            if var in ds_lnd:
                equilibrated, trend, annual = check_equilibration(ds_lnd, var)
                status = "✓ Equilibrated" if equilibrated else "⚠ Still trending"
                print(f"  {var}: {status} (trend: {trend:.6f}/year)")
                plot_timeseries(annual, var, output_dir)
    else:
        print("  No land files found")
    
    print("\n" + "="*60)
    print(f"Diagnostics complete. Plots saved to: {output_dir.absolute()}")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
