import pygame
from constants import COUNTER, WIDTH, HEIGHT
from stack import Stack
import time
import sys
#memory (4 KiloBytes of ram)

file_path = sys.argv[1]
shift_vx_in_place = int(sys.argv[2])
print(sys.argv)
ram = bytearray(4096) 
try:
    with open(file_path, "rb") as f:
        binary_file = f.read()
        for i in range(len(binary_file)):
            ram[0x200+i] = int(binary_file[i])

except FileNotFoundError:
    print("Error: The file was not found.")
except PermissionError:
    print("Error: You do not have permission to access this file.")
except OSError as e:
    print(f"An OS error occurred: {e}")
except Exception as e:
    print("Error! " + e)

#PROGRAM COUNTER (All programs start at location 0x200 in memory. Since instructions are 16 bits, instructions take up 16 bits (2 bytes of RAM)
pc = 0x200 + 1
print(f"{ram[pc]:02x}")
#timers
delay_timer = min(max(0, COUNTER), 255) #holder for 8-bit timer
sound_timer = min(max(0, COUNTER), 255)
#index register
I = 0
current_instruction = None

# for i in range(512, len(ram)):
#     ram[i] = hex(ram[i])

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
    current_instruction = f"{ram[pc]:02x}{ram[pc+1]:02x}"
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
                case"0E0":

                    screen.fill((0,0,0))
                case"0EE":
                    pc = stack_memory.pop()
    
        case"1":
            pc = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16) - 1
            print(f"jumped to {hex(pc)}")
        
        case "2":
            #store the last known position of program in stack_memory to be popped later before jumping
            stack_memory.push(pc)
            pc = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16) - 1
        case "3":
            VX = int("0x"+second_nibble, 16)
            NN = third_nibble + fourth_nibble
            if registry[VX]== NN:
                pc += 2
        case "4":
            VX = int("0x"+second_nibble, 16)
            NN = third_nibble + fourth_nibble
            if registry[VX] != NN:
                pc += 2
        case "5":
            VX = int("0x"+second_nibble, 16)
            VY = int("0x"+third_nibble, 16)
            if registry[VX] == registry[VY]:
                pc += 2

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
                    registry[VX] += registry[VY]
                    #if num goes over 8-bit limit, set flag register to 1/True
                    if registry[VX] > 255:
                        registry[15] = 1
                    else:
                        registry[15] = 0
                case "5":
                    registry[15] = 1 if registry[VX] > registry[VY] else 0
                    registry[VX] -= registry[VY]
                case "6":
                    if shift_vx_in_place == 0:
                        registry[VX] = registry[VY]
                    
                    shifted_out_val = registry[VX] & 1
                    registry[VX] >>= 1
                    registry[15] = shifted_out_val
                case "E" | "e":
                    if shift_vx_in_place == 0:
                        registry[VX] = registry[VY]
                    
                    shifted_out_val = registry[VX] & 128
                    registry[VX] <<= 1
                    registry[15] = shifted_out_val

                    
                    


                case "7":
                    registry[15] = 1 if registry[VY] > registry[VX] else 0
                    registry[VX] = registry[VY] - registry[VX]
                


        case "9":
            VX = int("0x"+second_nibble, 16)
            VY = int("0x"+third_nibble, 16)
            if registry[VX] != registry[VY]:
                pc += 2

        case "A" | "a":
            I = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            print(f"set I to {int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)} ")
        case "B":
            NNN = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            pc = NNN + registry[0]
        case "D" | "d":
            vx =int("0x"+second_nibble, 16)
            vy = int("0x"+third_nibble, 16)
            initial_x = (registry[vx] % 64)* 10 
            initial_y = (registry[vy] % 32 ) * 10
            registry[15] = 0
           
            
            n = int(fourth_nibble, 16)
            
            #iterate over rows
            for i in range(n):
                if I + i >= len(ram):
                    print("breaking in draw")
                    break
                draw_y = (initial_y + (i * 10)) % 320 
                current_pixel = ram[I+i]
                #iterate over cols
                for k in range(8):
                    draw_x = (initial_x + (k * 10)) % 640
                    #use bitshifting to get the rightmost bit in the byte and check if it is a 1
                    if (current_pixel >> (7 - k)) & 1:
                        if screen.get_at((draw_x, draw_y))[:3]!= (0,0,0):
                            pygame.draw.rect(screen, (0,0,0,255), (draw_x, draw_y, 10, 10))
                            print("clearing pixel")
                            registry[15] = 1
                    
                        else:
                            #screen.set_at((draw_x, draw_y), (255,255,255,255))
                            pygame.draw.rect(screen, (255,255,255,255), (draw_x, draw_y, 10, 10))
                            print("filling pixel")
    pc += 2


            



    # 3. Update Timers (60Hz)
    # 4. Update Screen
    pygame.display.flip()
    # 5. Sleep to maintain 500Hz-1kHz
    time.sleep(1)
