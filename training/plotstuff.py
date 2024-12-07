#!/usr/bin/python3

import argparse
import json
import math
from pathlib import Path
import matplotlib.pyplot as plt
import os
from collections import defaultdict
import sys

metrics_to_plot = [
    'p0loss',
    'p1loss',
    'p0softloss',
    'vloss',
    'tdvloss1',
    'tdsloss',
    'smloss',
    'leadloss',
    'sbcdfloss',
    'sbpdfloss',
    'oloss',
    'evstloss',
    'esstloss',
    'pacc1',
    'sloss',
    'fploss',
    'vtimeloss',
    'skloss',
    'gnorm_batch',
    'vsquare',
    'norm_normal_batch',
    'norm_normal_gamma_batch',
    'norm_output_batch',
    'norm_noreg_batch',
    'norm_output_noreg_batch',
    'pslr_batch',
    'wdnormal_batch',
]

nsamp_range = (100_000, 1_000_000_000)
ewma_log_scale = 1.0 / 3000.0

nan = float('nan')

def process_file(f, run_name, which_plot, data):
    """Read from f and accumulate the data into data[run_name]"""

    data[run_name] = {
        'nsamps': [],
        'values': defaultdict(list)
    }

    data_sums = defaultdict(float)
    data_weights = defaultdict(float)
    prev_log_nsamp = None
    for line in f:
        try:
            point = json.loads(line)
        except json.decoder.JSONDecodeError:
            continue
        if which_plot == "val":
            point["nsamp"] = point["nsamp_train"]

        if nsamp_range[0] <= point['nsamp'] <= nsamp_range[1]:
            data[run_name]['nsamps'].append(point['nsamp'])

            if ewma_log_scale is not None and ewma_log_scale > 0:
                log_nsamp = math.log(1 + point['nsamp'])
                if prev_log_nsamp is not None:
                    diff = log_nsamp - prev_log_nsamp
                    if diff > 0:
                        factor = math.exp(-diff / ewma_log_scale)
                        for key in data_sums:
                            data_sums[key] *= factor
                            data_weights[key] *= factor
                prev_log_nsamp = log_nsamp

                for metric in metrics_to_plot:
                    data_sums[metric] += nan if metric not in point else point[metric]
                    data_weights[metric] += 1.0

                for metric in metrics_to_plot:
                    data[run_name]['values'][metric].append(data_sums[metric] / data_weights[metric])

                for metric in metrics_to_plot:
                    if not math.isfinite(data_sums[metric]):
                        data_sums[metric] = 0.0
                        data_weights[metric] = 0.0
            else:
                for metric in metrics_to_plot:
                    data[run_name]['values'][metric].append(point[metric])


def main():
    parser = argparse.ArgumentParser(description='Process metrics files from all modelds trained for a run')
    parser.add_argument('-base-dir', required=True, help='Base directory for the whole training run')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-train', action='store_true', help='Process training metrics')
    group.add_argument('-val', action='store_true', help='Process validation metrics')

    args = parser.parse_args()

    # Determine which metrics file to look for based on arguments
    which_plot = "train" if args.train else "val"
    base_path = Path(args.base_dir)
    base_train_path = base_path / "train"

    if not base_path.exists():
        print(f"Error: Base directory '{args.base_dir}' does not exist")
        return 1
    if not base_train_path.exists():
        print(f"Error: Training directory '{args.base_train_dir}' within base directory does not exist")
        return 1

    found_files = False

    data = {}
    for run_dir in base_train_path.iterdir():
        if not run_dir.is_dir():
            continue

        metrics_path = run_dir / f"metrics_{which_plot}.json"
        if metrics_path.exists():
            found_files = True
            run_name = run_dir.name
            try:
                with open(metrics_path, 'r') as f:
                    print(f"Loading {metrics_path}",flush=True)
                    process_file(f, run_name, which_plot, data)
                    print(f"Loaded {metrics_path}",flush=True)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {metrics_path}")
            except Exception as e:
                print(f"Error processing {metrics_path}: {str(e)}")

    if not found_files:
        print(f"Warning: No metrics files found in any subdirectories of {args.base_dir}")
        return 1

    # Plot
    plt.rcParams['figure.figsize'] = [16, 10] # Bigger plots

    for metric in metrics_to_plot:
        fig, ax = plt.subplots()
        ax.set_title(metric)
        ax.set_xlabel('nsamp')
        ax.set_ylabel(metric)
        ax.set_xscale('log')

        ax.xaxis.grid(True, which='major')
        ax.yaxis.grid(True, which='major')
        ax.xaxis.grid(True, which='minor', alpha=0.2)
        ax.yaxis.grid(True, which='minor', alpha=0.2)

        if metric == "esstloss":
            ax.set_ylim(ymin=None, ymax=0.1)

        for run_name in data:
            ax.plot(data[run_name]['nsamps'], data[run_name]['values'][metric], label=run_name, linewidth=0.5)

        ax.legend()
        print(f"Writing {metric}.png")
        os.makedirs("plot", exist_ok=True)
        plt.savefig(f'plot/{metric}.png')

if __name__ == '__main__':
    exit(main())
