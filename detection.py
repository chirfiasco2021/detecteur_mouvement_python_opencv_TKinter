import cv2

class DetecteurMouvement:
    def __init__(self, seuil_aire=500):
        # On initialise le fond à None
        self.fond = None
        # Surface minimum pour être considéré comme un mouvement (pour éviter le bruit)
        self.seuil_aire = seuil_aire

    def mettre_a_jour_fond(self, image_traitee):
        """Force la mise à jour du fond de référence"""
        self.fond = image_traitee

    # CORRECTION 1 : On ajoute "seuil_variable" dans les paramètres de la fonction
    def detecter(self, image_traitee, seuil_variable=25):
        """
        Compare l'image traitée avec le fond.
        """
        # Si c'est la première image, on l'enregistre comme fond
        if self.fond is None:
            self.fond = image_traitee
            return [], None, None

        # CORRECTION 2 : On retire "seuil_variable" d'ici. absdiff ne prend que 2 images.
        # 1. Différence absolue (Mathématiques : Image A - Image B)
        delta = cv2.absdiff(self.fond, image_traitee)

        # CORRECTION 3 : C'est ICI qu'on utilise le seuil variable venant du slider
        # 2. Seuillage (Logique : Si pixel > seuil_variable alors Blanc, sinon Noir)
        _, thresh = cv2.threshold(delta, seuil_variable, 255, cv2.THRESH_BINARY)

        # Dilatation pour boucher les trous (rend les contours plus solides)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # 3. Contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rectangles = []
        for c in contours:
            # On filtre les mouvements trop petits
            if cv2.contourArea(c) < self.seuil_aire:
                continue
            # On stocke les coordonnées du rectangle
            rect = cv2.boundingRect(c)
            rectangles.append(rect)

        return rectangles, thresh, delta