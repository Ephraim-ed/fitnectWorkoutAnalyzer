def get_thresholds():

    _ANGLE_HIP_KNEE_VERT = {
                            #'NORMAL' : (80, 110),
                            #'TRANS'  : (130, 150),
                            #'PASS'   : (160, 180)
                            'NORMAL' : (80, 139),
                            'TRANS'  : (140, 160),
                            'PASS'   : (160, 180)
                           }    
    

        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'HIP_THRESH'   : [80, 100],
                    'ANKLE_THRESH' : 180,
                    'KNEE_THRESH'  : [140, 170, 180],




                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 15.0,

                    'CNT_FRAME_THRESH' : 50
                            
                }

    return thresholds
