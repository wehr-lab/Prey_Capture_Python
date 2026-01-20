import pathlib as pl
from copy import deepcopy
import os
import pandas as pd
import numpy as np
import prey_capture_python as preycap
import glob

# Load your pre-formatted summary CSV
mollys_hell = pd.read_csv("/Volumes/Projects/PreyCapture/ZIActivation/ViralChR2_Activation/formatted_conditions_summary_reordered_viral2_newcohort.csv")
new_stem = "/Volumes/Projects/PreyCapture/ZIActivation/ViralChR2_Activation"
print(new_stem)

# Data containers
result_frame = pd.DataFrame(dtype="object")
list_of_failed_mice = []
list_of_weird_mice = []
list_of_nofilter = []

# Loop through each row (each subsession)
for i, row in mollys_hell.iterrows():
    file = row["path"]
    print(file)

    # Extract session folder from the full path
    path_parts = list(pl.Path(file).parts)
    session_folder = path_parts[-2]
    session_path = os.path.join(new_stem, session_folder)

    try:
        os.chdir(session_path)
        csv_files = glob.glob('*_filtered.csv')
        if not csv_files:
            raise IndexError

        # Choose the most recently modified filtered CSV
        dates = [pl.Path(f).stat().st_mtime for f in csv_files]
        index = np.argmax(dates)
        csv_new = csv_files[index]

        print(csv_new)
        posix_csv_path = os.path.join(session_path, csv_new)

    except IndexError:
        posix_csv_path = np.nan
        list_of_nofilter.append(session_path)
        print(f"{session_path} likely has no filtered csv. Please manually check")

    # Save path in dataframe
    mollys_hell.at[i, "posix_csv_path"] = posix_csv_path
    folder_path = pl.Path(session_folder)

    if posix_csv_path is not np.nan:
        # Try to extract tracking data
        try:
            mouse_xy, cricket_p, cricket_xy, rear_xy, lear_xy, headbase_xy, cricket_front, cricket_back = preycap.extract_points(
                posix_csv_path,
                ['Rear', 'Lear', 'anteriorC', 'posteriorC', 'headbase']
            )

            # Run geometry calculations
            dist, cricket_spd, mouse_spd, az, c_length = preycap.geometries(
                mouse_xy, cricket_xy, rear_xy, lear_xy, headbase_xy,
                cricket_p, cricket_front, cricket_back
            )

            # Try to extract prey capture metrics
            try:
                start, end, approach, captureT, freqapproach, timetoapproach, interceptindex, timetointercept, prob_inter, prob_capture = preycap.preycap_metrics(
                    cricket_xy,
                    cricket_p, dist,
                    mouse_spd, az,
                    oldmodel=False
                )
            except IndexError:
                start, end, approach, captureT, freqapproach, timetoapproach, interceptindex, timetointercept, prob_inter, prob_capture = [0]*10

            # Store metrics in result frame
            result_frame.at[i, "filename"] = posix_csv_path
            result_frame.at[i, "folder_path"] = folder_path
            result_frame.at[i, "condition"] = row["Cond"]
            result_frame.at[i, "laser_value"] = row["Laser"]
            result_frame.at[i, "trials_to_drop"] = row["trials_to_drop"]
            result_frame.at[i, "dist"] = dist.astype("object")
            result_frame.at[i, "cricket_spd"] = cricket_spd.astype("object")
            result_frame.at[i, "mouse_spd"] = mouse_spd.astype("object")
            result_frame.at[i, "az"] = az.astype("object")
            result_frame.at[i, "captureT"] = captureT
            result_frame.at[i, "cricketdrop"] = start
            result_frame.at[i, "captureframe"] = end
            result_frame.at[i, "freqapproach"] = freqapproach
            result_frame.at[i, "timetoapproach"] = timetoapproach
            result_frame.at[i, "prob_inter"] = prob_inter
            result_frame.at[i, "prob_capture"] = prob_capture
            result_frame.at[i, "timetointercept"] = timetointercept
            result_frame.at[i, "interceptframe"] = interceptindex
            result_frame.at[i, "c_length"] = c_length

        except ValueError:
            clip = session_folder
            mouse = clip.split("DLC")[0]
            list_of_failed_mice.append([mouse, posix_csv_path])
            print(f"Trial {mouse} likely has no cricket. Please manually check")
        except IndexError:
            clip = session_folder
            mouse = clip.split("DLC")[0]
            list_of_weird_mice.append([mouse, posix_csv_path])
            print(f"Trial {mouse} likely has no finish for approach. Please manually check")

# Save final result HDF
result_frame.to_hdf("/Users/mollyshallow/Desktop/20251212_LD_viralvgat_newcohort.h5", key="df")

# Save logs of failed and missing data
mice_to_save = pd.DataFrame(data=list_of_failed_mice)
mice_to_save.to_csv("/Users/mollyshallow/Desktop/20251212_LD_viralvgat_newcohort.csv")

nofilter_to_save = pd.DataFrame(data=list_of_nofilter)
nofilter_to_save.to_csv("/Users/mollyshallow/Desktop/20251212_LD_viralvgat_notfiltered_newcohort.csv")

# Summary printouts
print(list_of_failed_mice)
print(len(list_of_nofilter))
print(len(list_of_failed_mice))
print(list_of_weird_mice)
