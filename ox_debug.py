# ==========================================
# Debug Formatting Utilities
# ==========================================

def format_row(board, start_index):
    cells = []
    for i in range(start_index, start_index + 3):
        char = board[i]
        if char == ' ':
            cells.append('.')
        else:
            cells.append(char)
    return cells[0] + " | " + cells[1] + " | " + cells[2]

def get_branch_score(branch):
    return branch['score']

def get_debug_text(tree, current_board, current_player, turn_number, chosen_move=None):
    branches, auto_best = tree.evaluate_branches(current_board, current_player)
    if len(branches) == 0:
        return f"--- Turn {turn_number} ({current_player}): ไม่พบกิ่งต่อไป ---"

    border_line = "=" * 70
    dash_line = "-" * 70

    lines = []
    lines.append(border_line)
    lines.append(f" [DEBUG] TURN {turn_number} - ผู้เล่น: {current_player} | สถานะตารางปัจจุบัน:")

    for start_idx in (0, 3, 6):
        row_str = format_row(current_board, start_idx)
        lines.append(f"       {row_str}")

    lines.append(dash_line)
    lines.append(f" กิ่งทางเลือกที่เป็นไปได้ทั้งหมดจากสถานะนี้ ({len(branches)} กิ่ง):")
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

        if b['minimax_val'] == 1:
            eval_desc = "การันตีชนะ (Force Win)"
        elif b['minimax_val'] == -1:
            eval_desc = "อาจพ่ายแพ้ (Losing branch)"
        else:
            eval_desc = "เสมอ (Draw)"

        lines.append(f"    └─ ผลวิเคราะห์เกม (Minimax): {eval_desc} (ค่า: {b['minimax_val']:+d})")

        r0 = format_row(b['next_board'], 0)
        r1 = format_row(b['next_board'], 3)
        r2 = format_row(b['next_board'], 6)

        lines.append(f"       Preview: [{r0}]")
        lines.append(f"                [{r1}]")
        lines.append(f"                [{r2}]")
        lines.append("")

    if chosen_move is not None:
        pick_move = chosen_move
    else:
        pick_move = auto_best

    r_sel = pick_move // 3
    c_sel = pick_move % 3
    lines.append(f" [สรุปการตัดสินใจ] AI เลือกเดินกิ่งช่อง ({r_sel}, {c_sel}) Index {pick_move}")
    lines.append(border_line)
    return "\n".join(lines)

