import matplotlib.pyplot as plt
import io
import numpy as np
import cv2
import seaborn as sns
sns.set_theme()

def imageGenerator(emotions, size_plot, size):

    # Create the matplotlib figure to display and the axis ax
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Emotions label
    label = ('angry', 'disgust', 'fear', 'happy', 'sad',
                    'surprise', 'neutral')

    #Create a plot of reference labels and
    y_pos = np.array([0, 1, 2, 3, 4, 5, 6])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(label)
    ax.axes.set_xlim([0, 1])

    ax.barh(y_pos,emotions, align='center')

    for i, v in enumerate(emotions):
        ax.text(v , i , str(v), color='green', fontweight='normal', fontsize=20)

    # Save figure as numpy array
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format ='raw', dpi = 100)
    io_buf.seek(0)
    image = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
                newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]),-1))

    ax.axes.cla()
    plt.close(fig)

    # Conver and resize image
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, size_plot, interpolation=cv2.INTER_CUBIC)

    # Overlay plot image with video
    overlay = np.zeros((size[1], size[0], 3), dtype='uint8')
    for i in range(0, size_plot[1]):
        for j in range(0, size_plot[0]):
            overlay[i+10, j+10] = image[i,j]


    return overlay

def overlayPlot (img, image, size):
    roi = img[0:size[1], 0:size[0]]

    # Now create a mask of logo and create its inverse mask also
    img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    # Now black-out the area of logo in ROI
    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    # Take only region of logo from logo image.
    img2_fg = cv2.bitwise_and(image, image, mask=mask)
    # Put logo in ROI and modify the main image
    dst = cv2.add(img1_bg, img2_fg)
    img[0:size[1], 0:size[0]] = dst

    return img


if __name__ == "__main__":
    print('nothing')