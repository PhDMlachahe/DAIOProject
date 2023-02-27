import cv2
from PoseModule import PoseDetector
import time
import os

dir_videos = r"C:\Users\MLACHAHE\PycharmProjects\DAIOProject\sauvegarde"
fichier_video_demo = None
if not os.path.isdir(dir_videos):
    os.mkdir(dir_videos)

cap = cv2.VideoCapture('DataVideos/50WaysToFall2.mp4')
pTime = 0
detector = PoseDetector()
while True:
    success, img = cap.read()
    img = cv2.resize(img, (int(img.shape[1]*0.50), int(img.shape[0]*0.50)), interpolation=cv2.INTER_AREA)
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)
    img = detector.drawLm(img, "all pts", ptsOfInterest=True)


    #if len(lmList)!=0:
        #print(lmList)
        #angle = detector.findAngle(img, 11, 23, 25)
    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS : {int(fps)}', (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

    # Création de la vidéo
    if fichier_video_demo is None:
        fichier_video_demo = os.path.join(dir_videos, "falling_pose1.avi")
        video_demo = cv2.VideoWriter(fichier_video_demo, cv2.VideoWriter_fourcc(*'DIVX'), 15, (img.shape[1], img.shape[0]))
    # Enregistrement de la frame dans la vidéo
    video_demo.write(img)

    cv2.imshow("Mediapipe Pose", img)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_demo.release()

# Release the VideoWriter object and close the display window
cv2.release()
cv2.destroyAllWindows()