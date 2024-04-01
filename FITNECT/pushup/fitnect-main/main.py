import mediapipe as mp
import cv2
import numpy as np

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds_beginner
pose = get_mediapipe_pose
cap = cv2.VideoCapture(0)
thresholds = get_thresholds_beginner()
live_process_frame = ProcessFrame(thresholds, flip_frame=True)

with mp.solutions.pose.Pose(
                        static_image_mode = False, 
                        model_complexity = 1,
                        smooth_landmarks = True,
                        min_detection_confidence = 0.5,
                        min_tracking_confidence = 0.5
                      ) as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
                break
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        frame, _ = live_process_frame.process(frame, pose)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
                       
        cv2.imshow('Pushup - Fitnect', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()