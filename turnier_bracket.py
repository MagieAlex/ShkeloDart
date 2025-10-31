import math
import tkinter as tk
from tkinter import ttk

def generate_bracket(players):
    num_players = len(players)
    next_pow2 = 1 << (num_players - 1).bit_length()
    num_rounds = int(math.log2(next_pow2))
    bracket = [[] for _ in range(num_rounds)]

    filled = players + [None] * (next_pow2 - num_players)
    first_round = [(filled[i], filled[i+1]) for i in range(0, next_pow2, 2)]
    bracket[0] = first_round

    for r in range(1, num_rounds):
        bracket[r] = [(None, None) for _ in range(len(bracket[r-1]) // 2)]

    return bracket

def draw_bracket(canvas, bracket):
    canvas.delete("all")
    max_matches = max(len(round) for round in bracket)
    canvas.config(scrollregion=(0, 0, 200 * len(bracket), 100 * max_matches))

    for r_idx, round in enumerate(bracket):
        for m_idx, match in enumerate(round):
            x = r_idx * 200 + 20
            y = m_idx * 100 + 40
            p1 = match[0] if match[0] else "BYE"
            p2 = match[1] if match[1] else "BYE"
            canvas.create_rectangle(x, y, x+160, y+60, outline="black")
            canvas.create_text(x+80, y+15, text=f"{p1}", font=("Arial", 10))
            canvas.create_text(x+80, y+40, text=f"{p2}", font=("Arial", 10))

def start_bracket():
    players_input = player_entry.get()
    players = [p.strip() for p in players_input.split(",") if p.strip()]
    if len(players) < 2:
        result_label.config(text="Mindestens 2 Spieler eingeben!")
        return
    bracket = generate_bracket(players)
    draw_bracket(canvas, bracket)
    result_label.config(text=f"Turnier gestartet mit {len(players)} Spielern.")

# GUI setup
root = tk.Tk()
root.title("🎯 Turnier Bracket Generator")

top_frame = ttk.Frame(root, padding=10)
top_frame.pack()

player_label = ttk.Label(top_frame, text="Spielernamen (kommagetrennt):")
player_label.pack()

player_entry = ttk.Entry(top_frame, width=80)
player_entry.pack()

start_button = ttk.Button(top_frame, text="🏁 Turnier starten", command=start_bracket)
start_button.pack(pady=10)

result_label = ttk.Label(top_frame, text="")
result_label.pack()

canvas_frame = ttk.Frame(root)
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, bg="white", height=600)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
scrollbar.pack(side="bottom", fill="x")
canvas.configure(xscrollcommand=scrollbar.set)

root.mainloop()
