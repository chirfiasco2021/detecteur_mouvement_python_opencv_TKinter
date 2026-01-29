import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import datetime
import numpy as np
import os  # <--- NOUVEAU
import time  # <--- NOUVEAU

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
        self.current_view = "grid"

        # --- GESTION ENREGISTREMENT (NOUVEAU) ---
        self.is_recording = False
        self.out = None
        self.last_motion_time = 0
        self.buffer_time = 5  # Continuer d'enregistrer 5s après la fin du mouvement

        # Création du dossier pour les vidéos
        if not os.path.exists("enregistrements"):
            os.makedirs("enregistrements")

        # --- 2. FRONTEND ---
        self.creer_layout_principal()

        # --- 3. DÉMARRAGE ---
        self.delay = 15
        self.update()
        self.window.mainloop()

    def creer_layout_principal(self):
        # ... (CETTE PARTIE NE CHANGE PAS, je la raccourcis ici pour la lisibilité) ...
        # === Copie exactement la même fonction creer_layout_principal que tu avais avant ===
        # Si tu as un doute, reprends celle du code précédent, elle est identique.

        # (Pour être sûr que tu aies un code qui marche direct, je remets le bloc complet ici :)
        self.main_container = tk.Frame(self.window, bg="black")
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.frame_grid = tk.Frame(self.main_container, bg="black")
        self.lbl_cam1 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam1.grid(row=0, column=0, padx=2, pady=2)
        self.lbl_cam2 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam2.grid(row=0, column=1, padx=2, pady=2)
        self.lbl_cam3 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam3.grid(row=1, column=0, padx=2, pady=2)
        self.lbl_cam4 = tk.Label(self.frame_grid, bg="black", bd=2, relief="sunken")
        self.lbl_cam4.grid(row=1, column=1, padx=2, pady=2)
        self.frame_zoom = tk.Frame(self.main_container, bg="black")
        self.lbl_zoom = tk.Label(self.frame_zoom, bg="black")
        self.lbl_zoom.pack(expand=True, fill=tk.BOTH)
        self.sidebar = tk.Frame(self.window, bg="#f0f0f0", width=300, relief="raised", bd=1)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="PANNEAU DE\nCONTRÔLE", font=("Segoe UI", 16, "bold"), bg="#f0f0f0",
                 fg="#333").pack(pady=20)

        # Indicateur d'enregistrement (Petit ajout visuel)
        self.lbl_rec = tk.Label(self.sidebar, text="⚫ STANDBY", fg="gray", bg="#f0f0f0", font=("Segoe UI", 12, "bold"))
        self.lbl_rec.pack(pady=5)

        frame_vues = tk.LabelFrame(self.sidebar, text="Mode d'affichage", bg="#f0f0f0", font=("Segoe UI", 10, "bold"))
        frame_vues.pack(fill=tk.X, padx=15, pady=10)
        btn_grid = tk.Button(frame_vues, text="⊞ Vue Grille (Dashboard)", command=lambda: self.changer_mode("grid"),
                             bg="#ddd")
        btn_grid.pack(fill=tk.X, padx=5, pady=2)
        btn_focus_orig = tk.Button(frame_vues, text="🔍 Focus : Caméra Live",
                                   command=lambda: self.changer_mode("focus_original"), bg="#b3e5fc")
        btn_focus_orig.pack(fill=tk.X, padx=5, pady=2)
        btn_focus_algo = tk.Button(frame_vues, text="👁️ Focus : Vision Ordi",
                                   command=lambda: self.changer_mode("focus_algo"), bg="#c8e6c9")
        btn_focus_algo.pack(fill=tk.X, padx=5, pady=2)
        frame_reglages = tk.LabelFrame(self.sidebar, text="Sensibilité", bg="#f0f0f0")
        frame_reglages.pack(fill=tk.X, padx=15, pady=10)
        self.scale_seuil = tk.Scale(frame_reglages, from_=5, to=100, orient=tk.HORIZONTAL, bg="#f0f0f0")
        self.scale_seuil.set(config.THRESHOLD_VALUE)
        self.scale_seuil.pack(fill=tk.X, padx=10, pady=5)
        self.btn_reset = tk.Button(self.sidebar, text="⚡ Recalibrer le Fond", command=self.reset_fond, bg="#ff9800",
                                   fg="white", font=("Segoe UI", 10, "bold"))
        self.btn_reset.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(self.sidebar, text="Journal Système:", bg="#f0f0f0", anchor="w").pack(fill=tk.X, padx=15)
        self.text_log = tk.Text(self.sidebar, height=10, bg="white", font=("Consolas", 8), state='disabled')
        self.text_log.pack(fill=tk.BOTH, padx=15, pady=5, expand=True)
        tk.Button(self.sidebar, text="QUITTER", command=self.quitter, bg="#d32f2f", fg="white").pack(side=tk.BOTTOM,
                                                                                                     fill=tk.X, padx=15,
                                                                                                     pady=20)
        self.changer_mode("grid")

    def changer_mode(self, mode):
        self.current_view = mode
        self.frame_grid.pack_forget()
        self.frame_zoom.pack_forget()
        if mode == "grid":
            self.frame_grid.pack(fill=tk.BOTH, expand=True)
        else:
            self.frame_zoom.pack(fill=tk.BOTH, expand=True)

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

            # --- LOGIQUE D'ENREGISTREMENT ---
            mouvement_detecte = len(rectangles) > 0

            if mouvement_detecte:
                self.last_motion_time = time.time()  # On met à jour le timer

                if not self.is_recording:
                    # DÉMARRAGE DE L'ENREGISTREMENT
                    self.is_recording = True
                    self.lbl_rec.config(text="🔴 REC (MOUVEMENT)", fg="red")

                    # Nom du fichier avec date et heure
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"enregistrements/alert_{timestamp}.avi"

                    # Configuration Codec (XVID est standard pour .avi)
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    h, w, _ = frame.shape
                    self.out = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
                    self.log(f"Début enregistrement: {filename}")

            # Si on enregistre...
            if self.is_recording:
                # On écrit l'image brute (pas celle avec les carrés verts) dans le fichier
                self.out.write(frame)

                # Si plus de mouvement depuis X secondes, on coupe
                if time.time() - self.last_motion_time > self.buffer_time:
                    self.is_recording = False
                    self.out.release()  # On ferme le fichier proprement
                    self.out = None
                    self.lbl_rec.config(text="⚫ STANDBY", fg="gray")
                    self.log("Fin enregistrement (Temporisation écoulée).")

            # --- VISUELS (RECTANGLES) ---
            vue_originale = frame.copy()
            # On dessine les rectangles seulement pour l'affichage écran (pas pour la vidéo enregistrée)
            for (x, y, w, h) in rectangles:
                cv2.rectangle(vue_originale, (x, y), (x + w, y + h), config.COLOR_RECTANGLE, 2)
                # Petit ajout : indication visuelle sur l'image
                if self.is_recording:
                    cv2.circle(vue_originale, (20, 50), 10, (0, 0, 255), -1)  # Point rouge

            # --- Préparation des autres vues (Reste inchangé) ---
            if img_thresh is not None:
                vue_algo = img_thresh.copy()
            else:
                vue_algo = np.zeros_like(image_traitee)

            # --- Affichage Tkinter (Reste inchangé) ---
            if self.current_view == "grid":
                w_grid = 380
                self.ajouter_texte(vue_originale, "LIVE")
                self.imgtk1 = self.convertir_pour_tkinter(vue_originale, w_grid)
                self.lbl_cam1.configure(image=self.imgtk1)

                vue_gris = image_traitee.copy()
                self.ajouter_texte(vue_gris, "INPUT (GRIS)", (255, 255, 255))
                self.imgtk2 = self.convertir_pour_tkinter(vue_gris, w_grid)
                self.lbl_cam2.configure(image=self.imgtk2)

                if img_delta is not None:
                    vue_delta = img_delta.copy()
                else:
                    vue_delta = np.zeros_like(image_traitee)
                self.ajouter_texte(vue_delta, "DELTA", (255, 255, 255))
                self.imgtk3 = self.convertir_pour_tkinter(vue_delta, w_grid)
                self.lbl_cam3.configure(image=self.imgtk3)

                self.ajouter_texte(vue_algo, "ALGO", (255, 255, 255))
                self.imgtk4 = self.convertir_pour_tkinter(vue_algo, w_grid)
                self.lbl_cam4.configure(image=self.imgtk4)

            else:
                w_zoom = 780
                if self.current_view == "focus_original":
                    image_a_afficher = vue_originale
                    self.ajouter_texte(image_a_afficher, "FOCUS : CAMERA LIVE", (0, 255, 255))
                elif self.current_view == "focus_algo":
                    image_a_afficher = vue_algo
                    self.ajouter_texte(image_a_afficher, "FOCUS : ALGORITHME", (0, 255, 255))

                self.imgtk_zoom = self.convertir_pour_tkinter(image_a_afficher, w_zoom)
                self.lbl_zoom.configure(image=self.imgtk_zoom)

        self.window.after(self.delay, self.update)

    def quitter(self):
        # Sécurité : Si on enregistre en quittant, on sauvegarde d'abord
        if self.is_recording and self.out is not None:
            self.out.release()
        self.camera.liberer()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SurveillanceApp(root, "Security Center v4.0 (REC)")