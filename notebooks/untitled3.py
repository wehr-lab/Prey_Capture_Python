import tkinter as tk
from tkinter import filedialog
import os
import argparse

def find_continuous_dat_files(folder):
    matches = []
    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file == "continuous.dat":
                matches.append(os.path.join(root_dir, file))
    return matches

def select_folders(start_dir=None):
    root = tk.Tk()
    root.withdraw()  # Hide main window

    selected_folders = []
    while True:
        folder = filedialog.askdirectory(
            title="Select a folder (Cancel to finish)",
            initialdir=start_dir if start_dir else os.getcwd()
        )
        if not folder:
            break
        selected_folders.append(folder)
        print(f"Selected folder: {folder}")
        start_dir = folder
    return selected_folders

def main(start_dir, data_dir, probe_path, n_chan_bin):
    selected_folders = select_folders(start_dir)

    continuous_files = []
    for folder in selected_folders:
        continuous_files.extend(find_continuous_dat_files(folder))

    print("\nList of continuous.dat files found:")
    for f in continuous_files:
        print(f)

    from kilosort import run_kilosort
    from kilosort.io import BinaryFileGroup, load_probe

    settings = {'n_chan_bin': n_chan_bin, 'nblocks': 0, 'fs': 30000, 'batch_size': 60000}

    probe = load_probe(probe_path)

    print("\nStarting kilosort batch...")
    run_kilosort(settings=settings, filename=continuous_files, probe=probe)
    print("Kilosort batch finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch run kilosort on multiple folders")
    parser.add_argument("--start_dir", type=str, required=True, help="Initial directory for folder selection dialog")
    parser.add_argument("--data_dir", type=str, required=True, help="Base data directory (if needed)")
    parser.add_argument("--probe_path", type=str, required=True, help="Path to the probe channel map file (.mat)")
    parser.add_argument("--n_chan_bin", type=int, default=32, help="Number of channels (default: 32)")

    args = parser.parse_args()
    main(start_dir=args.start_dir, data_dir=args.data_dir, probe_path=args.probe_path, n_chan_bin=args.n_chan_bin)
