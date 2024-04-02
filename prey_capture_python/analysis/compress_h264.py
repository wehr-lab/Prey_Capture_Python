import os
import time
import subprocess
from tqdm import tqdm
start = time.time()

# controls the quality of the encode
CRF_VALUE = '25'
# h.264 profile
PROFILE = 'high'
# encoding speed:compression ratio
PRESET = 'veryfast'
# path to ffmpeg bin
FFMPEG_PATH = '/usr/local/Cellar/ffmpeg'

def process():
    filelist = ['Volumes/Projects/PreyCapture/ZIActivation/2022-03-11_9-33-23_mouse-0897/Sky_mouse-0897_2022-03-11T09_33_23DLC_dlcrnetms5_optopreycapFeb16shuffle1_150000_el_bp_labeled.mp4']    #for file in filelist:
    for file in tqdm(filelist, position=0, ascii=True):
        encode(file)

def encode(file):
    name = ''.join(file.split('.')[:-1])
    output = '{}CRF25.mp4'.format(name)

    command = [
        FFMPEG_PATH, '-i', file,
        '-c:v', 'libx264', '-preset', PRESET, '-profile:v', PROFILE, '-crf', CRF_VALUE, '-pix_fmt', 'yuv420p', '-r', '60',
    ]

    command += ['-threads', '14', output]
    subprocess.call(command)                # encode the video!

if __name__ == "__main__":
    process()
    end = time.time()
    print(end - start)
    print("seconds")
