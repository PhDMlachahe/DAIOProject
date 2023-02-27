


class MethodeSeuillage():

    def __init__(self):
        self.none = None

    def PersonFallingDown_position(self, yHead, yShoulderCenter, yHipCenter, yAnkleLeft, yAnkleRight, Head_Ankle1, Head_Ankle2, thr, seuil):

        bool_alarme_position = 0

        if Head_Ankle1 == 0:
            Head_Ankle1 = yAnkleRight - yHead
            thr = Head_Ankle1 * 0.7
        else:
            Head_Ankle2 = yAnkleRight - yHead
            if Head_Ankle1 - Head_Ankle2 > thr:
                if yHead > seuil:
                    if yShoulderCenter > seuil:
                        if yHipCenter > seuil:
                            if yAnkleRight > seuil:
                                if yAnkleLeft > seuil:
                                    bool_alarme_position = 1

        return Head_Ankle1,Head_Ankle2, thr, bool_alarme_position


    def PersonFallingDown_velocity(self, vy_Head, vy_ShoulderCenter, vy_HipCenter, vy_AnkleLeft, vy_AnkleRight, seuil):

        bool_alarme_vitesse = 0

        if vy_Head > seuil:
            if vy_ShoulderCenter > seuil*0.5:
                if vy_HipCenter > seuil*0.5:
                    if vy_AnkleRight < 0 or vy_AnkleLeft < 0:
                        bool_alarme_vitesse = 1

        return bool_alarme_vitesse

    def PersonFallingDown_acceleration(self, ay_Head, ay_ShoulderCenter, ay_HipCenter, ay_AnkleLeft, ay_AnkleRight, seuil):

        bool_alarme_acceleration = 0

        if ay_Head > seuil:
            if ay_ShoulderCenter > seuil*0.5:
                if ay_HipCenter > seuil*0.3:
                    bool_alarme_acceleration = 1

        return bool_alarme_acceleration