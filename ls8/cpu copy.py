import sys
Skip to content
Search or jump to…

Pull requests
Issues
Marketplace
Explore


@janecyyu
easpaas
/
Computer-Architecture
forked from LambdaSchool/Computer-Architecture
0
0
1.2k
Code
Pull requests
2
Actions
Projects
Wiki
Security
Insights
Computer-Architecture/ls8/cpu.py /


@easpaas
easpaas mvp met
Latest commit 85ab894 2 hours ago
History
2 contributors


@easpaas@beejjorgensen
211 lines(167 sloc)  5.5 KB

Code navigation is available!
Navigate your code with ease. Click on function and method calls to jump to their definitions or references in the same repository. Learn more


# BINARY values
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000  # 00000rrr
RET = 0b00010001
ADD = 0b10100000  # 00000aaa 00000bbb
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256   # 256 bytes of memory
        self.reg = [0] * 9  # 8 byte register

        self.pc = 0    # program counter
        self.reg[7] = self.ram[0xF4]   # set default f4 in register 7
        self.sp = self.reg[7]  # sp == stackpointer

        self.dispatch_table = {}
        self.dispatch_table[LDI] = self.ldi
        self.dispatch_table[PRN] = self.prn
        self.dispatch_table[MUL] = self.mul
        self.dispatch_table[PUSH] = self.push
        self.dispatch_table[POP] = self.pop
        self.dispatch_table[CALL] = self.call
        self.dispatch_table[RET] = self.ret
        self.dispatch_table[ADD] = self.add

        # Sprint challenge: add default flag, CMP, JMP, JEQ and JNE
        self.fl = 0b00000000  # default flag

        self.dispatch_table[CMP] = self.cmp
        self.dispatch_table[JMP] = self.jmp
        self.dispatch_table[JEQ] = self.jeq
        self.dispatch_table[JNE] = self.jne

    def ram_read(self, pc):
        print(self.ram[pc])

    def ram_write(self, value):
        self.ram.append(value)

    def ldi(self):
        register = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]

        self.pc += 3
        self.reg[register] = value

    def prn(self):
        register = self.ram[self.pc + 1]
        print(self.reg[register])
        self.pc += 2

    def mul(self):
        register1 = self.ram[self.pc + 1]
        register2 = self.ram[self.pc + 2]
        self.alu("MUL", register1, register2)
        self.pc += 3

    def add(self):
        register1 = self.ram[self.pc + 1]
        register2 = self.ram[self.pc + 2]
        self.alu("ADD", register1, register2)
        self.pc += 3

    def push(self):
        self.sp -= 1
        register = self.ram[self.pc + 1]
        self.ram[self.sp] = self.reg[register]
        self.pc += 2

    def pop(self):
        register = self.ram[self.pc + 1]
        self.reg[register] = self.ram[self.sp]
        self.sp += 1
        self.pc += 2

    def call(self):
        self.sp -= 1
        return_address = self.pc + 2
        self.ram[self.sp] = return_address

        register = self.ram[self.pc + 1]
        self.pc = self.reg[register]

    def ret(self):
        self.pc = self.ram[self.sp]
        self.sp += 1

    # *************************************************
    # Sprint Challenge methods
    # *************************************************

    # Jump the address stored in given register
    def jne(self):
        register = self.ram[self.pc + 1]
        if (self.fl & HLT) == 0:
            self.pc = self.reg[register]
        else:
            self.pc += 2

    # Equal flag is set to true, jump to address at given register
    def jeq(self):
        register = self.ram[self.pc + 1]
        if (self.fl & HLT) > 0:
            self.pc = self.reg[register]
        else:
            self.pc += 2

    # cmp instruction handled by alu
    def cmp(self):
        register1 = self.ram[self.pc + 1]
        register2 = self.ram[self.pc + 2]
        self.alu("CMP", register1, register2)
        self.pc += 3

    # Jump to address stored in the given register
    def jmp(self):
        register = self.ram[self.pc + 1]
        self.pc = self.reg[register]

    # **********************************************

    def load(self):
        """Load a program into memory."""

        address = 0
        filename = sys.argv[1]
        program = []

        with open(filename) as f:
            for line in f:
                n = line.split('#')
                n[0] = n[0].strip()

                if n[0] == '':
                    continue
                val = int(n[0], 2)
                program.append(val)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]

        elif op == "CMP":
            register_a = self.reg[reg_a]
            register_b = self.reg[reg_b]

            # 'FL' bits = '00000LGE'
            if register_a == register_b:  # E
                self.fl = 0b00000001
            elif register_a > register_b:  # G
                self.fl = 0b00000010
            elif register_a < register_b:  # L
                self.fl = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

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

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            if self.ram[self.pc] == HLT:
                running = False
            else:
                self.dispatch_table[self.ram[self.pc]]()


© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
