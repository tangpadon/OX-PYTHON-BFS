# Debug Formatting Utilities
def format_row(board, start_index, size):
    cells = []
    for i in range(start_index, start_index + size):
        char = board[i]
        if char == ' ':
            cells.append('.')
        else:
            cells.append(char)
    return " | ".join(cells)

def get_branch_score(branch):
    return branch['score']

def get_debug_text(tree, current_board, current_player, turn_number, chosen_move=None):
    branches, auto_best = tree.evaluate_branches(current_board, current_player)
    if len(branches) == 0:
        return f"--- Turn {turn_number} ({current_player}): ไม่พบกิ่งต่อไป ---"

    size = int(len(current_board) ** 0.5)

    border_line = "=" * 70
    dash_line = "-" * 70

    lines = []
    lines.append(border_line)
    lines.append(f" [DEBUG] TURN {turn_number} - ผู้เล่น: {current_player} | สถานะตารางปัจจุบัน:")

    for r in range(size):
        row_str = format_row(current_board, r * size, size)
        lines.append(f"       {row_str}")

    lines.append(dash_line)
    lines.append(f" กิ่งสถานะที่เป็นไปได้ (Child Nodes: {len(branches)} กิ่ง):")
    lines.append(dash_line)

    sorted_branches = sorted(branches, key=get_branch_score, reverse=True)

    for idx, b in enumerate(sorted_branches, start=1):
        if chosen_move is not None:
            is_best = (b['move'] == chosen_move)
        else:
            is_best = (b['move'] == auto_best)

        if is_best:
            star = " ★ [BEST MOVE]"
        else:
            star = ""

        if b['direct_result'] is not None:
            direct_str = f" [DIRECT {b['direct_result']}!]"
        else:
            direct_str = ""

        lines.append(f" กิ่งที่ #{idx}: ช่อง ({b['row']}, {b['col']}) [Index {b['move']}]{star}{direct_str}")
        lines.append(f"    └─ Minimax Value: {b['minimax_val']:+d} | ชนะ: {b['wins']}, แพ้: {b['losses']}, เสมอ: {b['draws']}")

        for r in range(size):
            row_str = format_row(b['next_board'], r * size, size)
            if r == 0:
                lines.append(f"       Preview: [{row_str}]")
            else:
                lines.append(f"                [{row_str}]")
        lines.append("")

    if chosen_move is not None:
        pick_move = chosen_move
    else:
        pick_move = auto_best

    r_sel = pick_move // size
    c_sel = pick_move % size
    lines.append(f" AI เลือกเดิน: ช่อง ({r_sel}, {c_sel}) [Index {pick_move}]")
    lines.append(border_line)
    return "\n".join(lines)

