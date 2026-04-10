import random

import pygame
from constants import COUNTER, WIDTH, HEIGHT
from stack import Stack
import time
import sys
from pynput.keyboard import Key, Listener

#memory (4 KiloBytes of ram)

def check_for_collision():
    collision = False
    for dx in range(10):
        for dy in range(10):
            if screen.get_at((draw_x + dx, draw_y + dy))[:3] != (0, 0, 0):
                collision = True
                break
        if collision:
            break
    return collision
pygame_keys_to_keyboard = { pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF}
#stores keyboard 
keyboard_state = {}
prev_keyboard_state = {}

def pressed(py_game_key):
    if py_game_key not in pygame_keys_to_keyboard:
        return
    mapped_key = pygame_keys_to_keyboard[py_game_key]
    keyboard_state[mapped_key] = 1

def notPressed(py_game_key):
    if py_game_key not in pygame_keys_to_keyboard:
        return
    mapped_key = pygame_keys_to_keyboard[py_game_key]
    keyboard_state[mapped_key] = 1



file_path = sys.argv[1]
shift_vx_in_place = int(sys.argv[2])

ram = bytearray(4096) 
try:
    with open(file_path, "rb") as f:
        binary_file = f.read()
        ram[0x1ff: 0x1ff + len(binary_file)] = binary_file
except FileNotFoundError:
    print("Error: The file was not found.")
except PermissionError:
    print("Error: You do not have permission to access this file.")
except OSError as e:
    print(f"An OS error occurred: {e}")
except Exception as e:
    print("Error! " + e)

#PROGRAM COUNTER (All programs start at location 0x200 in memory. Since instructions are 16 bits, instructions take up 16 bits (2 bytes of RAM)
pc = 0x200

#timers
delay_timer = min(max(0, COUNTER), 255) #holder for 8-bit timer
sound_timer = min(max(0, COUNTER), 255)

#index register
I = 0
current_instruction = None

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
    if pc >= len(ram) - 1:
        print("Program reached end of memory.")
        break # or sys.exit()
    current_instruction = f"{ram[pc]:02x}{ram[pc+1]:02x}".lower()
    new_pc = pc + 2
    print("current_instruction:" +current_instruction)
   
  
    # 2. Decode & Execute instruction
        #obtain the first part of the hexadecimal number (0x2000)
    first_half_byte = current_instruction[0]
    second_nibble = current_instruction[1]
    third_nibble = current_instruction[2]
    fourth_nibble = current_instruction[3]
    #opcode = current_instruction[2:6]

    match first_half_byte:
        case"0":
            match second_nibble + third_nibble + fourth_nibble:
                case"0e0":

                    screen.fill((0,0,0))
                case"0ee":
                    new_pc = stack_memory.pop()
    
        case"1":
            new_pc = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16) 
            print(f"jumped to {hex(pc)}")
        
        case "2":
            #store the last known position of program in stack_memory to be popped later before jumping
            stack_memory.push(pc)
            new_pc = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16) 
        case "3":
            VX = int("0x"+second_nibble, 16)
            NN = int("0x"+third_nibble + fourth_nibble, 16)
            if registry[VX]== NN:
                new_pc += 2
        case "4":
            VX = int("0x"+second_nibble, 16)
            NN = int("0x"+third_nibble + fourth_nibble, 16)
            if registry[VX] != NN:
                new_pc += 2
        case "5":
            VX = int("0x"+second_nibble, 16)
            VY = int("0x"+third_nibble, 16)
            if registry[VX] == registry[VY]:
                new_pc += 2

        case "6":
            registry[int("0x"+second_nibble, 16)] = int("0x"+ third_nibble + fourth_nibble, 16)
            print(f"set registry at {int("0x"+second_nibble, 16)} to {registry[int("0x"+second_nibble, 16)]}")
        case "7":
            registry[int("0x"+second_nibble, 16)] = (registry[int("0x"+second_nibble, 16)] + int("0x"+third_nibble + fourth_nibble, 16)) & 0xff
            print(f"Result: {registry[int("0x"+second_nibble, 16)]} ")
        
        case "8":
            VX = int("0x"+second_nibble, 16)
            VY = int("0x"+third_nibble, 16) 
            match fourth_nibble:
                case "0":
                    
                    registry[VX] = registry[VY]
                case "1":
                    registry[VX] = registry[VX] | registry[VY]
                case "2":
                    registry[VX] = registry[VX] & registry[VY]
                case "3":
                    registry[VX] = registry[VX] ^ registry[VY]
                case "4":
                    sum_val = registry[VX] + registry[VY]
                    registry[15] = 1 if sum_val > 255 else 0
                    registry[VX] = sum_val & 0xFF
                case "5":
                    registry[15] = 1 if registry[VX] > registry[VY] else 0
                    registry[VX] = (registry[VX] - registry[VY]) & 0xFF
                case "6":
                    if shift_vx_in_place == 0:
                        registry[VX] = registry[VY]
                    
                    shifted_out_val = registry[VX] & 1
                    registry[VX] >>= 1
                    registry[15] = shifted_out_val
                case "e":
                    if shift_vx_in_place == 0:
                        registry[VX] = registry[VY]
                    
                    shifted_out_val = registry[VX] & 128
                    registry[VX] <<= 1
                    registry[15] = shifted_out_val
                
                case "7":
                    registry[15] = 1 if registry[VY] > registry[VX] else 0
                    registry[VX] = (registry[VY] - registry[VX]) & 0xFF
                
        case "9":
            VX = int("0x"+second_nibble, 16)
            VY = int("0x"+third_nibble, 16)
            if registry[VX] != registry[VY]:
                new_pc += 2

        case "a":
            I = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            print(f"set I to {int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)} ")

        case "b":
            NNN = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            new_pc = NNN + registry[0]
        case "c":
            VX = int("0x"+second_nibble, 16)
            NN = int("0x"+ third_nibble + fourth_nibble, 16)
            registry[VX] = random.randint(0, 255) & NN
        case "d":
            vx_idx = int(second_nibble, 16)
            vy_idx = int(third_nibble, 16)
            initial_x = registry[vx_idx] % 64
            initial_y = registry[vy_idx] % 32
            registry[15] = 0
            n = int(fourth_nibble, 16)
            
            for row in range(n):
                sprite_byte = ram[I + row]
                for col in range(8):
                    sprite_pixel = (sprite_byte >> (7 - col)) & 1
                    if sprite_pixel == 1:
                        # Calculate the actual screen pixel coordinates
                        curr_x = (initial_x + col)
                        curr_y = (initial_y + row)
                        
                        # Stop drawing if we hit the edge of the 64x32 space
                        if curr_x < 64 and curr_y < 32:
                            # Scale coordinates for Pygame (x10)
                            draw_x = curr_x * 10
                            draw_y = curr_y * 10
                            
                            collision = check_for_collision()
                            # Standard XOR logic
                            if collision:
                                registry[15] = 1
                                pygame.draw.rect(screen, (0, 0, 0), (draw_x, draw_y, 10, 10))
                            else:
                                pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, 10, 10))

        #gets the state of keyboard vals by checking for 
        case "e":
            VX = int("0x"+second_nibble, 16)
            #use a mask to only retrieve values from 0x0 to 0xF
            expected_keycode = registry[VX] & 0xF
            match(third_nibble+fourth_nibble):
                #checks keyboard state (1 for pressed, 0 for not pressed)
                case "9e":
                    if expected_keycode in keyboard_state:

                        if keyboard_state[expected_keycode] == 1:
                            new_pc += 2
                case "a1":
                    if expected_keycode not in keyboard_state or keyboard_state[expected_keycode] == 0:
                        new_pc += 2
        case "f":
            VX = int("0x"+second_nibble, 16)
            match(third_nibble+fourth_nibble):
                case "0a":
                        key_pressed = False
                        for i in range(16):
                            if i in prev_keyboard_state and prev_keyboard_state[i] == 1 and keyboard_state[i] == 0:
                                registry[VX] = i
                                key_pressed = True
                                break


                        if not key_pressed:
                            new_pc -= 2

                case "1e":
                    #since I is 16 bits, we mask it with a 16 bit mask 
                    I = (I + registry[VX]) & 0xFFFF
                case "29":
                    
                    #since one font character takes up 5 bytes, we multiply by 5 to get the correct starting point of the char in memory
                    I = 0x50 + ((registry[VX] & 0xF) * 5) 
                case "33":
                    number = registry[VX] & 0xFF
                    divisor = 100
                    current_i = I
                    while divisor >= 1: 
                        number_to_add_to_memory = number // divisor
                        if number_to_add_to_memory != 0:
                            ram[current_i] = number_to_add_to_memory
                        number = number % divisor
                        divisor /= 10




    #updated at a rate of 60 times a second
    if delay_timer > 0: delay_timer -= 1
    if sound_timer > 0: sound_timer -= 1
    pc = new_pc
    for event in pygame.event.get():
        #listens for any changes in keycode
        if event.type == pygame.KEYDOWN:
            pressed(event.key)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:
            notPressed(event.key)

            

    prev_keyboard_state = keyboard_state
    # 3. Update Timers (60Hz)
    # 4. Update Screen
    pygame.display.flip()
    # 5. Sleep to maintain 500Hz-1kHz
    time.sleep(1/60)


