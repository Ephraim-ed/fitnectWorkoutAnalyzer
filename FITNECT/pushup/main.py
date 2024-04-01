import mediapipe as mp
import cv2
import numpy as np

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds
cap = cv2.VideoCapture(0)
thresholds = get_thresholds()
live_process_frame = ProcessFrame(thresholds, flip_frame=True)
pose = get_mediapipe_pose()

with pose as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
                break
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        frame, _ = live_process_frame.process(frame, pose)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
        #frame = cv2.resize(frame,(880,880))

        cv2.imshow('Pushup', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()