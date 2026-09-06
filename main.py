import sys
import tkinter as tk
from gui import OXGameGUI
from ox_bfs_engine import OXBFSTree, check_board_winner

def run_gui():
    root = tk.Tk()
    app = OXGameGUI(root)
    root.mainloop()

def run_cli_demo():
    print("\n" + "=" * 55)
    print(" 🎮 เกม OX (Tic-Tac-Toe) - Terminal Demonstration")
    print("=" * 55)
    tree = OXBFSTree()
    board = ' ' * 9
    current_player = 'X'
    turn = 1

    while True:
        print(tree.get_debug_text(board, current_player, turn))
        _, best_move = tree.evaluate_branches(board, current_player)
        r, c = divmod(best_move, 3)
        print(f">> ผู้เล่น {current_player} เดินช่อง ({r}, {c})")
        board = board[:best_move] + current_player + board[best_move + 1:]
        
        winner = check_board_winner(board)
        if winner:
            print("\n---------------- จบเกม ----------------")
            for r in range(3):
                print(" | ".join(board[r*3:r*3+3]).replace(' ', '.'))
            print(f"ผลลัพธ์: {winner}\n")
            break
            
        current_player = 'O' if current_player == 'X' else 'X'
        turn += 1

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli_demo()
    else:
        run_gui()
