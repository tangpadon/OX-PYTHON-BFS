from collections import deque
import time
from ox_debug import get_debug_text

# ==========================================
# Board Utilities
# ==========================================

WINNING_COMBOS = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
)

def get_opponent(player):
    if player == 'X':
        return 'O'
    else:
        return 'X'

def place_symbol(board, position, player):
    board_list = list(board)
    board_list[position] = player
    return "".join(board_list)

def check_board_winner(board):
    for a, b, c in WINNING_COMBOS:
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None

# ==========================================
# Game Tree Node
# ==========================================

class GameNode:
    def __init__(self, board, player_turn, move=None, depth=0):
        self.board = board
        self.player_turn = player_turn
        self.move = move
        self.depth = depth
        self.children = []
        self.winner = check_board_winner(board)
        if self.winner is not None:
            self.is_terminal = True
        else:
            self.is_terminal = False
        self.wins_x = 0
        self.wins_o = 0
        self.draws = 0
        self.minimax_val = None

# ==========================================
# BFS Game Tree (Core Engine)
# ==========================================

class OXBFSTree:
    def __init__(self):
        self.root = None
        self.state_map = {}
        self.total_nodes = 0
        self.total_leaves = 0
        self.build_time = 0.0
        self._build_tree()

    def _build_tree(self):
        t0 = time.time()
        initial_board = ' ' * 9
        self.root = GameNode(initial_board, 'X', depth=0)
        
        queue = deque([self.root])
        all_nodes = [self.root]
        self.state_map[(initial_board, 'X')] = self.root

        while len(queue) > 0:
            node = queue.popleft()
            if node.is_terminal:
                continue

            next_player = get_opponent(node.player_turn)
            for pos in range(9):
                if node.board[pos] == ' ':
                    next_board = place_symbol(node.board, pos, node.player_turn)
                    child = GameNode(next_board, next_player, move=pos, depth=node.depth + 1)
                    node.children.append(child)
                    queue.append(child)
                    all_nodes.append(child)
                    self.state_map[(next_board, next_player)] = child

        self.total_nodes = len(all_nodes)

        for node in reversed(all_nodes):
            if node.is_terminal:
                self.total_leaves = self.total_leaves + 1
                if node.winner == 'X':
                    node.wins_x = 1
                    node.minimax_val = 1
                elif node.winner == 'O':
                    node.wins_o = 1
                    node.minimax_val = -1
                else:
                    node.draws = 1
                    node.minimax_val = 0
            else:
                for child in node.children:
                    node.wins_x = node.wins_x + child.wins_x
                    node.wins_o = node.wins_o + child.wins_o
                    node.draws = node.draws + child.draws

                child_values = []
                for child in node.children:
                    child_values.append(child.minimax_val)

                if node.player_turn == 'X':
                    node.minimax_val = max(child_values)
                else:
                    node.minimax_val = min(child_values)

        self.build_time = time.time() - t0
        total_leaves = self.root.wins_x + self.root.wins_o + self.root.draws
        print(f"[BFS Engine] Game Tree สร้างเสร็จสมบูรณ์ใน {self.build_time:.2f} วินาที")
        print(f"[BFS Engine] โหนดทั้งหมด: {self.total_nodes:,} โหนด | กิ่งปลายทางทั้งหมด: {total_leaves:,} กิ่ง")

    def get_node(self, board, player_turn):
        return self.state_map.get((board, player_turn))

    def evaluate_branches(self, current_board, current_player):
        opponent = get_opponent(current_player)
        node = self.get_node(current_board, current_player)

        is_transposed = False
        if node is None:
            trans_chars = []
            for char in current_board:
                if char == 'X':
                    trans_chars.append('O')
                elif char == 'O':
                    trans_chars.append('X')
                else:
                    trans_chars.append(' ')
            trans_board = "".join(trans_chars)
            trans_player = get_opponent(current_player)
            node = self.get_node(trans_board, trans_player)
            if node is not None:
                is_transposed = True

        if node is not None and len(node.children) > 0:
            branch_details = []
            for child in node.children:
                move = child.move
                row = move // 3
                col = move % 3

                if is_transposed:
                    wins = child.wins_x
                    losses = child.wins_o
                    child_minimax = child.minimax_val
                    if child.winner == 'X':
                        direct_result = 'O'
                    elif child.winner == 'O':
                        direct_result = 'X'
                    else:
                        direct_result = child.winner
                else:
                    if current_player == 'X':
                        wins = child.wins_x
                        losses = child.wins_o
                        child_minimax = child.minimax_val
                    else:
                        wins = child.wins_o
                        losses = child.wins_x
                        child_minimax = -child.minimax_val
                    direct_result = child.winner

                draws = child.draws
                total = wins + losses + draws
                score = (wins * 1) + (losses * -1)

                if total > 0:
                    win_rate = (wins / total) * 100.0
                else:
                    win_rate = 0.0

                next_board = place_symbol(current_board, move, current_player)

                branch_data = {
                    'move': move,
                    'row': row,
                    'col': col,
                    'next_board': next_board,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'total_branches': total,
                    'score': score,
                    'win_rate': win_rate,
                    'minimax_val': child_minimax,
                    'direct_result': direct_result
                }
                branch_details.append(branch_data)
        else:
            branch_details = self._bfs_search_from_state(current_board, current_player)

        if len(branch_details) == 0:
            return [], None

        for b in branch_details:
            if b['direct_result'] == current_player:
                return branch_details, b['move']

        for b in branch_details:
            opp_board = place_symbol(current_board, b['move'], opponent)
            if check_board_winner(opp_board) == opponent:
                return branch_details, b['move']

        all_minimax = []
        for b in branch_details:
            all_minimax.append(b['minimax_val'])
        best_minimax = max(all_minimax)

        candidates = []
        for b in branch_details:
            if b['minimax_val'] == best_minimax:
                candidates.append(b)

        best_candidate = None
        highest_score = None
        for b in candidates:
            if highest_score is None or b['score'] > highest_score:
                highest_score = b['score']
                best_candidate = b

        best_move = best_candidate['move']
        return branch_details, best_move

    def _bfs_search_from_state(self, current_board, current_player):
        opponent = get_opponent(current_player)
        
        valid_moves = []
        for i in range(9):
            if current_board[i] == ' ':
                valid_moves.append(i)

        branches = []
        for move in valid_moves:
            row = move // 3
            col = move % 3
            next_b = place_symbol(current_board, move, current_player)
            winner = check_board_winner(next_b)

            if winner is not None:
                if winner == current_player:
                    wins = 1
                    losses = 0
                    draws = 0
                    score = 1
                    win_rate = 100.0
                    minimax_val = 1
                elif winner == opponent:
                    wins = 0
                    losses = 1
                    draws = 0
                    score = -1
                    win_rate = 0.0
                    minimax_val = -1
                else:
                    wins = 0
                    losses = 0
                    draws = 1
                    score = 0
                    win_rate = 0.0
                    minimax_val = 0

                branches.append({
                    'move': move,
                    'row': row,
                    'col': col,
                    'next_board': next_b,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'total_branches': 1,
                    'score': score,
                    'win_rate': win_rate,
                    'minimax_val': minimax_val,
                    'direct_result': winner
                })
                continue

            sub_root = GameNode(next_b, opponent, move=move, depth=0)
            queue = deque([sub_root])
            nodes = [sub_root]

            while len(queue) > 0:
                curr = queue.popleft()
                if curr.is_terminal:
                    continue
                next_p = get_opponent(curr.player_turn)
                for pos in range(9):
                    if curr.board[pos] == ' ':
                        nb = place_symbol(curr.board, pos, curr.player_turn)
                        child = GameNode(nb, next_p, move=pos, depth=curr.depth + 1)
                        curr.children.append(child)
                        queue.append(child)
                        nodes.append(child)

            for n in reversed(nodes):
                if n.is_terminal:
                    if n.winner == current_player:
                        n.wins_x = 1
                        n.minimax_val = 1
                    elif n.winner == opponent:
                        n.wins_o = 1
                        n.minimax_val = -1
                    else:
                        n.draws = 1
                        n.minimax_val = 0
                else:
                    for ch in n.children:
                        n.wins_x = n.wins_x + ch.wins_x
                        n.wins_o = n.wins_o + ch.wins_o
                        n.draws = n.draws + ch.draws

                    child_values = []
                    for ch in n.children:
                        child_values.append(ch.minimax_val)

                    if n.player_turn == current_player:
                        n.minimax_val = max(child_values)
                    else:
                        n.minimax_val = min(child_values)

            total = sub_root.wins_x + sub_root.wins_o + sub_root.draws
            score = (sub_root.wins_x * 1) + (sub_root.wins_o * -1)
            if total > 0:
                win_rate = (sub_root.wins_x / total) * 100.0
            else:
                win_rate = 0.0

            branches.append({
                'move': move,
                'row': row,
                'col': col,
                'next_board': next_b,
                'wins': sub_root.wins_x,
                'losses': sub_root.wins_o,
                'draws': sub_root.draws,
                'total_branches': total,
                'score': score,
                'win_rate': win_rate,
                'minimax_val': sub_root.minimax_val,
                'direct_result': None
            })

        return branches

    def get_debug_text(self, current_board, current_player, turn_number, chosen_move=None):
        return get_debug_text(self, current_board, current_player, turn_number, chosen_move)
