import sys
import os 
from CodeWriter import CodeWriter

class Parser(object): 
    def __init__(self, filename):
        lines_no_comments = map(lambda x: x.split("//")[0], open(filename).readlines())
        self.lines = list(filter(lambda x: x != "", map(lambda x: x.strip(" \n"), lines_no_comments)))
        self.base = os.path.splitext(filename)[0]
    
    def parse(self):
        with open(f"{self.base}.asm", "w+") as f:
            for instruction in self.lines:
                code_writer = CodeWriter(os.path.basename(self.base), instruction)
                f.writelines(f"{l}\n" for l in code_writer.get_lines())
            end = CodeWriter(self.base, "end")
            f.writelines(f"{l}\n" for l in end.get_lines())

if len(sys.argv) < 2:
    raise Exception("Expected filename in command line argument")
parser = Parser(sys.argv[1])
parser.parse()

