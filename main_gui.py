import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import datetime
import numpy as np

# Tes imports
import config
from video import VideoCamera
from traitement import traitement_frame
from detection import DetecteurMouvement
from utils import redimensionner


class SurveillanceApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1100x700")
        self.window.configure(bg="#e1e1e1")

        # --- 1. BACKEND ---
        self.camera = VideoCamera(source=config.CAMERA_INDEX)
        self.detecteur = DetecteurMouvement(seuil_aire=config.MIN_AREA)

        # État actuel de la vue : 'grid', 'focus_original', 'focus_algo'
        self.current_view = "grid"

        # --- 2. FRONTEND ---
        self.creer_layout_principal()

        # --- 3. DÉMARRAGE ---
        self.delay = 15
        self.update()
        self.window.mainloop()

    def creer_layout_principal(self):
        # === ZONE GAUCHE : LE CADRE PRINCIPAL ===
        # Ce cadre va contenir SOIT la grille, SOIT le zoom
        self.main_container = tk.Frame(self.window, bg="black")
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- SOUS-FRAME 1 : LA GRILLE (4 Écrans) ---
        self.frame_grid = tk.Frame(self.main_container, bg="black")
        # On ne la pack pas tout de suite, on laisse la fonction changer_mode le faire

        # Initialisation des 4 labels de la grille
        self.lbl_cam1 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam1.grid(row=0, column=0, padx=2, pady=2)
        self.lbl_cam2 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam2.grid(row=0, column=1, padx=2, pady=2)
        self.lbl_cam3 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam3.grid(row=1, column=0, padx=2, pady=2)
        self.lbl_cam4 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam4.grid(row=1, column=1, padx=2, pady=2)

        # --- SOUS-FRAME 2 : LE ZOOM (1 Grand Écran) ---
        self.frame_zoom = tk.Frame(self.main_container, bg="black")
        self.lbl_zoom = tk.Label(self.frame_zoom, bg="black")
        self.lbl_zoom.pack(expand=True, fill=tk.BOTH)

        # === ZONE DROITE : SIDEBAR ===
        self.sidebar = tk.Frame(self.window, bg="#f0f0f0", width=300, relief="raised", bd=1)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Titre
        tk.Label(self.sidebar, text="PANNEAU DE\nCONTRÔLE", font=("Segoe UI", 16, "bold"), bg="#f0f0f0",
                 fg="#333").pack(pady=20)

        # -- NOUVEAU : BOUTONS DE FOCUS --
        frame_vues = tk.LabelFrame(self.sidebar, text="Mode d'affichage", bg="#f0f0f0", font=("Segoe UI", 10, "bold"))
        frame_vues.pack(fill=tk.X, padx=15, pady=10)

        # Bouton Grille (Retour)
        btn_grid = tk.Button(frame_vues, text="⊞ Vue Grille (Dashboard)", command=lambda: self.changer_mode("grid"),
                             bg="#ddd")
        btn_grid.pack(fill=tk.X, padx=5, pady=2)

        # Bouton Focus Original
        btn_focus_orig = tk.Button(frame_vues, text="🔍 Focus : Caméra Live",
                                   command=lambda: self.changer_mode("focus_original"), bg="#b3e5fc")
        btn_focus_orig.pack(fill=tk.X, padx=5, pady=2)

        # Bouton Focus Algo
        btn_focus_algo = tk.Button(frame_vues, text="👁️ Focus : Vision Ordi",
                                   command=lambda: self.changer_mode("focus_algo"), bg="#c8e6c9")
        btn_focus_algo.pack(fill=tk.X, padx=5, pady=2)

        # -- Reste des contrôles (Comme avant) --
        frame_reglages = tk.LabelFrame(self.sidebar, text="Sensibilité", bg="#f0f0f0")
        frame_reglages.pack(fill=tk.X, padx=15, pady=10)
        self.scale_seuil = tk.Scale(frame_reglages, from_=5, to=100, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.scale_seuil.set(config.THRESHOLD_VALUE)
        self.scale_seuil.pack(fill=tk.X, padx=10, pady=5)

        self.btn_reset = tk.Button(self.sidebar, text="⚡ Recalibrer le Fond", command=self.reset_fond, bg="#ff9800",
                                   fg="white", font=("Segoe UI", 10, "bold"))
        self.btn_reset.pack(fill=tk.X, padx=15, pady=10)

        # Logs
        tk.Label(self.sidebar, text="Log Système:", bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=15)
        self.text_log = tk.Text(self.sidebar, height=10, bg="white", font=("Consolas", 8), state='disabled')
        self.text_log.pack(fill=tk.BOTH, padx=15, pady=5, expand=True)

        tk.Button(self.sidebar, text="QUITTER", command=self.quitter, bg="#d32f2f", fg="white").pack(side=tk.BOTTOM,
                                                                                                     fill=tk.X, padx=15,
                                                                                                     pady=20)

        # Initialisation du mode par défaut
        self.changer_mode("grid")

    def changer_mode(self, mode):
        """Cette fonction gère l'affichage/masquage des frames"""
        self.current_view = mode

        # On cache tout d'abord
        self.frame_grid.pack_forget()
        self.frame_zoom.pack_forget()

        if mode == "grid":
            self.frame_grid.pack(fill=tk.BOTH, expand=True)
            self.log("Mode : Grille Dashboard")
        else:
            self.frame_zoom.pack(fill=tk.BOTH, expand=True)
            if "original" in mode:
                self.log("Mode : Focus Caméra")
            else:
                self.log("Mode : Focus Algorithme")

    def reset_fond(self):
        self.detecteur.fond = None
        self.log("Calibration du fond effectuée.")

    def log(self, message):
        heure = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_log.config(state='normal')
        self.text_log.insert(tk.END, f"[{heure}] {message}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state='disabled')

    def convertir_pour_tkinter(self, image_opencv, width):
        img_small = redimensionner(image_opencv, width=width)
        if len(img_small.shape) == 2:
            img_rgb = cv2.cvtColor(img_small, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(image=Image.fromarray(img_rgb))

    def ajouter_texte(self, image, texte, couleur=(0, 255, 0)):
        cv2.putText(image, texte, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, couleur, 2)

    def update(self):
        frame = self.camera.lire_frame()

        if frame is not None:
            image_traitee = traitement_frame(frame)
            seuil_actuel = self.scale_seuil.get()
            rectangles, img_thresh, img_delta = self.detecteur.detecter(image_traitee, seuil_variable=seuil_actuel)

            # Préparation des images de base
            vue_originale = frame.copy()
            for (x, y, w, h) in rectangles:
                cv2.rectangle(vue_originale, (x, y), (x + w, y + h), config.COLOR_RECTANGLE, 2)

            # Gestion de l'image Algo (pour éviter le crash si None)
            if img_thresh is not None:
                vue_algo = img_thresh.copy()
            else:
                vue_algo = np.zeros_like(image_traitee)

            # --- LOGIQUE D'AFFICHAGE SELON LE MODE ---

            # CAS 1 : MODE GRILLE (On affiche les 4 petits écrans)
            if self.current_view == "grid":
                w_grid = 380  # Taille petite

                # Cam 1 (Originale)
                self.ajouter_texte(vue_originale, "LIVE")
                self.imgtk1 = self.convertir_pour_tkinter(vue_originale, w_grid)
                self.lbl_cam1.configure(image=self.imgtk1)

                # Cam 2 (Gris)
                vue_gris = image_traitee.copy()
                self.ajouter_texte(vue_gris, "INPUT (GRIS)", (255, 255, 255))
                self.imgtk2 = self.convertir_pour_tkinter(vue_gris, w_grid)
                self.lbl_cam2.configure(image=self.imgtk2)

                # Cam 3 (Delta)
                if img_delta is not None:
                    vue_delta = img_delta.copy()
                else:
                    vue_delta = np.zeros_like(image_traitee)
                self.ajouter_texte(vue_delta, "DELTA", (255, 255, 255))
                self.imgtk3 = self.convertir_pour_tkinter(vue_delta, w_grid)
                self.lbl_cam3.configure(image=self.imgtk3)

                # Cam 4 (Algo)
                self.ajouter_texte(vue_algo, "ALGO", (255, 255, 255))
                self.imgtk4 = self.convertir_pour_tkinter(vue_algo, w_grid)
                self.lbl_cam4.configure(image=self.imgtk4)

            # CAS 2 : MODE FOCUS (On affiche 1 grand écran)
            else:
                w_zoom = 780  # Taille grande

                if self.current_view == "focus_original":
                    image_a_afficher = vue_originale
                    self.ajouter_texte(image_a_afficher, "MODE FOCUS : CAMERA LIVE", (0, 255, 255))
                elif self.current_view == "focus_algo":
                    image_a_afficher = vue_algo
                    self.ajouter_texte(image_a_afficher, "MODE FOCUS : ALGORITHME", (0, 255, 255))

                self.imgtk_zoom = self.convertir_pour_tkinter(image_a_afficher, w_zoom)
                self.lbl_zoom.configure(image=self.imgtk_zoom)

        self.window.after(self.delay, self.update)

    def quitter(self):
        self.camera.liberer()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SurveillanceApp(root, "Security Center v3.0")