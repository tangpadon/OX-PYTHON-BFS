from collections import deque
from ox_debug import get_debug_text

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

def swap_symbols(board):
    return board.translate(str.maketrans('XO', 'OX'))

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
        self._build_tree()

    def _build_tree(self):
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

        # Minimax Bottom-Up
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

    def get_node(self, board, player_turn):
        return self.state_map.get((board, player_turn))

    def evaluate_branches(self, current_board, current_player):
        node = self.state_map.get((current_board, current_player))
        if node is None:
            node = self.state_map.get((swap_symbols(current_board), get_opponent(current_player)))
            is_swapped = True
        else:
            is_swapped = False

        if node is None or not node.children:
            return [], None

        opponent = get_opponent(current_player)
        branches = []
        for child in node.children:
            if is_swapped:
                wins, losses, minimax_val = child.wins_x, child.wins_o, child.minimax_val
                direct_result = ('O' if child.winner == 'X' else
                                 'X' if child.winner == 'O' else child.winner)
            elif current_player == 'X':
                wins, losses, minimax_val = child.wins_x, child.wins_o, child.minimax_val
                direct_result = child.winner
            else:
                wins, losses, minimax_val = child.wins_o, child.wins_x, -child.minimax_val
                direct_result = child.winner

            total = wins + losses + child.draws
            branches.append({
                'move': child.move,
                'row': child.move // 3,
                'col': child.move % 3,
                'next_board': place_symbol(current_board, child.move, current_player),
                'wins': wins,
                'losses': losses,
                'draws': child.draws,
                'total_branches': total,
                'score': wins - losses,
                'win_rate': wins / total * 100.0 if total else 0.0,
                'minimax_val': minimax_val,
                'direct_result': direct_result,
            })

        # 1. เดินแล้วชนะทันที
        for b in branches:
            if b['direct_result'] == current_player:
                return branches, b['move']

        # 2. บล็อกคู่แข่งที่กำลังจะชนะในตาถัดไป
        for b in branches:
            if check_board_winner(place_symbol(current_board, b['move'], opponent)) == opponent:
                return branches, b['move']

        # 3. กลุ่ม Minimax สูงสุด → เลือกกิ่งคะแนนรวมสูงสุด
        best_minimax = max(b['minimax_val'] for b in branches)
        best_move = max((b for b in branches if b['minimax_val'] == best_minimax),
                        key=lambda b: b['score'])['move']
        return branches, best_move

    def get_debug_text(self, current_board, current_player, turn_number, chosen_move=None):
        return get_debug_text(self, current_board, current_player, turn_number, chosen_move)
