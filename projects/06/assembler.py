import sys 
import os 

class AInstruction(object): 
    def __init__(self, instruction, symbols):
        addressstr = instruction[1:]
        try: 
            address = int(addressstr)
        except:
            address = symbols.get(addressstr)
            if address is None:
                raise Exception(f"Don't recognise address {addressstr}")
        
        self.address = address
    
    def get_binary(self):
        address = "{0:b}".format(self.address).zfill(15)
        return f"0{address}"

class CInstruction(object):
    JUMPS = {
        None: "000",
        "JGT": "001", 
        "JEQ": "010", 
        "JGE": "011",
        "JLT": "100", 
        "JNE": "101", 
        "JLE": "110",
        "JMP": "111"
    }
    DESTS = {
        None: "000",
        "M": "001", 
        "D": "010", 
        "MD": "011",
        "A": "100", 
        "AM": "101", 
        "AD": "110",
        "AMD": "111"
    }
    OPERATIONS = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "M": "1110000",
        "!D": "0001101",
        "!A": "0110001",
        "!M": "1110001",
        "-D": "0001111",
        "-A": "0110011",
        "-M": "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "D+M": "1000010",
        "D-A": "0010011",
        "D-M": "1010011",
        "A-D": "0000111",
        "M-D": "1000111",
        "D&A": "0000000",
        "D&M": "1000000",
        "D|A": "0010101",
        "D|M": "1010101"
    }

    def __init__(self, instruction):
        dest_opjump = instruction.split("=")
        if len(dest_opjump) == 2:
            self.dest = dest_opjump[0].strip()
            op_jump = dest_opjump[1].strip()
        else:
            self.dest = None
            op_jump = dest_opjump[0]
        
        op_jump = op_jump.split(";")
        if len(op_jump) == 2:
            self.jump = op_jump[1].strip()
            self.operation = op_jump[0].strip()
        else:
            self.jump = None
            self.operation = op_jump[0]
    
    def get_operation_binary(self):
        """
        Get 7 digit binary number for operation: a c1 c2 c3 c4 c5 c6
        """
        return CInstruction.OPERATIONS[self.operation]

    def get_dest_binary(self):
        """
        Get 3 digit binary number for destination: d1 d2 d3
        """
        return CInstruction.DESTS[self.dest]
    
    def get_jump_binary(self):
        """
        Get 3 digit binary number for jump: j1 j2 j3
        """
        return CInstruction.JUMPS[self.jump]

        
    def get_binary(self):
        return f"111{self.get_operation_binary()}{self.get_dest_binary()}{self.get_jump_binary()}"


class Instruction(object):
    def __init__(self, line):
        self.line = line
    
    def get_binary(self, symbols):
        if self.line.startswith("("):
            return None
        if self.line.startswith("@"):
            instruction = AInstruction(self.line, symbols)
        else:
            instruction = CInstruction(self.line)
        
        return instruction.get_binary()


class ASM(object):
    def __init__(self, filename):
        self.filename = filename
        self.symbols = {"SCREEN": 16384, "KBD": 24576, "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4}
        for i in range(16):
            self.symbols[f"R{i}"] = i

        lines_no_comments = map(lambda x: x.split("//")[0], open(filename).readlines())
        self.lines = list(filter(lambda x: x != "", map(lambda x: x.strip(" \n"), lines_no_comments)))

        base = os.path.splitext(self.filename)[0]
        self.hack_filename = f"{base}.hack"
    
    def load_labels(self):
        i = 0
        for line in self.lines: 
            if line.startswith("("):
                # Label
                self.symbols[line.strip("()")] = i
            else:
                i += 1
        
    def load_variables(self):
        symbol_count = 16
        for line in self.lines:             
            if line.startswith("@"):
                try: 
                    int(line[1:])
                except:
                    # Variable
                    if not line[1:] in self.symbols:
                        self.symbols[line[1:]] = symbol_count
                        symbol_count += 1
        
    def parse_instructions(self):
        with open(self.hack_filename, "w+") as f:
            for line in self.lines:
                binary = Instruction(line).get_binary(self.symbols)
                if binary:
                    f.write(f"{binary}\n")

    def assemble(self):
        self.load_labels()
        self.load_variables()
        self.parse_instructions()
        return self.hack_filename


if len(sys.argv) < 2:
    raise Exception("Expected filename in command line argument")
assembler = ASM(sys.argv[1])
assembler.assemble()

