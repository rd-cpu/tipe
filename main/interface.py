import tkinter as tk
from tkinter import filedialog, messagebox
from messagerie_final import *

class CryptoApp:
    def __init__(self, root):
        chemin_fichier_message_crypte = nom_fichier_message_crypte(CEstand)
        chemin_fichier_dico_direct = nom_fichier_dico_direct(CEstand)
        chemin_fichier_dico_recip = nom_fichier_dico_recip(CEstand)

        self.root = root
        self.root.title("Cryptographie El Gamal sur Courbes Elliptiques")
        self.root.geometry("600x500")

        # Frame pour l'envoyeur
        self.frame_envoyeur = tk.LabelFrame(root, text="Envoyeur", padx=10, pady=10)
        self.frame_envoyeur.pack(padx=10, pady=10, fill="both")

        tk.Label(self.frame_envoyeur, text="Message à envoyer :").grid(row=0, column=0, sticky="w")
        self.message_entry = tk.Entry(self.frame_envoyeur, width=40)
        self.message_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.frame_envoyeur, text="Dictionnaire direct :").grid(row=1, column=0, sticky="w")
        self.dico_direct_entry = tk.Entry(self.frame_envoyeur, width=40)
        self.dico_direct_entry.grid(row=1, column=1, padx=5, pady=5)
        self.dico_direct_entry.insert(0, chemin_fichier_dico_direct)
        tk.Button(self.frame_envoyeur, text="Parcourir", command=self.browse_dico_direct).grid(row=1, column=2, padx=5)


        tk.Label(self.frame_envoyeur, text="Fichier de sortie :").grid(row=2, column=0, sticky="w")
        self.fichier_sortie_entry = tk.Entry(self.frame_envoyeur, width=40)
        self.fichier_sortie_entry.grid(row=2, column=1, padx=5, pady=5)
        self.fichier_sortie_entry.insert(0, chemin_fichier_message_crypte)
        tk.Button(self.frame_envoyeur, text="Parcourir", command=self.browse_fichier_sortie).grid(row=2, column=2, padx=5)

        tk.Button(self.frame_envoyeur, text="Envoyer (Chiffrer)", command=self.envoyer).grid(row=3, column=0, columnspan=3, pady=10)

        # Frame pour le receveur
        self.frame_receveur = tk.LabelFrame(root, text="Receveur", padx=10, pady=10)
        self.frame_receveur.pack(padx=10, pady=10, fill="both")

        tk.Label(self.frame_receveur, text="Fichier message crypté :").grid(row=0, column=0, sticky="w")
        self.message_crypte_entry = tk.Entry(self.frame_receveur, width=40)
        self.message_crypte_entry.grid(row=0, column=1, padx=5, pady=5)
        self.message_crypte_entry.insert(0, chemin_fichier_message_crypte)
        tk.Button(self.frame_receveur, text="Parcourir", command=self.browse_message_crypte).grid(row=0, column=2, padx=5)

        tk.Label(self.frame_receveur, text="Dictionnaire réciproque :").grid(row=1, column=0, sticky="w")
        self.dico_recip_entry = tk.Entry(self.frame_receveur, width=40)
        self.dico_recip_entry.grid(row=1, column=1, padx=5, pady=5)
        self.dico_recip_entry.insert(0, chemin_fichier_dico_recip)
        tk.Button(self.frame_receveur, text="Parcourir", command=self.browse_dico_recip).grid(row=1, column=2, padx=5)

        tk.Button(self.frame_receveur, text="Recevoir (Déchiffrer)", command=self.recevoir).grid(row=2, column=0, columnspan=3, pady=10)

        # Zone de résultat
        self.result_label = tk.Label(root, wraplength=500, justify="left")
        self.result_label.pack(pady=10)

    def browse_dico_direct(self):
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if fichier:
            self.dico_direct_entry.delete(0, tk.END)
            self.dico_direct_entry.insert(0, fichier)

    def browse_fichier_sortie(self):
        fichier = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Fichiers texte", "*.txt")])
        if fichier:
            self.fichier_sortie_entry.delete(0, tk.END)
            self.fichier_sortie_entry.insert(0, fichier)

    def browse_message_crypte(self):
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if fichier:
            self.message_crypte_entry.delete(0, tk.END)
            self.message_crypte_entry.insert(0, fichier)

    def browse_dico_recip(self):
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])
        if fichier:
            self.dico_recip_entry.delete(0, tk.END)
            self.dico_recip_entry.insert(0, fichier)

    def envoyer(self):
        try:
            message = self.message_entry.get()
            dico_direct = self.dico_direct_entry.get()
            fichier_sortie = self.fichier_sortie_entry.get()
            if not message or not dico_direct or not fichier_sortie:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return
            envoyeur(message, cle_publique, CEstand)
            self.result_label.config(text=f"Message chiffré sauvegardé dans '{fichier_sortie}'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chiffrement : {str(e)}")

    def recevoir(self):
        try:
            message_crypte = self.message_crypte_entry.get()
            dico_recip = self.dico_recip_entry.get()
            if not message_crypte or not dico_recip:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return
            message_dechiffre = receveur(CEstand, cle_secrete)
            self.result_label.config(text=f"Message déchiffré : {message_dechiffre}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du déchiffrement : {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()