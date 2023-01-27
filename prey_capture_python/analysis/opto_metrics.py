import pathlib as pl
from copy import deepcopy
import os
import pandas as pd
import numpy as np
import prey_capture_python as preycap
import glob

# %% testing loading in file names and converting to posix + finding csv
mollys_hell = pd.read_csv("/Volumes/Projects/PreyCapture/ZIActivation/DataDirs.csv")
new_stem = "/Volumes/Projects/PreyCapture/ZIActivation/"
# print(new_stem)
result_frame = pd.DataFrame(dtype="object")
list_of_failed_mice = []
list_of_weird_mice = []

for i, row in mollys_hell.iterrows():
    file = row["path"]
    # print(file)
    path_parts = list(pl.PureWindowsPath(file).parts)
    path_parts = [path_parts[-1]]
    # print(path_parts)
    for path in path_parts:
        # print(path)
        path=str(new_stem+path)
        # print(path)
        ext='csv'
        os.chdir(path)
        try:
            csv=glob.glob('*_filtered.{}'.format(ext))
            csv=str(csv[0])
            # print(csv)
            posix_csv_path=str(path+'/'+csv)
            # print(posix_csv_path)
        except IndexError:
            posix_csv_path=np.nan

    path_parts_og = deepcopy(path_parts)

    mollys_hell.at[i, "posix_csv_path"] = posix_csv_path
    # print(posix_csv_path)
    folder_path = pl.Path(*path_parts_og)
    # Do we want to replace SelectedFolders with Posix path instead of Windows?
    if posix_csv_path is not np.nan:
        mouse_xy, cricket_p, cricket_xy, rear_xy, lear_xy, headbase_xy, cricket_front, cricket_back = preycap.extract_points(posix_csv_path,
                                                                                                ['Rear', 'Lear',
                                                                                                 'anteriorC',
                                                                                                 'posteriorC',
                                                                                                 'headbase'])
        # Cricket variables above give NaNs for this csv
        try:
            dist, cricket_spd, mouse_spd, az, c_length = preycap.geometries(mouse_xy, cricket_xy, rear_xy, lear_xy, headbase_xy,
                                                                  cricket_p, cricket_font, cricket_back)
            try:
                start, end, approach, captureT, freqapproach, timetoapproach, interceptindex, timetointercept, prob_inter, prob_capture= preycap.preycap_metrics(
                    cricket_xy,
                    cricket_p, dist,
                    mouse_spd, az,
                    oldmodel=False)
            except IndexError:
                start,end, approach, captureT, freqapproach, timetoapproach, interceptindex, timetointercept, prob_inter, prob_capture= [0, 0, 0,
                                                                                                               0, 0, 0,
                                                                                                               0, 0, 0, 0]

            result_frame.at[i, "filename"] = posix_csv_path
            result_frame.at[i, "folder_path"] = folder_path
            result_frame.at[i, "condition"] = row["Cond"]
            result_frame.at[i, "laser_value"] = row["Laser"]
            result_frame.at[i, "circle"] = row["Circ"]
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
            clip = path_parts[-1]
            mouse = clip.split("DLC")[0]
            list_of_failed_mice.append([mouse, posix_csv_path])
            print("trial {} likely has no cricket. Please manually check".format(mouse))
        except IndexError:
            clip = path_parts[-1]
            mouse = clip.split("DLC")[0]
            list_of_weird_mice.append([mouse, posix_csv_path])
            print("trial {} likely has no finish for approach. please manually check".format(mouse))

result_frame.to_hdf("/Users/mollyshallow/Desktop/20221028_allmice_alltrials_LD.h5", key="df")
print(list_of_failed_mice)
mice_to_save = pd.DataFrame(data=list_of_failed_mice)
mice_to_save.to_csv("/Users/mollyshallow/Desktop/20221028_failed_mice.csv")
print(len(list_of_failed_mice))
print(list_of_weird_mice)
