def get_thresholds():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL' : (0, 32),#32
                            'TRANS'  : (35, 60),#35 60
                            'PASS'   : (70, 100)
                           }    
    

        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,

                    'HIP_THRESH'   : [10, 50],
                    'ANKLE_THRESH' : 45,
                    'KNEE_THRESH'  : [50, 80, 100],




                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 15.0,

                    'CNT_FRAME_THRESH' : 50
                            
                }

    return thresholds
