import sys
import re
import os

class Instruction:
    byName = {}
    def __init__(self, byteCode, name, regex = None, extraArgs = None):
        self.byteCode = byteCode
        self.name = name
        self.regex = regex + r"$" if regex else name + r"$"
        self.extraArgs = [] if extraArgs is None else extraArgs
        Instruction.byName[name] = self


if __name__ == '__main__':
    try:
        inputFileName = sys.argv[1] if len(sys.argv) > 1 else "program.txt"
        outputFileName = sys.argv[2] if len(sys.argv) > 2 else "program"
        instructionFileName = sys.argv[2] if len(sys.argv) > 2 else "instructionList.txt"

        programLines = []
        with open(inputFileName, "r") as inputFile:
            for line in inputFile.readlines():
                programLines.append(line)
        instructions = {}
        with open(instructionFileName, "r") as instructionFile:
            for line in instructionFile.readlines():
                match = re.match(r"(\w*) \| (\w*)(:? (.*))?", line)
                if match:
                    byteCode = int(match.group(1), 16)
                    name, args = match.group(2, 3)
                    regex = name
                    extraArgs = None
                    if args:
                        dataMatch = re.match(r".*data", args)
                        addrMatch = re.match(r".*addr", args)
                        if dataMatch:
                            regex += re.sub(r"data", r"(\\d*?)", args)
                            extraArgs = [(1, 1)]
                        elif addrMatch:
                            regex += re.sub(r"addr", r"(\\d*?)", args)
                            extraArgs = [(1, 2)]
                        else:
                            regex += args
                    Instruction(byteCode, name + (args if args else ""), regex, extraArgs)
                else:
                    raise Exception("Line \"{}\" does not match expected pattern".format(line))
                
        outArr = []
        for line in programLines:
            match, instruction = None, None
            for instrName, instr in Instruction.byName.items():
                instrMatch = re.match(instr.regex, line.strip())
                if instrMatch:
                    match = instrMatch
                    instruction = instr
                    break
            if match:
                outArr.append(instruction.byteCode)
                for argTuple in instruction.extraArgs:
                    arg = int(match.group(argTuple[0]))
                    for i in len(argTuple[i]):
                        outArr.append((arg >> (i * 8)) % 2**8)

        with open(os.path.join("EEPROMFiles", outputFileName), "wb+") as outFile:
            outFile.write(bytes(outArr))
            outFile.close()
        

            

    except KeyboardInterrupt:
        print()