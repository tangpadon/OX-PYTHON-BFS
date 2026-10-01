import os
import ctypes
import tkinter as tk
from tkinter import ttk
from collections import deque


# Board & Rules
class OXBoard:
    WINNING_COMBOS = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    )

    @staticmethod
    def get_opponent(player):
        if player == 'X':
            return 'O'
        return 'X'

    @staticmethod
    def swap_symbols(board):
        mapping = {'X': 'O', 'O': 'X', ' ': ' '}
        return "".join(mapping[char] for char in board)

    @staticmethod
    def place_symbol(board, position, player):
        return board[:position] + player + board[position + 1:]

    @staticmethod
    def check_winner(board):
        for a, b, c in OXBoard.WINNING_COMBOS:
            if board[a] != ' ' and board[a] == board[b] == board[c]:
                return board[a]
        if ' ' not in board:
            return 'Draw'
        return None


# Tree Node
class GameNode:
    def __init__(self, board, player_turn, move=None):
        self.board = board
        self.player_turn = player_turn
        self.move = move
        self.children = []
        self.winner = OXBoard.check_winner(board)
        self.is_terminal = (self.winner is not None)
        self.wins_x = 0
        self.wins_o = 0
        self.draws = 0
        self.minimax_val = None
        self.steps_to_end = 0


# BFS Engine
class OXBFSTree:
    def __init__(self):
        self.root = None
        self.state_map = {} #node index
        self.total_nodes = 0
        self.total_leaves = 0
        self._build_tree()

    def _build_tree(self):
        self.root = GameNode(' ' * 9, 'X')
        queue = deque([self.root])
        all_nodes = [self.root]
        self.state_map[(' ' * 9, 'X')] = self.root

        while queue:
            node = queue.popleft()
            if node.is_terminal:
                continue

            next_player = OXBoard.get_opponent(node.player_turn)
            for pos in range(9):
                if node.board[pos] == ' ':
                    next_board = OXBoard.place_symbol(node.board, pos, node.player_turn)
                    child = GameNode(next_board, next_player, pos)
                    node.children.append(child)
                    queue.append(child)
                    all_nodes.append(child)
                    self.state_map[(child.board, next_player)] = child

        self.total_nodes = len(all_nodes)
        for node in reversed(all_nodes):
            if node.is_terminal:
                self.total_leaves += 1
                node.steps_to_end = 0
                if node.winner == 'X':
                    node.minimax_val = 1
                    node.wins_x = 1
                elif node.winner == 'O':
                    node.minimax_val = -1
                    node.wins_o = 1
                else:
                    node.minimax_val = 0
                    node.draws = 1
            else:
                for child in node.children:
                    node.wins_x += child.wins_x
                    node.wins_o += child.wins_o
                    node.draws += child.draws

                vals = [child.minimax_val for child in node.children]
                if node.player_turn == 'X':
                    best_val = max(vals)
                    is_winning = (best_val == 1)
                    is_losing = (best_val == -1)
                else:
                    best_val = min(vals)
                    is_winning = (best_val == -1)
                    is_losing = (best_val == 1)

                node.minimax_val = best_val
                best_children = [child for child in node.children if child.minimax_val == best_val]
                if is_winning:
                    node.steps_to_end = min(child.steps_to_end for child in best_children) + 1
                elif is_losing:
                    node.steps_to_end = max(child.steps_to_end for child in best_children) + 1
                else:
                    node.steps_to_end = min(child.steps_to_end for child in best_children) + 1

    def evaluate_branches(self, current_board, current_player):
        node = self.state_map.get((current_board, current_player))
        is_swapped = False
        if not node:
            swapped_board = OXBoard.swap_symbols(current_board)
            opponent_player = OXBoard.get_opponent(current_player)
            node = self.state_map.get((swapped_board, opponent_player))
            is_swapped = True

        if not node or not node.children:
            return [], None

        branches = []
        for child in node.children:
            if is_swapped or current_player == 'X':
                wins = child.wins_x
                losses = child.wins_o
                val = child.minimax_val
            else:
                wins = child.wins_o
                losses = child.wins_x
                val = -child.minimax_val

            direct = child.winner
            if is_swapped and child.winner in ('X', 'O'):
                direct = OXBoard.get_opponent(child.winner)

            branches.append({
                'move': child.move,
                'row': child.move // 3,
                'col': child.move % 3,
                'next_board': OXBoard.place_symbol(current_board, child.move, current_player),
                'wins': wins,
                'losses': losses,
                'draws': child.draws,
                'score': wins - losses,
                'minimax_val': val,
                'steps': child.steps_to_end + 1,
                'direct_result': direct
            })

        best_minimax = max(branch['minimax_val'] for branch in branches)
        best_candidates = [branch for branch in branches if branch['minimax_val'] == best_minimax]
        if best_minimax == 1:
            min_steps = min(branch['steps'] for branch in best_candidates)
            for branch in best_candidates:
                if branch['steps'] == min_steps:
                    best_move = branch['move']
                    break
        elif best_minimax == -1:
            max_steps = max(branch['steps'] for branch in best_candidates)
            for branch in best_candidates:
                if branch['steps'] == max_steps:
                    best_move = branch['move']
                    break
        else:
            best_move = best_candidates[0]['move']
        return branches, best_move


# Debug
class OXDebugger:
    @staticmethod
    def format_row(board, start_index):
        cells = [char if char != ' ' else '.' for char in board[start_index:start_index + 3]]
        return " | ".join(cells)

    def get_debug_text(self, tree, board, player, turn, chosen_move=None):
        branches, auto_best = tree.evaluate_branches(board, player)
        if not branches:
            return f"--- Turn {turn} ({player}): ไม่พบกิ่งต่อไป ---"

        lines = [
            "=" * 70,
            f" [DEBUG] TURN {turn} - ผู้เล่น: {player} | สถานะตารางปัจจุบัน:"
        ]
        for r in range(3):
            lines.append(f"       {self.format_row(board, r * 3)}")

        lines.append("-" * 70)
        lines.append(f" กิ่งสถานะที่เป็นไปได้ (Child Nodes: {len(branches)} กิ่ง):")
        lines.append("-" * 70)

        if chosen_move is not None:
            selected_move = chosen_move
        else:
            selected_move = auto_best

        def branch_sort_key(branch):
            if branch['minimax_val'] == 1:
                step_priority = -branch['steps']
            elif branch['minimax_val'] == -1:
                step_priority = branch['steps']
            else:
                step_priority = 0
            return (branch['minimax_val'], step_priority)

        sorted_branches = sorted(branches, key=branch_sort_key, reverse=True)
        for idx, branch in enumerate(sorted_branches, start=1):
            if branch['move'] == selected_move:
                selected_tag = " ★ [SELECTED]"
            else:
                selected_tag = ""

            if branch['direct_result']:
                direct_tag = f" [DIRECT {branch['direct_result']}!]"
            else:
                direct_tag = ""

            if branch['minimax_val'] == 1:
                val_str = f"+1 (ชนะใน {branch['steps']} ตา)"
            elif branch['minimax_val'] == -1:
                val_str = "-1"
            else:
                val_str = "0"

            lines.append(f" กิ่งที่ #{idx}: ช่อง ({branch['row']}, {branch['col']}) [Index {branch['move']}]{selected_tag}{direct_tag}")
            lines.append(f"    └─ Minimax Value: {val_str}")
            lines.append(f"       Preview: [{self.format_row(branch['next_board'], 0)}]")
            lines.append(f"                [{self.format_row(branch['next_board'], 3)}]")
            lines.append(f"                [{self.format_row(branch['next_board'], 6)}]\n")

        lines.append(f" AI เลือกเดิน: ช่อง ({selected_move // 3}, {selected_move % 3}) [Index {selected_move}]")
        lines.append("=" * 70)
        return "\n".join(lines)


# GUI Application
class OXGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OX Game")
        self.root.geometry("1180x720")
        self.root.minsize(980, 620)
        self.root.configure(bg="#F0F2F5")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_dir, 'icon.ico')
        png_path = os.path.join(base_dir, 'icon.png')
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(default=ico_path)
            except Exception:
                pass
        if os.path.exists(png_path):
            try:
                self.icon_photo = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, self.icon_photo)
            except Exception:
                pass

        self.board = ' ' * 9
        self.current_player = 'X'
        self.turn_count = 1
        self.game_over = False
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.ai_job = None

        self.tree = OXBFSTree()
        self.debugger = OXDebugger()

        self._create_widgets()
        self.start_new_game()

    def _create_widgets(self):
        main = tk.Frame(self.root, bg="#F0F2F5")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        main.columnconfigure(0, weight=48, uniform="col")
        main.columnconfigure(1, weight=52, uniform="col")
        main.rowconfigure(0, weight=1)

        left = tk.Frame(main, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), ipadx=10, ipady=10)

        tk.Button(
            left,
            text="Reset",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self.start_new_game
        ).pack(fill=tk.X, padx=15, pady=(5, 5))

        score_f = tk.Frame(left, bg="#F1F5F9", relief=tk.GROOVE, bd=1)
        score_f.pack(fill=tk.X, padx=15, pady=5)

        self.lbl_x = tk.Label(score_f, text="👤 ผู้เล่น (X): 0", font=("Segoe UI", 9, "bold"), fg="#1565C0", bg="#F1F5F9")
        self.lbl_x.pack(side=tk.LEFT, expand=True, pady=8)

        self.lbl_draw = tk.Label(score_f, text="🤝 เสมอ: 0", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#F1F5F9")
        self.lbl_draw.pack(side=tk.LEFT, expand=True, pady=8)

        self.lbl_o = tk.Label(score_f, text="🤖 บอท (O): 0", font=("Segoe UI", 9, "bold"), fg="#D84315", bg="#F1F5F9")
        self.lbl_o.pack(side=tk.LEFT, expand=True, pady=8)

        self.status_lbl = tk.Label(
            left,
            text="เทิร์น: ตาเดินของผู้เล่น (X)",
            font=("Segoe UI", 12, "bold"),
            bg="#E2E8F0",
            fg="#0F172A",
            height=2,
            relief=tk.RIDGE
        )
        self.status_lbl.pack(fill=tk.X, padx=15, pady=8)

        b_frame = tk.Frame(left, bg="#CBD5E1", bd=2, relief=tk.SUNKEN)
        b_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        for r in range(3):
            b_frame.rowconfigure(r, weight=1, uniform="cell")
            b_frame.columnconfigure(r, weight=1, uniform="cell")

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                b_frame,
                text=" ",
                font=("Segoe UI", 32, "bold"),
                bg="#FFFFFF",
                activebackground="#E3F2FD",
                relief=tk.FLAT,
                bd=1,
                cursor="hand2",
                command=lambda idx=i: self._on_cell_clicked(idx)
            )
            btn.grid(row=i // 3, column=i % 3, sticky="nsew", padx=4, pady=4)
            self.buttons.append(btn)

        right = tk.Frame(main, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        right.grid(row=0, column=1, sticky="nsew")

        d_header = tk.Frame(right, bg="#0F172A", height=40)
        d_header.pack(fill=tk.X)
        tk.Label(
            d_header,
            text="DEBUG Console: กิ่งที่เป็นไปได้ทั้งหมด",
            font=("Consolas", 10, "bold"),
            fg="#38BDF8",
            bg="#0F172A"
        ).pack(side=tk.LEFT, padx=12, pady=8)

        self.debug_text = tk.Text(
            right,
            wrap=tk.NONE,
            font=("Consolas", 9),
            bg="#020617",
            fg="#E2E8F0",
            insertbackground="#38BDF8",
            padx=10,
            pady=10,
            relief=tk.FLAT
        )
        v_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.debug_text.pack(fill=tk.BOTH, expand=True)

    def _append_debug_log(self, text):
        print(text)
        self.debug_text.insert(tk.END, text)
        self.debug_text.see(tk.END)

    def start_new_game(self):
        if self.ai_job:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.debug_text.delete("1.0", tk.END)
        self.board = ' ' * 9
        self.current_player = 'X'
        self.turn_count = 1
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=" ", bg="#FFFFFF", fg="#000000", state=tk.NORMAL)

        self._update_status("เทิร์นที่ 1: ตาเดินของคุณ (X)")
        self._append_debug_log(">>> เริ่มเกมกระดานใหม่ (New Match Started) <<<\n")

    def _update_status(self, text, is_over=False):
        if is_over:
            bg_color = "#FEF08A"
            fg_color = "#854D0E"
        else:
            bg_color = "#E2E8F0"
            fg_color = "#0F172A"
        self.status_lbl.config(text=text, bg=bg_color, fg=fg_color)

    def _update_scoreboard(self):
        self.lbl_x.config(text=f"👤 ผู้เล่น (X): {self.scores['X']}")
        self.lbl_o.config(text=f"🤖 บอท (O): {self.scores['O']}")
        self.lbl_draw.config(text=f"🤝 เสมอ: {self.scores['Draw']}")

    def _check_game_end(self):
        winner = OXBoard.check_winner(self.board)
        if not winner:
            return False

        self.game_over = True
        self.scores[winner] += 1
        self._update_scoreboard()

        if winner == 'Draw':
            self._update_status("🤝 ผลการแข่งขัน: เสมอกัน (Draw)!", is_over=True)
            self._append_debug_log(f"\n[ผลการแข่งขัน] เสมอกัน (Draw) ในเทิร์นที่ {self.turn_count}!\n\n")
        else:
            if winner == 'X':
                who = "👤 คุณ (X)"
            else:
                who = "🤖 บอท BFS (O)"

            for combo in OXBoard.WINNING_COMBOS:
                if all(self.board[pos] == winner for pos in combo):
                    for idx in combo:
                        self.buttons[idx].config(bg="#C8E6C9")
                    break

            self._update_status(f"🎉 {who} เป็นฝ่ายชนะ!", is_over=True)
            self._append_debug_log(f"\n[ผลการแข่งขัน] {who} ชนะเกมในเทิร์นที่ {self.turn_count}!\n\n")

        return True

    def _on_cell_clicked(self, idx):
        if not self.game_over and self.board[idx] == ' ' and self.current_player == 'X':
            self._execute_move(idx)

    def _execute_move(self, move_idx):
        if self.current_player == 'O':
            debug_info = self.debugger.get_debug_text(self.tree, self.board, 'O', self.turn_count, move_idx)
            self._append_debug_log(debug_info + "\n")

        self.board = OXBoard.place_symbol(self.board, move_idx, self.current_player)

        if self.current_player == 'X':
            fg_color = "#1565C0"
        else:
            fg_color = "#D84315"
        self.buttons[move_idx].config(text=self.current_player, fg=fg_color)

        if self._check_game_end():
            return

        self.current_player = OXBoard.get_opponent(self.current_player)

        self.turn_count += 1
        if self.current_player == 'O':
            self._update_status(f"เทิร์นที่ {self.turn_count}: 🤖 บอท BFS กำลังวิเคราะห์กิ่ง...")
            self.ai_job = self.root.after(250, self._ai_turn)
        else:
            self._update_status(f"เทิร์นที่ {self.turn_count}: ตาเดินของคุณ (X)")

    def _ai_turn(self):
        if not self.game_over and self.current_player == 'O':
            _, best_move = self.tree.evaluate_branches(self.board, 'O')
            if best_move is not None:
                self._execute_move(best_move)


# Main
if __name__ == '__main__':
    try:
        myappid = 'oxbfs.tictactoe.game.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    root = tk.Tk()
    app = OXGameGUI(root)
    root.mainloop()
