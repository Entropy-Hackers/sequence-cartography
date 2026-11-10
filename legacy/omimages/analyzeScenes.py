import os
import cv2
import numpy as np
import csv

import scenedetect
from scenedetect.video_manager  import VideoManager
from scenedetect.scene_manager  import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager  import StatsManager
from scenedetect.detectors      import ContentDetector



filename = "../test-data/2017-11-23 08-24-16.mp4"
filename = "../test-data/BERGWEIHNACHT.mp4"
filename = "../test-data/v.avi"

abspath = os.path.abspath(filename)
basename = os.path.basename(abspath)
dirname = os.path.dirname(abspath)
omimagedir = os.path.join(dirname, basename.rsplit('.', 1)[0] + ".omimagedata")
fn = os.path.join(omimagedir,"_scenes.csv")


video_manager = VideoManager([filename])
stats_manager = StatsManager()
scene_manager = SceneManager(stats_manager)

scene_manager.add_detector(ContentDetector(threshold=35.0, min_scene_len=25))
base_timecode = video_manager.get_base_timecode()

print (base_timecode )

start_time = base_timecode     # 00:00:00.667
end_time   = base_timecode + 200000    # 00:00:20.000

video_manager.set_duration(start_time=start_time, end_time=end_time)

video_manager.set_downscale_factor()

video_manager.start()

scene_manager.detect_scenes(frame_source=video_manager)

scene_list = scene_manager.get_scene_list(base_timecode)

print('')
print('List of scenes obtained:')

with open(fn, mode='w') as scene_file:
    scene_writer = csv.writer(scene_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)


    for i, scene in enumerate(scene_list):
        print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
            i+1,
            scene[0].get_timecode(), scene[0].get_frames(),
            scene[1].get_timecode(), scene[1].get_frames(),))
        scene_writer.writerow([scene[0].get_frames(), scene[1].get_frames()])



video_manager.release()