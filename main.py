import pygame
from constants import COUNTER, WIDTH, HEIGHT
from stack import Stack
import time
import sys
#memory (4 KiloBytes of ram)

file_path = sys.argv[1]
ram = bytearray(4096) 
try:
    with open(file_path, "rb") as f:
        binary_file = f.read()
        ram[512:] = binary_file

except FileNotFoundError:
    print("Error: The file was not found.")
except PermissionError:
    print("Error: You do not have permission to access this file.")
except OSError as e:
    print(f"An OS error occurred: {e}")
#PROGRAM COUNTER (All programs start at location 0x200 in memory. Since instructions are 16 bits, instructions take up 16 bits (2 bytes of RAM)
pc = 0x200
#timers
delay_timer = max(max(0, COUNTER), 255) #holder for 8-bit timer
sound_timer = max(max(0, COUNTER), 255)
#index register
current_instruction = None

for i in range(512, len(ram)):
    num = int(ram[i], 2)
    ram[i] = hex(num)

registry = [0]*16
stack_memory = Stack()

ram[0x050:0x09f] = [0xF0, 0x90, 0x90, 0x90, 0xF0, #0
0x20, 0x60, 0x20, 0x20, 0x70, # 1
0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
0x90, 0x90, 0xF0, 0x10, 0x10, # 4
0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
0xF0, 0x10, 0x20, 0x40, 0x40, # 7
0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
0xF0, 0x90, 0xF0, 0x90, 0x90, # A
0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
0xF0, 0x80, 0x80, 0x80, 0xF0, # C
0xE0, 0x90, 0x90, 0x90, 0xE0, # D
0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
0xF0, 0x80, 0xF0, 0x80, 0x80 ] # F


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

while True:
    # 1. Fetch 16-bit opcode (2 bytes)
    current_instruction = ram[pc:pc + 2]
    pc += 2
    
    # 2. Decode & Execute instruction
        #obtain the first part of the hexadecimal number (0x200)
    # first_half_byte = current_instruction[2]
    # second_nibble = current_instruction[3]
    # third_nibble = current_instruction[4]
    # fourth_nibble = current_instruction[5]
    opcode = current_instruction[2:6]

    match opcode:
        case("00E0"):
            screen.fill((0,0,0))

    # 3. Update Timers (60Hz)
    # 4. Update Screen
    # 5. Sleep to maintain 500Hz-1kHz
    time.sleep(1/60)
    pass