def get_thresholds():

    _ANGLE_ELBOW_HIP_VERT = {
                            #'NORMAL' : (0, 10),
                            #'TRANS'  : (20, 80 ),#20
                            #'PASS'   : (75, 110 ),
                            #'FAILED' : (30,45)
                            'NORMAL' : (0, 15),#5 #25 #10
                            'TRANS'  : (20, 70 ),#30
                            'PASS'   : (75, 110 )
                           }    

        
    thresholds = {
                    'ELBOW_HIP_VERT': _ANGLE_ELBOW_HIP_VERT,

                    'HIP_THRESH'   : [0, 90],
                    'ANKLE_THRESH' : 120,
                    'KNEE_THRESH'  : [0, 90],
                    'SHLDR_THRESH' : [0, 180],
                    'ELBOW_THRESH'  :[40, 75, 110],

                    'OFFSET_THRESH'    : 35.0,
                    'INACTIVE_THRESH'  : 15.0,

                    'CNT_FRAME_THRESH' : 50
                            
                }

    return thresholds
