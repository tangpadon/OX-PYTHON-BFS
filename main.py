import tkinter as tk
from collections import deque

EMPTY_BOARD = ' ' * 9


class OXBoard:
    WINNING_COMBOS = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    )

    @staticmethod
    def get_opponent(player):
        return 'O' if player == 'X' else 'X'

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


class GameNode:
    def __init__(self, board, player_turn, move=None):
        self.board = board
        self.player_turn = player_turn
        self.move = move
        self.children = []
        self.winner = OXBoard.check_winner(board)
        self.minimax_val = None
        self.steps_to_end = 0


def branch_sort_key(b, player):
    win_val = 1 if player == 'O' else -1
    loss_val = -1 if player == 'O' else 1
    if b['minimax_val'] == win_val:
        return (1, -b['steps'])
    if b['minimax_val'] == loss_val:
        return (-1, b['steps'])
    return (0, 0)


def format_row(board, start_index):
    cells = [char if char != ' ' else '.' for char in board[start_index:start_index + 3]]
    return " | ".join(cells)


def get_debug_text(board, player, turn, branches, selected_move):
    if not branches:
        who = "ผู้เล่น (X)" if player == 'X' else "บอท (O)"
        return f"--- Turn {turn} ({who}): ไม่พบกิ่งต่อไป ---"

    who = "ผู้เล่น (X)" if player == 'X' else "บอท (O)"
    chooser = "ผู้เล่น" if player == 'X' else "บอท"

    lines = [
        "=" * 70,
        f" [DEBUG] TURN {turn} - {who} | สถานะตารางปัจจุบัน:",
        f"       {format_row(board, 0)}",
        f"       {format_row(board, 3)}",
        f"       {format_row(board, 6)}",
        "-" * 70,
        f" กิ่งสถานะที่เป็นไปได้ (Child Nodes: {len(branches)} กิ่ง):",
        "-" * 70
    ]

    for idx, b in enumerate(branches, start=1):
        selected_tag = " ★ [SELECTED]" if b['move'] == selected_move else ""
        direct_tag = f" [DIRECT {b['direct_result']}!]" if b['direct_result'] else ""
        val_str = "+1" if b['minimax_val'] == 1 else str(b['minimax_val'])

        row, col = b['move'] // 3, b['move'] % 3
        lines.append(f" กิ่งที่ #{idx}: ช่อง ({row}, {col}) [Index {b['move']}]{selected_tag}{direct_tag}")
        lines.append(f"    └─ Minimax Value: {val_str}")
        lines.append(f"       Preview: [{format_row(b['next_board'], 0)}]")
        lines.append(f"                [{format_row(b['next_board'], 3)}]")
        lines.append(f"                [{format_row(b['next_board'], 6)}]\n")

    lines.append(f" {chooser}เลือกเดิน: ช่อง ({selected_move // 3}, {selected_move % 3}) [Index {selected_move}]")
    lines.append("=" * 70)
    return "\n".join(lines)



class OXBFSTree:
    def __init__(self):
        self.state_map = {}
        self._build_tree()

    def _build_tree(self):
        root = GameNode(EMPTY_BOARD, 'X')
        queue = deque([root])
        all_nodes = [root]
        self.state_map[(EMPTY_BOARD, 'X')] = root

        while queue:
            node = queue.popleft()
            if node.winner:
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

        for node in reversed(all_nodes):
            if node.winner:
                if node.winner == 'O':
                    node.minimax_val = 1
                elif node.winner == 'X':
                    node.minimax_val = -1
                else:
                    node.minimax_val = 0
            else:
                vals = [child.minimax_val for child in node.children]
                if node.player_turn == 'O':
                    best_val = max(vals)
                    is_losing = (best_val == -1)
                else:
                    best_val = min(vals)
                    is_losing = (best_val == 1)

                node.minimax_val = best_val
                best_children = [c for c in node.children if c.minimax_val == best_val]
                if is_losing:
                    node.steps_to_end = max(c.steps_to_end for c in best_children) + 1
                else:
                    node.steps_to_end = min(c.steps_to_end for c in best_children) + 1

    def evaluate_branches(self, current_board, player):
        node = self.state_map.get((current_board, player))
        if not node or not node.children:
            return [], None

        branches = []
        for child in node.children:
            branches.append({
                'move': child.move,
                'next_board': child.board,
                'minimax_val': child.minimax_val,
                'steps': child.steps_to_end + 1,
                'direct_result': child.winner
            })

        branches.sort(key=lambda b: branch_sort_key(b, player), reverse=True)
        best_move = branches[0]['move']
        return branches, best_move


class OXGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OX Game")
        self.root.geometry("450x540")
        self.root.minsize(380, 460)
        self.root.configure(bg="#F8FAFC")

        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.ai_job = None
        self.tree = OXBFSTree()

        self._create_widgets()
        self.start_new_game()

    def _create_widgets(self):
        # แถบ Layout Header ด้านบน
        header = tk.Frame(self.root, bg="#FFFFFF", relief=tk.SOLID, bd=1)
        header.pack(fill=tk.X, side=tk.TOP)

        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)
        header.columnconfigure(2, weight=1)
        header.columnconfigure(3, weight=0)
        header.columnconfigure(4, weight=2)
        header.columnconfigure(5, weight=0)
        header.columnconfigure(6, weight=1)

        #ปุ่ม Reset
        btn_reset = tk.Button(
            header, text="↺\nReset", font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9", fg="#334155", activebackground="#E2E8F0",
            relief=tk.FLAT, bd=0, cursor="hand2", command=self.start_new_game
        )
        btn_reset.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # เส้นคั่น Reset - X
        tk.Frame(header, bg="#E2E8F0", width=1).grid(row=0, column=1, sticky="ns")

        #ฝั่งผู้เล่น X
        frame_x = tk.Frame(header, bg="#FFFFFF")
        frame_x.grid(row=0, column=2, sticky="nsew", pady=6)
        tk.Label(frame_x, text="X", font=("Segoe UI", 16, "bold"), fg="#DC2626", bg="#FFFFFF").pack()
        self.lbl_x = tk.Label(frame_x, font=("Segoe UI", 9, "bold"), fg="#DC2626", bg="#FFFFFF")
        self.lbl_x.pack()

        #เส้นคั่น X - Score
        tk.Frame(header, bg="#EF4444", width=2).grid(row=0, column=3, sticky="ns")

        #ส่วน Score
        frame_score = tk.Frame(header, bg="#FFFFFF")
        frame_score.grid(row=0, column=4, sticky="nsew", pady=4)
        tk.Label(frame_score, text="SCORE", font=("Segoe UI", 10, "bold"), fg="#64748B", bg="#FFFFFF").pack()
        self.lbl_draw = tk.Label(frame_score, font=("Segoe UI", 8), fg="#64748B", bg="#FFFFFF")
        self.lbl_draw.pack()
        self.status_lbl = tk.Label(frame_score, font=("Segoe UI", 9, "bold"), fg="#0F172A", bg="#FFFFFF")
        self.status_lbl.pack()

        #เส้นคั่น Score - O
        tk.Frame(header, bg="#3B82F6", width=2).grid(row=0, column=5, sticky="ns")

        #ฝั่งบอท O
        frame_o = tk.Frame(header, bg="#FFFFFF")
        frame_o.grid(row=0, column=6, sticky="nsew", pady=6)
        tk.Label(frame_o, text="O", font=("Segoe UI", 16, "bold"), fg="#2563EB", bg="#FFFFFF").pack()
        self.lbl_o = tk.Label(frame_o, font=("Segoe UI", 9, "bold"), fg="#2563EB", bg="#FFFFFF")
        self.lbl_o.pack()

        self._update_scoreboard()

        #ตาราง 3x3
        b_frame = tk.Frame(self.root, bg="#CBD5E1", bd=2, relief=tk.SUNKEN)
        b_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        for r in range(3):
            b_frame.rowconfigure(r, weight=1, uniform="cell")
            b_frame.columnconfigure(r, weight=1, uniform="cell")

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                b_frame, text=" ", font=("Segoe UI", 36, "bold"),
                bg="#FFFFFF", activebackground="#F1F5F9", relief=tk.FLAT, bd=1,
                cursor="hand2", command=lambda idx=i: self._on_cell_clicked(idx)
            )
            btn.grid(row=i // 3, column=i % 3, sticky="nsew", padx=3, pady=3)
            self.buttons.append(btn)

    def start_new_game(self):
        if self.ai_job:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.board = EMPTY_BOARD
        self.current_player = 'X'
        self.turn_count = 1
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=" ", bg="#FFFFFF")

        self._update_status("ตาเดิน: X")
        print(">>> เริ่มเกมกระดานใหม่ <<<\n")

    def _update_status(self, text, is_over=False):
        fg = "#B45309" if is_over else "#0F172A"
        self.status_lbl.config(text=text, fg=fg)

    def _update_scoreboard(self):
        self.lbl_x.config(text=f"คุณ: {self.scores['X']}")
        self.lbl_o.config(text=f"บอท: {self.scores['O']}")
        self.lbl_draw.config(text=f"เสมอ: {self.scores['Draw']}")

    def _check_game_end(self):
        winner = OXBoard.check_winner(self.board)
        if not winner:
            return False

        self.game_over = True
        self.scores[winner] += 1
        self._update_scoreboard()

        if winner == 'Draw':
            result_text = "เสมอกัน"
        else:
            who = "ผู้เล่น (X)" if winner == 'X' else "บอท (O)"
            for a, b, c in OXBoard.WINNING_COMBOS:
                if self.board[a] == self.board[b] == self.board[c] == winner:
                    for idx in (a, b, c):
                        self.buttons[idx].config(bg="#DCFCE7")
                    break
            result_text = f"{who} ชนะ"

        self._update_status(result_text, is_over=True)
        print(f"\nผลการแข่งขัน : {result_text}\n\n")
        return True

    def _on_cell_clicked(self, idx):
        if not self.game_over and self.board[idx] == ' ' and self.current_player == 'X':
            branches, _ = self.tree.evaluate_branches(self.board, 'X')
            if branches:
                debug_info = get_debug_text(self.board, 'X', self.turn_count, branches, idx)
                print(debug_info + "\n")
            self._execute_move(idx)

    def _execute_move(self, move_idx):
        self.board = OXBoard.place_symbol(self.board, move_idx, self.current_player)
        fg_color = "#DC2626" if self.current_player == 'X' else "#2563EB"
        self.buttons[move_idx].config(text=self.current_player, fg=fg_color)

        if self._check_game_end():
            return

        self.current_player = OXBoard.get_opponent(self.current_player)
        self.turn_count += 1
        if self.current_player == 'O':
            self._update_status("บอทกำลังคิด...")
            self.ai_job = self.root.after(350, self._ai_turn)
        else:
            self._update_status("ตาเดิน: X")

    def _ai_turn(self):
        if not self.game_over and self.current_player == 'O':
            branches, best_move = self.tree.evaluate_branches(self.board, 'O')
            if best_move is not None:
                debug_info = get_debug_text(self.board, 'O', self.turn_count, branches, best_move)
                print(debug_info + "\n")
                self._execute_move(best_move)


if __name__ == '__main__':
    root = tk.Tk()
    app = OXGameGUI(root)
    root.mainloop()
