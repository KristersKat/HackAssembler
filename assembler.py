import sys

variables = {
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
}

# Decimal values of jump instruction
jump_to_binary = {
    'JGT': 1,
    'JEQ': 2,
    'JGE': 3,
    'JLT': 4,
    'JNE': 5,
    'JLE': 6,
    'JMP': 7,
}

# See C instruction specification for explanation
comp_to_binary = {
    '0':   2688,
    '1':   4032,
    '-1':  3712,
    'D':   768,
    'A':   3072,
    '!D':  823,
    '!A':  3136,
    '-D':  960,
    '-A':  3136,
    'D+1': 1984,
    'A+1': 3520,
    'D-1': 896,
    'A-1': 3200,
    'D+A': 128,
    'D-A': 1216,
    'A-D': 448,
    'D&A': 0,
    'D|A': 1344,
}

if len(sys.argv) != 2:
    sys.exit('Invalid argument count')

file_name = sys.argv[1]
if file_name[-4:] != '.asm':
    sys.exit('Invalid file type')

symbolic_instructions = []

try:
    with open(file_name) as file:
        lines = file.readlines()
        for line in lines:
            instruction = line.strip().split('//')[0]
            if instruction != "":
                symbolic_instructions.append(instruction)

except FileNotFoundError:
    sys.exit('File not found')

latest_var_value = 15
var_num = 0
instructions = []
cleaned_symbolic_instructions = []

# L instructions
for idx, symbolic_instruction in enumerate(symbolic_instructions):
    if symbolic_instruction[0] == '(' and symbolic_instruction[-1] == ')':
        variables[symbolic_instruction[1:-1]] = idx - var_num
        var_num += 1
    else:
        cleaned_symbolic_instructions.append(symbolic_instruction)

# Second loop after variables have been set
for instruction in cleaned_symbolic_instructions:
    # A instructions
    if instruction[0] == '@':
        # If the value after @ is a number
        if instruction[1:].isnumeric():
            instructions.append(f'0{int(instruction[1:]):015b}')
        else:
            # If the variable already exists
            try:
                instructions.append(f'0{variables[instruction[1:]]:015b}')
            # New variable is declared
            # Could add some limit to not override SCREEN and KBD
            except KeyError:
                latest_var_value += 1
                variables[instruction[1:]] = latest_var_value
                instructions.append(f'0{latest_var_value:015b}')

    # C instructions
    else:
        binary_instruction = 57344  # Sets instruction to 1110 0000 0000 0000
        # Handles the jump part
        if ';' in instruction:
            dest_comp, jump = instruction.split(';')
            binary_instruction += jump_to_binary[jump]
        else:
            dest_comp = instruction

        # Handles dest part
        if '=' in dest_comp:
            dest, comp = dest_comp.split('=')
            if 'M' in dest:
                binary_instruction += 8   # 00 1000
            if 'D' in dest:
                binary_instruction += 16  # 01 0000
            if 'A' in dest:
                binary_instruction += 32  # 10 0000
        else:
            comp = dest_comp

        # Handles comp part
        if 'M' in comp:
            binary_instruction += 4096  # Adds a set to 1 (1 0000 0000 0000)
            comp = comp.replace('M', 'A')
        binary_instruction += comp_to_binary[comp]

        # Appends C instruction
        instructions.append(f'{binary_instruction:015b}')

with open(file_name[:-4] + '.hack', 'w') as output:
    for line in instructions:
        output.write(f'{line}\n')
