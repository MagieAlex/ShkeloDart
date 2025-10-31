# ShkeloDart – Komplettes Spielsystem (normal + Turnier + Bracket + History + Gesamtsiege)

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import random
import json

from turnier_bracket import canvas


class BracketWindow(tk.Toplevel):
    def __init__(self, master, bracket_data):
        super().__init__(master)
        self.title("\U0001F3C6 Turnierbaum")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")

        # Erstelle ein Canvas und einen Scrollbar für die Darstellung
        canvas = tk.Canvas(self, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.bracket_frame = tk.Frame(canvas, bg="#f0f0f0")

        # Vergrößere den sichtbaren Bereich, wenn der Inhalt wächst
        self.bracket_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.bracket_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(fill="both", expand=True)
        scrollbar.pack(fill="x")

        self.draw_bracket(bracket_data)

    def draw_bracket(self, bracket_data):
        round_width = 170
        match_height = 60
        padding = 50
        vertical_spacing = 150  # Abstand zwischen den Runden

        for r_index, round_matches in enumerate(bracket_data):
            for m_index, match in enumerate(round_matches):
                # X-Position: Abhängig von der Runde
                x = r_index * round_width + 20
                # Y-Position: Abstand zwischen den Matches
                y = m_index * match_height + padding * (r_index + 1)

                # Erstelle das Frame für das Match
                frame = tk.Frame(self.bracket_frame, bg="#ffffff", bd=2, relief="groove")
                frame.place(x=x, y=y, width=150, height=50)

                p1 = match.get("p1", "")
                p2 = match.get("p2", "")
                winner = match.get("winner", None)

                # Hintergrundfarbe für Gewinner und Nicht-Gewinner
                bg1 = "#DFF0D8" if winner == p1 else "#F9F9F9" if p1 else "#CCCCCC"
                bg2 = "#DFF0D8" if winner == p2 else "#F9F9F9" if p2 else "#CCCCCC"

                # Label für den ersten Spieler
                tk.Label(frame, text=p1 or "❓", anchor="w", bg=bg1).pack(fill="x")
                # Label für den zweiten Spieler
                tk.Label(frame, text=p2 or "❓", anchor="w", bg=bg2).pack(fill="x")

        # Sicherstellen, dass das Canvas immer den gesamten Bereich anzeigt
        self.bracket_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))



class ShkeloDart:
    def __init__(self, master):
        self.master = master
        self.master.title("ShkeloDart 🎯")
        self.master.geometry("850x750")
        self.master.configure(bg="#f0f0f0")

        self.players = []
        self.scores = {}
        self.total_scores = {}
        self.history = []
        self.pairings = []
        self.bracket_data = []
        self.remaining_players = []
        self.tournament_bracket = []
        self.current_match = {}
        self.current_round_matches = []
        self.tournament_round = 1
        self.start_score = 501
        self.mode = "normal"

        self.setup_ui()
        self.load_history()
        self.load_totals()

    def setup_ui(self):
        self.top_frame = tk.Frame(self.master, bg="#f0f0f0")
        self.top_frame.pack(pady=10)

        self.entry = tk.Entry(self.top_frame, font=("Arial", 12), width=25)
        self.entry.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(self.top_frame, text="➕ Spieler hinzufügen", command=self.add_player,
                                    bg="#4CAF50", fg="white", font=("Arial", 10))
        self.add_button.pack(side=tk.LEFT)

        self.players_label = tk.Label(self.master, text="Spieler: ", font=("Arial", 11), bg="#f0f0f0")
        self.players_label.pack()

        self.start_button = tk.Button(self.master, text="🎮 Normales Spiel starten", command=self.start_normal_game,
                                      bg="#2196F3", fg="white", font=("Arial", 11))
        self.start_button.pack(pady=5)

        self.tournament_button = tk.Button(self.master, text="🏆 Turnier starten", command=self.setup_tournament,
                                           bg="#673AB7", fg="white", font=("Arial", 10))
        self.tournament_button.pack(pady=5)

        self.score_option = tk.IntVar(value=501)
        tk.Label(self.master, text="Startscore wählen:", bg="#f0f0f0").pack()
        for val in [301, 501, 701]:
            tk.Radiobutton(self.master, text=str(val), variable=self.score_option, value=val, bg="#f0f0f0").pack()

        self.match_label = tk.Label(self.master, text="", font=("Arial", 16, "bold"), pady=20, bg="#f0f0f0")
        self.match_label.pack()

        self.winner_frame = tk.Frame(self.master, bg="#f0f0f0")
        self.winner_frame.pack(pady=10)

        self.score_label = tk.Label(self.master, text="", font=("Arial", 12), bg="#f0f0f0")
        self.score_label.pack(pady=10)

        self.bracket_btn = tk.Button(self.master, text="📈 Turnierbaum anzeigen", command=self.show_bracket,
                                     bg="#03A9F4", fg="white", font=("Arial", 10))
        self.bracket_btn.pack(pady=5)

        self.history_btn = tk.Button(self.master, text="📜 History anzeigen", command=self.show_history,
                                     bg="#795548", fg="white", font=("Arial", 10))
        self.history_btn.pack(pady=5)

        self.total_btn = tk.Button(self.master, text="🏅 Gesamtsiege anzeigen", command=self.show_totals,
                                   bg="#388E3C", fg="white", font=("Arial", 10))
        self.total_btn.pack(pady=5)

        self.reset_btn = tk.Button(self.master, text="🧼 Neues Spiel starten", command=self.reset_ui,
                                   bg="#E53935", fg="white", font=("Arial", 10))
        self.reset_btn.pack(pady=10)

    def add_player(self):
        name = self.entry.get().strip()
        if name and name not in self.players:
            self.players.append(name)
            self.scores[name] = 0
            self.entry.delete(0, tk.END)
            self.players_label.config(text="Spieler: " + ", ".join(self.players))

    def start_normal_game(self):
        if len(self.players) < 2:
            messagebox.showinfo("Fehler", "Mindestens zwei Spieler erforderlich.")
            return
        self.mode = "normal"
        self.pairings = self.generate_pairings()
        self.next_match()

    def generate_pairings(self):
        p = self.players[:]
        random.shuffle(p)
        return [(p[i], p[i + 1]) for i in range(0, len(p) - 1, 2)]

    def next_match(self):
        for widget in self.winner_frame.winfo_children():
            widget.destroy()

        if not self.pairings:
            self.end_game()
            return

        p1, p2 = self.pairings.pop(0)
        self.match_label.config(text=f"{p1} 🎯 vs 🎯 {p2}")

        tk.Button(self.winner_frame, text=f"🏆 {p1} gewinnt", command=lambda: self.declare_winner(p1),
                  bg="#FF9800", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(self.winner_frame, text=f"🏆 {p2} gewinnt", command=lambda: self.declare_winner(p2),
                  bg="#FF9800", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

    def declare_winner(self, winner):
        self.scores[winner] += 1
        self.total_scores[winner] = self.total_scores.get(winner, 0) + 1
        self.save_totals()
        self.next_match()

    def end_game(self):
        score_text = "\n".join(f"{i+1}. {name}: {pts} Siege" for i, (name, pts) in enumerate(
            sorted(self.scores.items(), key=lambda x: -x[1])
        ))
        timestamp = datetime.now().strftime("%d.%m.%Y – %H:%M Uhr")
        result = f"{timestamp}\n🏁 Endstand:\n\n{score_text}"
        self.history.append(result)
        self.score_label.config(text=result)
        self.match_label.config(text="🎉 Spiel beendet!")

    def setup_tournament(self):
        if len(self.players) < 2:
            messagebox.showinfo("Fehler", "Mindestens zwei Spieler erforderlich.")
            return

        self.start_score = self.score_option.get()
        self.mode = "tournament"
        self.remaining_players = self.players[:]
        self.tournament_round = 1
        self.bracket_data = []
        self.prepare_next_round()

    def prepare_next_round(self):
        self.match_label.config(text=f"Turnierrunde {self.tournament_round}")
        self.current_round_matches = []
        players = self.remaining_players[:]
        random.shuffle(players)
        self.remaining_players = []

        if len(players) % 2 == 1:
            bye = players.pop()
            self.remaining_players.append(bye)
            self.current_round_matches.append({"p1": bye, "p2": "Freilos", "winner": bye})

        while players:
            p1 = players.pop()
            p2 = players.pop()
            self.current_round_matches.append({"p1": p1, "p2": p2, "winner": None})

        self.bracket_data.append(self.current_round_matches)
        self.tournament_bracket = self.current_round_matches[:]
        self.start_next_match()

    def declare_tournament_winner(self, winner):
        for match in self.current_round_matches:
            if winner in (match["p1"], match["p2"]) and match["winner"] is None:
                match["winner"] = winner
                break
        self.remaining_players.append(winner)
        self.start_next_match()

    def start_next_match(self):
        for widget in self.winner_frame.winfo_children():
            widget.destroy()

        if not self.tournament_bracket:
            if len(self.remaining_players) == 1:
                winner = self.remaining_players[0]
                self.match_label.config(text=f"🏆 {winner} ist Turniersieger!")
                self.total_scores[winner] = self.total_scores.get(winner, 0) + 1
                self.save_totals()
            else:
                self.tournament_round += 1
                self.prepare_next_round()
            return

        match = self.tournament_bracket.pop(0)
        if match["p2"] == "Freilos":
            self.start_next_match()
            return

        self.current_match = match
        p1, p2 = match["p1"], match["p2"]
        scores = {p1: self.start_score, p2: self.start_score}
        turn = p1

        def update():
            for widget in self.winner_frame.winfo_children():
                widget.destroy()

            self.match_label.config(text=f"{p1} ({scores[p1]}) 🎯 vs 🎯 {p2} ({scores[p2]})")
            tk.Label(self.winner_frame, text=f"{turn} ist am Zug:").pack()
            entry = tk.Entry(self.winner_frame)
            entry.pack()

            def submit():
                nonlocal turn
                try:
                    val = int(entry.get())
                    scores[turn] -= val
                    if scores[turn] == 0:
                        self.declare_tournament_winner(turn)
                    elif scores[turn] < 0:
                        scores[turn] += val
                        messagebox.showinfo("Ungültig", "Punkte überschritten!")
                    else:
                        turn = p1 if turn == p2 else p2
                        update()
                except:
                    messagebox.showinfo("Fehler", "Ungültige Eingabe")

            tk.Button(self.winner_frame, text="Punkte abziehen", command=submit, bg="#FF9800").pack(pady=5)

        update()

    def show_bracket(self):
        if not self.bracket_data:
            messagebox.showinfo("Fehler", "Noch kein Turnierbaum vorhanden.")
            return
        BracketWindow(self.master, self.bracket_data)

    def reset_ui(self):
        self.players = []
        self.scores = {}
        self.players_label.config(text="Spieler: ")
        self.entry.delete(0, tk.END)
        self.score_label.config(text="")
        self.match_label.config(text="")
        for w in self.winner_frame.winfo_children():
            w.destroy()

    def show_history(self):
        if not self.history:
            messagebox.showinfo("Hinweis", "Noch keine Spiele gespielt.")
            return
        top = tk.Toplevel(self.master)
        top.title("📜 Spiel-History")
        text_widget = tk.Text(top)
        text_widget.insert("1.0", "\n\n====================\n\n".join(self.history))
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both")

    def show_totals(self):
        if not self.total_scores:
            messagebox.showinfo("Hinweis", "Noch keine Statistik vorhanden.")
            return
        top = tk.Toplevel(self.master)
        top.title("🏅 Gesamtsiege")
        text_widget = tk.Text(top)
        text_widget.insert("1.0", "\n".join(
            f"{i+1}. {name}: {score} Gesamtsiege" for i, (name, score) in enumerate(
                sorted(self.total_scores.items(), key=lambda x: -x[1])
            )
        ))
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both")

    def save_totals(self):
        with open("totals.json", "w", encoding="utf-8") as f:
            json.dump(self.total_scores, f, ensure_ascii=False, indent=2)

    def load_totals(self):
        try:
            with open("totals.json", "r", encoding="utf-8") as f:
                self.total_scores = json.load(f)
        except FileNotFoundError:
            self.total_scores = {}

    def load_history(self):
        try:
            with open("history.txt", "r", encoding="utf-8") as f:
                raw = f.read()
                self.history = [h.strip() for h in raw.split("\n\n---\n\n") if h.strip()]
        except FileNotFoundError:
            self.history = []


if __name__ == "__main__":
    root = tk.Tk()
    app = ShkeloDart(root)
    root.mainloop()
