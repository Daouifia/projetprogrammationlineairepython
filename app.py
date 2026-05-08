
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

from solver import resoudre
from graph import creer_graphique

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Optimisation Nutritionnelle")
        self.geometry("1100x700")
        self.resizable(False, False)

        # Stocker les derniers résultats pour le graphique
        self.last_result = None
        self.last_apports = None
        self.last_besoins = None
        self.last_couts = None

        # ===== FRAME PRINCIPALE =====
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Colonne gauche (saisie) et colonne droite (résultats)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):

        left = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#F0F4FF")
        left.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="nsew")

        # Titre
        ctk.CTkLabel(
            left,
            text="📥  Données du Problème",
            font=("Arial", 18, "bold"),
            text_color="#1D3557"
        ).grid(row=0, column=0, columnspan=3, pady=(18, 8))

        # ── Coûts ──
        ctk.CTkLabel(
            left, text="Coûts des aliments (dh)",
            font=("Arial", 14, "bold"), text_color="#457B9D"
        ).grid(row=1, column=0, columnspan=3, pady=(10, 4))

        self.cost_entries = []
        for i in range(3):
            entry = ctk.CTkEntry(
                left, width=110, height=35,
                placeholder_text=f"Coût x{i+1}"
            )
            entry.grid(row=2, column=i, padx=12, pady=5)
            self.cost_entries.append(entry)

        # Valeurs par défaut du rapport
        for val, entry in zip([4, 6, 5], self.cost_entries):
            entry.insert(0, str(val))

        # ── Apports nutritionnels ──
        ctk.CTkLabel(
            left, text="Apports Nutritionnels  (matrice 3×3)",
            font=("Arial", 14, "bold"), text_color="#457B9D"
        ).grid(row=3, column=0, columnspan=3, pady=(16, 4))

        headers = ["x₁", "x₂", "x₃"]
        nutriments = ["Protéines", "Vitamines", "Minéraux"]
        for j, h in enumerate(headers):
            ctk.CTkLabel(left, text=h, font=("Arial", 11, "bold"),
                         text_color="#2A9D8F").grid(row=4, column=j, pady=2)

        self.nutrition_entries = []
        default_nutrition = [
            [10, 20, 15],
            [10,  5,  8],
            [10,  8, 12],
        ]
        for i in range(3):
            row_entries = []
            ctk.CTkLabel(left, text=nutriments[i], font=("Arial", 10),
                         text_color="#1D3557").grid(row=5+i, column=0, padx=(10,2))
            for j in range(3):
                entry = ctk.CTkEntry(
                    left, width=80, height=32,
                    placeholder_text=f"a{i+1}{j+1}"
                )
                entry.grid(row=5+i, column=j, padx=6, pady=5)
                entry.insert(0, str(default_nutrition[i][j]))
                row_entries.append(entry)
            self.nutrition_entries.append(row_entries)

        # ── Besoins minimaux ──
        ctk.CTkLabel(
            left, text="Besoins Minimaux",
            font=("Arial", 14, "bold"), text_color="#457B9D"
        ).grid(row=8, column=0, columnspan=3, pady=(16, 4))

        self.need_entries = []
        for i, val in enumerate([60, 40, 50]):
            entry = ctk.CTkEntry(
                left, width=110, height=35,
                placeholder_text=f"B{i+1}"
            )
            entry.grid(row=9, column=i, padx=12, pady=5)
            entry.insert(0, str(val))
            self.need_entries.append(entry)

        # ── Boutons ──
        ctk.CTkButton(
            left, text="▶  Résoudre", width=200, height=42,
            font=("Arial", 14, "bold"),
            fg_color="#2A9D8F", hover_color="#1F7A6D",
            command=self.lancer_resolution
        ).grid(row=10, column=0, columnspan=3, pady=(20, 8))

        ctk.CTkButton(
            left, text="📊  Voir le Graphique", width=200, height=38,
            font=("Arial", 13),
            fg_color="#457B9D", hover_color="#345F7A",
            command=self.afficher_graphique
        ).grid(row=11, column=0, columnspan=3, pady=(0, 18))

    def create_right_panel(self):

        right = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#F8F9FA")
        right.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="nsew")

        ctk.CTkLabel(
            right,
            text="📤  Résultats",
            font=("Arial", 18, "bold"),
            text_color="#1D3557"
        ).pack(pady=(18, 10))

        # Zone de texte pour afficher les résultats
        self.result_box = ctk.CTkTextbox(
            right, width=420, height=420,
            font=("Courier", 13),
            fg_color="white", text_color="#1D3557",
            corner_radius=12
        )
        self.result_box.pack(padx=20, pady=10)
        self.result_box.insert("end", "Les résultats s'afficheront ici\naprès avoir cliqué sur Résoudre.")
        self.result_box.configure(state="disabled")

        # Bouton réinitialiser
        ctk.CTkButton(
            right, text="🔄  Réinitialiser", width=180, height=36,
            font=("Arial", 12),
            fg_color="#E63946", hover_color="#B52A35",
            command=self.reinitialiser
        ).pack(pady=(10, 18))


    def valider_donnees(self):
        try:
            couts = [float(e.get()) for e in self.cost_entries]
            nutrition = [[float(e.get()) for e in row] for row in self.nutrition_entries]
            besoins = [float(e.get()) for e in self.need_entries]

            for v in couts + besoins:
                if v < 0:
                    raise ValueError("Valeur négative détectée")
            for row in nutrition:
                for v in row:
                    if v < 0:
                        raise ValueError("Valeur négative détectée")

            return couts, nutrition, besoins

        except ValueError:
            messagebox.showerror(
                "Erreur de saisie",
                "Veuillez entrer uniquement des nombres positifs."
            )
            return None

    def lancer_resolution(self):
        donnees = self.valider_donnees()
        if donnees is None:
            return

        couts, nutrition, besoins = donnees

        # Appel du solver
        resultat = resoudre(couts, nutrition, besoins)

        # Sauvegarder pour le graphique
        self.last_result  = resultat
        self.last_couts   = couts
        self.last_apports = [tuple(row) for row in nutrition]
        self.last_besoins = besoins

        # Afficher les résultats
        self.afficher_resultats(resultat, couts)

    # ============================================================
    # AFFICHAGE DES RÉSULTATS
    # ============================================================
    def afficher_resultats(self, resultat, couts):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")

        if resultat['succes']:
            q = resultat['quantites']
            z = resultat['cout_total']
            texte = (
                "═══════════════════════════════\n"
                "   ✅  SOLUTION OPTIMALE\n"
                "═══════════════════════════════\n\n"
                f"  x₁ (Aliment A)  =  {q[0]:.4f}\n"
                f"  x₂ (Aliment B)  =  {q[1]:.4f}\n"
                f"  x₃ (Aliment C)  =  {q[2]:.4f}\n\n"
                "───────────────────────────────\n"
                f"  Coût minimal    =  {z:.4f} dh\n"
                "───────────────────────────────\n\n"
                "  Vérification des contraintes :\n\n"
            )

            nutrition = [list(row) for row in self.last_apports]
            besoins   = self.last_besoins
            noms      = ["Protéines ", "Vitamines ", "Minéraux  "]
            for i in range(3):
                valeur = sum(nutrition[i][j] * q[j] for j in range(3))
                ok = "✅" if valeur >= besoins[i] - 0.001 else "❌"
                texte += f"  {noms[i]}: {valeur:.2f} ≥ {besoins[i]}  {ok}\n"

            texte += "\n═══════════════════════════════"
        else:
            texte = (
                "═══════════════════════════════\n"
                "   ❌  AUCUNE SOLUTION\n"
                "═══════════════════════════════\n\n"
                f"  {resultat['message']}\n\n"
                "  Vérifiez vos données et\n"
                "  réessayez.\n"
                "═══════════════════════════════"
            )

        self.result_box.insert("end", texte)
        self.result_box.configure(state="disabled")

    # ============================================================
    # AFFICHER LE GRAPHIQUE
    # ============================================================
    def afficher_graphique(self):
        if self.last_result is None or not self.last_result['succes']:
            messagebox.showwarning(
                "Graphique indisponible",
                "Veuillez d'abord résoudre le problème avec succès."
            )
            return

        # Nouvelle fenêtre pour le graphique
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Graphique — Région Réalisable & Solution Optimale")
        fenetre.geometry("700x580")
        fenetre.resizable(False, False)

        ctk.CTkLabel(
            fenetre,
            text="Visualisation Graphique",
            font=("Arial", 16, "bold"),
            text_color="#1D3557"
        ).pack(pady=(12, 4))


        fig, canvas = creer_graphique(
            couts   = self.last_couts,
            apports = self.last_apports,
            besoins = self.last_besoins,
            x_opt   = self.last_result['quantites'],
            z_opt   = self.last_result['cout_total'],
            master  = fenetre
        )

        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # ============================================================
    # RÉINITIALISER
    # ============================================================
    def reinitialiser(self):
        self.last_result  = None
        self.last_couts   = None
        self.last_apports = None
        self.last_besoins = None

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "Les résultats s'afficheront ici\naprès avoir cliqué sur Résoudre.")
        self.result_box.configure(state="disabled")

# ============================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()