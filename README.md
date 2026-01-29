# 📹 Security Center v3.0 - Python Computer Vision

Un système de surveillance vidéo intelligent développé en Python. Il utilise la vision par ordinateur pour détecter les mouvements, analyser les changements de pixels et afficher un tableau de bord de contrôle en temps réel.

## 🚀 Fonctionnalités

* **Détection de mouvement en temps réel** : Analyse les différences entre les frames vidéo.
* **Dashboard Multi-Vues** :
    * Vue Grille (4 écrans : Live, Gris, Delta, Seuil).
    * Mode Focus (Zoom sur une vue spécifique).
* **Algorithme Adaptatif** :
    * Réglage de la sensibilité en direct (Slider).
    * Recalibration du fond dynamique (Bouton Reset).
* **Interface Graphique (GUI)** : Interface complète construite avec Tkinter (Logs, Boutons, Contrôles).

## 🛠️ Installation

1.  **Cloner le projet**
    ```bash
    git clone [https://github.com/TON_NOM_UTILISATEUR/security-center-python.git](https://github.com/TON_NOM_UTILISATEUR/security-center-python.git)
    cd security-center-python
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Utilisation

Lancez simplement le fichier principal :

```bash
python main.py