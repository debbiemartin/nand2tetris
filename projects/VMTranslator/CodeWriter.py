from itertools import count

class Instruction(object):
    cmp_label = count(0)
    return_address_label = count(0)

    def __init__(self, instruction):
        self.assembly_lines = [f"//{instruction}"]

        
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
        self._decrement_sp()
        self._a_command("SP")
        self._c_command(dest="A", computation="M")
        self._c_command(dest=dest, computation="M")
    
    def _write_sp(self, source):
        self._a_command("SP")
        self._c_command(dest="A", computation="M")
        self._c_command(dest="M", computation=source)
        self._increment_sp()

    def _operate_one(self, computation):
        self._read_sp("D")                      # D=*SP
        self._c_command(dest="D", computation=computation)
                                                # D=COMP
        self._write_sp("D")                     # *SP=D

    def _operate_two(self, computation):
        self._read_sp("D")                      # D=*SP
        self._read_sp("A")                      # A=*SP
        self._c_command(dest="D", computation=computation)       
                                                # D=comp
        self._write_sp("D")                     # *SP=D
    
    def _compare_two(self, jump):
        cmp_label = next(self.cmp_label)
        self._read_sp("D")                      # D=*SP
        self._read_sp("A")                      # A=*SP
        self._c_command(dest="D", computation="A-D")             
                                                # D=A-D
        self._a_command(f"EQ{cmp_label}")       # @EQ
        self._c_command("D", jump=jump)         # D;jump to label_eq
        self._write_sp('0')                     # *SP=0
        self._a_command(f"NE{cmp_label}")       # @NE
        self._c_command('0', jump='JMP')        # 0;JMP to NE
        self._label(f"EQ{cmp_label}")           # (EQ)
        self._write_sp('-1')                    # *SP=-1
        self._label(f"NE{cmp_label}")           # (NE)
    
    def _push(self, push_type, val):
        if push_type == "constant":
            self._a_command(val)                            
            self._c_command(dest="D", computation="A")      # D=VAL
        elif push_type == "pointer":
            self._a_command("THIS" if val == "0" else "THAT")
            self._c_command(dest="D", computation="M")      # D=*(THIS|THAT)
        elif push_type in ("this", "that", "local", "argument"):
            mapping = {
                "this": "THIS", 
                "that": "THAT", 
                "local": "LCL",
                "argument": "ARG"
            }
            self._a_command(mapping[self.push_type])
            self._c_command(dest="D", computation="M")
            self._a_command(val)
            self._c_command(dest="A", computation="D+A")
            self._c_command(dest="D", computation="M")      # D=*(SEG+val)
        elif push_type == "temp":
            self._a_command("5")
            self._c_command(dest="D", computation="A")
            self._a_command(val)
            self._c_command(dest="A", computation="D+A")
            self._c_command(dest="D", computation="M")      # D=*(5+val)
        elif push_type == "static":
            self._a_command(f"{self.basename}.{self.val}")
            self._c_command(dest="D", computation="M")      # D=*(basename.val)
        else:
            raise Exception(f"Don't recognise push type {push_type}")

        self._write_sp("D")                                 # *SP=D
    
    def _pop(self, pop_type, val=None):
        if pop_type == "pointer":
            self._a_command("THIS" if val == "0" else "THAT")
            self._c_command(dest="D", computation="A")      # D=THIS|THAT
        elif pop_type in ("this", "that", "local", "argument"):
            mapping = {
                "this": "THIS",
                "that": "THAT",
                "local": "LCL",
                "argument": "ARG"
            }
            self._a_command(mapping[pop_type])
            self._c_command(dest="D", computation="M")
            self._a_command(val)
            self._c_command(dest="D", computation="D+A")    # D=SEG+val
        elif pop_type == "temp":
            self._a_command("5")
            self._c_command(dest="D", computation="A")
            self._a_command(val)
            self._c_command(dest="D", computation="D+A")    # D=5+val
        elif pop_type == "static":
            self._a_command(f"{self.basename}.{val}")
            self._c_command(dest="D", computation="A")      # D=basename.val
        else:
            raise Exception(f"Don't recognise pop type {pop_type}")

        self._a_command("R13")                     # @R13
        self._c_command(dest="M", computation="D") # M=D
        self._read_sp("D")                         # D=*SP
        self._a_command("R13")                     # @R13
        self._c_command(dest="A", computation="M") # A=M
        self._c_command(dest="M", computation="D") # M=D
    
    def _endframe_to_seg(self, seg, minus):
        # <seg>=*(endFrame-<minus>)
        self._a_command("endFrame")
        self._c_command(dest="D", computation="M")
        self._a_command(f"{minus}")
        self._c_command(dest="A", computation="D-A")
        self._c_command(dest="D", computation="M")
        self._a_command(seg)
        self._c_command(dest="M", computation="D") 
    
    def _call(self, functionname, call_functionname, num_args):
        return_addr = f"{functionname}$ret.{next(self.return_address_label)}"
        self._a_command(return_addr)
        self._c_command(dest="D", computation="A")
        self._write_sp("D")                        # *SP=returnAddr
        self._a_command("LCL")
        self._c_command(dest="D", computation="M")
        self._write_sp("D")                        # push LCL
        self._a_command("ARG")
        self._c_command(dest="D", computation="M")
        self._write_sp("D")                        # push ARG
        self._a_command("THIS")
        self._c_command(dest="D", computation="M")
        self._write_sp("D")                        # push THIS
        self._a_command("THAT")
        self._c_command(dest="D", computation="M")
        self._write_sp("D")                        # push THAT
        self._a_command(f"{5 + int(num_args)}")
        self._c_command(dest="D", computation="A")
        self._a_command("SP")
        self._c_command(dest="D", computation="M-D")
        self._a_command("ARG")
        self._c_command(dest="M", computation="D") # ARG = SP-5-nArgs
        self._a_command("SP")
        self._c_command(dest="D", computation="M")
        self._a_command("LCL")
        self._c_command(dest="M", computation="D") # LCL=SP
        self._goto(goto=call_functionname)         # goto call_functionname
        self._label(return_addr)                   # (functionname$ret.i)
    
    def _goto(self, goto):
        self._a_command(f"{goto}")                     # @GOTO
        self._c_command(computation="0", jump="JMP")   # 0; JMP
    
    @staticmethod
    def _create_label(basename, this_functionname, label):
        return f"{basename}.{this_functionname}${label}"
    
    def write_assembly(self):
        raise NotImplementedError

    def get_assembly(self):
        return self.assembly_lines


class Operate(Instruction): 
    def __init__(self, instruction, basename, functionname):
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
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.push_type, self.val = instruction.split()[1], instruction.split()[2]
        super().__init__(instruction)
    
    def write_assembly(self):
        self._push(push_type=self.push_type, val=self.val)


class Pop(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.pop_type, self.val = instruction.split()[1], instruction.split()[2]
        super().__init__(instruction)
    
    def write_assembly(self):
        self._pop(pop_type=self.pop_type, val=self.val)


class Label(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.functionname = functionname
        self.label = instruction.split()[1]
        super().__init__(instruction)
    
    def write_assembly(self):
        label = self._create_label(self.basename, self.functionname, self.label)
        self._label(label)


class GoTo(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.functionname = functionname
        self.goto = instruction.split()[1]
        super().__init__(instruction)
    
    def write_assembly(self):
        label = self._create_label(self.basename, self.functionname, self.goto)
        self._goto(label)


class IfGoTo(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.functionname = functionname
        self.goto = instruction.split()[1]
        super().__init__(instruction)
    
    def write_assembly(self):
        self._read_sp("D")                                                   # D=*SP
        label = self._create_label(self.basename, self.functionname, self.goto)
        self._a_command(label)                                               # @GOTO
        self._c_command(computation="D", jump="JNE")                         # D; JNE
    
class Call(Instruction): 
    def __init__(self, instruction, basename, functionname):
        self.this_functionname = functionname
        self.call_functionname, self.num_args = instruction.split()[1], instruction.split()[2]
        super().__init__(instruction)
    
    def write_assembly(self):
        self._call(functionname=self.this_functionname,
                   call_functionname=self.call_functionname, 
                   num_args=self.num_args)


class Function(Instruction): 
    def __init__(self, instruction, basename, functionname):
        self.baseandfunctionname, self.num_vars = instruction.split()[1], instruction.split()[2]
        super().__init__(instruction)
    
    def write_assembly(self):
        self._label(self.baseandfunctionname)                # (basename.functionname)
        for i in range(int(self.num_vars)):
            self._push(push_type="constant", val="0") 


class Return(Instruction): 
    def __init__(self, instruction, basename, functionname):
        self.basename = basename
        self.functionname = functionname
        self.instruction = instruction
        super().__init__(instruction)
        
    def write_assembly(self):
        self._a_command("LCL")
        self._c_command(dest="D", computation="M")
        self._a_command("endFrame")
        self._c_command(dest="M", computation="D")   # endFrame=LCL
        self._endframe_to_seg("retAddr", 5)          # retAddr = *(endFrame-5)
        self._pop(pop_type="argument", val="0")
        self._a_command("ARG")
        self._c_command(dest="D", computation="M+1")
        self._a_command("SP")
        self._c_command(dest="M", computation="D")   # SP=ARG+1

        self._endframe_to_seg("THAT", 1)             # THAT=*(endFrame-1)
        self._endframe_to_seg("THIS", 2)             # THIS=*(endFrame-2)
        self._endframe_to_seg("ARG", 3)              # ARG=*(endFrame-3)
        self._endframe_to_seg("LCL", 4)              # LCL=*(endFrame-4)

        self._a_command("retAddr")
        self._c_command(dest="A", computation="M")
        self._c_command(computation="0", jump="JMP") # @GOTO retAddr


class Init(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.instruction = instruction
        super().__init__(instruction)
    
    def write_assembly(self):
        self._a_command("256")
        self._c_command(dest="D", computation="A")
        self._a_command("SP")
        self._c_command(dest="M", computation="D")
        self._call(functionname=None, 
                   call_functionname="Sys.init",
                   num_args="0")


class End(Instruction):
    def __init__(self, instruction, basename, functionname):
        self.instruction = instruction
        super().__init__(instruction)
    
    def write_assembly(self):
        self._label("END")
        self._a_command("END")
        self._c_command(dest=None, computation="0", jump="JMP")


class CodeWriter(Instruction): 
    mapping = {
        "init": Init,
        "end": End,
        "push": Push,
        "pop": Pop,
        "label": Label,
        "goto": GoTo,
        "if-goto": IfGoTo,
        "call": Call,
        "function": Function,
        "return": Return
    }   

    def __init__(self, basename, instruction, functionname):
        self.basename = basename

        for m, handler in self.mapping.items():
            if instruction.startswith(m):
                self.instruction = handler(instruction, basename, functionname)
                break
        else:
            self.instruction = Operate(instruction, basename, functionname)
        
    def get_lines(self):
        self.instruction.write_assembly()
        return self.instruction.get_assembly() 