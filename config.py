# Paramètres de la caméra
CAMERA_INDEX = 0  # 0 pour webcam, 1 pour externe, ou chemin "video.mp4"

# Paramètres du Flou (Traitement)
# Doit être un tuple impair, ex: (21, 21)
BLUR_KERNEL = (21, 21)

# Paramètres de la Détection
THRESHOLD_VALUE = 25  # Sensibilité (plus bas = plus sensible)
MIN_AREA = 500        # Taille min du mouvement pour être détecté

# Couleurs (Format BGR pour OpenCV)
COLOR_RECTANGLE = (0, 255, 0) # Vert
COLOR_TEXTE = (0, 0, 255)     # Rouge