import cv2, sys, os
from videobarplot import imageGenerator, overlayPlot
import pandas as pd

def VideoProcess(*args):

    video = args[0]
    path = args[1]

    try:
        # Load csv file and delete the firs column
        data = pd.read_csv(path+'/emotion.csv')
        if data.shape[1] == 1:
            raise Exception
    except:
        # Load csv file and delete the firs column
        data = pd.read_csv(path+'/emotion.csv', delimiter=';')

    #Proces emotiosn and convert to numpy and get time for check with fps
    cols = data.shape[0]
    time = data.at[cols-1,'time']
    fps1 = cols/time
    if args[2] == '1':
        data = data.drop(['Unnamed: 0','trigger', 'time'], axis=1).to_numpy().astype(float)
    else:
        data = data.drop(['Unnamed: 0','time'], axis=1).to_numpy().astype(float)

    emotions = data[:,0::1]

    # Open the video and get dimensions and fps
    cap = cv2.VideoCapture(video)
    video_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_heigth = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Check the video fps
    if fps > fps1:
        fps = fps1
    size = (int(video_width), int(video_heigth))
    size_plot = (int(video_width*0.35), int(video_heigth*0.35))

    # Initialize the video writer
    out = cv2.VideoWriter(path + '/output_processed.avi',
                          cv2.VideoWriter_fourcc(*'MJPG'), fps, size)

    # Initialize the detector
    file = os.getcwd()
    face_cascade = cv2.CascadeClassifier(file + '/main/assets/haarcascade_frontalface_default.xml')


    j = 0
    jend = cols

    # Do operations while video is opened
    while (cap.isOpened()):
        # ret is the boolean True is video opened and frame is the frame in this moment
        ret, img = cap.read()

        try:
            # Convert frame to gray color and detect face
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                # draw rectangle to main image
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if j < jend:
                # Generate plot image
                try:
                    image = imageGenerator(emotions[j], size_plot, size)
                    img = overlayPlot(img, image, size)
                except Exception:
                    break

            else:
                break

        except:
            break

        out.write(img)
        j += 1
        if j == int(0.2*jend):
            sys.stderr.write("Total complete: 20%\n")
        elif j == int(0.4 * jend):
            sys.stderr.write("Total complete: 40%\n")
        elif j == int(0.6 * jend):
            sys.stderr.write("Total complete: 60%\n")
        elif j == int(0.8 * jend):
            sys.stderr.write("Total complete: 80%\n")

        # ESC to quit
        if (cv2.waitKey(1) & 0xFF == ord('q')) or not ret:
            break

    sys.stderr.write("Total complete: 100%\n")
    # kill open cv things
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    a = sys.argv[1]
    b = sys.argv[2]
    c = sys.argv[3]

    VideoProcess(a, b, c)
