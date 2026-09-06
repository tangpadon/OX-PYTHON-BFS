import tkinter as tk
from tkinter import ttk, messagebox
import time
from ox_bfs_engine import OXBFSTree, WINNING_COMBOS

def place_symbol(board, position, player):
    board_list = list(board)
    board_list[position] = player
    return "".join(board_list)

# ==========================================
# GUI Application
# ==========================================

class OXGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OX Game (Tic-Tac-Toe) - ผู้เล่น (X) vs บอท BFS (O)")
        self.root.geometry("1180x740")
        self.root.minsize(980, 620)
        self.root.configure(bg="#F0F2F5")

        self.COLOR_BG = "#F0F2F5"
        self.COLOR_CARD = "#FFFFFF"
        self.COLOR_X = "#1565C0"
        self.COLOR_O = "#D84315"
        self.COLOR_WIN = "#C8E6C9"
        self.COLOR_BTN = "#FFFFFF"
        self.COLOR_BTN_HOVER = "#E3F2FD"

        self.board = ' ' * 9
        self.current_player = 'X'
        self.turn_count = 1
        self.game_over = False
        self.scores = {'X': 0, 'O': 0, 'Draw': 0}
        self.ai_job = None
        self.ai_delay_ms = 250

        self.tree = None
        self._init_engine()
        self._create_widgets()
        self.start_new_game()

    def _init_engine(self):
        t0 = time.time()
        print("[GUI] กำลังโหลดและสร้าง BFS Game Tree...")
        self.tree = OXBFSTree()
        print(f"[GUI] โหลด BFS Engine สำเร็จ ใช้เวลา {time.time() - t0:.2f} วินาที")

    # ==========================================
    # Layout Components
    # ==========================================

    def _create_widgets(self):
        header = tk.Frame(self.root, bg="#1E293B", height=65)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="🎮 เกม OX (Tic-Tac-Toe)",
            font=("Segoe UI", 15, "bold"),
            fg="#F8FAFC",
            bg="#1E293B"
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        header_right = tk.Frame(header, bg="#1E293B")
        header_right.pack(side=tk.RIGHT, padx=20, pady=10)

        self.btn_restart = tk.Button(
            header_right,
            text="🔄 Restart ตาราง",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.start_new_game
        )
        self.btn_restart.pack(side=tk.RIGHT)

        main_container = tk.Frame(self.root, bg=self.COLOR_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        main_container.columnconfigure(0, weight=4, uniform="col")
        main_container.columnconfigure(1, weight=6, uniform="col")
        main_container.rowconfigure(0, weight=1)

        # Left Panel: Board & Status
        left_panel = tk.Frame(main_container, bg=self.COLOR_CARD, bd=1, relief=tk.SOLID)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), ipadx=10, ipady=10)

        info_frame = tk.LabelFrame(left_panel, text=" 👥 ข้อมูลการแข่งขัน ", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg="#334155")
        info_frame.pack(fill=tk.X, padx=15, pady=(5, 10))

        tk.Label(info_frame, text="👤 ผู้เล่น: สัญลักษณ์ X (เดินก่อน)", font=("Segoe UI", 9, "bold"), fg=self.COLOR_X, bg=self.COLOR_CARD).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(info_frame, text="🤖 บอท BFS: สัญลักษณ์ O ", font=("Segoe UI", 9, "bold"), fg=self.COLOR_O, bg=self.COLOR_CARD).pack(anchor=tk.W, padx=10, pady=2)

        score_frame = tk.Frame(left_panel, bg="#F1F5F9", relief=tk.GROOVE, bd=1)
        score_frame.pack(fill=tk.X, padx=15, pady=5)

        self.lbl_score_x = tk.Label(score_frame, text="👤 ผู้เล่น (X): 0", font=("Segoe UI", 9, "bold"), fg=self.COLOR_X, bg="#F1F5F9")
        self.lbl_score_x.pack(side=tk.LEFT, expand=True, pady=8)

        self.lbl_score_draw = tk.Label(score_frame, text="🤝 เสมอ: 0", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#F1F5F9")
        self.lbl_score_draw.pack(side=tk.LEFT, expand=True, pady=8)

        self.lbl_score_o = tk.Label(score_frame, text="🤖 บอท (O): 0", font=("Segoe UI", 9, "bold"), fg=self.COLOR_O, bg="#F1F5F9")
        self.lbl_score_o.pack(side=tk.LEFT, expand=True, pady=8)

        self.status_lbl = tk.Label(
            left_panel,
            text="เทิร์น: ตาเดินของคุณ (X)",
            font=("Segoe UI", 12, "bold"),
            bg="#E2E8F0",
            fg="#0F172A",
            height=2,
            relief=tk.RIDGE
        )
        self.status_lbl.pack(fill=tk.X, padx=15, pady=8)

        board_frame = tk.Frame(left_panel, bg="#CBD5E1", bd=2, relief=tk.SUNKEN)
        board_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        for r in range(3):
            board_frame.rowconfigure(r, weight=1, uniform="cell")
            board_frame.columnconfigure(r, weight=1, uniform="cell")

        self.buttons = []
        for i in range(9):
            row = i // 3
            col = i % 3
            btn = tk.Button(
                board_frame,
                text=" ",
                font=("Segoe UI", 32, "bold"),
                bg=self.COLOR_BTN,
                activebackground=self.COLOR_BTN_HOVER,
                relief=tk.FLAT,
                bd=1,
                cursor="hand2",
                command=lambda index=i: self._on_cell_clicked(index)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            self.buttons.append(btn)

        # Right Panel: Debug Console
        right_panel = tk.Frame(main_container, bg=self.COLOR_CARD, bd=1, relief=tk.SOLID)
        right_panel.grid(row=0, column=1, sticky="nsew")

        debug_header = tk.Frame(right_panel, bg="#0F172A", height=40)
        debug_header.pack(fill=tk.X, side=tk.TOP)

        debug_title = tk.Label(
            debug_header,
            text="📊 DEBUG Console: การแตกกิ่งที่เป็นไปได้ทั้งหมด (All BFS Branches Analysis)",
            font=("Consolas", 10, "bold"),
            fg="#38BDF8",
            bg="#0F172A"
        )
        debug_title.pack(side=tk.LEFT, padx=12, pady=8)

        btn_copy = tk.Button(
            debug_header,
            text="📋 Copy Log",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="#F8FAFC",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._copy_debug_log
        )
        btn_copy.pack(side=tk.RIGHT, padx=5, pady=5)

        btn_clear = tk.Button(
            debug_header,
            text="🧹 Clear Log",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="#F8FAFC",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._clear_debug_log, 
        )
        btn_clear.pack(side=tk.RIGHT, padx=5, pady=5)

        self.debug_text = tk.Text(
            right_panel,
            wrap=tk.NONE,
            font=("Consolas", 9),
            bg="#020617",
            fg="#E2E8F0",
            insertbackground="#38BDF8",
            padx=10,
            pady=10,
            relief=tk.FLAT
        )
        
        v_scroll = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.debug_text.yview)
        h_scroll = ttk.Scrollbar(right_panel, orient=tk.HORIZONTAL, command=self.debug_text.xview)
        self.debug_text.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.debug_text.pack(fill=tk.BOTH, expand=True)

        self.debug_text.tag_config("turn_header", foreground="#38BDF8", font=("Consolas", 9, "bold"))
        self.debug_text.tag_config("best_move", foreground="#4ADE80", font=("Consolas", 9, "bold"))

        border_line = "=" * 70
        welcome_msg = (
            border_line + "\n"
            " ระบบวิเคราะห์กิ่งเกม OX ด้วย Breadth-First Search (BFS)\n"
            " โหมด: 👤 ผู้เล่น (X) vs 🤖 บอท BFS (O)\n"
            " โครงสร้าง: เริ่มต้นจากตารางว่างเปล่า 3x3 (' '*9) แตกกิ่งทั้งหมด 549,946 โหนด\n"
            + border_line + "\n\n"
        )
        self._append_debug_log(welcome_msg)

    # ==========================================
    # Game Events & Move Execution
    # ==========================================

    def _append_debug_log(self, text):
        print(text)
        self.debug_text.insert(tk.END, text)
        self.debug_text.see(tk.END)

    def _clear_debug_log(self):
        self.debug_text.delete("1.0", tk.END)

    def _copy_debug_log(self):
        content = self.debug_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("คัดลอกสำเร็จ", "คัดลอกเนื้อหา DEBUG Log ไปยังคลิปบอร์ดแล้ว!")

    def start_new_game(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self._clear_debug_log()
        self.board = ' ' * 9
        self.current_player = 'X'
        self.turn_count = 1
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=" ", bg=self.COLOR_BTN, fg="#000000", state=tk.NORMAL)

        self._update_status("เทิร์นที่ 1: ตาเดินของคุณ (X)")
        self._append_debug_log(">>> เริ่มเกมกระดานใหม่ (New Match Started) <<<\n")

    def _update_status(self, text, is_over=False):
        self.status_lbl.config(text=text)
        if is_over:
            self.status_lbl.config(bg="#FEF08A", fg="#854D0E")
        else:
            self.status_lbl.config(bg="#E2E8F0", fg="#0F172A")

    def _update_scoreboard(self):
        self.lbl_score_x.config(text=f"👤 ผู้เล่น (X): {self.scores['X']}")
        self.lbl_score_o.config(text=f"🤖 บอท (O): {self.scores['O']}")
        self.lbl_score_draw.config(text=f"🤝 เสมอ: {self.scores['Draw']}")

    def _highlight_winning_line(self, combo):
        for idx in combo:
            self.buttons[idx].config(bg=self.COLOR_WIN)

    def _check_game_end(self):
        for combo in WINNING_COMBOS:
            a, b, c = combo
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                winner = self.board[a]
                self.game_over = True
                self.scores[winner] = self.scores[winner] + 1
                self._update_scoreboard()
                self._highlight_winning_line(combo)

                if winner == 'X':
                    who = "👤 คุณ (X)"
                else:
                    who = "🤖 บอท BFS (O)"

                self._update_status(f"🎉 {who} เป็นฝ่ายชนะ!", is_over=True)
                self._append_debug_log(f"\n[ผลการแข่งขัน] {who} ชนะเกมในเทิร์นที่ {self.turn_count}!\n\n")
                return True

        if ' ' not in self.board:
            self.game_over = True
            self.scores['Draw'] = self.scores['Draw'] + 1
            self._update_scoreboard()
            self._update_status("🤝 ผลการแข่งขัน: เสมอกัน (Draw)!", is_over=True)
            self._append_debug_log(f"\n[ผลการแข่งขัน] เสมอกัน (Draw) ในเทิร์นที่ {self.turn_count}!\n\n")
            return True

        return False

    def _on_cell_clicked(self, idx):
        if self.game_over:
            return
        if self.board[idx] != ' ':
            return
        if self.current_player != 'X':
            return
        self._execute_move(idx)

    def _execute_move(self, move_idx):
        debug_output = self.tree.get_debug_text(
            self.board, self.current_player, self.turn_count, chosen_move=move_idx
        )
        self._append_debug_log(debug_output + "\n")

        self.board = place_symbol(self.board, move_idx, self.current_player)

        if self.current_player == 'X':
            color = self.COLOR_X
        else:
            color = self.COLOR_O

        self.buttons[move_idx].config(text=self.current_player, fg=color)

        if self._check_game_end():
            return

        if self.current_player == 'X':
            self.current_player = 'O'
        else:
            self.current_player = 'X'

        self.turn_count = self.turn_count + 1
        
        if self.current_player == 'O':
            self._update_status(f"เทิร์นที่ {self.turn_count}: 🤖 บอท BFS กำลังวิเคราะห์กิ่ง...")
            self.ai_job = self.root.after(self.ai_delay_ms, self._ai_turn)
        else:
            self._update_status(f"เทิร์นที่ {self.turn_count}: ตาเดินของคุณ (X)")

    def _ai_turn(self):
        if self.game_over:
            return
        if self.current_player != 'O':
            return

        branches, best_move = self.tree.evaluate_branches(self.board, self.current_player)
        if best_move is not None:
            self._execute_move(best_move)
