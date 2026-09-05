"""
test_engine.py
==============
ชุดทดสอบระบบ BFS Game Tree Engine สำหรับเกม OX
"""

import unittest
from ox_bfs_engine import OXBFSTree, check_board_winner

class TestOXBFSEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- เริ่มต้นสร้าง BFS Game Tree สำหรับการทดสอบ ---")
        cls.tree = OXBFSTree()

    def test_tree_construction(self):
        """ทดสอบการสร้างโหนดและกิ่งทั้งหมดใน Tree"""
        self.assertEqual(self.tree.total_nodes, 549946, "จำนวนโหนดทั้งหมดต้องเป็น 549,946 โหนด")
        total_leaves = self.tree.root.wins_x + self.tree.root.wins_o + self.tree.root.draws
        self.assertEqual(total_leaves, 255168, "จำนวนกิ่งปลายทาง (Leaves) ทั้งหมดต้องเป็น 255,168 กิ่ง")
        self.assertEqual(self.tree.root.wins_x, 131184, "กิ่ง X ชนะต้องมี 131,184 กิ่ง")
        self.assertEqual(self.tree.root.wins_o, 77904, "กิ่ง O ชนะต้องมี 77,904 กิ่ง")
        self.assertEqual(self.tree.root.draws, 46080, "กิ่งเสมอต้องมี 46,080 กิ่ง")
        self.assertEqual(self.tree.root.minimax_val, 0, "ผลลัพธ์เกมที่สมบูรณ์แบบของ OX ต้องเป็นเสมอ (0)")

    def test_first_turn_center_preference(self):
        """ทดสอบว่ากิ่งกลางกระดาน (1,1) ให้ Branch Score สูงสุดในเทิร์นแรก"""
        branches, best_move = self.tree.evaluate_branches(' ' * 9, 'X')
        self.assertEqual(len(branches), 9, "เทิร์นแรกต้องมี 9 กิ่งทางเลือก")
        self.assertEqual(best_move, 4, "ตาเดินแรกที่ดีที่สุดควรเป็นช่องตรงกลาง (Index 4)")

        # ช่อง 4 ต้องมีคะแนนรวมสูงสุด
        center_branch = next(b for b in branches if b['move'] == 4)
        for b in branches:
            if b['move'] != 4:
                self.assertGreater(center_branch['score'], b['score'])

    def test_direct_win_priority(self):
        """ทดสอบว่า AI เลือกกิ่งที่ชนะทันที (Direct Win) เมื่อมีโอกาส"""
        # กระดานที่ O กำลังจะชนะที่ช่อง 2
        # O O .
        # X X .
        # . . .
        board = 'OO ' + 'XX ' + '   '
        branches, best_move = self.tree.evaluate_branches(board, 'O')
        self.assertEqual(best_move, 2, "AI (O) ต้องเลือกเดินช่อง 2 เพื่อชนะทันที")

    def test_block_opponent_threat(self):
        """ทดสอบว่า AI บล็อกการชนะของคู่แข่ง"""
        # กระดานที่ X ขู่จะชนะที่ช่อง 2
        # X X .
        # . O .
        # . . .
        board = 'XX ' + ' O ' + '   '
        branches, best_move = self.tree.evaluate_branches(board, 'O')
        self.assertEqual(best_move, 2, "AI (O) ต้องเลือกเดินช่อง 2 เพื่อบล็อก X")

    def test_o_first_move_evaluation(self):
        """ทดสอบว่าเมื่อ O เป็นฝ่ายเดินก่อน ตารางว่างเปล่ายังวิเคราะห์กิ่งได้ถูกต้อง"""
        branches, best_move = self.tree.evaluate_branches(' ' * 9, 'O')
        self.assertEqual(len(branches), 9, "เทิร์นแรกของ O ต้องมี 9 กิ่งทางเลือก")
        self.assertEqual(best_move, 4, "ตาเดินแรกที่ดีที่สุดสำหรับ O บนตารางว่างคือช่องกลาง (Index 4)")

    def test_debug_text_generation(self):
        """ทดสอบการสร้างข้อความ DEBUG ประจำเทิร์น"""
        debug_str = self.tree.get_debug_text(' ' * 9, 'X', turn_number=1)
        self.assertIn("[DEBUG] TURN 1", debug_str)
        self.assertIn("กิ่งทางเลือกที่เป็นไปได้ทั้งหมดจากสถานะนี้ (9 กิ่ง):", debug_str)
        self.assertIn("[BEST MOVE]", debug_str)

    def test_full_ai_vs_ai_game(self):
        """ทดสอบการจำลองบอทเล่นกับตัวเองจนจบเกม ต้องได้ผลเสมอตามทฤษฎีเกม"""
        board = ' ' * 9
        current_p = 'X'
        turns = 0
        while check_board_winner(board) is None and ' ' in board:
            turns += 1
            _, move = self.tree.evaluate_branches(board, current_p)
            board = board[:move] + current_p + board[move+1:]
            current_p = 'O' if current_p == 'X' else 'X'
            self.assertLessEqual(turns, 9)
        
        self.assertEqual(check_board_winner(board), 'Draw', "เมื่อบอทเล่นด้วยกลยุทธ์สมบูรณ์แบบ ผลต้องเป็นเสมอ")

if __name__ == '__main__':
    unittest.main()

