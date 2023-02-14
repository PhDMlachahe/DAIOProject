import cv2
import mediapipe as mp
import time
import math

class PoseDetector():

    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon


        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=self.upBody,
            smooth_segmentation=self.smooth,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True, couleur=(0, 0, 0)):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, couleur, cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):

        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 3, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 5, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 3, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 3, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 5, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

    def findCenter(self, img, p1, p2, draw=True, couleur=(0, 0, 255)):

        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]

        x3, y3 = (x1+x2)//2, (y1+y2)//2

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), couleur, 2)
            cv2.circle(img, (x1, y1), 3, couleur, cv2.FILLED)
            cv2.circle(img, (x2, y2), 3, couleur, cv2.FILLED)
            cv2.circle(img, (x2, y2), 3, couleur, cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, couleur, 2)
            cv2.putText(img, f'({x3}, {y3})', (x3, y3), cv2.FONT_HERSHEY_PLAIN, 2, couleur,2)

        return x3, y3

    def findDistance(self, img, p1, p2, draw=True, couleur=(0, 0, 255)):

        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]

        # Calculate the euclidian distance
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), couleur, 2)
            cv2.circle(img, (x1, y1), 3, couleur, cv2.FILLED)
            cv2.circle(img, (x1, y1), 5, couleur, 2)
            cv2.circle(img, (x2, y2), 3, couleur, cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, couleur, 2)
            cv2.putText(img, str(int(distance)), ((x1+x2)//2, (y1+y2)//2), cv2.FONT_HERSHEY_PLAIN, 2, couleur, 2)
        return distance


    def DrawLm(self, img, lmList, couleur=(255,0,0)):
        #if self.results.pose_landmarks:
        #    self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        for lm in lmList:
            cx, cy = lm[1], lm[2]
            cv2.circle(img, (cx, cy), 5, couleur, cv2.FILLED)
        return img

def main():
    cap = cv2.VideoCapture('DataVideos/50WaysToFall2.mp4')
    pTime = 0
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        #img = cv2.resize(img, (int(img.shape[1]*0.75), int(img.shape[0]*0.75)), interpolation=cv2.INTER_AREA)
        img = detector.findPose(img)
        lmList = detector.findPosition(img)

        if len(lmList)!=0:
            print(lmList)
            #angle = detector.findAngle(img, 11, 23, 25)
        # Frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS : {int(fps)}', (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

        cv2.imshow("Mediapipe Pose", img)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()