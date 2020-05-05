import soundfile as sf
import numpy as np
import cv2
import sys

# data, samplerate = sf.read("/Users/caillotantoine/APT_04052020_1346.wav")
data, samplerate = sf.read(sys.argv[1])
sizeFile = len(data)
toAdd = 2080-(sizeFile%2080)

voidData = np.zeros((toAdd, 1), dtype=float)
data = np.concatenate((data, voidData), axis=None)
sizeFile = len(data)

for i in range(sizeFile):
    if data[i] < 0.0:
        data[i] = 0.0
    else:
        data[i] *= 255.0

data = data.astype(np.uint8)

imgRAW = np.reshape(data, (int(sizeFile/2080), 2080))
img = cv2.equalizeHist(imgRAW)
print(imgRAW)
color_image = np.zeros((512,512,3), np.uint8)
cv2.imshow("IMG BW", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("out.png", img)
cv2.imwrite(sys.argv[2], imgRAW)
