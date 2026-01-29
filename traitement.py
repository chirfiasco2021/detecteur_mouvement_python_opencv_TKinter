import cv2


def traitement_frame(frame):  # prends une image brute en entree et ensuite retourne une version pretraitee
    #  Etapes:
    # 1. convertion en niveaux de gris
    # 2.Application d'un flou gaussien
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)

    return blurred