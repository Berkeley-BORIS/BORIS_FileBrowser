import subprocess
import os
from glob import glob

import cv2

# def printnow(s):
    # sys.

tempdir= './temp_for_video'
if os.path.exists(tempdir):
    print "Removing temp_for_video directory"
    subprocess.call('rm -rf {0}'.format(tempdir), shell=True)

print "Creating temp_for_video directory"
os.mkdir(tempdir)
ims = glob('*.png')
ims.sort()

for i, imname in enumerate(ims):
    im = cv2.imread(imname, cv2.CV_LOAD_IMAGE_GRAYSCALE)

    cv2.imwrite('{0}/img{1:0>5}.png'.format(tempdir, i+1), im)
    if (i+1) % 100 == 0:
        print "Image", i+1

cmd = r"ffmpeg -f image2 -r 30 -q:v 2 -i ./temp_for_video/img%05d.png -y ./eye_video.mp4"
print cmd
subprocess.call(cmd, shell=True)

subprocess.call('rm -rf {0}'.format(tempdir), shell=True)