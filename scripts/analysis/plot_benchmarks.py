#!/usr/bin/env python3
"""
plot_benchmarks.py
Visualize CESM3 scaling performance on CSCS Eiger from actual benchmark runs.

Usage:
    python plot_benchmarks.py [--output OUTPUT_DIR]

Generates:
    - scaling_throughput.png: Throughput vs nodes
    - scaling_efficiency.png: Parallel efficiency vs nodes
    - scaling_cost.png: Cost (NH/year) vs nodes
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse

# Actual benchmark data from October 2025 runs
# Format: (nodes, years_per_day, seconds_per_day)
BENCHMARK_DATA = [
    (4, 4.51, 52.485),
    (6, 6.67, 35.502),
    (8, 8.35, 28.363),
    (12, 11.16, 21.209),
]

def calculate_metrics(data):
    """
    Calculate derived metrics from benchmark data.
    
    Returns:
        nodes: array of node counts
        throughput: simulated years/day
        speedup: relative to 4-node baseline
        efficiency: parallel efficiency (%)
        nh_per_year: node-hours per simulation year
    """
    nodes = np.array([d[0] for d in data])
    throughput = np.array([d[1] for d in data])
    
    # Speedup relative to 4-node baseline
    baseline_throughput = throughput[0]
    speedup = throughput / baseline_throughput
    
    # Parallel efficiency
    baseline_nodes = nodes[0]
    node_ratio = nodes / baseline_nodes
    efficiency = (speedup / node_ratio) * 100
    
    # Node-hours per simulation year
    nh_per_year = (24.0 / throughput) * nodes
    
    return nodes, throughput, speedup, efficiency, nh_per_year


def plot_throughput(nodes, throughput, output_dir):
    """Plot throughput scaling."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Actual data
    ax.plot(nodes, throughput, 'o-', linewidth=2, markersize=10,
            label='Actual Performance', color='#2E86AB')
    
    # Ideal linear scaling
    ideal = throughput[0] * (nodes / nodes[0])
    ax.plot(nodes, ideal, '--', linewidth=1.5, 
            label='Ideal Linear Scaling', color='#A23B72', alpha=0.6)
    
    # Annotations
    for n, t in zip(nodes, throughput):
        ax.annotate(f'{t:.2f}', 
                   xy=(n, t), 
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor='gray', alpha=0.7))
    
    ax.set_xlabel('Number of Nodes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (simulated years/day)', fontsize=12, fontweight='bold')
    ax.set_title('CESM3 Scaling: Model Throughput on Eiger.Alps', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    ax.set_xticks(nodes)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scaling_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: scaling_throughput.png")


def plot_efficiency(nodes, speedup, efficiency, output_dir):
    """Plot parallel efficiency and speedup."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left plot: Speedup
    ax1.plot(nodes, speedup, 'o-', linewidth=2, markersize=10,
            label='Actual Speedup', color='#2E86AB')
    
    ideal_speedup = nodes / nodes[0]
    ax1.plot(nodes, ideal_speedup, '--', linewidth=1.5,
            label='Ideal Speedup', color='#A23B72', alpha=0.6)
    
    for n, s in zip(nodes, speedup):
        ax1.annotate(f'{s:.2f}x', 
                    xy=(n, s), 
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9)
    
    ax1.set_xlabel('Number of Nodes', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Speedup (relative to 4 nodes)', fontsize=12, fontweight='bold')
    ax1.set_title('Strong Scaling: Speedup', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11)
    ax1.set_xticks(nodes)
    
    # Right plot: Efficiency
    ax2.plot(nodes, efficiency, 'o-', linewidth=2, markersize=10,
            label='Parallel Efficiency', color='#F18F01')
    ax2.axhline(y=100, linestyle='--', color='#A23B72', linewidth=1.5,
               alpha=0.6, label='Ideal (100%)')
    ax2.axhline(y=80, linestyle=':', color='gray', linewidth=1,
               alpha=0.5, label='80% Threshold')
    
    # Color-code efficiency annotations
    for n, e in zip(nodes, efficiency):
        color = '#2D6A4F' if e >= 90 else '#F77F00' if e >= 80 else '#D62828'
        ax2.annotate(f'{e:.0f}%', 
                    xy=(n, e), 
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    color=color,
                    fontweight='bold')
    
    ax2.set_xlabel('Number of Nodes', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Parallel Efficiency (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Strong Scaling: Efficiency', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=11)
    ax2.set_xticks(nodes)
    ax2.set_ylim(70, 105)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scaling_efficiency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: scaling_efficiency.png")


def plot_cost(nodes, nh_per_year, output_dir):
    """Plot cost in node-hours per simulation year."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#2D6A4F', '#52B788', '#95D5B2', '#B7E4C7']
    bars = ax.bar(nodes, nh_per_year, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=1.5)
    
    # Annotate bars
    for bar, nh in zip(bars, nh_per_year):
        height = bar.get_height()
        ax.annotate(f'{nh:.1f}', 
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5),
                   textcoords='offset points',
                   ha='center',
                   fontsize=11,
                   fontweight='bold')
    
    # Add overhead percentage annotation
    baseline_nh = nh_per_year[0]
    for i, (n, nh) in enumerate(zip(nodes[1:], nh_per_year[1:]), 1):
        overhead = ((nh - baseline_nh) / baseline_nh) * 100
        ax.annotate(f'+{overhead:.0f}% overhead', 
                   xy=(n, nh),
                   xytext=(0, -20),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   style='italic',
                   color='#6C757D')
    
    ax.set_xlabel('Number of Nodes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Node-Hours per Simulation Year', fontsize=12, fontweight='bold')
    ax.set_title('Resource Cost: Node-Hours Required per Simulation Year', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_xticks(nodes)
    ax.set_ylim(0, max(nh_per_year) * 1.15)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scaling_cost.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: scaling_cost.png")


def create_summary_figure(nodes, throughput, efficiency, nh_per_year, output_dir):
    """Create a comprehensive 3-panel summary figure."""
    fig = plt.figure(figsize=(18, 6))
    gs = fig.add_gridspec(1, 3, hspace=0.3, wspace=0.3)
    
    # Panel 1: Throughput
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(nodes, throughput, 'o-', linewidth=2.5, markersize=12,
            color='#2E86AB', markeredgecolor='white', markeredgewidth=2)
    for n, t in zip(nodes, throughput):
        ax1.annotate(f'{t:.2f}', xy=(n, t), xytext=(0, 8),
                    textcoords='offset points', ha='center', fontsize=10)
    ax1.set_xlabel('Nodes', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Years/Day', fontsize=11, fontweight='bold')
    ax1.set_title('Throughput', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(nodes)
    
    # Panel 2: Efficiency
    ax2 = fig.add_subplot(gs[0, 1])
    colors_eff = ['#2D6A4F' if e >= 90 else '#F77F00' if e >= 80 else '#D62828' 
                  for e in efficiency]
    bars = ax2.bar(nodes, efficiency, color=colors_eff, alpha=0.8,
                   edgecolor='black', linewidth=1.5)
    ax2.axhline(y=80, linestyle='--', color='gray', linewidth=1, alpha=0.6)
    for bar, e in zip(bars, efficiency):
        ax2.annotate(f'{e:.0f}%', 
                    xy=(bar.get_x() + bar.get_width() / 2, e),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Nodes', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Efficiency (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Parallel Efficiency', fontsize=12, fontweight='bold')
    ax2.set_ylim(70, 105)
    ax2.set_xticks(nodes)
    
    # Panel 3: Cost
    ax3 = fig.add_subplot(gs[0, 2])
    bars = ax3.bar(nodes, nh_per_year, color='#52B788', alpha=0.8,
                   edgecolor='black', linewidth=1.5)
    for bar, nh in zip(bars, nh_per_year):
        ax3.annotate(f'{nh:.1f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, nh),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', fontsize=10, fontweight='bold')
    ax3.set_xlabel('Nodes', fontsize=11, fontweight='bold')
    ax3.set_ylabel('NH/Year', fontsize=11, fontweight='bold')
    ax3.set_title('Resource Cost', fontsize=12, fontweight='bold')
    ax3.set_xticks(nodes)
    ax3.set_ylim(0, max(nh_per_year) * 1.15)
    
    fig.suptitle('CESM3 Scaling Performance Summary - Eiger.Alps', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig(output_dir / 'scaling_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: scaling_summary.png")


def main():
    parser = argparse.ArgumentParser(
        description='Generate CESM3 benchmark scaling plots'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='.',
        help='Output directory for plots (default: current directory)'
    )
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("CESM3 Benchmark Visualization Tool")
    print("="*60)
    print(f"\nData from {len(BENCHMARK_DATA)} benchmark runs:")
    for nodes, ypd, spd in BENCHMARK_DATA:
        print(f"  - {nodes:2d} nodes: {ypd:5.2f} years/day ({spd:.1f} sec/day)")
    
    # Calculate metrics
    nodes, throughput, speedup, efficiency, nh_per_year = calculate_metrics(
        BENCHMARK_DATA
    )
    
    print(f"\nGenerating plots in: {output_dir.absolute()}")
    print("-" * 60)
    
    # Generate plots
    plot_throughput(nodes, throughput, output_dir)
    plot_efficiency(nodes, speedup, efficiency, output_dir)
    plot_cost(nodes, nh_per_year, output_dir)
    create_summary_figure(nodes, throughput, efficiency, nh_per_year, output_dir)
    
    print("-" * 60)
    print("✓ All plots generated successfully!")
    print("="*60 + "\n")
    
    # Print summary statistics
    print("Summary Statistics:")
    print(f"  Best efficiency:  {max(efficiency):.1f}% ({nodes[np.argmax(efficiency)]} nodes)")
    print(f"  Best throughput:  {max(throughput):.2f} years/day ({nodes[np.argmax(throughput)]} nodes)")
    print(f"  Lowest cost:      {min(nh_per_year):.1f} NH/year ({nodes[np.argmin(nh_per_year)]} nodes)")
    print(f"  12-node speedup:  {speedup[-1]:.2f}x (efficiency: {efficiency[-1]:.0f}%)")
    print()


if __name__ == '__main__':
    main()
