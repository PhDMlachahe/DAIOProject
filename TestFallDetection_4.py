import os
import sys
import cv2
import time
import numpy as np
import random
import requests

from PoseModule import PoseDetector
from KalmanFilter import KalmanFilter2
from GraphicDesigner import Drawing
from FallDetectionMethod import MethodeSeuillage

from twilio.rest import Client
# Your Account Sid and Auth Token from twilio account
account_sid = "ACe223d493df1c844ed3846dc7361b000b"
auth_token = "c4cd50f3a00416184af2ea787eaf51e9"
# instantiating the Client
client = Client(account_sid, auth_token)


def resizeFrame(frame, desired_height=200):
    # Calcul du ratio de redimensionnement
    ratio = desired_height / frame.shape[0]
    # Largeur souhaitée
    desired_width = int(frame.shape[1] * ratio)
    return cv2.resize(frame, (desired_width, desired_height),interpolation=cv2.INTER_AREA)

# Initilisation des couleurs
couleur_fond = (50, 50, 50)
couleur_infos = (255, 255, 255)
couleur_alarme_position = (255, 0, 0)
couleur_alarme_acceleration = (255, 0, 0)
couleur_fin_alarme = (0, 128, 255)
couleur_seuil_position=(10,10,200)
couleur_seuil_position_thr=(0,100,255)


# Instanciation
poseDetector = PoseDetector() # détecteur des points de squelette
fallDetector = MethodeSeuillage() # détecteur de chute
drw = Drawing() # dessinateur

# Initialisation de certaines variables de mouvement
Head_Ankle1, Head_Ankle2 = 0, 0
thr = 0


# Initialisation du fichier_video de sauvegarde
modesave = 1
dir_videos = r"C:\Users\MLACHAHE\PycharmProjects\DAIOProject\sauvegarde"
fichier_video = None
fichier_video_demo = None
if not os.path.isdir(dir_videos):
    os.mkdir(dir_videos)
# Initialisation du 'temps' d'enregistremnt de la vidéo de sauvegarde
fin_mouvement = 80
cpt_fin_mouvement = 0

# Initialisation des tailles des fenêtres d'analyse
desired_height = 300
fenetre_analytic_largeur = 300
barre_infos_hauteur = 25
graph_temporelle_hauteur = 60


# Initialisation des points de squelette
dict_joint_point = {"Head": [0,0], "ShoulderCenter": [0,0], "HipCenter": [0,0],
                    "AnkleLeft": [0,0], "AnkleRight": [0,0], "Head_Ankle1": [0,0], "Head_Ankle2": [0,0]}

# Initialisation du filtre de Kalman sur chaque point de squelette
dict_KF_points = {}
for nom_point, coord in dict_joint_point.items():
    # Si c'est pas des points de sqltte, tu sautes
    if nom_point=="Head_Ankle1" or nom_point=="Head_Ankle2":
        continue
    dict_KF_points[nom_point] = KalmanFilter2(0.1, coord)
dict_KF_etats = {}

# Initialisation des historiques des alertes
historique_bool_alarme_acceleration = np.zeros((fenetre_analytic_largeur), dtype=np.int32)
historique_bool_alarme_position = np.zeros((fenetre_analytic_largeur), dtype=np.int32)

# Initialisation des historiques de la position et de la acceleration des points de squelette
dict_historique_position = {}
dict_historique_acceleration = {}
for nom_point in dict_joint_point.keys():
    dict_historique_acceleration["historique_" + nom_point] = np.zeros((fenetre_analytic_largeur), dtype=np.int32)
    dict_historique_position["historique_"+nom_point] = np.zeros((fenetre_analytic_largeur), dtype=np.int32)
historique_diff_Head_Ankle = np.zeros((fenetre_analytic_largeur), dtype=np.int32)

# Initialisation des booléens-alarmes
bool_alarme_position = 0
bool_alarme_acceleration = 0
bool_etat_chute = 0
couleur_alarme_position = (255, 0, 0)
couleur_alarme_acceleration = (255, 0, 0)

# Charger la vidéo à partir du fichier
cap = cv2.VideoCapture('DataVideos/Squat.mp4')

# Initialisation des seuils
frame = cap.read()[1]
frame = resizeFrame(frame, desired_height=desired_height) if (frame.shape[0]!=desired_height) else frame
seuil_position = frame.shape[0] // 2
seuil_acceleration = frame.shape[0] // 6

# Boucle sur chaque frame de la vidéo # Arrêter la boucle si la vidéo est terminée
while cap.isOpened():
    # Lire la frame suivante
    ret, frame = cap.read()
    frame = resizeFrame(frame, desired_height=desired_height) if (frame.shape[0]!=desired_height) else frame
    # Copier la frame
    img = frame.copy()
    # fenetre_analytic_largeur = img.shape[1]

    # Détecter les points de squelette
    img = poseDetector.findPose(img, draw=True)
    lmList = poseDetector.findPosition(img, draw=False)
    # Dessiner des axes sur l'image
    drw.axes(img)

    # Dupliquer l'image : une image pour l'analyse de position + une image pour l'analyse de acceleration
    img_acceleration = img.copy()
    img_position = img.copy()

    # Dessiner les points de squelette
    img_acceleration = poseDetector.drawLm(img_acceleration, "all pts", ptsOfInterest=True, couleur=couleur_alarme_acceleration)
    img_position = poseDetector.drawLm(img_position, "all pts", ptsOfInterest=True, couleur=couleur_alarme_position)

    ###############################
    # ----- DETECTION DE CHUTE
    if (len(lmList) > 0):

        # Récupération des coordonnées des points de corps
        dict_joint_point["Head"] = lmList[0][1:]
        dict_joint_point["ShoulderCenter"] = poseDetector.findCenter(img_position, 11, 12, draw=False)
        dict_joint_point["HipCenter"] = poseDetector.findCenter(img_position, 23, 24, draw=False)
        dict_joint_point["AnkleLeft"] = lmList[27][1:]
        dict_joint_point["AnkleRight"] = lmList[28][1:]

        # @ Détection de chute via position des points en y
        Head_Ankle1, Head_Ankle2, thr, bool_alarme_position = fallDetector.PersonFallingDown_position(dict_joint_point["Head"][1],
                                                                     dict_joint_point["ShoulderCenter"][1],
                                                                     dict_joint_point["HipCenter"][1],
                                                                     dict_joint_point["AnkleLeft"][1],
                                                                     dict_joint_point["AnkleRight"][1],
                                                                     Head_Ankle1, Head_Ankle2, thr, seuil_position)

        dict_joint_point["Head_Ankle1"] = [0, Head_Ankle1]
        dict_joint_point["Head_Ankle2"] = [0, Head_Ankle2]

        # Dessiner l'analyse de cette détection de chute sur img_position
        drw.draw_PersonFallingDown_position_threshold(img_position, dict_joint_point["Head"],
                                                                     dict_joint_point["ShoulderCenter"],
                                                                     dict_joint_point["HipCenter"],
                                                                     dict_joint_point["AnkleLeft"],
                                                                     dict_joint_point["AnkleRight"],
                                                                     Head_Ankle1, Head_Ankle2, thr, seuil_position,
                                                                    couleur_seuil_position=couleur_seuil_position,
                                                                    couleur_seuil_position_thr=couleur_seuil_position_thr)

        # Application du filtre de Kalman sur chaque point
        dict_KF_etats = {}
        for nom_point, KF in dict_KF_points.items():
            if nom_point == "Head_Ankle1" or nom_point == "Head_Ankle2":
                continue
            # Prédiction de l'état du point
            dict_KF_etats[nom_point] = KF.predict().astype(np.int32)
            # Récupération des coordonnées du point à partir de l'état prédit
            x, y = int(dict_KF_etats[nom_point][0]), int(dict_KF_etats[nom_point][1])
            vx, vy = int(dict_KF_etats[nom_point][2]), int(dict_KF_etats[nom_point][3])
            ax, ay = int(dict_KF_etats[nom_point][4]), int(dict_KF_etats[nom_point][5])
            # Dessiner les points de Kalman sur img_acceleration
            drw.draw_KF_state(img_acceleration, (x, y), (ax, ay))

            KF.update(np.expand_dims([dict_joint_point[nom_point][0], dict_joint_point[nom_point][1]], axis=-1))

        # @ Détection de chute via acceleration des points en y
        bool_alarme_acceleration = fallDetector.PersonFallingDown_acceleration(int(dict_KF_etats["Head"][3]),
                                                   int(dict_KF_etats["ShoulderCenter"][3]),
                                                   int(dict_KF_etats["HipCenter"][3]),
                                                   int(dict_KF_etats["AnkleLeft"][3]),
                                                   int(dict_KF_etats["AnkleRight"][3]),
                                                   seuil_acceleration)

    ###############################
    # ----- ALARME
    if bool_alarme_acceleration:
        couleur_alarme_acceleration = (0, 0, 255)
        cv2.putText(img_acceleration, "ALARME", (img.shape[1] - 80, 20), cv2.FONT_HERSHEY_PLAIN, 1, couleur_alarme_acceleration, 2)
    else:
        couleur_alarme_acceleration = (255, 0, 0)

    if bool_alarme_position:
        couleur_alarme_position = (0, 0, 255)
        cv2.putText(img_position, "ALARME", (img.shape[1] - 80, 20), cv2.FONT_HERSHEY_PLAIN, 1, couleur_alarme_position, 2)
    else:
        couleur_alarme_position = (255, 0, 0)

    # Etat de la chute
    bool_etat_chute = int(bool_alarme_position and bool_alarme_acceleration)

    ###############################
    # ----- ENREGISTREMENT DE LA CHUTE

    if bool_etat_chute:
        cv2.putText(frame, "CHUTE !", (img.shape[1] - 80, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 2)
        if modesave:
            # Enregistrement de la première frame en PNG
            cv2.imwrite("sauvegarde/chute.png", frame)
            # Création de la vidéo
            if fichier_video is None:
                fichier_video = os.path.join(dir_videos, time.strftime("%Y_%m_%d_%H_%M_%S") + ".avi")
                video = cv2.VideoWriter(fichier_video, cv2.VideoWriter_fourcc(*'DIVX'), 15, (img.shape[1], img.shape[0]))
            # Enregistrement de la frame dans la vidéo
            video.write(frame)
            # Initilisation du compteur
            cpt_fin_mouvement = fin_mouvement
    else:
        if modesave:
            # Décrémentation du compteur
            cpt_fin_mouvement = cpt_fin_mouvement - 1
            if fichier_video is not None:
                # Arrêt de l'enregistrement
                if cpt_fin_mouvement == 0:
                    video.release()
                    fichier_video = None
                    # sending message
                    #message = client.messages.create(body='Attention, une personne est tombée ! Les secours ont été prévenu ! ',
                    #                                 from_="+16088893302", to="+33620023990")
                # On continue l'enregistrement tant que le compteur n'est pas nul
                else:
                    cv2.putText(frame, "CHUTE !", (img.shape[1] - 80, 20), cv2.FONT_HERSHEY_PLAIN, 1, couleur_fin_alarme, 2)
                    cv2.putText(frame, "Sauvegarde...", (img.shape[1] - 80, 30), cv2.FONT_HERSHEY_PLAIN, 0.7, couleur_fin_alarme, 1)
                    # Enregistrement de la frame dans la vidéo
                    video.write(frame)

    ###############################
    # Envoi requête sur Rasberry
    # if bool_etat_chute:
    #     url = "http://192.168.43.204/set_chute.php?chute=true"
    #     # Envoi de la requête HTTP POST avec la variable
    #     response = requests.get(url)
    #     # Vérification de la réponse
    #     if response.status_code == 200:
    #         print("Variable envoyée avec succès")
    #     else:
    #         print("Erreur lors de l'envoi de la variable")

    ###############################
    # ---- FENETRES D'ANALYSES DE LA CHUTE

    coef = img.shape[0]/graph_temporelle_hauteur

    # Fenêtre graph acceleration de chaque points
    fenetre_acceleration = drw.barre_infos(fenetre_analytic_largeur, barre_infos_hauteur, texte=f"[p|m]Seuil_acceleration: {seuil_acceleration}")
    # A partir de chaque point et de son historique, on va dessiner le graphique temporelle
    for (nom_point, etat), (nom_historique, historique) in zip(dict_KF_etats.items(),
                                                                dict_historique_acceleration.items()):
        # définition des différents seuils
        addseuil = False if nom_point=="AnkleLeft" or nom_point=="AnkleRight" else True
        s = seuil_acceleration*0.50 if nom_point=="ShoulderCenter" else seuil_acceleration*0.30 if nom_point=="HipCenter" else 0 if nom_point=="AnkleLeft" or nom_point=="AnkleRight" else seuil_acceleration

        # définition des modes neg ou non
        negmode = 1

        # Réactualiser l'historique + traçage du graph
        dict_historique_acceleration[nom_historique], graph_temporelle_acceleration = drw.graph_temporelle(
            fenetre_analytic_largeur, graph_temporelle_hauteur,
            nom_variable="ay_" + nom_point,
            variable=int(etat[3]), texte_seuil=f"seuil_a : {s}", seuil=s, historique=historique, coef=coef/3,
            couleur_fond=couleur_fond, addseuil=addseuil, couleur_seuil=couleur_seuil_position, negatifvaluemode=negmode)
        # Concaténation des fenêtres
        fenetre_acceleration = drw.regrouper_fenetre(fenetre_acceleration, graph_temporelle_acceleration)
        barre_separation = drw.barre_infos(fenetre_analytic_largeur, 3, texte="")
        fenetre_acceleration = drw.regrouper_fenetre(fenetre_acceleration, barre_separation)

    # Fenêtre graph booléen alarme acceleration
    historique_bool_alarme_acceleration, graph_temporelle_bool_alarme_acceleration = drw.graph_temporelle(fenetre_analytic_largeur,
                                                                                        graph_temporelle_hauteur,
                                                                                        nom_variable="bool_alarme_acceleration",
                                                                                        variable=bool_alarme_acceleration,
                                                                                        texte_seuil="", seuil=0,
                                                                                        historique=historique_bool_alarme_acceleration,
                                                                                        coef=coef / 100,
                                                                                        couleur_fond=(0, 0, 0),
                                                                                        negatifvaluemode=0)
    # Concaténation des graph des points + graph du booléen alarme acceleration
    fenetre_acceleration = drw.regrouper_fenetre(fenetre_acceleration, graph_temporelle_bool_alarme_acceleration)


    # Fenêtre graph position de chaque points
    fenetre_position = drw.barre_infos(fenetre_analytic_largeur, barre_infos_hauteur, texte=f"[o|l]Seuil_position: {seuil_position}")
    # A partir de chaque point et de son historique, on va dessiner le graphique temporelle
    for (nom_point,point),(nom_historique, historique) in zip(dict_joint_point.items(), dict_historique_position.items()):
        # définition des différents seuils
        addseuil = False if nom_point == "Head_Ankle1" or nom_point == "Head_Ankle2" else True
        # définition des modes neg ou non
        negmode = 1 if nom_point == "Head_Ankle1" or nom_point == "Head_Ankle2" else 0
        # Réactualiser l'historique + traçage du graph
        dict_historique_position[nom_historique], graph_temporelle_position = drw.graph_temporelle(fenetre_analytic_largeur, graph_temporelle_hauteur,
                                                                    nom_variable="y_"+nom_point,
                                                                    variable=point[1], texte_seuil=f"seuil_p : {seuil_position}", seuil=seuil_position, historique=historique, coef=coef,
                                                                    couleur_fond=couleur_fond, addseuil=addseuil, couleur_seuil=couleur_seuil_position, negatifvaluemode=negmode)
        # Concaténation des fenêtres
        fenetre_position = drw.regrouper_fenetre(fenetre_position, graph_temporelle_position)
        barre_separation = drw.barre_infos(fenetre_analytic_largeur, 3, texte="")
        fenetre_position = drw.regrouper_fenetre(fenetre_position, barre_separation)

    historique_diff_Head_Ankle, graph_temporelle_diff_Head_Ankle = drw.graph_temporelle(fenetre_analytic_largeur, graph_temporelle_hauteur,
                                                                                        nom_variable="Head_Ankle1-Head_Ankle2",variable=Head_Ankle1-Head_Ankle2,
                                                                                        texte_seuil=f"thr : {round(thr,2)}", seuil=thr, historique=historique_diff_Head_Ankle, coef=coef,
                                                                                        couleur_fond=couleur_fond,couleur_seuil=couleur_seuil_position_thr,negatifvaluemode=0)
    fenetre_position = drw.regrouper_fenetre(fenetre_position, graph_temporelle_diff_Head_Ankle)

    # Fenêtre graph booléen alarme acceleration
    historique_bool_alarme_position, graph_temporelle_bool_alarme_position = drw.graph_temporelle(fenetre_analytic_largeur, graph_temporelle_hauteur,
                                                                                        nom_variable="bool_alarme_position",variable=bool_alarme_position,
                                                                                        texte_seuil="", seuil=0, historique=historique_bool_alarme_position, coef=coef/100,
                                                                                        couleur_fond=(0,0,0),negatifvaluemode=0)
    # Concaténation des graph des points + graph du booléen alarme position
    fenetre_position = drw.regrouper_fenetre(fenetre_position, graph_temporelle_bool_alarme_position)


    ###############################
    # ---- Affichage des fenêtres
    cv2.imshow("Image de sortie", frame)
    cv2.imshow("Analyse position", fenetre_position)
    cv2.imshow("Analyse acceleration", fenetre_acceleration)
    cv2.imshow("Image position", img_position)
    cv2.imshow("Image acceleration", img_acceleration)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    # Commandes
    seuil_acceleration += 1 if key == ord('p') else 10 if key == ord('P') else 0
    seuil_acceleration = max(-100, seuil_acceleration - 1) if key == ord('m') else max(-100, seuil_acceleration - 10) if key == ord(
        'M') else seuil_acceleration
    seuil_position += 1 if key == ord('o') else 10 if key == ord('O') else 0
    seuil_position = max(10, seuil_position - 1) if key == ord('l') else max(10, seuil_position - 10) if key == ord('L') else seuil_position


cap.release()
cv2.destroyAllWindows()



