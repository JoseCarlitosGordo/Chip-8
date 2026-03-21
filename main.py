import pygame
from constants import COUNTER, WIDTH, HEIGHT
from stack import Stack
import time
import sys
#memory (4 KiloBytes of ram)

file_path = sys.argv[1]
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
pc = 0x200+1
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
    pc += 2
  
    # 2. Decode & Execute instruction
        #obtain the first part of the hexadecimal number (0x2000)
    first_half_byte = current_instruction[0]
    second_nibble = current_instruction[1]
    third_nibble = current_instruction[2]
    fourth_nibble = current_instruction[3]
    #opcode = current_instruction[2:6]

    match first_half_byte:
        case"0":
            match fourth_nibble:
                case"0":

                    screen.fill((0,0,0))
                case"E":
                    pass
    
        case"1":

            pc = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            print(f"jumped to {str(pc)}")
            break
        case "6":
            registry[int("0x"+second_nibble, 16)] = int("0x"+ third_nibble + fourth_nibble, 16)
            print(f"set registry at {int("0x"+second_nibble, 16)} to {registry[int("0x"+second_nibble, 16)]}")
            #break
        case "7":
            registry[int("0x"+second_nibble, 16)] += int("0x"+third_nibble + fourth_nibble, 16)
            print(f"Result: {registry[int("0x"+second_nibble, 16)]} ")
            break
        case "A":
            I = int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)
            print(f"set I to {int("0x"+ second_nibble + third_nibble + fourth_nibble, 16)} ")
            break
        case "D":
            vx =int("0x"+second_nibble, 16)
            vy = int("0x"+third_nibble, 16)
            initial_x = (registry[vx] % 64)* 10 
            initial_y = (registry[vy] % 32 ) * 10
            registry[15] = 0
           
            
            n = int(fourth_nibble, 16)
            
            for i in range(n):
                if I + i >= len(ram):
                    print("breaking in draw")
                    break
                draw_y = (initial_y + (i * 10)) % 320 
                current_pixel = ram[I+i]
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



            



    # 3. Update Timers (60Hz)
    # 4. Update Screen
    pygame.display.flip()
    # 5. Sleep to maintain 500Hz-1kHz
    time.sleep(1/60)
# while True:
#     # 1. Fetch 16-bit opcode
#     if pc >= len(ram) - 1:
#         print("Program reached end of memory.")
#         break

#     # Use bitwise instead of strings for cleaner decoding
#     opcode = (ram[pc] << 8) | ram[pc+1]
    
#     # We increment PC here, so Jumps need to account for this or use 'continue'
#     pc += 2 
  
#     # Extract nibbles
#     first_nibble  = (opcode & 0xF000) >> 12
#     second_nibble = (opcode & 0x0F00) >> 8
#     third_nibble  = (opcode & 0x00F0) >> 4
#     fourth_nibble = (opcode & 0x000F)
#     nnn           = (opcode & 0x0FFF)
#     nn            = (opcode & 0x00FF)

#     match first_nibble:
#         case 0:
#             if nnn == 0x0E0:
#                 screen.fill((0, 0, 0))
        
#         case 1: # JP addr
#             pc = nnn # Jump to address
#             # We don't want the pc += 2 at the top to skip the first instruction of the jump
#             # so we 'continue' to start the loop over with the new PC immediately
#             continue 

#         case 6: # LD Vx, byte
#             registry[second_nibble] = nn
            
#         case 7: # ADD Vx, byte
#             registry[second_nibble] = (registry[second_nibble] + nn) & 0xFF
            
#         case 0xA: # LD I, addr
#             I = nnn
            
#         case 0xD: # DRW Vx, Vy, nibble
#             vx = registry[second_nibble]
#             vy = registry[third_nibble]
#             n  = fourth_nibble
#             registry[15] = 0
            
#             for row in range(n):
#                 sprite_byte = ram[I + row]
#                 for col in range(8):
#                     if I + row >= len(ram):
#                         print(f"I out of bounds: {I + row}")
#                         break
#                     if (sprite_byte & (0x80 >> col)):
#                         # Scale coordinates by 10 (64 -> 640, 32 -> 320)
#                         # We use % to wrap around the screen (standard CHIP-8 behavior)
#                         draw_x = ((vx + col) % 64) * 10
#                         draw_y = ((vy + row) % 32) * 10
                        
#                         # Draw a 10x10 block for the "pixel"
#                         pixel_rect = pygame.Rect(draw_x, draw_y, 10, 10)
                        
#                         # Simplistic XOR: if pixel is white, make it black (and set VF=1)
#                         # For the IBM logo, it usually starts black, so we just draw white
#                         current_color = screen.get_at((draw_x, draw_y))
#                         if current_color == (255, 255, 255, 255):
#                             pygame.draw.rect(screen, (0, 0, 0), pixel_rect)
#                             registry[15] = 1
#                         else:
#                             pygame.draw.rect(screen, (255, 255, 255), pixel_rect)

#     # 4. Update Screen (Crucial! Without this, the window stays black)
#     pygame.display.flip()

#     # 5. Handle Pygame events (prevents "Not Responding" freeze)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()

#     time.sleep(1/500) # IBM Logo looks better at higher speeds (~500Hz)