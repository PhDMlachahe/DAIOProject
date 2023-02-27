import cv2
import numpy as np
import math
import matplotlib

matplotlib.use("TkAgg")
from matplotlib import pyplot as plt


class Legend():

    def __init__(self, img):
        self.img = img
        self.hauteur, self.largeur = self.img.shape[0], self.img.shape[1]

    # Dessiner une barre vertical suivant un point
    def vline_following_point(self, texte, point, left_right=0, couleur=(0,0,0),taille_texte=0.75):
        x,y = point[0], point[1]
        texte = f'{texte} : {y}'
        if left_right:
            # On right
            cv2.putText(self.img, texte, (int(self.largeur*0.90), y - 5), cv2.FONT_HERSHEY_PLAIN, taille_texte, couleur, 1)
            cv2.line(self.img, (0, y), (self.largeur, y), couleur, 1)
        else:
            # On left
            cv2.putText(self.img, texte, (int(self.largeur*0.01), y - 5),
                        cv2.FONT_HERSHEY_PLAIN, taille_texte, couleur, 1)
            cv2.line(self.img, (0, y), (self.largeur, y), couleur, 1)

    # Dessiner une demi-barre vertical suivant un point
    def semi_vline_following_point(self, texte, point, left_right=0, couleur=(0,0,0), taille_texte=0.75):
        x,y = point[0], point[1]
        texte = f'{texte} : {y}'
        if left_right:
            # On right
            cv2.putText(self.img, texte, (int(self.largeur-len(texte)*self.largeur*0.015), y - 5), cv2.FONT_HERSHEY_PLAIN, taille_texte, couleur, 1)
            cv2.line(self.img, (self.largeur, y), (x, y), couleur, 1)
        else:
            # On left
            cv2.putText(self.img, texte, (int(self.largeur*0.01), y - 5),
                        cv2.FONT_HERSHEY_PLAIN, taille_texte, couleur, 1)
            cv2.line(self.img, (0, y), (x, y), couleur, 1)

    # Dessiner une demi-barre horizontal entre deux points
    def hline_between_ypoint(self, texte, point1, point2, left_right=0, couleur=(0,0,0), taille_texte=0.75):
        x1,y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        y = y2-y1
        texte = f'{texte} : {y}'
        if left_right:
            # On right
            cv2.putText(self.img, texte, (int(self.largeur-len(texte)*self.largeur*0.015), int((y1+y2) / 2)),
                        cv2.FONT_HERSHEY_PLAIN, taille_texte,
                        couleur, 1)
            cv2.line(self.img, (self.largeur, y2), (self.largeur, y1), couleur, 5)
        else:
            # On left
            cv2.putText(self.img, texte, (int(self.largeur * 0.01), int((y1+y2) / 2)),
                        cv2.FONT_HERSHEY_PLAIN, taille_texte,
                        couleur, 1)
            cv2.line(self.img, (0, y2), (0, y1), couleur, 5)



class Drawing():

    def __init__(self, fallstate=False):
        self.fallstate = fallstate

    # Dessiner des axes x et y sur l'image
    def axes(self, img):
        cv2.arrowedLine(img, (5, 5), (5, img.shape[0] - 5), color=(255, 255, 255), thickness=1, tipLength=0.01)
        cv2.putText(img, 'y', (10, img.shape[0] - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.arrowedLine(img, (5, 5), (img.shape[1] - 5, 5), color=(255, 255, 255), thickness=1, tipLength=0.01)
        cv2.putText(img, 'x', (img.shape[1] - 15, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    # Dessiner l'état du point : vitesse
    def draw_KF_state(self, img, position, vitesse, legend=False):

        # Pointer le point
        cv2.circle(img, position, 2, (0, 255, 0), 4)

        # Norme de la vitesse du point
        norme = lambda p: math.sqrt(p[0] ** 2 + p[1] ** 2)

        # Tracer une flèche pour l'accélération
        cv2.arrowedLine(img,
                        position,
                        (position[0] + vitesse[0], position[1] + vitesse[1]),
                        color=(0, 255, 0), thickness=2, tipLength=0.2)

        # Ajouter une légende
        if legend:
            cv2.putText(img, f'a = {round(norme(vitesse), 1)}',
                        (position[0] + vitesse[0] + 20, position[1] + vitesse[1]),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)



    # Visualiser les positions des points de squelette et les seuils, pour l'analyse de détection de chute via la position
    def draw_PersonFallingDown_position_threshold(self, img, lmHead, lmShoulderCenter, lmHipCenter, lmAnkleLeft, lmAnkleRight,
                                         Head_Ankle1, Head_Ankle2, thr, seuil,couleur_seuil_position=(0,100,255), couleur_seuil_position_thr=(50,50,255)):

        # légender les points d'interêts
        legend = Legend(img)

        legend.semi_vline_following_point("yHead", lmHead, left_right=1)
        legend.semi_vline_following_point("yShoulderCenter", lmShoulderCenter, left_right=0)
        legend.semi_vline_following_point("yHipCenter", lmHipCenter, left_right=0)
        legend.semi_vline_following_point("yAnkleLeft", lmAnkleLeft, left_right=0)
        legend.semi_vline_following_point("yAnkleRight", lmAnkleRight, left_right=1)

        legend.vline_following_point("thr", (0,int(round(thr,0))), left_right=0, couleur=couleur_seuil_position_thr)
        legend.vline_following_point("seuil", (0, seuil), left_right=0, couleur=couleur_seuil_position, taille_texte=0.75)

        legend.hline_between_ypoint("yHead-yAnkleRight", lmHead, lmAnkleRight, left_right=1, couleur=(0,0,0), taille_texte=0.75)
        #legend.hline_between_ypoint("Head_Ankle1-Head_Ankle2", (0,0), (0,Head_Ankle1-Head_Ankle2), left_right=0, couleur=(50, 50, 255),taille_texte=0.75)
        legend.vline_following_point("Head_Ankle1", (0, Head_Ankle1), left_right=0, couleur=couleur_seuil_position_thr, taille_texte=0.75)

    # Créer une barre d'inforamtion : une fenêtre avec un texte choisi
    def barre_infos(self, largeur, hauteur, texte, couleur_fond=(0,0,0), couleur_infos=(255, 255, 255)):
        barre_infos = np.full((hauteur, largeur, 3), couleur_fond, dtype=np.float32)
        position_texte = (int(barre_infos.shape[1]*0.01), int(barre_infos.shape[0]*0.6))
        taille_texte = 1 - barre_infos.shape[0] / 100
        texte = "/// "+texte if len(texte)>0 else ""
        cv2.putText(barre_infos, texte, position_texte, cv2.FONT_HERSHEY_PLAIN, taille_texte, couleur_infos, 1)
        return barre_infos

    # Visualiser l'évolution d'une variable au cours du temps : visualiser son historique
    def graph_temporelle(self, largeur, hauteur, nom_variable, variable, texte_seuil, seuil, historique, coef=5, addseuil=True, negatifvaluemode=1, couleur_seuil=(0,0,255),couleur_fond=(0,0,0)):
        # Historique
        historique = np.roll(historique, 1)
        historique[0] = int(variable / coef)
        # Seuil
        ligne_seuil = int(seuil / coef)

        graph_temporelle = np.full((hauteur, largeur, 3), couleur_fond, dtype=np.float32)

        # Pour chaque valeur dans l'historique
        for i in range(historique.shape[0]):
            couleur = (0, 0, 255) if historique[i] > ligne_seuil and addseuil else (0, 255, 0)

            # Mode affichage des valeurs positives et négatives
            if negatifvaluemode:
                barre_point_depart = (i, graph_temporelle.shape[0] // 2)
                barre_point_arrivee = (i, (graph_temporelle.shape[0] - historique[i]) // 2)
                ligne_seuil_point_depart = (0, (graph_temporelle.shape[0] - ligne_seuil) // 2)
                ligne_seuil_point_arrivee = (largeur, (graph_temporelle.shape[0] - ligne_seuil) // 2)
            # Mode affichage des valeurs positives
            else:
                barre_point_depart = (i, graph_temporelle.shape[0])
                barre_point_arrivee = (i, graph_temporelle.shape[0] - historique[i])
                ligne_seuil_point_depart = (0, graph_temporelle.shape[0] - ligne_seuil)
                ligne_seuil_point_arrivee = (largeur, graph_temporelle.shape[0] - ligne_seuil)

            # Tracer la barre horizontale
            cv2.line(graph_temporelle, barre_point_depart, barre_point_arrivee, couleur,1)

        if addseuil:
            # Tracer la barre horizontal du seuil
            cv2.line(graph_temporelle, ligne_seuil_point_depart, ligne_seuil_point_arrivee, couleur_seuil, 1)
            cv2.putText(graph_temporelle, texte_seuil, (ligne_seuil_point_arrivee[0]-100, ligne_seuil_point_arrivee[1]-1), cv2.FONT_HERSHEY_PLAIN, 0.75, couleur_seuil, 1)

        # Dessiner les axes
        cv2.arrowedLine(graph_temporelle, (5, graph_temporelle.shape[0] - 1), (5,5) , color=(255, 255, 255), thickness=1, tipLength=0.05)
        texte_variable = f'{nom_variable} : {variable}'
        cv2.putText(graph_temporelle, texte_variable, (10, 15), cv2.FONT_HERSHEY_PLAIN, 0.75, (255,255,255), 1)

        if negatifvaluemode:
            cv2.arrowedLine(graph_temporelle, (5, graph_temporelle.shape[0] // 2),
                            (graph_temporelle.shape[1] - 5, graph_temporelle.shape[0] // 2), color=(255, 255, 255),
                            thickness=1, tipLength=0.01)
            cv2.putText(graph_temporelle, "t", (graph_temporelle.shape[1] - 15, graph_temporelle.shape[0] // 2 - 8), cv2.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 1)
        else:
            cv2.arrowedLine(graph_temporelle, (5, graph_temporelle.shape[0]-1),
                            (graph_temporelle.shape[1] - 5, graph_temporelle.shape[0]-1), color=(255, 255, 255),
                            thickness=1, tipLength=0.01)
            cv2.putText(graph_temporelle, "t", (graph_temporelle.shape[1] - 15, graph_temporelle.shape[0] - 8),
                        cv2.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 1)

        return historique, graph_temporelle

    # Concatener deux fenêtres verticalement
    def regrouper_fenetre(self, block1, block2):
        fenetre = np.zeros((block1.shape[0] + block2.shape[0], block1.shape[1], block1.shape[2]), dtype=np.uint8)
        fenetre[:block1.shape[0], :, :] = block1
        fenetre[block1.shape[0]:, :, :] = block2
        return fenetre


    def histogramme(self, frame, nbr_classes=180, mode=0):
        if mode:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([frame], [0], None, [nbr_classes], [0, 256])
            label = "Intensité"
        else:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0], None, [nbr_classes], [0, 180])
            label = "Couleur"
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        plt.clf()
        plt.plot(hist)
        plt.title(label)
        plt.show(block=False)
        plt.pause(0.001)
