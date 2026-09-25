import tkinter as tk
from gui import OXGameGUI

def main():
    root = tk.Tk()
    app = OXGameGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
