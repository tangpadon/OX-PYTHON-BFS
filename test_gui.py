"""
test_gui.py
===========
ทดสอบการทำงานของ GUI และ Event Handling โดยไม่ค้างหน้าต่าง
"""

import unittest
import tkinter as tk
from gui import OXGameGUI

class TestOXGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        # ซ่อนหน้าต่างขณะทดสอบ
        self.root.withdraw()
        self.app = OXGameGUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_gui_initial_state(self):
        """ทดสอบสถานะเริ่มต้นของ GUI"""
        self.assertEqual(self.app.board, ' ' * 9)
        self.assertEqual(self.app.current_player, 'X')
        self.assertEqual(self.app.turn_count, 1)
        self.assertFalse(self.app.game_over)
        self.assertEqual(len(self.app.buttons), 9)

    def test_cell_click_and_debug_output(self):
        """ทดสอบการคลิกเลือกช่องตารางและสร้างข้อความ DEBUG"""
        # ผู้เล่นคลิกช่องกลาง (Index 4)
        self.app._on_cell_clicked(4)
        self.assertEqual(self.app.board[4], 'X')
        self.assertEqual(self.app.current_player, 'O')
        self.assertEqual(self.app.turn_count, 2)

        # ตรวจสอบว่า Text Widget มีข้อความ DEBUG
        log_content = self.app.debug_text.get("1.0", tk.END)
        self.assertIn("[DEBUG] TURN 1", log_content)
        self.assertIn("ช่อง (1, 1) [Index 4]", log_content)

    def test_new_game_reset(self):
        """ทดสอบการรีเซ็ตเกม"""
        self.app._on_cell_clicked(0)
        self.assertNotEqual(self.app.board, ' ' * 9)
        self.app.start_new_game()
        self.assertEqual(self.app.board, ' ' * 9)
        self.assertEqual(self.app.current_player, 'X')
        self.assertEqual(self.app.turn_count, 1)

if __name__ == '__main__':
    unittest.main()

