from collections import deque
import time
from ox_debug import get_debug_text

# Board Settings
BOARD_SIZE = 3
TOTAL_CELLS = BOARD_SIZE * BOARD_SIZE

def get_winning_combos(size):
    combos = []
    
    # 1. แนวนอน
    for r in range(size):
        row = []
        for c in range(size):
            row.append(r * size + c)
        combos.append(tuple(row))
        
    # 2. แนวตั้ง
    for c in range(size):
        col = []
        for r in range(size):
            col.append(r * size + c)
        combos.append(tuple(col))
        
    # 3. แนวทแยงซ้ายไปขวา
    diag1 = []
    for i in range(size):
        diag1.append(i * size + i)
    combos.append(tuple(diag1))
    
    # 4. แนวทแยงขวาไปซ้าย
    diag2 = []
    for i in range(size):
        diag2.append(i * size + (size - 1 - i))
    combos.append(tuple(diag2))
    
    return tuple(combos)

WINNING_COMBOS = get_winning_combos(BOARD_SIZE)

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
    for combo in WINNING_COMBOS:
        first = combo[0]
        if board[first] != ' ':
            all_match = True
            for pos in combo:
                if board[pos] != board[first]:
                    all_match = False
                    break
            if all_match:
                return board[first]
    if ' ' not in board:
        return 'Draw'
    return None

# Game Tree Node
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

# BFS Game Tree (Core Engine)
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
        initial_board = ' ' * TOTAL_CELLS
        self.root = GameNode(initial_board, 'X', depth=0)
        
        queue = deque([self.root])
        all_nodes = [self.root]
        self.state_map[(initial_board, 'X')] = self.root

        while len(queue) > 0:
            node = queue.popleft()
            if node.is_terminal:
                continue

            next_player = get_opponent(node.player_turn)
            for pos in range(TOTAL_CELLS):
                if node.board[pos] == ' ':
                    next_board = place_symbol(node.board, pos, node.player_turn)
                    child = GameNode(next_board, next_player, move=pos, depth=node.depth + 1)
                    node.children.append(child)
                    queue.append(child)
                    all_nodes.append(child)
                    self.state_map[(next_board, next_player)] = child

        self.total_nodes = len(all_nodes)

        # คำนวณผลสรุปและค่า Minimax ย้อนกลับจากล่างขึ้นบน (Bottom-Up)
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

    def get_node(self, board, player_turn):
        return self.state_map.get((board, player_turn))

    def evaluate_branches(self, current_board, current_player):
        opponent = get_opponent(current_player)
        node = self.state_map.get((current_board, current_player))

        # ถ้าไม่พบสถานะนี้ ให้สลับ X กับ O เพื่อค้นหาใน Tree
        if node is None:
            swapped_board = ""
            for char in current_board:
                if char == 'X':
                    swapped_board = swapped_board + 'O'
                elif char == 'O':
                    swapped_board = swapped_board + 'X'
                else:
                    swapped_board = swapped_board + ' '
            swapped_player = get_opponent(current_player)
            node = self.state_map.get((swapped_board, swapped_player))
            is_swapped = True
        else:
            is_swapped = False

        if node is None or len(node.children) == 0:
            return [], None

        branches = []
        for child in node.children:
            move = child.move
            row = move // BOARD_SIZE
            col = move % BOARD_SIZE

            if is_swapped:
                wins = child.wins_x
                losses = child.wins_o
                minimax_val = child.minimax_val
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
                    minimax_val = child.minimax_val
                else:
                    wins = child.wins_o
                    losses = child.wins_x
                    minimax_val = -child.minimax_val
                direct_result = child.winner

            draws = child.draws
            total = wins + losses + draws
            score = (wins * 1) + (losses * -1)

            if total > 0:
                win_rate = (wins / total) * 100.0
            else:
                win_rate = 0.0

            next_board = place_symbol(current_board, move, current_player)

            branch = {
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
                'minimax_val': minimax_val,
                'direct_result': direct_result
            }
            branches.append(branch)

        # 1. ถ้าเดินแล้วชนะเลย ให้เดินช่องนั้นทันที
        for b in branches:
            if b['direct_result'] == current_player:
                return branches, b['move']

        # 2. ถ้าคู่แข่งกำลังจะชนะ ต้องเดินบล็อก
        for b in branches:
            opp_board = place_symbol(current_board, b['move'], opponent)
            if check_board_winner(opp_board) == opponent:
                return branches, b['move']

        # 3. หากิ่งที่ Minimax สูงที่สุด
        best_minimax = -999
        for b in branches:
            if b['minimax_val'] > best_minimax:
                best_minimax = b['minimax_val']

        # 4. ในกลุ่ม Minimax สูงสุด ให้เลือกกิ่งที่ได้คะแนนสูงสุด
        best_move = None
        highest_score = -999999
        for b in branches:
            if b['minimax_val'] == best_minimax:
                if b['score'] > highest_score:
                    highest_score = b['score']
                    best_move = b['move']

        return branches, best_move

    def get_debug_text(self, current_board, current_player, turn_number, chosen_move=None):
        return get_debug_text(self, current_board, current_player, turn_number, chosen_move)
