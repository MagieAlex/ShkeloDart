# Fortsetzung: Grafische Bracket-Darstellung und Integration in das Spielsystem

import tkinter as tk
from tkinter import ttk

class BracketWindow(tk.Toplevel):
    def __init__(self, master, bracket_data):
        super().__init__(master)
        self.title("🏆 Turnier-Bracket")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")

        canvas = tk.Canvas(self, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.bracket_frame = tk.Frame(canvas, bg="#f0f0f0")

        self.bracket_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.bracket_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True)
        scrollbar.pack(fill="x")

        self.draw_bracket(bracket_data)

    def draw_bracket(self, bracket_data):
        round_width = 150
        match_height = 60
        padding = 40

        for round_idx, round_matches in enumerate(bracket_data):
            for match_idx, match in enumerate(round_matches):
                x = round_idx * round_width + 20
                y = match_idx * match_height + padding * (2 ** round_idx)

                frame = tk.Frame(self.bracket_frame, bg="#ffffff", bd=2, relief="groove")
                frame.place(x=x, y=y, width=140, height=50)

                p1 = match.get("p1", "")
                p2 = match.get("p2", "")
                winner = match.get("winner", None)

                p1_label = tk.Label(frame, text=p1, font=("Arial", 10, "bold"), anchor="w",
                                    bg="#DFF0D8" if winner == p1 else "white")
                p1_label.pack(fill="x")

                p2_label = tk.Label(frame, text=p2, font=("Arial", 10, "bold"), anchor="w",
                                    bg="#DFF0D8" if winner == p2 else "white")
                p2_label.pack(fill="x")

# Integration in ShkeloDartApp (Anleitung):
# 1. Füge oben in shkelodart.py hinzu: from bracket_window import BracketWindow
# 2. Im __init__ der ShkeloDartApp:
#     self.bracket_data = []
#     self.current_round_matches = []
#     ...
#     self.bracket_button = tk.Button(master, text="📈 Turnierbaum anzeigen", command=self.show_bracket,
#                                     bg="#03A9F4", fg="white", font=("Arial", 10))
#     self.bracket_button.pack(pady=5)
# 3. Implementiere Methode in ShkeloDartApp:
#     def show_bracket(self):
#         if not self.bracket_data:
#             messagebox.showinfo("Hinweis", "Noch kein Turnierbaum vorhanden.")
#             return
#         BracketWindow(self.master, self.bracket_data)
# 4. Beim Start jeder Turnierrunde:
#     self.current_round_matches = []
#     self.bracket_data.append(self.current_round_matches)
# 5. Bei jedem Match (Freilos oder normal):
#     self.current_round_matches.append({"p1": p1, "p2": p2, "winner": None})
#     ...
#     self.current_round_matches.append({"p1": bye, "p2": "Freilos", "winner": bye})
# 6. Beim Sieg:
#     for m in self.current_round_matches:
#         if winner in (m["p1"], m["p2"]):
#             m["winner"] = winner
#             break
