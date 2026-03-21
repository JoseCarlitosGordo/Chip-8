class Stack():
    def __init__(self):
        self.list = []
    
    def pop(self):
        content = self.list.pop()
        return content
    
    def push(self, content):
        self.list.append(content)
    def top(self):
        return self.list[-1]

rom = bytes([
    0x60, 0x00,  # 6000 → V0 = 0
    0x61, 0x00,  # 6100 → V1 = 0

    0x70, 0x08,  # 7008 → V0 += 8
    0x71, 0x04,  # 7104 → V1 += 4

    0x12, 0x10,  # 1210 → Jump to 0x210 (skip next instruction)

    0x60, 0xFF,  # 60FF → (SHOULD BE SKIPPED if jump works)

    0xA2, 0x20,  # A220 → I = 0x220
    0xD0, 0x15,  # D015 → Draw sprite at (V0, V1), height 5

    0x12, 0x16,  # 1216 → Infinite loop (stay on screen)

    # Padding to reach 0x220
] + [0x00] * (0x220 - 0x210) + [

    # Sprite data at 0x220 (simple square)
    0xF0,  # ####
    0x90,  # #  #
    0x90,  # #  #
    0x90,  # #  #
    0xF0   # ####
])

with open("test.ch8", "wb") as f:
    f.write(rom)