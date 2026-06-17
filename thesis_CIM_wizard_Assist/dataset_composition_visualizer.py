#!/usr/bin/env python3
"""
Dataset Composition Visualizer
==============================

Generates comprehensive charts comparing dataset composition before and after curation.
Visualizes task type distribution, domain type distribution, complexity, and other key metrics.

Usage:
    python dataset_composition_visualizer.py \
        --merged ai4db/training_datasets/merged_dataset_phase4.jsonl \
        --curated ai4db/training_datasets/curated_q2sql/q2sql_train.jsonl \
        --output thesis/Figures/dataset_composition
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from matplotlib.gridspec import GridSpec

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Color palette
COLORS = {
    'merged': '#3498db',  # Blue
    'curated': '#2ecc71',  # Green
    'benchmark': '#9b59b6',  # Purple
    'diff': '#e74c3c'  # Red for differences
}
def build_palette(num_datasets: int) -> List:
    """Return a consistent palette for up to three datasets."""
    if num_datasets <= 0:
        return []
    base = [COLORS['merged'], COLORS['curated'], COLORS['benchmark']]
    if num_datasets <= len(base):
        return base[:num_datasets]
    extra = sns.color_palette("Set2", num_datasets - len(base))
    return base + extra

# Task type order (by frequency)
TASK_TYPE_ORDER = [
    'SQL_AGGREGATION', 'SIMPLE_SELECT', 'AMBIGUOUS', 'SPATIAL_JOIN',
    'SPATIAL_MEASUREMENT', 'OUT_OF_SCOPE', 'SPATIAL_PREDICATE',
    'SPATIAL_PROCESSING', 'SQL_JOIN', 'NESTED_QUERY', 'SPATIAL_ACCESSOR',
    'SPATIAL_CLUSTERING', 'MULTI_SQL_JOIN', 'RASTER_ANALYSIS',
    'RASTER_VECTOR', 'MULTI_SPATIAL_JOIN'
]

# Domain type order
DOMAIN_TYPE_ORDER = [
    'SINGLE_SCHEMA_CIM_VECTOR', 'AMBIGUOUS', 'OUT_OF_SCOPE',
    'MULTI_SCHEMA_WITH_CIM_VECTOR', 'SINGLE_SCHEMA_OTHER', 'MULTI_SCHEMA_COMPLEX'
]


def load_dataset(filepath: Path) -> List[Dict[str, Any]]:
    """Load JSONL dataset"""
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def extract_distributions(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract distribution statistics from samples"""
    stats = {
        'total': len(samples),
        'task_type': Counter(),
        'domain_type': Counter(),
        'task_complexity': Counter(),
        'domain_complexity': Counter(),
        'task_frequency': Counter(),
        'domain_frequency': Counter(),
        'question_tone': Counter(),
        'sample_dirtiness': Counter(),
        'spatial_functions': Counter()
    }
    
    for sample in samples:
        # Task type
        task_type = sample.get('task_type', 'UNKNOWN')
        stats['task_type'][task_type] += 1
        
        # Domain type
        domain_type = sample.get('domain_type', 'UNKNOWN')
        stats['domain_type'][domain_type] += 1
        
        # Complexity
        task_comp = sample.get('task_complexity', 1)
        domain_comp = sample.get('domain_complexity', 1)
        stats['task_complexity'][f"{task_comp}_Easy" if task_comp == 1 else 
                                 f"{task_comp}_Medium" if task_comp == 2 else 
                                 f"{task_comp}_Hard"] += 1
        stats['domain_complexity'][f"{domain_comp}_Easy" if domain_comp == 1 else 
                                   f"{domain_comp}_Medium" if domain_comp == 2 else 
                                   f"{domain_comp}_Hard"] += 1
        
        # Frequency
        task_freq = sample.get('task_frequency', 1)
        domain_freq = sample.get('domain_frequency', 1)
        stats['task_frequency'][f"{task_freq}_Very_Frequent" if task_freq == 1 else 
                                f"{task_freq}_Frequent" if task_freq == 2 else 
                                f"{task_freq}_Rare"] += 1
        stats['domain_frequency'][f"{domain_freq}_Very_Frequent" if domain_freq == 1 else 
                                  f"{domain_freq}_Frequent" if domain_freq == 2 else 
                                  f"{domain_freq}_Rare"] += 1
        
        # Question tone
        question_tone = sample.get('question_tone', 'UNKNOWN')
        stats['question_tone'][question_tone] += 1
        
        # Sample dirtiness
        sample_dirtiness = sample.get('sample_dirtiness', 'CLEAN')
        stats['sample_dirtiness'][sample_dirtiness] += 1
        
        # Spatial functions
        spatial_funcs = sample.get('spatial_functions', [])
        for func in spatial_funcs:
            stats['spatial_functions'][func] += 1
    
    return stats


def create_summary_comparison(dataset_stats: List[tuple], output_path: Path):
    """Create summary comparison chart"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Dataset Composition: Before vs After Curation', fontsize=16, fontweight='bold')
    
    # 1. Total samples
    ax = axes[0, 0]
    dataset_labels = [label for label, _ in dataset_stats]
    values = [stats['total'] for _, stats in dataset_stats]
    palette = build_palette(len(dataset_stats))
    bars = ax.bar(dataset_labels, values, color=palette,
                  alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Number of Samples', fontweight='bold')
    ax.set_title('Total Samples', fontweight='bold', pad=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for (label, _), bar, val in zip(dataset_stats, bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # 2. Sample retention
    ax = axes[0, 1]
    merged_stats = dataset_stats[0][1]
    train_stats = dataset_stats[1][1] if len(dataset_stats) > 1 else merged_stats
    retention_rate = train_stats['total'] / merged_stats['total'] * 100 if merged_stats['total'] else 0
    categories = ['Train Split', 'Val/Test Split']
    values = [train_stats['total'], max(merged_stats['total'] - train_stats['total'], 0)]
    colors = [COLORS['curated'], COLORS['diff']]
    wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors, autopct='%1.1f%%',
                                       startangle=90, textprops={'fontweight': 'bold', 'fontsize': 11})
    ax.set_title(f'Train vs Val/Test Split\n({retention_rate:.1f}% train)', fontweight='bold', pad=10)
    
    # 3. Task categories
    ax = axes[1, 0]
    width = 0.5
    x = np.arange(len(dataset_stats))
    spatial_counts = []
    non_spatial_counts = []
    for _, stats in dataset_stats:
        spatial = sum(stats['task_type'][t] for t in stats['task_type']
                        if 'SPATIAL' in t or 'RASTER' in t)
        spatial_counts.append(spatial)
        non_spatial_counts.append(max(stats['total'] - spatial, 0))
    
    ax.bar(x, spatial_counts, width,
           label='Spatial/Raster', color='#9b59b6', alpha=0.8, edgecolor='black', linewidth=1)
    ax.bar(x, non_spatial_counts, width,
           bottom=spatial_counts,
           label='Non-Spatial SQL', color='#f39c12', alpha=0.8, edgecolor='black', linewidth=1)
    ax.set_ylabel('Number of Samples', fontweight='bold')
    ax.set_title('Task Categories', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(dataset_labels)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 4. Sample dirtiness
    ax = axes[1, 1]
    dirtiness_categories = ['CLEAN', 'AMBIGUOUS', 'OUT_OF_SCOPE']
    x = np.arange(len(dirtiness_categories))
    width = 0.8 / len(dataset_stats)
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        values = [stats['sample_dirtiness'].get(cat, 0) for cat in dirtiness_categories]
        color = palette[idx] if idx < len(palette) else sns.color_palette("Set2")[idx % len(dataset_stats)]
        ax.bar(offsets, values, width, label=label, color=color,
               alpha=0.85, edgecolor='black', linewidth=1)
    ax.set_ylabel('Number of Samples', fontweight='bold')
    ax.set_title('Sample Quality Distribution', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(dirtiness_categories, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path / '01_summary_comparison.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Saved: 01_summary_comparison.png")


def create_task_type_comparison(dataset_stats: List[tuple], output_path: Path):
    """Create task type distribution comparison"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Get all task types and sort by merged count
    primary_stats = dataset_stats[0][1]
    all_task_types = set()
    for _, stats in dataset_stats:
        all_task_types |= set(stats['task_type'].keys())
    task_types = sorted(all_task_types, key=lambda x: primary_stats['task_type'].get(x, 0), reverse=True)
    
    # Prepare data
    x = np.arange(len(task_types))
    width = 0.8 / len(dataset_stats)
    palette = build_palette(len(dataset_stats))
    bars_collection = []
    
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['task_type'].get(t, 0) / stats['total'] * 100) if stats['total'] else 0 for t in task_types]
        bars = ax.bar(offsets, pct, width, label=label,
                      color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
        bars_collection.append(bars)
    
    ax.set_xlabel('Task Type', fontweight='bold', fontsize=12)
    ax.set_ylabel('Percentage of Samples (%)', fontweight='bold', fontsize=12)
    ax.set_title('Task Type Distribution Comparison', fontweight='bold', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(task_types, rotation=45, ha='right', fontsize=9)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    max_height = max((bar.get_height() for bars in bars_collection for bar in bars), default=1)
    ax.set_ylim(0, max_height * 1.15 if max_height else 1)
    
    for bars in bars_collection:
        for bar in bars:
            height = bar.get_height()
            if height > 1:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path / '02_task_type_comparison.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Saved: 02_task_type_comparison.png")


def create_domain_type_comparison(dataset_stats: List[tuple], output_path: Path):
    """Create domain type distribution comparison"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all domain types
    primary_stats = dataset_stats[0][1]
    all_domain_types = set()
    for _, stats in dataset_stats:
        all_domain_types |= set(stats['domain_type'].keys())
    domain_types = sorted(all_domain_types, key=lambda x: primary_stats['domain_type'].get(x, 0), reverse=True)
    
    # Prepare data
    x = np.arange(len(domain_types))
    width = 0.8 / len(dataset_stats)
    palette = build_palette(len(dataset_stats))
    bars_collection = []
    
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['domain_type'].get(d, 0) / stats['total'] * 100) if stats['total'] else 0 for d in domain_types]
        bars = ax.bar(offsets, pct, width, label=label,
                      color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
        bars_collection.append(bars)
    
    ax.set_xlabel('Domain Type', fontweight='bold', fontsize=12)
    ax.set_ylabel('Percentage of Samples (%)', fontweight='bold', fontsize=12)
    ax.set_title('Domain Type Distribution Comparison', fontweight='bold', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(domain_types, rotation=15, ha='right', fontsize=10)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    max_height = max((bar.get_height() for bars in bars_collection for bar in bars), default=1)
    ax.set_ylim(0, max_height * 1.15 if max_height else 1)
    
    for bars in bars_collection:
        for bar in bars:
            height = bar.get_height()
            if height > 0.5:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path / '03_domain_type_comparison.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Saved: 03_domain_type_comparison.png")


def create_complexity_comparison(dataset_stats: List[tuple], output_path: Path):
    """Create complexity distribution comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Complexity Distribution Comparison', fontsize=16, fontweight='bold')
    
    # Task complexity
    ax = axes[0, 0]
    task_comp_order = ['1_Easy', '2_Medium', '3_Hard']
    x = np.arange(len(task_comp_order))
    width = 0.8 / len(dataset_stats)
    palette = build_palette(len(dataset_stats))
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['task_complexity'].get(t, 0) / stats['total'] * 100) if stats['total'] else 0 for t in task_comp_order]
        ax.bar(offsets, pct, width, label=label,
               color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Task Complexity', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Domain complexity
    ax = axes[0, 1]
    domain_comp_order = ['1_Easy', '2_Medium', '3_Hard']
    x = np.arange(len(domain_comp_order))
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['domain_complexity'].get(d, 0) / stats['total'] * 100) if stats['total'] else 0 for d in domain_comp_order]
        ax.bar(offsets, pct, width, label=label if idx == 0 else None,
               color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Domain Complexity', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Task frequency
    ax = axes[1, 0]
    task_freq_order = ['1_Very_Frequent', '2_Frequent', '3_Rare']
    x = np.arange(len(task_freq_order))
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['task_frequency'].get(t, 0) / stats['total'] * 100) if stats['total'] else 0 for t in task_freq_order]
        ax.bar(offsets, pct, width, label=label if idx == 0 else None,
               color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Task Frequency', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['Very Frequent', 'Frequent', 'Rare'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Domain frequency
    ax = axes[1, 1]
    domain_freq_order = ['1_Very_Frequent', '2_Frequent', '3_Rare']
    x = np.arange(len(domain_freq_order))
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['domain_frequency'].get(d, 0) / stats['total'] * 100) if stats['total'] else 0 for d in domain_freq_order]
        ax.bar(offsets, pct, width, label=label if idx == 0 else None,
               color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Domain Frequency', fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['Very Frequent', 'Frequent', 'Rare'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path / '04_complexity_comparison.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Saved: 04_complexity_comparison.png")


def create_question_tone_comparison(dataset_stats: List[tuple], output_path: Path):
    """Create question tone distribution comparison"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Get all question tones
    primary_stats = dataset_stats[0][1]
    all_tones = set()
    for _, stats in dataset_stats:
        all_tones |= set(stats['question_tone'].keys())
    tones = sorted(all_tones, key=lambda x: primary_stats['question_tone'].get(x, 0), reverse=True)
    
    # Prepare data
    x = np.arange(len(tones))
    width = 0.8 / len(dataset_stats)
    palette = build_palette(len(dataset_stats))
    bars_collection = []
    
    for idx, (label, stats) in enumerate(dataset_stats):
        offsets = x + (idx - (len(dataset_stats) - 1) / 2) * width
        pct = [(stats['question_tone'].get(t, 0) / stats['total'] * 100) if stats['total'] else 0 for t in tones]
        bars = ax.bar(offsets, pct, width, label=label,
                      color=palette[idx], alpha=0.85, edgecolor='black', linewidth=1)
        bars_collection.append(bars)
    
    ax.set_xlabel('Question Tone', fontweight='bold', fontsize=12)
    ax.set_ylabel('Percentage of Samples (%)', fontweight='bold', fontsize=12)
    ax.set_title('Question Tone Distribution Comparison', fontweight='bold', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(tones, fontsize=10)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    max_height = max((bar.get_height() for bars in bars_collection for bar in bars), default=1)
    ax.set_ylim(0, max_height * 1.15 if max_height else 1)
    
    for bars in bars_collection:
        for bar in bars:
            height = bar.get_height()
            if height > 1:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path / '05_question_tone_comparison.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Saved: 05_question_tone_comparison.png")


def main():
    parser = argparse.ArgumentParser(
        description='Generate dataset composition visualization charts',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--merged', type=str, required=True,
                       help='Path to merged dataset (before curation) JSONL file')
    parser.add_argument('--curated', type=str, required=True,
                       help='Path to curated training dataset (after curation) JSONL file')
    parser.add_argument('--benchmark', type=str,
                       help='Optional benchmark dataset JSONL to compare stratification')
    parser.add_argument('--output', type=str, default='thesis/Figures',
                       help='Output directory for charts (default: thesis/Figures)')
    
    args = parser.parse_args()
    
    merged_path = Path(args.merged)
    curated_path = Path(args.curated)
    benchmark_path = Path(args.benchmark) if args.benchmark else None
    output_path = Path(args.output)
    
    # Validate inputs
    if not merged_path.exists():
        print(f"Error: Merged dataset not found: {merged_path}")
        return
    if not curated_path.exists():
        print(f"Error: Curated dataset not found: {curated_path}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("DATASET COMPOSITION VISUALIZER")
    print("="*80)
    print(f"\nLoading datasets...")
    print(f"  Merged: {merged_path}")
    print(f"  Curated: {curated_path}")
    if benchmark_path:
        print(f"  Benchmark: {benchmark_path}")
    print(f"  Output: {output_path}")
    
    # Load datasets
    print("\n[1/2] Loading datasets...")
    merged_samples = load_dataset(merged_path)
    curated_samples = load_dataset(curated_path)
    benchmark_samples = []
    if benchmark_path:
        if benchmark_path.exists():
            benchmark_samples = load_dataset(benchmark_path)
            print(f"  ✓ Loaded {len(benchmark_samples):,} benchmark samples")
        else:
            print(f"  ⚠ Benchmark dataset not found: {benchmark_path}")
    print(f"  ✓ Loaded {len(merged_samples):,} merged samples")
    print(f"  ✓ Loaded {len(curated_samples):,} curated samples")
    
    # Extract distributions
    print("\n[2/2] Extracting distributions...")
    merged_stats = extract_distributions(merged_samples)
    curated_stats = extract_distributions(curated_samples)
    benchmark_stats = extract_distributions(benchmark_samples) if benchmark_samples else None
    print(f"  ✓ Extracted statistics")
    
    dataset_stats = [
        ('Merged Dataset (Full)', merged_stats),
        ('Train Split (70%)', curated_stats)
    ]
    if benchmark_stats:
        dataset_stats.append(('Benchmark (FTv3)', benchmark_stats))
    
    print("\nNote: 'Train Split (70%)' represents the stratified training partition produced by curator.py.")
    print("The difference between merged and train counts corresponds to validation/test splits, not filtering.")
    
    # Generate charts
    print("\n" + "="*80)
    print("GENERATING CHARTS")
    print("="*80)
    
    create_summary_comparison(dataset_stats, output_path)
    create_task_type_comparison(dataset_stats, output_path)
    create_domain_type_comparison(dataset_stats, output_path)
    create_complexity_comparison(dataset_stats, output_path)
    create_question_tone_comparison(dataset_stats, output_path)
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print(f"\nGenerated charts saved to: {output_path}")
    print(f"\nCharts generated:")
    print(f"  1. 01_summary_comparison.png - Overview comparison")
    print(f"  2. 02_task_type_comparison.png - Task type distribution")
    print(f"  3. 03_domain_type_comparison.png - Domain type distribution")
    print(f"  4. 04_complexity_comparison.png - Complexity distributions")
    print(f"  5. 05_question_tone_comparison.png - Question tone distribution")


if __name__ == '__main__':
    main()

