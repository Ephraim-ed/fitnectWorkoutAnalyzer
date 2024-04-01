def get_thresholds():

    _ANGLE_HIP_KNEE_VERT = {
                            #'NORMAL' : (20, 30),
                            #'TRANS'  : (31, 75), #50
                            #'PASS'   : (70, 100) #gumagana
                            #'NORMAL' : (15, 20),
                            #'TRANS'  : (75, 95),
                            #'PASS'   : (80, 130)
                            'NORMAL' : (30, 44),
                            'TRANS'  : (45, 69), #50
                            'PASS'   : (70, 100)
                           }    
    

        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'LEFT_HIP_THRESH'   : [0, 100],
                    'LEFT_ANKLE_THRESH' : [0, 150],
                    'LEFT_KNEE_THRESH'  : [50, 70, 100],#80 95 100
                    'RIGHT_HIP_THRESH'   : [0, 100],
                    'RIGHT_ANKLE_THRESH' : [0, 150],
                    'RIGHT_KNEE_THRESH'  : [50, 70, 100],




                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 30.0,

                    'CNT_FRAME_THRESH' : 50
                            
                }

    return thresholds
