"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        # Sprint
        self.fl = 0b00000000  # default flag
        self.branchtable[AND] = self.and_a_b
        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne
        self.branchtable[CMP] = self.cmp

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.strip()
                        line = line.split('#', 1)[0]
                        line = int(line, 2)
                        # print(line)
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

    # *************************************************
    # Sprint Challenge
    # *************************************************

    def jmp(self):
        register = self.ram[self.pc + 1]
        self.pc = self.reg[register]

    def jeq(self):
        if self.fl > 0:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        if self.fl == 0:
            self.jmp()
        else:
            self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            register_a = self.reg[reg_a]
            register_b = self.reg[reg_b]
            if register_a == register_b:
                self.fl = 0b00000001
            elif register_a > register_b:
                self.fl = 0b00000001
            elif register_a < register_b:
                self.fl = 0b00000001

        # stretch
        elif op == "AND":
            register_a = self.reg[reg_a]
            register_b = self.reg[reg_b]
            if register_a and register_b:
                # store the result in registerA
                register_a = register_a and register_b

        elif op == "OR":
            register_a = self.reg[reg_a]
            register_b = self.reg[reg_b]
            if register_a or register_b:
                # store the result in registerA
                register_a = register_a or register_b

        else:
            raise Exception("Unsupported ALU operation")

    def cmp(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def and_a_b(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("AND", operand_a, operand_b)
        self.pc += 3

    def or_a_b(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("OR", operand_a, operand_b)
        self.pc += 3
    # **********************************************

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def call(self):
        # get addredd of the next instruction
        return_addr = self.pc + 2

        # push that on the stack
        self.reg[SP] -= 1
        addr_to_push_to = self.reg[SP]
        self.ram[addr_to_push_to] = return_addr

        # set the pc to the subroutine address
        reg_num = self.ram[self.pc + 1]
        sub_addr = self.reg[reg_num]

        self.pc = sub_addr

    def ret(self):
        # get return address from the top of the stack
        address_pop_from = self.reg[SP]
        return_addr = self.ram[address_pop_from]
        self.reg[SP] += 1

        # set the PC to the return address
        self.pc = return_addr

    # sent to stack
    def push(self):
        # decrement stack pointer
        self.reg[SP] -= 1

        # get register value
        reg_num = self.ram_read(self.pc + 1)
        value = self.reg[reg_num]

        # Store in memory
        push_to = self.reg[SP]
        self.ram[push_to] = value

        self.pc += 2

    # sent from stack
    def pop(self):
        # Get value from RAM
        address_pop_from = self.reg[SP]
        value = self.ram[address_pop_from]

        # Store in the given register
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value

        # Increment SP
        self.reg[SP] += 1

        self.pc += 2

    def mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def hlt(self):
        self.running = False

    def ldi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])
        self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.pc
            inst = self.ram[ir]
            self.branchtable[inst]()
