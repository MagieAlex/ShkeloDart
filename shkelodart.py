import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime
import json

class DartApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ShkeloDart 🎯")
        self.master.geometry("500x600")
        self.master.configure(bg="#f0f0f0")

        self.players = []
        self.scores = {}
        self.pairings = []
        self.history = []
        self.total_scores = {}
        self.score_visible = False
        self.countdown_after_id = None

        self.top_frame = tk.Frame(master, bg="#f0f0f0")
        self.top_frame.pack(pady=10)

        self.entry = tk.Entry(self.top_frame, font=("Arial", 12), width=25)
        self.entry.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(self.top_frame, text="➕ Spieler hinzufügen", command=self.add_player,
                                    bg="#4CAF50", fg="white", font=("Arial", 10))
        self.add_button.pack(side=tk.LEFT)

        self.start_button = tk.Button(master, text="🎮 Spiel starten", command=self.start_game,
                                      bg="#2196F3", fg="white", font=("Arial", 11, "bold"))
        self.start_button.pack(pady=10)

        self.players_label = tk.Label(master, text="Spieler: ", font=("Arial", 11), bg="#f0f0f0")
        self.players_label.pack()

        self.match_label = tk.Label(master, text="", font=("Arial", 16, "bold"), pady=20, bg="#f0f0f0")
        self.match_label.pack()

        self.winner_frame = tk.Frame(master, bg="#f0f0f0")
        self.winner_frame.pack(pady=10)

        self.score_label = tk.Label(master, text="", font=("Arial", 12), bg="#f0f0f0", justify="left")
        self.score_label.pack(pady=10)

        self.restart_button = tk.Button(master, text="🔄 Erneut spielen", command=self.restart_game,
                                        bg="#9C27B0", fg="white", font=("Arial", 10))
        self.restart_button.pack(pady=10)
        self.restart_button.pack_forget()

        self.new_game_button = tk.Button(master, text="🧼 Neues Spiel starten", command=self.new_game,
                                         bg="#E53935", fg="white", font=("Arial", 10))
        self.new_game_button.pack(pady=5)
        self.new_game_button.pack_forget()

        self.show_score_button = tk.Button(master, text="📊 Spielstand anzeigen", command=self.show_current_scores,
                                           bg="#607D8B", fg="white", font=("Arial", 10))

        self.show_pairings_button = tk.Button(master, text="📝 Paarungen anzeigen", command=self.show_pairing_preview,
                                              bg="#FFA000", fg="white", font=("Arial", 10))

        self.history_button = tk.Button(master, text="📜 History anzeigen", command=self.show_history,
                                        bg="#795548", fg="white", font=("Arial", 10))

        self.total_button = tk.Button(master, text="🏅 Gesamtsiege anzeigen", command=self.show_totals,
                                      bg="#388E3C", fg="white", font=("Arial", 10))

        self.place_control_buttons()

        self.load_history()
        self.load_totals()

    def place_control_buttons(self):
        self.show_score_button.pack(pady=5)
        self.show_pairings_button.pack(pady=5)
        self.history_button.pack(pady=5)
        self.total_button.pack(pady=5)

    def hide_input_widgets(self):
        self.entry.pack_forget()
        self.add_button.pack_forget()
        self.start_button.pack_forget()
        self.players_label.pack_forget()

    def show_input_widgets(self):
        self.entry.pack(side=tk.LEFT, padx=5)
        self.add_button.pack(side=tk.LEFT)
        self.start_button.pack(pady=10)
        self.players_label.pack()

    def add_player(self):
        name = self.entry.get().strip()
        if name and name not in self.players:
            self.players.append(name)
            self.scores[name] = 0
            self.entry.delete(0, tk.END)
            self.update_player_list()
        else:
            messagebox.showinfo("Fehler", "Name ist leer oder bereits hinzugefügt.")

    def update_player_list(self):
        self.players_label.config(text="Spieler: " + ", ".join(self.players))

    def start_game(self):
        if len(self.players) < 2:
            messagebox.showinfo("Fehler", "Mindestens zwei Spieler erforderlich.")
            return

        self.pairings = self.generate_pairings()
        self.clear_winner_buttons()
        self.hide_input_widgets()
        self.score_label.config(text="")
        self.restart_button.pack_forget()
        self.new_game_button.pack_forget()
        self.show_pairing_preview(autostart=True)

    def show_pairing_preview(self, autostart=False):
        if not self.pairings:
            messagebox.showinfo("Keine Paarungen", "Es konnten keine gültigen Paarungen erzeugt werden.")
            return

        preview_text = "\n".join(f"{i+1}. {p1} vs. {p2}" for i, (p1, p2) in enumerate(self.pairings))

        top = tk.Toplevel(self.master)
        top.title("📝 Anstehende Paarungen")
        top.geometry("400x300")
        top.resizable(False, False)

        label = tk.Label(top, text="Anstehende Paarungen", font=("Arial", 14, "bold"))
        label.pack(pady=10)

        if autostart:
            sublabel = tk.Label(top, text="Spiel startet in 5 Sekunden...", font=("Arial", 10))
            sublabel.pack(pady=(0, 10))

        text = tk.Text(top, wrap="word", font=("Arial", 11))
        text.insert("1.0", preview_text)
        text.config(state="disabled")
        text.pack(expand=True, fill="both", padx=10, pady=10)

        def update_countdown(seconds):
            if seconds > 0:
                self.countdown_after_id = top.after(1000, lambda: update_countdown(seconds - 1))
            else:
                top.destroy()
                self.show_next_pairing()

        def on_close_preview():
            if self.countdown_after_id:
                try:
                    top.after_cancel(self.countdown_after_id)
                except Exception:
                    pass
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close_preview)

        if autostart:
            update_countdown(5)

    def generate_pairings(self):
        shuffled = self.players[:]
        random.shuffle(shuffled)
        return [(shuffled[i], shuffled[i + 1]) for i in range(0, len(shuffled) - 1, 2)]

    def show_next_pairing(self):
        self.clear_winner_buttons()

        if not self.pairings:
            self.show_scores()
            return

        p1, p2 = self.pairings.pop(0)
        self.match_label.config(text=f"{p1} 🎯 vs. 🎯 {p2}")

        btn1 = tk.Button(self.winner_frame, text=f"🏆 {p1} gewinnt", command=lambda: self.declare_winner(p1),
                         bg="#FF9800", fg="white", font=("Arial", 10), width=18)
        btn1.pack(side=tk.LEFT, padx=10)

        btn2 = tk.Button(self.winner_frame, text=f"🏆 {p2} gewinnt", command=lambda: self.declare_winner(p2),
                         bg="#FF9800", fg="white", font=("Arial", 10), width=18)
        btn2.pack(side=tk.LEFT, padx=10)

    def clear_winner_buttons(self):
        for widget in self.winner_frame.winfo_children():
            widget.destroy()

    def declare_winner(self, winner):
        self.scores[winner] += 1
        self.total_scores[winner] = self.total_scores.get(winner, 0) + 1
        self.save_totals()

        if self.pairings:
            self.show_next_pairing()
        else:
            self.show_scores()

    def show_scores(self):
        self.clear_winner_buttons()
        sorted_scores = sorted(self.scores.items(), key=lambda x: -x[1])
        score_text = "\n".join(f"{i + 1}. {name}: {wins} Siege" for i, (name, wins) in enumerate(sorted_scores))
        timestamp = datetime.now().strftime("%d.%m.%Y – %H:%M Uhr")
        full_entry = f"{timestamp}\n🏁 Endstand:\n\n{score_text}"
        self.score_label.config(text=full_entry)
        self.match_label.config(text="🎉 Spiel beendet!")
        self.restart_button.pack()
        self.new_game_button.pack()
        self.history.append(full_entry)

    def restart_game(self):
        for name in self.players:
            self.scores[name] = 0
        self.score_label.config(text="")
        self.score_visible = False
        self.match_label.config(text="")
        self.restart_button.pack_forget()
        self.new_game_button.pack_forget()
        self.clear_winner_buttons()
        self.start_game()

    def new_game(self):
        self.players = []
        self.scores = {}
        self.pairings = []
        self.score_label.config(text="")
        self.score_visible = False
        self.match_label.config(text="")
        self.entry.delete(0, tk.END)
        self.players_label.config(text="Spieler: ")
        self.restart_button.pack_forget()
        self.new_game_button.pack_forget()
        self.clear_winner_buttons()
        self.show_input_widgets()
        self.reset_ui()

    def show_current_scores(self):
        if self.score_visible:
            self.score_label.config(text="")
            self.show_score_button.config(text="📊 Spielstand anzeigen")
            self.score_visible = False
        else:
            sorted_scores = sorted(self.scores.items(), key=lambda x: -x[1])
            score_text = "📊 Aktueller Spielstand:\n\n" + "\n".join(
                f"{i + 1}. {name}: {wins} Siege" for i, (name, wins) in enumerate(sorted_scores)
            )
            self.score_label.config(text=score_text)
            self.show_score_button.config(text="❌ Spielstand verstecken")
            self.score_visible = True

    def show_history(self):
        if not self.history:
            messagebox.showinfo("Keine History", "Es wurden noch keine Spiele abgeschlossen.")
            return

        def clear_history():
            if messagebox.askyesno("History löschen", "Willst du wirklich die gesamte History löschen?"):
                self.history.clear()
                top.destroy()
                messagebox.showinfo("Gelöscht", "Die Spiel-History wurde gelöscht.")

        history_text = "\n\n====================\n\n".join(self.history)
        top = tk.Toplevel(self.master)
        top.title("📜 Spiel-History")
        top.geometry("500x500")
        top.minsize(400, 400)

        text_widget = tk.Text(top, wrap="word", font=("Arial", 10))
        text_widget.insert("1.0", history_text)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        delete_button = tk.Button(top, text="🗑️ History löschen", command=clear_history, bg="#F44336",
                                  fg="white", font=("Arial", 10))
        delete_button.pack(pady=(0, 10))

    def save_history(self):
        try:
            with open("history.txt", "w", encoding="utf-8") as f:
                for entry in self.history:
                    f.write(entry + "\n\n---\n\n")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der History:\n{e}")

    def load_history(self):
        try:
            with open("history.txt", "r", encoding="utf-8") as f:
                raw = f.read()
                self.history = [block.strip() for block in raw.split("\n\n---\n\n") if block.strip()]
        except FileNotFoundError:
            self.history = []

    def save_totals(self):
        try:
            with open("totals.json", "w", encoding="utf-8") as f:
                json.dump(self.total_scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Gesamtstatistik:\n{e}")

    def load_totals(self):
        try:
            with open("totals.json", "r", encoding="utf-8") as f:
                self.total_scores = json.load(f)
        except FileNotFoundError:
            self.total_scores = {}

    def show_totals(self):
        if not self.total_scores:
            messagebox.showinfo("Noch keine Statistik", "Es wurden noch keine Siege gespeichert.")
            return

        def clear_totals():
            if messagebox.askyesno("Gesamtsiege löschen", "Willst du wirklich alle Gesamtsiege löschen?"):
                self.total_scores.clear()
                self.save_totals()
                top.destroy()
                messagebox.showinfo("Gelöscht", "Die Gesamtsiege wurden gelöscht.")

        sorted_totals = sorted(self.total_scores.items(), key=lambda x: -x[1])
        text = "\n".join(f"{i+1}. {name}: {wins} Gesamtsiege" for i, (name, wins) in enumerate(sorted_totals))

        top = tk.Toplevel(self.master)
        top.title("🏅 Gesamtsiege")
        top.geometry("400x400")
        top.minsize(300, 300)

        text_widget = tk.Text(top, wrap="word", font=("Arial", 10))
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=(10, 5))

        delete_button = tk.Button(top, text="🗑️ Gesamtsiege löschen", command=clear_totals,
                                  bg="#D32F2F", fg="white", font=("Arial", 10))
        delete_button.pack(pady=(0, 10))

    def reset_ui(self):
        for widget in self.master.winfo_children():
            widget.pack_forget()

        self.top_frame.pack(pady=10)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.add_button.pack(side=tk.LEFT)

        self.start_button.pack(pady=10)
        self.players_label.pack()
        self.match_label.config(text="")
        self.match_label.pack()
        self.winner_frame.pack(pady=10)
        self.score_label.config(text="")
        self.score_label.pack(pady=10)

        self.show_score_button.pack(pady=5)
        self.show_pairings_button.pack(pady=5)
        self.history_button.pack(pady=5)
        self.total_button.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = DartApp(root)

    def on_close():
        app.save_history()
        app.save_totals()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
