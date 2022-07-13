import pathlib as pl
from copy import deepcopy
import os
import pandas as pd
import numpy as np
import prey_capture_python as preycap

# %% testing loading in file names and converting to posix + finding csv
mollys_hell = pd.read_csv("/mnt/rig4/lab/djmaus/Data/Molly/MollysHell_All.csv")
new_stem = "/mnt/ion-nas/Rig4/Molly/ZIActivation"
result_frame = pd.DataFrame(dtype="object")
list_of_failed_mice = []
list_of_weird_mice = []

for i, row in mollys_hell.iterrows():
    file = row["SelectedFolders"]
    path_parts = list(pl.PureWindowsPath(file).parts)
    path_parts = [path_parts[-1]]
    path_parts.insert(0, new_stem)
    path_parts_og = deepcopy(path_parts)
    path_parts.append(row["Var4"])
    try:
        posix_csv_path = pl.Path(*path_parts)
    except TypeError:
        posix_csv_path = np.nan
    mollys_hell.at[i, "posix_csv_path"] = posix_csv_path
    folder_path = pl.Path(*path_parts_og)
    # Do we want to replace SelectedFolders with Posix path instead of Windows?
    # print(posix_csv_path)
    if posix_csv_path is not np.nan:
        mouse_xy, cricket_p, cricket_xy, rear_xy, lear_xy, headbase_xy = preycap.extract_points(posix_csv_path,
                                                                                                ['Rear', 'Lear',
                                                                                                 'anteriorC',
                                                                                                 'posteriorC',
                                                                                                 'headbase'],
                                                                                                startonly=True)
        # Cricket variables above give NaNs for this csv
        try:
            dist, cricket_spd, mouse_spd, az = preycap.geometries(mouse_xy, cricket_xy, rear_xy, lear_xy, headbase_xy,
                                                                  cricket_p)
            try:
                approach, captureT, freqapproach, timetoapproach, timetointercept, prob_inter, prob_capture = preycap.preycap_metrics(
                    cricket_xy,
                    cricket_p, dist,
                    mouse_spd, az,
                    oldmodel=False)
            except IndexError:
                approach, captureT, freqapproach, timetoapproach, timetointercept, prob_inter, prob_capture = [0, 0, 0,
                                                                                                               0, 0, 0,
                                                                                                               0]

            result_frame.at[i, "filename"] = posix_csv_path
            result_frame.at[i, "folder_path"] = folder_path
            result_frame.at[i, "condition"] = row["Condition_T"]
            result_frame.at[i, "laser_value"] = row["LaserValues_T"]
            result_frame.at[i, "dist"] = dist.astype("object")
            result_frame.at[i, "cricket_spd"] = cricket_spd.astype("object")
            result_frame.at[i, "mouse_spd"] = mouse_spd.astype("object")
            result_frame.at[i, "az"] = az.astype("object")
            result_frame.at[i, "captureT"] = captureT
            result_frame.at[i, "freqapproach"] = freqapproach
            result_frame.at[i, "timetoapproach"] = timetoapproach
            result_frame.at[i, "prob_inter"] = prob_inter
            result_frame.at[i, "prob_capture"] = prob_capture
            result_frame.at[i, "timetointercept"] = timetointercept

        except ValueError:
            clip = path_parts[-1]
            mouse = clip.split("DLC")[0]
            list_of_failed_mice.append([mouse, posix_csv_path])
            print("trial {} likely has no cricket. Please manually check".format(mouse))
        except IndexError:
            clip = path_parts[-1]
            mouse = clip.split("DLC")[0]
            list_of_weird_mice.append([mouse, posix_csv_path])
            print("trial {} likely has no finish for approach. please manually check".format(mouse))

result_frame.to_hdf("/home/lab/Desktop/20220603alltrials_start_LD.h5", key="df")
print(list_of_failed_mice)
mice_to_save = pd.DataFrame(data=list_of_failed_mice)
mice_to_save.to_csv("/home/lab/Desktop/20220603_failed_mice.csv")
print(len(list_of_failed_mice))
print(list_of_weird_mice)
