import sys
import os 
from CodeWriter import CodeWriter

class Parser(object): 
    def __init__(self, input):
        if os.path.isfile(input):
            self.filenames = [input]
            self.asm = f"{os.path.splitext(input)[0]}.asm"
        elif os.path.isdir(input):
            self.filenames = [os.path.join(input, f) for f in os.listdir(input) if os.path.splitext(f)[1] == ".vm"]
            self.asm = os.path.join(input, f"{os.path.basename(os.path.normpath(input))}.asm")
        else: 
            raise Exception(f"Input {input} is neither file nor directory")

    def parse(self):
        with open(self.asm, "w+") as f:
            if len(self.filenames) > 1:
                init = CodeWriter(instruction="init", basename=None, functionname=None)
                f.writelines(f"{l}\n" for l in init.get_lines())
            for filename in self.filenames:
                functionname = "null"
                lines_no_comments = map(lambda x: x.split("//")[0], open(filename).readlines())
                lines = list(filter(lambda x: x != "", map(lambda x: x.strip(" \n"), lines_no_comments)))
                base = os.path.basename(os.path.splitext(filename)[0])

                for instruction in lines:
                    if instruction.startswith("function"):
                        functionname = instruction.split()[1]
            
                    code_writer = CodeWriter(instruction=instruction, basename=base, functionname=functionname)
                    f.writelines(f"{l}\n" for l in code_writer.get_lines())

            end = CodeWriter(instruction="end", basename=None, functionname=None)
            f.writelines(f"{l}\n" for l in end.get_lines())

if len(sys.argv) < 2:
    raise Exception("Expected filename or directory in command line argument")
parser = Parser(sys.argv[1])
parser.parse()

