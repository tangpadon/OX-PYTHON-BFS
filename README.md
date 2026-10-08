# คำอธิบายฟังก์ชันทั้งหมดใน main.py

คู่มือสรุปการทำงานของฟังก์ชันและเมธอดทั้งหมดในโปรแกรมเกม OX (Tic-Tac-Toe) อธิบายหน้าที่ พารามิเตอร์ และขั้นตอนการทำงานอย่างละเอียดสำหรับผู้เริ่มต้นถึงระดับปานกลาง

---

## สารบัญฟังก์ชัน

1. [ฟังก์ชันในคลาส `OXBoard` (กฎกติกาและกระดาน)](#1-ฟังก์ชันในคลาส-oxboard-กฎกติกาและกระดาน)
   - [`get_opponent(player)`](#get_opponentplayer)
   - [`place_symbol(board, position, player)`](#place_symbolboard-position-player)
   - [`check_winner(board)`](#check_winnerboard)
2. [ฟังก์ชันในคลาส `GameNode` (โครงสร้างโหนดสถานะเกม)](#2-ฟังก์ชันในคลาส-gamenode-โครงสร้างโหนดสถานะเกม)
   - [`__init__(self, board, player_turn, move)`](#__initself-board-player_turn-move)
3. [ฟังก์ชันตัวช่วยนอกคลาส (Helper Functions)](#3-ฟังก์ชันตัวช่วยนอกคลาส-helper-functions)
   - [`branch_sort_key(b, player)`](#branch_sort_keyb-player)
   - [`format_row(board, start_index)`](#format_rowboard-start_index)
   - [`get_debug_text(board, player, turn, branches, selected_move)`](#get_debug_textboard-player-turn-branches-selected_move)
4. [ฟังก์ชันในคลาส `OXBFSTree` (สมองกล AI: BFS & Minimax)](#4-ฟังก์ชันในคลาส-oxbfstree-สมองกล-ai-bfs--minimax)
   - [`__init__(self)`](#__initself)
   - [`_build_tree(self)`](#_build_treeself)
   - [`evaluate_branches(self, current_board, player)`](#evaluate_branchesself-current_board-player)
5. [ฟังก์ชันในคลาส `OXGameGUI` (ระบบหน้าต่างเกมและการเล่น)](#5-ฟังก์ชันในคลาส-oxgamegui-ระบบหน้าต่างเกมและการเล่น)
   - [`__init__(self, root)`](#__initself-root)
   - [`_create_widgets(self)`](#_create_widgetsself)
   - [`start_new_game(self)`](#start_new_gameself)
   - [`_update_status(self, text, is_over)`](#_update_statusself-text-is_over)
   - [`_update_scoreboard(self)`](#_update_scoreboardself)
   - [`_check_game_end(self)`](#_check_game_endself)
   - [`_on_cell_clicked(self, idx)`](#_on_cell_clickedself-idx)
   - [`_execute_move(self, move_idx)`](#_execute_moveself-move_idx)
   - [`_ai_turn(self)`](#_ai_turnself)

---

## 1. ฟังก์ชันในคลาส `OXBoard` (กฎกติกาและกระดาน)

คลาสนี้เป็นคลังฟังก์ชันคำนวณเกี่ยวกับกฎกติกาของเกม โดยสามารถเรียกใช้งานผ่านชื่อคลาสได้ทันที เช่น `OXBoard.check_winner(board)` โดยไม่จำเป็นต้องสร้างอ็อบเจกต์

---

### `get_opponent(player)`

```python
def get_opponent(player):
    return 'O' if player == 'X' else 'X'
```

* **ใช้ทำอะไร:** สลับสัญลักษณ์เพื่อหาว่าใครคือผู้เล่นฝ่ายตรงข้าม
* **ข้อมูลที่รับเข้า (Input):**
  * `player` (str): สัญลักษณ์ผู้เล่นปัจจุบัน (`'X'` หรือ `'O'`)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * คืนค่า `'O'` หากส่ง `'X'` เข้ามา และคืนค่า `'X'` หากส่งตัวอื่นเข้ามา
* **ทำงานยังไง:**
  * ใช้คำสั่งเงื่อนไขแบบบรรทัดเดียว (Ternary Operator) ตรวจสอบว่า `player == 'X'` หรือไม่ ถ้าใช่ให้ส่ง `'O'` ถ้าไม่ใช่ส่ง `'X'` ใช้สำหรับการสลับตาเดินทั้งในเกมจริงและตอนสร้างต้นไม้จำลอง

---

### `place_symbol(board, position, player)`

```python
def place_symbol(board, position, player):
    return board[:position] + player + board[position + 1:]
```

* **ใช้ทำอะไร:** วางหมากของผู้เล่นลงบนตำแหน่งที่ระบุ และสร้างกระดานสถานะใหม่ออกมา
* **ข้อมูลที่รับเข้า (Input):**
  * `board` (str): สตริงสถานะกระดานเดิม ความยาว 9 ตัวอักษร
  * `position` (int): ตำแหน่งช่องที่ต้องการวาง (ดัชนี 0 ถึง 8)
  * `player` (str): สัญลักษณ์ที่จะวาง (`'X'` หรือ `'O'`)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * `str`: สตริงกระดานใหม่ขนาด 9 ตัวอักษรที่มีสัญลักษณ์ถูกแทนที่เรียบร้อยแล้ว
* **ทำงานยังไง:**
  1. `board[:position]`: ตัดสตริงท่อนหน้าก่อนถึงตำแหน่งที่จะลง
  2. `+ player`: นำสัญลักษณ์ใหม่มาต่อตรงกลาง
  3. `+ board[position + 1:]`: นำสตริงท่อนหลังตั้งแต่ถัดจากตำแหน่งนั้นมาต่อท้าย
  *(เนื่องจากสตริงในภาษา Python แก้ไขค่าในตำแหน่งเดิมโดยตรงไม่ได้ จึงต้องใช้วิธีตัดต่อแล้วสร้างสตริงใหม่ส่งกลับไป)*

---

### `check_winner(board)`

```python
def check_winner(board):
    for a, b, c in OXBoard.WINNING_COMBOS:
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None
```

* **ใช้ทำอะไร:** ตรวจสอบสถานะกระดานว่ามีฝ่ายใดชนะ เสมอกัน หรือเกมยังไม่จบ
* **ข้อมูลที่รับเข้า (Input):**
  * `board` (str): สตริงสถานะกระดาน 9 ตัวอักษร
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * คืนค่า `'X'` หรือ `'O'` หากมีผู้ชนะครบ 3 ช่อง
  * คืนค่า `'Draw'` หากไม่มีช่องว่างเหลือแล้วและไม่มีใครชนะ
  * คืนค่า `None` หากเกมยังดำเนินอยู่ (ยังมีช่องว่างและยังไม่มีใครชนะ)
* **ทำงานยังไง:**
  1. วนลูปตรวจสอบตำแหน่งดัชนี 3 ช่อง `(a, b, c)` ตามรูปแบบเส้นชนะทั้ง 8 เส้นใน `WINNING_COMBOS` (แนวนอน 3 เส้น, แนวตั้ง 3 เส้น, แนวทแยง 2 เส้น)
  2. ถ้าช่อง `a` ไม่ใช่ช่องว่าง และทั้ง 3 ช่องเป็นตัวอักษรเดียวกัน (`board[a] == board[b] == board[c]`) ให้คืนค่าตัวอักษรของผู้ชนะทันที
  3. ถ้าตรวจครบ 8 เส้นแล้วไม่มีผู้ชนะ แต่ไม่มีช่องว่างเหลือบนกระดาน (`' ' not in board`) ให้คืนค่า `'Draw'`
  4. หากไม่ตรงเงื่อนไขข้างต้นทั้งหมด ให้คืนค่า `None`

---

## 2. ฟังก์ชันในคลาส `GameNode` (โครงสร้างโหนดสถานะเกม)

---

### `__init__(self, board, player_turn, move=None)`

```python
def __init__(self, board, player_turn, move=None):
    self.board = board
    self.player_turn = player_turn
    self.move = move
    self.children = []
    self.winner = OXBoard.check_winner(board)
    self.minimax_val = None
    self.steps_to_end = 0
```

* **ใช้ทำอะไร:** ตัวสร้าง (Constructor) สำหรับสร้างอ็อบเจกต์โหนด 1 โหนดในต้นไม้ค้นหา เพื่อเก็บข้อมูลสถานะของกระดานในขณะนั้น
* **ข้อมูลที่รับเข้า (Input):**
  * `board` (str): สตริงสถานะกระดาน 9 ตัวอักษร
  * `player_turn` (str): สัญลักษณ์ผู้เล่นที่มีสิทธิ์เดินในตานี้ (`'X'` หรือ `'O'`)
  * `move` (int, default=None): ตำแหน่งช่อง (0–8) ที่เพิ่งเดินมาจนเกิดเป็นกระดานนี้ (ถ้าเป็นโหนดรากแรกสุดจะเป็น `None`)
* **ตัวแปรภายในที่ถูกกำหนด (Attributes):**
  * `self.children`: ลิสต์สำหรับเก็บโหนดลูกที่เป็นไปได้ทั้งหมดในตาถัดไป
  * `self.winner`: บันทึกผลแพ้ชนะทันทีโดยเรียก `OXBoard.check_winner(board)`
  * `self.minimax_val`: คะแนนประเมินผลลัพธ์เกม (บอทชนะ = +1, คนชนะ = -1, เสมอ = 0) โดยเริ่มต้นเป็น `None` รอการคำนวณ
  * `self.steps_to_end`: จำนวนก้าวเดินที่สั้นที่สุดที่จะนำไปสู่จุดจบเกม

---

## 3. ฟังก์ชันตัวช่วยนอกคลาส (Helper Functions)

---

### `branch_sort_key(b, player)`

```python
def branch_sort_key(b, player):
    win_val = 1 if player == 'O' else -1
    loss_val = -1 if player == 'O' else 1
    if b['minimax_val'] == win_val:
        return (1, -b['steps'])
    if b['minimax_val'] == loss_val:
        return (-1, b['steps'])
    return (0, 0)
```

* **ใช้ทำอะไร:** กำหนดเกณฑ์ตัดสินใจเพื่อจัดอันดับกิ่งทางเลือก (Branches) จากดีที่สุดไปแย่ที่สุด โดยปรับเป้าหมายคะแนนตามผู้เล่นตานั้น
* **ข้อมูลที่รับเข้า (Input):**
  * `b` (dict): ดิกชันนารีข้อมูลของกิ่ง มีคีย์สำคัญคือ `'minimax_val'` และ `'steps'`
  * `player` (str): ผู้เล่นที่กำลังเดิน (`'X'` หรือ `'O'`)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * `tuple`: คู่ลำดับลำดับความสำคัญ เช่น `(1, -steps)`, `(0, 0)`, หรือ `(-1, steps)`
* **ทำงานยังไง:**
  1. กำหนดค่าคะแนนเป้าหมาย:
     * หากเป็นบอท (`'O'`): ชนะต้องการ `+1` (`win_val = 1`), แพ้คือ `-1`
     * หากเป็นคน (`'X'`): ชนะต้องการ `-1` (`win_val = -1`), แพ้คือ `+1` *(ยึดสเกลมาตรฐาน: บอทชนะ = +1, คนชนะ = -1, เสมอ = 0)*
  2. เปรียบเทียบผลลัพธ์:
     * **กิ่งที่ชนะ (`minimax_val == win_val`):** ส่งคืน `(1, -b['steps'])` ค่าแรกคือ 1 ได้ความสำคัญสูงสุด ค่าที่สองติดลบจำนวนก้าวเพื่อให้ตาที่ชนะเร็วที่สุด (ก้าวน้อยกว่า) ถูกจัดอยู่อันดับแรก
     * **กิ่งที่แพ้ (`minimax_val == loss_val`):** ส่งคืน `(-1, b['steps'])` ค่าแรกคือ -1 ได้ความสำคัญต่ำสุด ค่าที่สองเป็นบวกจำนวนก้าวเพื่อเลือกตาที่ยื้อเกมได้นานที่สุด
     * **กิ่งที่เสมอ (`minimax_val == 0`):** ส่งคืน `(0, 0)` ให้อยู่ระดับปานกลาง

---

### `format_row(board, start_index)`

```python
def format_row(board, start_index):
    cells = [char if char != ' ' else '.' for char in board[start_index:start_index + 3]]
    return " | ".join(cells)
```

* **ใช้ทำอะไร:** แปลงตัวอักษร 3 ช่องในแถวของกระดานให้เป็นข้อความที่อ่านง่ายสำหรับแสดงผลใน Terminal
* **ข้อมูลที่รับเข้า (Input):**
  * `board` (str): สตริงกระดาน 9 ตัวอักษร
  * `start_index` (int): ตำแหน่งดัชนีเริ่มต้นของแถวนั้น (0 สำหรับแถวแรก, 3 สำหรับแถวกลาง, 6 สำหรับแถวล่าง)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * `str`: ข้อความแถวกระดาน เช่น `'X | . | O'`
* **ทำงานยังไง:**
  1. ตัดตัวอักษร 3 ตัวจากดัชนี `start_index` ถึง `start_index + 3`
  2. หากช่องใดเป็นช่องว่าง `' '` จะเปลี่ยนเป็นจุด `.` เพื่อให้มองเห็นตำแหน่งช่องชัดเจน
  3. เชื่อมตัวอักษรทั้งสามด้วยเครื่องหมายคั่น `" | "`

---

### `get_debug_text(board, player, turn, branches, selected_move)`

```python
def get_debug_text(board, player, turn, branches, selected_move):
    ...
```

* **ใช้ทำอะไร:** จัดรูปแบบข้อมูลการวิเคราะห์ต้นไม้เกมของตานั้นทั้งหมด เป็นข้อความรายงานสรุปสวยงามเพื่อพิมพ์ลง Terminal
* **ข้อมูลที่รับเข้า (Input):**
  * `board` (str): สตริงกระดานปัจจุบัน
  * `player` (str): ผู้เล่นที่กำลังเดิน (`'X'` หรือ `'O'`)
  * `turn` (int): ลำดับเทิร์นปัจจุบัน
  * `branches` (list): ลิสต์ของกิ่งทางเลือกที่เป็นไปได้ทั้งหมดที่จัดเรียงลำดับแล้ว
  * `selected_move` (int): ช่องที่ถูกเลือกเดินจริงในตานั้น
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * `str`: ข้อความรายงานสรุป Debug ทั้งหมด
* **ทำงานยังไง:**
  1. สร้างส่วนหัวระบุเทิร์นและผู้เล่น เช่น `[DEBUG] TURN 1 - ผู้เล่น (X)` พร้อมวาดรูปกระดานปัจจุบัน 3 แถวด้วย `format_row`
  2. วนลูปผ่านทุกกิ่งใน `branches`:
     * แสดงพิกัดช่อง `(row, col)` และหมายเลข Index
     * แสดงคะแนน `Minimax Value` (`+1`, `0`, หรือ `-1`)
     * แสดงภาพจำลองกระดานล่วงหน้า (Preview) หลังเดินกิ่งนั้น
     * หากกิ่งนั้นเป็นตาที่เลือกเดินจริง จะใส่ป้ายกำกับ `★ [SELECTED]`
     * หากกิ่งนั้นชนะทันที จะใส่ป้ายกำกับพิเศษ เช่น `[DIRECT X!]` หรือ `[DIRECT O!]`
  3. แสดงบรรทัดสรุปปิดท้ายว่าผู้เล่นหรือบอทตัดสินใจเลือกเดินช่องใด

---

## 4. ฟังก์ชันในคลาส `OXBFSTree` (สมองกล AI: BFS & Minimax)

---

### `__init__(self)`

```python
def __init__(self):
    self.state_map = {}
    self._build_tree()
```

* **ใช้ทำอะไร:** กำหนดค่าเริ่มต้นของระบบ AI สร้างตารางจำสถานะ และสั่งสร้างต้นไม้เกมล่วงหน้า
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ทำงานยังไง:**
  1. ประกาศตัวแปร `self.state_map = {}` เป็นพจนานุกรม (Dictionary) ใช้ค้นหาโหนดสถานะแบบ $O(1)$
  2. เรียกใช้งานเมธอด `self._build_tree()` ทันทีเพื่อสร้างต้นไม้เกมทั้งหมดเตรียมไว้ในหน่วยความจำ

---

### `_build_tree(self)`

```python
def _build_tree(self):
    ...
```

* **ใช้ทำอะไร:** สร้างโครงสร้างต้นไม้เกมที่เป็นไปได้ทั้งหมดขนาด 549,946 โหนดด้วย **BFS** และคำนวณคะแนน **Minimax** ย้อนหลังจากล่างขึ้นบน
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ผลลัพธ์ที่ส่งกลับ (Output):** ไม่มี (บันทึกข้อมูลลงในโหนดและ `self.state_map`)
* **ทำงานยังไง (แบ่งเป็น 2 ขั้นตอนหลัก):**
  1. **ขั้นตอนที่ 1: แตกกิ่งค้นหาทุกสถานะด้วย BFS (Top-Down)**
     * เริ่มต้นจากกระดานว่างและให้ X เดินก่อน นำโหนดรากใส่ในคิว `queue = deque([root])`
     * วนลูปดึงโหนดหน้าสุดออกมา (`queue.popleft()`) ถ้าโหนดนั้นจบเกมแล้ว (`node.winner`) จะไม่แตกกิ่งต่อ
     * หากยังไม่จบ จะหาช่องว่างที่เหลือทั้งหมดบนกระดาน จำลองการวางหมาก สร้างโหนดลูก (`GameNode`) นำไปเก็บใน `node.children`, ใส่ลงในคิวเพื่อขยายต่อ, และบันทึกลงใน `state_map`
  2. **ขั้นตอนที่ 2: คำนวณคะแนน Minimax ย้อนกลับ (Bottom-Up)**
     * วนลูปย้อนหลังจากโหนดปลายทางขึ้นมาสู่โหนดรากด้วย `reversed(all_nodes)`
     * **ถ้าเป็นโหนดจบเกม:**
       * บอท (O) ชนะ $\rightarrow$ กำหนด `minimax_val = 1`
       * คน (X) ชนะ $\rightarrow$ กำหนด `minimax_val = -1`
       * เสมอ $\rightarrow$ กำหนด `minimax_val = 0`
     * **ถ้าเป็นโหนดระหว่างเล่น:**
       * ตรวจสอบคะแนนจากโหนดลูกทั้งหมด
       * ในตาของบอท (O): เลือกคะแนนสูงสุด (`max`) เพราะบอทต้องการชนะ (+1)
       * ในตาของคน (X): เลือกคะแนนต่ำสุด (`min`) เพราะคนต้องการให้บอทแพ้ (-1)
       * บันทึกจำนวนก้าว `steps_to_end` ไปยังจุดจบเกมที่สั้นที่สุด

---

### `evaluate_branches(self, current_board, player)`

```python
def evaluate_branches(self, current_board, player):
    ...
```

* **ใช้ทำอะไร:** ค้นหากิ่งทางเลือกทั้งหมดจากกระดานปัจจุบัน ประเมินผล และคัดเลือกตาเดินที่ดีที่สุดสำหรับผู้เล่นคนนั้น
* **ข้อมูลที่รับเข้า (Input):**
  * `current_board` (str): สตริงสถานะกระดานปัจจุบัน 9 ตัวอักษร
  * `player` (str): ผู้เล่นที่กำลังเดิน (`'X'` หรือ `'O'`)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * คืนค่า Tuple `(branches, best_move)`:
    * `branches` (list): รายการกิ่งทางเลือกทั้งหมดที่จัดเรียงจากดีที่สุดไปแย่ที่สุด
    * `best_move` (int): ตำแหน่งช่องที่ดีที่สุด (ดัชนี 0–8) หรือ `None` หากไม่มีกิ่งเดินต่อ
* **ทำงานยังไง:**
  1. ค้นหาโหนดจากตารางสถานะ `self.state_map.get((current_board, player))` ด้วยเวลา $O(1)$
  2. รวบรวมข้อมูลโหนดลูกทั้งหมดลงในลิสต์ `branches` (ประกอบด้วยช่องที่เดิน, กระดานถัดไป, ค่า Minimax, จำนวนก้าว, และผลชนะทันที)
  3. จัดเรียงอันดับกิ่งด้วย `branches.sort(key=lambda b: branch_sort_key(b, player), reverse=True)`
  4. เลือกตาเดินอันดับ 1 เป็น `best_move = branches[0]['move']` แล้วส่งค่ากลับ

---

## 5. ฟังก์ชันในคลาส `OXGameGUI` (ระบบหน้าต่างเกมและการเล่น)

---

### `__init__(self, root)`

```python
def __init__(self, root):
    self.root = root
    ...
```

* **ใช้ทำอะไร:** ตัวสร้าง (Constructor) สำหรับเริ่มต้นหน้าต่างโปรแกรม กำหนดขนาด ตัวแปรสถิติ โหลดสมองกล AI และสร้างวิดเจ็ต
* **ข้อมูลที่รับเข้า (Input):**
  * `root` (tk.Tk): อ็อบเจกต์หน้าต่างหลักของ Tkinter
* **ทำงานยังไง:**
  1. ตั้งชื่อไตเติลหน้าต่าง กำหนดขนาดเริ่มต้นเป็น `450x540` พิกเซล และตั้งสีพื้นหลัง
  2. กำหนดตัวแปรคะแนน `self.scores = {'X': 0, 'O': 0, 'Draw': 0}` และตัวนับงานหน่วงเวลา `self.ai_job = None`
  3. โหลดสมองกล AI ด้วย `self.tree = OXBFSTree()`
  4. เรียกเมธอด `self._create_widgets()` เพื่อวาดส่วนประกอบบนหน้าจอ
  5. เรียกเมธอด `self.start_new_game()` เพื่อเริ่มต้นกระดานแรก

---

### `_create_widgets(self)`

```python
def _create_widgets(self):
    ...
```

* **ใช้ทำอะไร:** สร้างและจัดวางองค์ประกอบกราฟิกทั้งหมด (Header, ป้ายคะแนน, ปุ่มกระดาน 9 ช่อง) ลงบนหน้าต่าง
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ทำงานยังไง:**
  1. **สร้างแถบ Header ด้านบน:**
     * จัดคอลัมน์ด้วย `columnconfigure` (0 ถึง 6)
     * วางปุ่ม Reset ทางซ้ายสุด
     * วางกล่องแสดงผู้เล่น X สีแดง
     * วางกล่องกลางแสดงคำว่า `SCORE`, จำนวนครั้งที่เสมอ และป้ายข้อความสถานะเกม
     * วางกล่องแสดงบอท O สีน้ำเงิน
     * ใส่เส้นคั่นแนวตั้งระหว่างแต่ละส่วน
  2. **สร้างตารางกระดาน 3x3 ด้านล่าง:**
     * สร้างเฟรมหลัก `b_frame` แบบตาราง
     * วนลูป 9 รอบสร้างปุ่ม `tk.Button` ขนาดใหญ่ ผูกฟังก์ชันคลิกด้วยคำสั่ง `command=lambda idx=i: self._on_cell_clicked(idx)` แล้วเก็บไว้ในลิสต์ `self.buttons`

---

### `start_new_game(self)`

```python
def start_new_game(self):
    ...
```

* **ใช้ทำอะไร:** รีเซ็ตสถานะของเกมเพื่อเริ่มเล่นกระดานใหม่
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ทำงานยังไง:**
  1. ตรวจสอบและยกเลิกคิวหน่วงเวลาของบอทที่อาจค้างอยู่ด้วย `root.after_cancel`
  2. รีเซ็ตกระดานเป็นค่าว่าง `self.board = EMPTY_BOARD`
  3. กำหนดให้ตาเดินแรกเป็น `'X'`, ตั้งรอบเป็นเทิร์นที่ 1, และตั้ง `self.game_over = False`
  4. ล้างข้อความบนปุ่มทั้ง 9 ช่องให้เป็นค่าว่าง และปรับสีพื้นหลังกลับเป็นสีขาว
  5. อัปเดตป้ายสถานะเป็น `"ตาเดิน: X"` และพิมพ์ข้อความแจ้งเตือนลงใน Terminal

---

### `_update_status(self, text, is_over=False)`

```python
def _update_status(self, text, is_over=False):
    fg = "#B45309" if is_over else "#0F172A"
    self.status_lbl.config(text=text, fg=fg)
```

* **ใช้ทำอะไร:** อัปเดตข้อความและสีตัวอักษรของป้ายสถานะเกมบนแถบ Header
* **ข้อมูลที่รับเข้า (Input):**
  * `text` (str): ข้อความที่ต้องการให้แสดง (เช่น `"ตาเดิน: X"` หรือ `"บอทกำลังคิด..."`)
  * `is_over` (bool, default=False): สถานะว่าเกมจบแล้วหรือไม่
* **ทำงานยังไง:**
  * หากจบเกม (`is_over=True`) จะใช้สีส้มน้ำตาล (`#B45309`) เพื่อให้ผู้เล่นสังเกตเห็นชัดเจน หากยังเล่นอยู่จะใช้สีเทาเข้ม (`#0F172A`) จากนั้นอัปเดตข้อความลงบน `self.status_lbl`

---

### `_update_scoreboard(self)`

```python
def _update_scoreboard(self):
    self.lbl_x.config(text=f"คุณ: {self.scores['X']}")
    self.lbl_o.config(text=f"บอท: {self.scores['O']}")
    self.lbl_draw.config(text=f"เสมอ: {self.scores['Draw']}")
```

* **ใช้ทำอะไร:** อัปเดตตัวเลขสถิติคะแนนการแข่งขันบนหน้าจอให้ตรงกับข้อมูลล่าสุด
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ทำงานยังไง:**
  * นำค่าสถิติจำนวนครั้งที่ชนะของ X, ชนะของ O, และผลเสมอ จากพจนานุกรม `self.scores` ไปอัปเดตลงบน Label แต่ละจุดบนแถบ Header

---

### `_check_game_end(self)`

```python
def _check_game_end(self):
    ...
```

* **ใช้ทำอะไร:** ตรวจสอบว่ากระดานปัจจุบันจบเกมหรือยัง ปรับปรุงคะแนน ไฮไลท์ช่องที่ชนะ และสรุปผล
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ผลลัพธ์ที่ส่งกลับ (Output):**
  * `bool`: คืนค่า `True` หากเกมจบลงแล้ว (มีคนชนะหรือเสมอ) และคืนค่า `False` หากเกมยังไม่จบ
* **ทำงานยังไง:**
  1. เรียก `OXBoard.check_winner(self.board)` หากได้ผลลัพธ์เป็น `None` ให้ส่ง `False` กลับไปเพื่อเล่นต่อ
  2. หากเกมจบ: ตั้งค่า `self.game_over = True`, บวกคะแนนให้ผู้ชนะใน `self.scores`, และเรียก `_update_scoreboard()`
  3. หากมีผู้ชนะ: วนลูปหาแถว 3 ช่องที่ชนะ แล้วเปลี่ยนสีพื้นหลังของปุ่มทั้งสามเป็นสีเขียวอ่อน (`#DCFCE7`)
  4. อัปเดตข้อความบนป้ายสถานะด้วย `_update_status` และพิมพ์สรุปผลการแข่งขันลง Terminal

---

### `_on_cell_clicked(self, idx)`

```python
def _on_cell_clicked(self, idx):
    if not self.game_over and self.board[idx] == ' ' and self.current_player == 'X':
        branches, _ = self.tree.evaluate_branches(self.board, 'X')
        if branches:
            debug_info = get_debug_text(self.board, 'X', self.turn_count, branches, idx)
            print(debug_info + "\n")
        self._execute_move(idx)
```

* **ใช้ทำอะไร:** ตอบสนองต่อการคลิกช่องกระดานของผู้เล่น ตรวจสอบความถูกต้อง วิเคราะห์กิ่ง และพิมพ์ Debug ของฝั่งผู้เล่น
* **ข้อมูลที่รับเข้า (Input):**
  * `idx` (int): ตำแหน่งดัชนีของช่องที่ถูกคลิก (0 ถึง 8)
* **ทำงานยังไง:**
  1. **Guard Clauses ตรวจสอบ 3 เงื่อนไข:** เกมต้องยังไม่จบ (`not self.game_over`), ช่องที่คลิกต้องยังว่าง (`self.board[idx] == ' '`), และต้องเป็นตาของผู้เล่นมนุษย์ (`self.current_player == 'X'`)
  2. เรียก `self.tree.evaluate_branches(self.board, 'X')` เพื่อประเมินกิ่งทางเลือกทั้งหมดของกระดานในมุมมองของผู้เล่น
  3. นำข้อมูลไปสร้างข้อความ Debug ด้วย `get_debug_text()` โดยช่องที่คลิกจะได้รับแท็ก `★ [SELECTED]` แล้วพิมพ์ออกทาง Terminal
  4. สั่งดำเนินการวางหมากจริงด้วย `self._execute_move(idx)`

---

### `_execute_move(self, move_idx)`

```python
def _execute_move(self, move_idx):
    ...
```

* **ใช้ทำอะไร:** ดำเนินการวางหมากบนกระดาน เปลี่ยนสัญลักษณ์บนปุ่ม ตรวจสอบผลแพ้ชนะ และสลับเทิร์นไปยังผู้เล่นคนถัดไป
* **ข้อมูลที่รับเข้า (Input):**
  * `move_idx` (int): ตำแหน่งช่องที่จะวางหมาก (0 ถึง 8)
* **ทำงานยังไง:**
  1. อัปเดตสตริงกระดานด้วย `OXBoard.place_symbol`
  2. แสดงตัวอักษรบนปุ่ม (X สีแดง, O สีน้ำเงิน)
  3. ตรวจสอบการจบเกมด้วย `_check_game_end()` หากจบเกมให้หยุดการทำงานทันที
  4. สลับผู้เล่นด้วย `OXBoard.get_opponent` และเพิ่มรอบเทิร์นขึ้น 1
  5. หากสลับมาเป็นตาของบอท (O): ขึ้นป้าย `"บอทกำลังคิด..."` แล้วหน่วงเวลา 350 มิลลิวินาทีก่อนเรียกฟังก์ชัน `_ai_turn` ด้วย `self.root.after(350, self._ai_turn)`
  6. หากสลับมาเป็นตาของผู้เล่น (X): แสดงข้อความ `"ตาเดิน: X"`

---

### `_ai_turn(self)`

```python
def _ai_turn(self):
    if not self.game_over and self.current_player == 'O':
        branches, best_move = self.tree.evaluate_branches(self.board, 'O')
        if best_move is not None:
            debug_info = get_debug_text(self.board, 'O', self.turn_count, branches, best_move)
            print(debug_info + "\n")
            self._execute_move(best_move)
```

* **ใช้ทำอะไร:** คำนวณและดำเนินการเดินหมากโดยอัตโนมัติสำหรับบอท AI (O)
* **ข้อมูลที่รับเข้า (Input):** ไม่มี (นอกจาก `self`)
* **ทำงานยังไง:**
  1. ตรวจสอบว่าเกมยังไม่จบและเป็นตาเดินของบอท (`'O'`) จริง
  2. เรียก `self.tree.evaluate_branches(self.board, 'O')` เพื่อดึงกิ่งทางเลือกทั้งหมดและตาเดินที่ดีที่สุด (`best_move`) ของบอท
  3. สร้างข้อความรายงาน Debug ของบอทด้วย `get_debug_text()` (ตาที่เลือกจะติดป้าย `★ [SELECTED]`) แล้วพิมพ์ออกทาง Terminal
  4. เรียก `self._execute_move(best_move)` เพื่อวางหมากของบอทลงบนกระดานจริง
