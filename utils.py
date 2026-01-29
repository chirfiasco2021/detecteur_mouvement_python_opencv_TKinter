import cv2

def redimensionner(image, width=None, height=None):
    """
    Redimensionne une image en gardant les proportions.
    Utile pour créer un dashboard propre.
    """
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        # On calcule le ratio basé sur la hauteur
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        # On calcule le ratio basé sur la largeur
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
