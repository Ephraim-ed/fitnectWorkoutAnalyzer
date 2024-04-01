import time
import cv2
import numpy as np
from utils import find_angle, get_landmark_features, draw_text, draw_dotted_line
from thresholds import get_thresholds

class ProcessFrame:
    
    def __init__(self, thresholds, flip_frame = False):
        
        # Set if frame should be flipped or not.
        self.flip_frame = flip_frame

        # self.thresholds
        self.thresholds = thresholds

        # Font type.
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # line type
        self.linetype = cv2.LINE_AA

        # set radius to draw arc
        self.radius = 20

        # Colors in BGR format.
        self.COLORS = {
                        'blue'       : (0, 127, 255),
                        'red'        : (255, 50, 50),
                        'green'      : (0, 255, 127),
                        'light_green': (100, 233, 127),
                        'yellow'     : (255, 255, 0),
                        'magenta'    : (255, 0, 255),
                        'white'      : (255,255,255),
                        'cyan'       : (0, 255, 255),
                        'light_blue' : (102, 204, 255)
                      }



        # Dictionary to maintain the various landmark features.
        self.dict_features = {}
        self.left_features = {
                                'shoulder': 11,
                                'elbow'   : 13,
                                'wrist'   : 15,                    
                                'hip'     : 23,
                                'knee'    : 25,
                                'ankle'   : 27,
                                'foot'    : 31
                             }

        self.right_features = {
                                'shoulder': 12,
                                'elbow'   : 14,
                                'wrist'   : 16,
                                'hip'     : 24,
                                'knee'    : 26,
                                'ankle'   : 28,
                                'foot'    : 32
                              }

        self.dict_features['left'] = self.left_features
        self.dict_features['right'] = self.right_features
        self.dict_features['nose'] = 0

        
        # For tracking counters and sharing states in and out of callbacks.
        self.state_tracker = {
            'state_seq': [],

            'start_inactive_time': time.perf_counter(),
            'start_inactive_time_front': time.perf_counter(),
            'INACTIVE_TIME': 0.0,
            'INACTIVE_TIME_FRONT': 0.0,

            # 0 --> Bend Backwards, 1 --> Bend Forward, 2 --> Keep shin straight, 3 --> Deep squat
            'DISPLAY_TEXT' : np.full((4,), False),
            'COUNT_FRAMES' : np.zeros((4,), dtype=np.int64),

            'LOWER_ELBOW': False,

            'INCORRECT_POSTURE': False,

            'prev_state': None,
            'curr_state':None,

            'PUSHUP_COUNT': 0,
            'IMPROPER_PUSHUP':0
            
        }
        
        self.FEEDBACK_ID_MAP = {
                                0: ('GOOD PUSH UP', 110, (0, 153, 255)),#lalabas pag nahit ung 60N 2
                                1: ('GO LOWER', 160, (0, 0, 0)), #lalabas pag na hit ung 30 1
                                2: ('GO LOW', 170, (0, 153, 255)),
                                3: ('OVER PUSHUP', 125, (255, 80, 80))#pag lumagpas sa 110 3
                               }

        


    def _get_state(self, elbow_angle):
        
        elbow = None        

        if self.thresholds['ELBOW_HIP_VERT']['NORMAL'][0] <= elbow_angle <= self.thresholds['ELBOW_HIP_VERT']['NORMAL'][1]:
            elbow = 1
        elif self.thresholds['ELBOW_HIP_VERT']['TRANS'][0] <= elbow_angle <= self.thresholds['ELBOW_HIP_VERT']['TRANS'][1]:
            elbow = 2
        elif self.thresholds['ELBOW_HIP_VERT']['PASS'][0] <= elbow_angle <= self.thresholds['ELBOW_HIP_VERT']['PASS'][1]:
            elbow = 3
        #elif self.thresholds['ELBOW_HIP_VERT']['FAILED'][0] <= elbow_angle <= self.thresholds['ELBOW_HIP_VERT']['FAILED'][1]:
        #    elbow = 4

        return f's{elbow}' if elbow else None



    
    def _update_state_sequence(self, state):

        if state == 's2':
            if (('s3' not in self.state_tracker['state_seq']) and (self.state_tracker['state_seq'].count('s2'))==0) or \
                    (('s3' in self.state_tracker['state_seq']) and (self.state_tracker['state_seq'].count('s2')==1)):
                        self.state_tracker['state_seq'].append(state)
            

        elif state == 's3':
            if (state not in self.state_tracker['state_seq']) and 's2' in self.state_tracker['state_seq']: 
                self.state_tracker['state_seq'].append(state)

            


    def _show_feedback(self, frame, c_frame, dict_maps, lower_elbow_disp):


        if lower_elbow_disp:
            draw_text(
                    frame, 
                    'BEND YOUR ELBOW', 
                    pos=(30, 80),
                    text_color=(0, 0, 0),
                    font_scale=0.6,
                    text_color_bg=(255, 255, 0)
                )  

        for idx in np.where(c_frame)[0]:
            draw_text(
                    frame, 
                    dict_maps[idx][0], 
                    pos=(30, dict_maps[idx][1]),
                    text_color=(255, 255, 230),
                    font_scale=0.6,
                    text_color_bg=dict_maps[idx][2]
                )

        return frame



    def process(self, frame: np.array, pose):
        play_sound = None
       

        frame_height, frame_width, _ = frame.shape

        # Process the image.
        keypoints = pose.process(frame)

        if keypoints.pose_landmarks:
            ps_lm = keypoints.pose_landmarks

            nose_coord = get_landmark_features(ps_lm.landmark, self.dict_features, 'nose', frame_width, frame_height)
            
            left_shldr_coord, left_elbow_coord, left_wrist_coord, left_hip_coord, left_knee_coord, left_ankle_coord, left_foot_coord = \
                                get_landmark_features(ps_lm.landmark, self.dict_features, 'left', frame_width, frame_height)
                                
            right_shldr_coord, right_elbow_coord, right_wrist_coord, right_hip_coord, right_knee_coord, right_ankle_coord, right_foot_coord = \
                                get_landmark_features(ps_lm.landmark, self.dict_features, 'right', frame_width, frame_height)
                                                      

            offset_angle = find_angle(left_shldr_coord, right_shldr_coord, nose_coord)

            if offset_angle > self.thresholds['OFFSET_THRESH']:
                
                display_inactivity = False

                end_time = time.perf_counter()
                self.state_tracker['INACTIVE_TIME_FRONT'] += end_time - self.state_tracker['start_inactive_time_front']
                self.state_tracker['start_inactive_time_front'] = end_time

                if self.state_tracker['INACTIVE_TIME_FRONT'] >= self.thresholds['INACTIVE_THRESH']:
                    self.state_tracker['PUSHUP_COUNT'] = 0
                    self.state_tracker['IMPROPER_PUSHUP'] = 0
                    display_inactivity = True

                cv2.circle(frame, nose_coord, 7, self.COLORS['white'], -1)
                cv2.circle(frame, left_shldr_coord, 7, self.COLORS['yellow'], -1)
                cv2.circle(frame, right_shldr_coord, 7, self.COLORS['magenta'], -1)

                if self.flip_frame:
                    frame = cv2.flip(frame, 1)

                if display_inactivity:
                    cv2.putText(frame, 'Resetting PUSHUP_COUNT due to inactivity', (10, frame_height - 90), self.font, 0.5, self.COLORS['blue'], 2, lineType=self.linetype)
                    play_sound = 'reset_counters'
                    self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
                    self.state_tracker['start_inactive_time_front'] = time.perf_counter()

                draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['PUSHUP_COUNT']), 
                    pos=(int(frame_width*0.68), 30),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(18, 185, 0)
                )  
                

                draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_PUSHUP']), 
                    pos=(int(frame_width*0.68), 80),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(221, 0, 0),
                    
                )  
                
                
                draw_text(
                    frame, 
                    'CAMERA NOT ALIGNED PROPERLY!!!', 
                    pos=(30, frame_height-60),
                    text_color=(255, 255, 230),
                    font_scale=0.65,
                    text_color_bg=(255, 153, 0),
                ) 
                
                
                draw_text(
                    frame, 
                    'OFFSET ANGLE: '+str(offset_angle), 
                    pos=(30, frame_height-30),
                    text_color=(255, 255, 230),
                    font_scale=0.65,
                    text_color_bg=(255, 153, 0),
                ) 

                # Reset inactive times for side view.
                self.state_tracker['start_inactive_time'] = time.perf_counter()
                self.state_tracker['INACTIVE_TIME'] = 0.0
                self.state_tracker['prev_state'] =  None
                self.state_tracker['curr_state'] = None
            
            # Camera is aligned properly.
            else:

                self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
                self.state_tracker['start_inactive_time_front'] = time.perf_counter()


                dist_l_sh_hip = abs(left_foot_coord[1]- left_shldr_coord[1])
                dist_r_sh_hip = abs(right_foot_coord[1] - right_shldr_coord[1])
              
                
                # left_shldr_coord = left_shldr_coord
                # left_elbow_coord = left_elbow_coord
                # left_wrist_coord = left_wrist_coord
                # left_hip_coord = left_hip_coord
                # left_knee_coord = left_knee_coord
                # left_ankle_coord = left_ankle_coord
                # left_foot_coord = left_foot_coord
                # right_shldr_coord = right_shldr_coord
                # right_elbow_coord = right_elbow_coord
                # right_wrist_coord = right_wrist_coord
                # right_hip_coord = right_hip_coord
                # right_knee_coord = right_knee_coord
                # right_ankle_coord = right_ankle_coord
                # right_foot_coord = right_foot_coord
                
                
                shldr_coord = None
                elbow_coord = None
                wrist_coord = None
                hip_coord = None
                knee_coord = None
                ankle_coord = None
                foot_coord = None


                if dist_l_sh_hip > dist_r_sh_hip:
                    shldr_coord = left_shldr_coord
                    elbow_coord = left_elbow_coord
                    wrist_coord = left_wrist_coord
                    hip_coord = left_hip_coord
                    knee_coord = left_knee_coord
                    ankle_coord = left_ankle_coord
                    foot_coord = left_foot_coord

                    multiplier = -1
                                     
                
                else:
                    shldr_coord = right_shldr_coord
                    elbow_coord = right_elbow_coord
                    wrist_coord = right_wrist_coord
                    hip_coord = right_hip_coord
                    knee_coord = right_knee_coord
                    ankle_coord = right_ankle_coord
                    foot_coord = right_foot_coord

                    multiplier = 1
                    

                # ------------------- Verical Angle calculation --------------
                elbow_vertical_angle = find_angle(shldr_coord, np.array([elbow_coord[0], 0]), elbow_coord)
                cv2.ellipse(frame, elbow_coord, (30, 30), 
                            angle = 0, startAngle = -90, endAngle = -90+multiplier*elbow_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3, lineType = self.linetype)

                draw_dotted_line(frame, elbow_coord, start=elbow_coord[1]-80, end=elbow_coord[1]+20, line_color=self.COLORS['blue'])

                shldr_vertical_angle = find_angle(elbow_coord, np.array([shldr_coord[0], 0]), shldr_coord)
                cv2.ellipse(frame, shldr_coord, (30, 30), 
                            angle = 0, startAngle = -90, endAngle = -90+multiplier*shldr_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3, lineType = self.linetype)

                draw_dotted_line(frame, shldr_coord, start=shldr_coord[1]-80, end=shldr_coord[1]+20, line_color=self.COLORS['blue'])

                hip_vertical_angle = find_angle(shldr_coord, np.array([hip_coord[0], 0]), hip_coord)
                cv2.ellipse(frame, hip_coord, (30, 30), 
                            angle = 0, startAngle = -90, endAngle = -90+multiplier*hip_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3, lineType = self.linetype)

                draw_dotted_line(frame, hip_coord, start=hip_coord[1]-80, end=hip_coord[1]+20, line_color=self.COLORS['blue'])




                knee_vertical_angle = find_angle(hip_coord, np.array([knee_coord[0], 0]), knee_coord)
                cv2.ellipse(frame, knee_coord, (20, 20), 
                            angle = 0, startAngle = -90, endAngle = -90-multiplier*knee_vertical_angle, 
                            color = self.COLORS['white'], thickness = 3,  lineType = self.linetype)

                draw_dotted_line(frame, knee_coord, start=knee_coord[1]-50, end=knee_coord[1]+20, line_color=self.COLORS['blue'])



                ankle_vertical_angle = find_angle(knee_coord, np.array([ankle_coord[0], 0]), ankle_coord)
                cv2.ellipse(frame, ankle_coord, (30, 30),
                            angle = 0, startAngle = -90, endAngle = -90 + multiplier*ankle_vertical_angle,
                            color = self.COLORS['white'], thickness = 3,  lineType=self.linetype)

                draw_dotted_line(frame, ankle_coord, start=ankle_coord[1]-50, end=ankle_coord[1]+20, line_color=self.COLORS['blue'])

                # ------------------------------------------------------------
        
                
                # Join landmarks.
                cv2.line(frame, left_shldr_coord, left_elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, left_wrist_coord, left_elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, left_shldr_coord, left_hip_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, left_knee_coord, left_hip_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, left_ankle_coord, left_knee_coord,self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, left_ankle_coord, left_foot_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, right_shldr_coord, right_elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, right_wrist_coord, right_elbow_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, right_shldr_coord, right_hip_coord, self.COLORS['light_blue'], 4, lineType=self.linetype)
                cv2.line(frame, right_knee_coord, right_hip_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, right_ankle_coord, right_knee_coord,self.COLORS['light_blue'], 4,  lineType=self.linetype)
                cv2.line(frame, right_ankle_coord, right_foot_coord, self.COLORS['light_blue'], 4,  lineType=self.linetype)
                
                # Plot landmark points
                cv2.circle(frame, left_shldr_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_elbow_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_wrist_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_hip_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_knee_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_ankle_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, left_foot_coord, 7, self.COLORS['yellow'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_shldr_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_elbow_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_wrist_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_hip_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_knee_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_ankle_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)
                cv2.circle(frame, right_foot_coord, 7, self.COLORS['magenta'], -1,  lineType=self.linetype)


                

                current_state = self._get_state(int(elbow_vertical_angle))
                self.state_tracker['curr_state'] = current_state
                self._update_state_sequence(current_state)



                # -------------------------------------- COMPUTE COUNTERS --------------------------------------

                if current_state == 's1':

                    if len(self.state_tracker['state_seq']) == 3 and not self.state_tracker['INCORRECT_POSTURE']:
                        self.state_tracker['PUSHUP_COUNT']+=1
                        play_sound = str(self.state_tracker['PUSHUP_COUNT'])
                        
                    elif 's2' in self.state_tracker['state_seq'] and len(self.state_tracker['state_seq'])==1:
                        self.state_tracker['IMPROPER_PUSHUP']+=1
                        play_sound = 'incorrect'

                    elif self.state_tracker['INCORRECT_POSTURE']:
                        self.state_tracker['IMPROPER_PUSHUP']+=1
                        play_sound = 'incorrect'
                        
                    
                    self.state_tracker['state_seq'] = []
                    self.state_tracker['INCORRECT_POSTURE'] = False


                # ----------------------------------------------------------------------------------------------------




                # -------------------------------------- PERFORM FEEDBACK ACTIONS --------------------------------------

                else:
                    if elbow_vertical_angle > self.thresholds['ELBOW_THRESH'][1]:
                        self.state_tracker['DISPLAY_TEXT'][0] = True
                        

                    elif elbow_vertical_angle < self.thresholds['ELBOW_THRESH'][0] and \
                         self.state_tracker['state_seq'].count('s2')==1:
                            self.state_tracker['DISPLAY_TEXT'][1] = True
                        
                                        
                    
                    if self.thresholds['ELBOW_THRESH'][0] < elbow_vertical_angle < self.thresholds['ELBOW_THRESH'][1] and \
                       self.state_tracker['state_seq'].count('s2')==1:
                        self.state_tracker['LOWER_ELBOW'] = True


                    elif elbow_vertical_angle > self.thresholds['ELBOW_THRESH'][2]:
                        self.state_tracker['DISPLAY_TEXT'][3] = True
                        self.state_tracker['INCORRECT_POSTURE'] = True

                    
                    if (ankle_vertical_angle > self.thresholds['ANKLE_THRESH']):
                        self.state_tracker['DISPLAY_TEXT'][2] = True
                        self.state_tracker['INCORRECT_POSTURE'] = True


                # ----------------------------------------------------------------------------------------------------


                
                
                # ----------------------------------- COMPUTE INACTIVITY ---------------------------------------------

                display_inactivity = False
                
                if self.state_tracker['curr_state'] == self.state_tracker['prev_state']:

                    end_time = time.perf_counter()
                    self.state_tracker['INACTIVE_TIME'] += end_time - self.state_tracker['start_inactive_time']
                    self.state_tracker['start_inactive_time'] = end_time

                    if self.state_tracker['INACTIVE_TIME'] >= self.thresholds['INACTIVE_THRESH']:
                        self.state_tracker['PUSHUP_COUNT'] = 0
                        self.state_tracker['IMPROPER_PUSHUP'] = 0
                        display_inactivity = True

                
                else:
                    
                    self.state_tracker['start_inactive_time'] = time.perf_counter()
                    self.state_tracker['INACTIVE_TIME'] = 0.0

                # -------------------------------------------------------------------------------------------------------
              
                elbow_text_coord_x = elbow_coord[0] + 15
                shldr_text_coord_x = shldr_coord[0] + 10
                hip_text_coord_x = hip_coord[0] + 10
                knee_text_coord_x = knee_coord[0] + 10
                ankle_text_coord_x = ankle_coord[0] + 10

                if self.flip_frame:
                    frame = cv2.flip(frame, 1)
                    elbow_text_coord_x = frame_width - elbow_coord[0] + 15
                    shldr_text_coord_x = frame_width - shldr_coord[0] + 10
                    hip_text_coord_x = frame_width - hip_coord[0] + 10
                    knee_text_coord_x = frame_width - knee_coord[0] + 10
                    ankle_text_coord_x = frame_width - ankle_coord[0] + 10

                
                
                if 's3' in self.state_tracker['state_seq'] or current_state == 's1':
                    self.state_tracker['LOWER_ELBOW'] = False

                self.state_tracker['COUNT_FRAMES'][self.state_tracker['DISPLAY_TEXT']]+=1

                frame = self._show_feedback(frame, self.state_tracker['COUNT_FRAMES'], self.FEEDBACK_ID_MAP, self.state_tracker['LOWER_ELBOW'])



                if display_inactivity:
                    # cv2.putText(frame, 'Resetting COUNTERS due to inactivity!!!', (10, frame_height - 20), self.font, 0.5, self.COLORS['blue'], 2, lineType=self.linetype)
                    play_sound = 'reset_counters'
                    self.state_tracker['start_inactive_time'] = time.perf_counter()
                    self.state_tracker['INACTIVE_TIME'] = 0.0

                cv2.putText(frame, str(int(hip_vertical_angle)), (hip_text_coord_x, hip_coord[1]), self.font, .6, self.COLORS['light_green'], 2, lineType=self.linetype)
                #cv2.putText(frame, str(int(knee_vertical_angle)), (knee_text_coord_x, knee_coord[1]), self.font, .6, self.COLORS['light_green'], 2, lineType=self.linetype)
                cv2.putText(frame, str(int(ankle_vertical_angle)), (ankle_text_coord_x, ankle_coord[1]), self.font, .6, self.COLORS['light_green'], 2, lineType=self.linetype)
                cv2.putText(frame, str(int(shldr_vertical_angle)), (shldr_text_coord_x, shldr_coord[1]+10), self.font, .6, self.COLORS['light_green'], 2, lineType=self.linetype)
                cv2.putText(frame, str(int(elbow_vertical_angle)), (elbow_text_coord_x, elbow_coord[1]+10), self.font, .6, self.COLORS['light_green'], 2, lineType=self.linetype)
                draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['PUSHUP_COUNT']), 
                    pos=(int(frame_width*0.68), 30),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(18, 185, 0)
                )  
                

                draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_PUSHUP']), 
                    pos=(int(frame_width*0.68), 80),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(221, 0, 0),
                    
                )  
                
                
                self.state_tracker['DISPLAY_TEXT'][self.state_tracker['COUNT_FRAMES'] > self.thresholds['CNT_FRAME_THRESH']] = False
                self.state_tracker['COUNT_FRAMES'][self.state_tracker['COUNT_FRAMES'] > self.thresholds['CNT_FRAME_THRESH']] = 0    
                self.state_tracker['prev_state'] = current_state
                                  

       
        
        else:

            if self.flip_frame:
                frame = cv2.flip(frame, 1)

            end_time = time.perf_counter()
            self.state_tracker['INACTIVE_TIME'] += end_time - self.state_tracker['start_inactive_time']

            display_inactivity = False

            if self.state_tracker['INACTIVE_TIME'] >= self.thresholds['INACTIVE_THRESH']:
                self.state_tracker['PUSHUP_COUNT'] = 0
                self.state_tracker['IMPROPER_PUSHUP'] = 0
                cv2.putText(frame, 'Resetting PUSHUP_COUNT due to inactivity!!!', (10, frame_height - 25), self.font, 0.7, self.COLORS['blue'], 2)
                display_inactivity = True

            self.state_tracker['start_inactive_time'] = end_time

            draw_text(
                    frame, 
                    "CORRECT: " + str(self.state_tracker['PUSHUP_COUNT']), 
                    pos=(int(frame_width*0.68), 30),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(18, 185, 0)
                )  
                

            draw_text(
                    frame, 
                    "INCORRECT: " + str(self.state_tracker['IMPROPER_PUSHUP']), 
                    pos=(int(frame_width*0.68), 80),
                    text_color=(255, 255, 230),
                    font_scale=0.7,
                    text_color_bg=(221, 0, 0),
                    
                )  

            if display_inactivity:
                play_sound = 'reset_counters'
                self.state_tracker['start_inactive_time'] = time.perf_counter()
                self.state_tracker['INACTIVE_TIME'] = 0.0
            
            
            # Reset all other state variables
            
            self.state_tracker['prev_state'] =  None
            self.state_tracker['curr_state'] = None
            self.state_tracker['INACTIVE_TIME_FRONT'] = 0.0
            self.state_tracker['INCORRECT_POSTURE'] = False
            self.state_tracker['DISPLAY_TEXT'] = np.full((5,), False)
            self.state_tracker['COUNT_FRAMES'] = np.zeros((5,), dtype=np.int64)
            self.state_tracker['start_inactive_time_front'] = time.perf_counter()
            
            
            
        return frame, play_sound

                    
