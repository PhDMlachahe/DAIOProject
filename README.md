<br />
<div align="center">
<h1 align="center">DAÏO v1.0 - Fall detection from 2D skeleton points</h1>

  <p align="center">
    Simple fall detection system: Mediapipe, OpenCV and Kalman filter
  </p>

</div>

## Description

To detect a fall, we set up a video surveillance pipeline with three key steps : 
1. **Detection** of body points of interest - by Mediapipe
2. **Tracking** the position and acceleration of these points - using the Kalman filter
3. **Recognition** of the fall according to the position and acceleration thresholds reached by these points.

For more information, you can read my Medium article on the subject :
- 🇫🇷 [📰 Détection de chute à partir des points du squelette en 2D](https://medium.com/wanabilini/détection-de-chute-à-partir-des-points-du-squelette-en-2d-6cfaa1a7fd72)
- 🇬🇧 [📰 Fall detection from 2D skeleton points](https://medium.com/wanabilini/détection-de-chute-à-partir-des-points-du-squelette-en-2d-6cfaa1a7fd72)


## Execution

1. Make sure you have installed the above prerequisites
2. Download or clone this repository to your computer
3. Change the function cv2.VideoCapture('DataVideos/video_exemple.mp4') and enter the path of your video
4. Run the file `Test_FallDetection.py`.

You should now see the application running 🚀 !

![App Screenshot](images%2Fdaio_demo_fall_detection.gif)

## Contact

- 📬 mlachahe.saidsalimo@gmail.com
- Find me on <a href="https://www.linkedin.com/in/mlachahesaidsalimo/">LinkedIn</a>
- Read me on <a href="https://medium.com/wanabilini">Medium</a> !




