from itertools import count

class Instruction(object):
    instance_count = count(0)

    def __init__(self, instruction):
        self.assembly_lines = [f"//{instruction}"]
        self.instance = next(self.instance_count)

        
    def _c_command(self, computation, dest=None, jump=None):
        first_half = f"{dest}={computation}" if dest else computation
        self.assembly_lines += [
            f"{first_half}; {jump}" 
            if jump else f"{first_half}"
        ]
    
    def _a_command(self, address):
        self.assembly_lines += [
            f"@{address}"
        ]
    
    def _label(self, label):
        self.assembly_lines += [
            f"({label})"
        ]
    
    def _decrement_sp(self):
        self._a_command("SP")
        self._c_command(dest="M", computation="M-1")
    
    def _increment_sp(self):
        self._a_command("SP")
        self._c_command(dest="M", computation="M+1")
    
    def _read_sp(self, dest):
        self._a_command("SP")
        self._c_command(dest="A", computation="M")
        self._c_command(dest=dest, computation="M")
    
    def _write_sp(self, source):
        self._a_command("SP")
        self._c_command(dest="A", computation="M")
        self._c_command(dest="M", computation=source)

    def _operate_one(self, computation):
        self._decrement_sp()                    # --SP
        self._read_sp("D")                      # D=*SP
        self._c_command(dest="D", computation=computation)
                                                # D=COMP
        self._write_sp("D")                     # *SP=D
        self._increment_sp()                    # ++SP

    def _operate_two(self, computation):
        self._decrement_sp()                    # --SP
        self._read_sp("D")                      # D=*SP
        self._decrement_sp()                    # --SP
        self._read_sp("A")                      # A=*SP
        self._c_command(dest="D", computation=computation)       
                                                # D=comp
        self._write_sp("D")                     # *SP=D
        self._increment_sp()                    # ++SP
    
    def _compare_two(self, jump):
        self._decrement_sp()                    # --SP
        self._read_sp("D")                      # D=*SP
        self._decrement_sp()                    # --SP
        self._read_sp("A")                      # A=*SP
        self._c_command(dest="D", computation="A-D")             
                                                # D=A-D
        self._a_command(f"EQ{self.instance}")   # @EQ
        self._c_command("D", jump=jump)         # D;jump to label_eq
        self._write_sp('0')                     # *SP=0
        self._a_command(f"NE{self.instance}")   # @NE
        self._c_command('0', jump='JMP')        # 0;JMP to NE
        self._label(f"EQ{self.instance}")       # (EQ)
        self._write_sp('-1')                    # *SP=-1
        self._label(f"NE{self.instance}")       # (NE)
        self._increment_sp()                    # ++SP
    
    def write_assembly(self):
        raise NotImplementedError

    def get_assembly(self):
        return self.assembly_lines

class Operate(Instruction): 
    def __init__(self, instruction):
        self.instruction = instruction
        super().__init__(instruction)
    
    def write_assembly(self):
        instructions = {
            "add": (self._operate_two, {"computation": "A+D"}),
            "sub": (self._operate_two, {"computation": "A-D"}),
            "neg": (self._operate_one, {"computation": "-D"}),
            "and": (self._operate_two, {"computation": "A&D"}),
            "or": (self._operate_two, {"computation": "D|A"}),
            "not": (self._operate_one, {"computation": "!D"}),
            "lt": (self._compare_two, {"jump": "JLT"}),
            "gt": (self._compare_two, {"jump": "JGT"}),
            "eq": (self._compare_two, {"jump": "JEQ"}),
        }
        operation, kwargs = instructions[self.instruction]
        operation(**kwargs)

class Push(Instruction):
    def __init__(self, instruction, base_name):
        self.base_name = base_name
        self.push_type, self.val = instruction.split()[1], instruction.split()[2]

        super().__init__(instruction)
    
    def write_assembly(self):
        if self.push_type == "constant":
            self._a_command(self.val)                            
            self._c_command(dest="D", computation="A")      # D=VAL
        elif self.push_type == "pointer":
            self._a_command("THIS" if self.val == "0" else "THAT")
            self._c_command(dest="D", computation="M")      # D=*(THIS|THAT)
        elif self.push_type in ("this", "that", "local", "argument"):
            mapping = {
                "this": "THIS", 
                "that": "THAT", 
                "local": "LCL",
                "argument": "ARG"
            }
            self._a_command(mapping[self.push_type])
            self._c_command(dest="D", computation="M")
            self._a_command(self.val)
            self._c_command(dest="A", computation="D+A")
            self._c_command(dest="D", computation="M")      # D=*(SEG+val)
        elif self.push_type == "temp":
            self._a_command("5")
            self._c_command(dest="D", computation="A")
            self._a_command(self.val)
            self._c_command(dest="A", computation="D+A")
            self._c_command(dest="D", computation="M")      # D=*(5+val)
        elif self.push_type == "static":
            self._a_command(f"{self.base_name}.{self.val}")
            self._c_command(dest="D", computation="M")      # D=*(base_name.val)
        else:
            raise Exception(f"Don't recognise push type {self.push_type}")

        self._write_sp("D")                                 # *SP=D
        self._increment_sp()                                # SP++

class Pop(Instruction):
    def __init__(self, instruction, base_name):
        self.base_name = base_name
        self.pop_type, self.val = instruction.split()[1], instruction.split()[2]
        super().__init__(instruction)
    
    def write_assembly(self):
        if self.pop_type == "pointer":
            self._a_command("THIS" if self.val == "0" else "THAT")
            self._c_command(dest="D", computation="A")      # D=THIS|THAT
        elif self.pop_type in ("this", "that", "local", "argument"):
            mapping = {
                "this": "THIS",
                "that": "THAT",
                "local": "LCL",
                "argument": "ARG"
            }
            self._a_command(mapping[self.pop_type])
            self._c_command(dest="D", computation="M")
            self._a_command(self.val)
            self._c_command(dest="D", computation="D+A")    # D=SEG+val
        elif self.pop_type == "temp":
            self._a_command("5")
            self._c_command(dest="D", computation="A")
            self._a_command(self.val)
            self._c_command(dest="D", computation="D+A")    # D=5+val
        elif self.pop_type == "static":
            self._a_command(f"{self.base_name}.{self.val}")
            self._c_command(dest="D", computation="A")      # D=basename.val
        else:
            raise Exception(f"Don't recognise pop type {self.pop_type}")

        self._a_command("R13")                     # @R13
        self._c_command(dest="M", computation="D") # M=D
        self._decrement_sp()                       # SP--
        self._read_sp("D")                         # D=*SP
        self._a_command("R13")                     # @R13
        self._c_command(dest="A", computation="M") # A=M
        self._c_command(dest="M", computation="D") # M=D
    

class End(Instruction):
    def __init__(self, instruction):
        self.instruction = instruction
        super().__init__(instruction)
    
    def write_assembly(self):
        self._label("END")
        self._a_command("END")
        self._c_command(dest=None, computation="0", jump="JMP")


class CodeWriter(Instruction):    
    def __init__(self, base_name, instruction):
        self.base_name = base_name

        if instruction == "end":
            self.instruction = End(instruction)
        elif instruction.startswith("push"):
            self.instruction = Push(instruction, base_name)
        elif instruction.startswith("pop"):
            self.instruction = Pop(instruction, base_name)
        else:
            self.instruction = Operate(instruction)
        
    def get_lines(self):
        self.instruction.write_assembly()
        return self.instruction.get_assembly() 
        