from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import scipy
from scipy import signal
import cv2

vid_writer = cv2.VideoWriter('/home/stephen/Desktop/3dgraph.avi',
                             cv2.VideoWriter_fourcc('M','J','P','G'),
                             60, (400,400))

#read .csv source data to a data frame (df)
data_source = '/home/stephen/Desktop/663_tracking.csv'
df = pd.read_csv(data_source)

#get column names
cols = []
for i in df: cols.append(i)

#list of colors
colors = 'red', 'green', 'red', 'green', 'purple','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black','green', 'red', 'blue', 'purple', 'black'

#make blank 3d plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.axis('off')

#make a z axis
z = []
for i in range(len(df[cols[0]])):  z.append(i)
start, stop = 234,345

z = z[start:stop]


#plot
for col in range(int(len(cols)/2)):
    x  = df[cols[col*2]]
    x = signal.savgol_filter(x, 11, 2)
    x = x[start:stop]
    y  = df[cols[col*2+1]]
    y = signal.savgol_filter(y, 11, 2)
    y = y[start:stop]
    if col == 4: ax.plot(z, x, -y, c=colors[col], linewidth=6)
    else: ax.plot(z, x, -y, c=colors[col], linewidth=3)

#plt.show()

# rotate the axes and update
for angle in range(0, 360):
    ax.view_init(30, angle)
    plt.draw()
    plt.pause(.01)
    plt.savefig('/home/stephen/Desktop/test.png')
    img = cv2.imread('/home/stephen/Desktop/test.png')
    img = img[40:440, 120:520]
    vid_writer.write(img)
vid_writer.release()
