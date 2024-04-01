def get_thresholds():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL' : (30, 49),
                            'TRANS'  : (50, 79),
                            'PASS'   : (80, 130)
                            #'NORMAL' : (20, 40),
                            #'TRANS'  : (50, 80),
                            #'PASS'   : (90, 130)
                           }    
    

        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'LEFT_HIP_THRESH'   : [0, 90],
                    'LEFT_ANKLE_THRESH' : [0, 180],
                    'LEFT_KNEE_THRESH'  : [60, 80, 130],
                    'RIGHT_HIP_THRESH'   : [0, 90],
                    'RIGHT_ANKLE_THRESH' : [0, 180],
                    'RIGHT_KNEE_THRESH'  : [60, 80, 130],




                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 10.0,

                    'CNT_FRAME_THRESH' : 50
                            
                }

    return thresholds
