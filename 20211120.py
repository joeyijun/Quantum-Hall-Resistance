# coding=gbk
import pandas as pd
from skimage import transform
from skimage.feature import (match_descriptors, corner_harris,
                             corner_peaks, ORB, plot_matches)
from skimage.color import rgb2gray
import matplotlib.pyplot as plt


#   img1为参考图片
df1 = pd.read_table(r'C://Users/fujun/Desktop/新建文件夹/2021年11月17日_20_52_15_data.txt', header=None)
#  将dataframe转换为 numpy array
img1 = df1.to_numpy()
img2 = transform.rotate(img1, 180)

plt.imshow(img2)


descriptor_extractor = ORB(n_keypoints=2)

descriptor_extractor.detect_and_extract(img1)
keypoints1 = descriptor_extractor.keypoints
descriptors1 = descriptor_extractor.descriptors

descriptor_extractor.detect_and_extract(img2)
keypoints2 = descriptor_extractor.keypoints
descriptors2 = descriptor_extractor.descriptors



matches12 = match_descriptors(descriptors1, descriptors2, cross_check=True)


fig, ax = plt.subplots(nrows=1, ncols=1)

plt.gray()

plot_matches(ax, img1, img2, keypoints1, keypoints2, matches12)
ax.axis('off')
ax.set_title("Ref Image vs. Transformed Image")
plt.show()


