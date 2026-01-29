import cv2
import numpy as np


#classe pour ouvrir la camera, lis les frames(images) et libere la camera a la fin
#la classe ne fait aucun traitement
class VideoCamera():
    def __init__(self, source=0): #sourcr=0 pour webcam par defaut, source=1 pour seconde camera et source ="video.mp4" fichier video
        self.source = source
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception("Impossible d'ouvrir la camera")


    def lire_frame(self):
        ret,frame = self.cap.read()
        if not ret:
            return None
        return frame


    def liberer(self):
        if self.cap.isOpened():
            self.cap.release()


