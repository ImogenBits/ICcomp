import sys





if __name__ == '__main__':
    try:
        inputFileName = sys.argv[1] if len(sys.argv) > 1 else "program.txt"
        outputFileName = sys.argv[2] if len(sys.argv) > 2 else "compiledProgram.txt"
        instructionFileName = sys.argv[2] if len(sys.argv) > 2 else "instructionList.txt"

        programLines = []
        with open(inputFileName, "r") as inputFile:
            for line in inputFile.readlines():
                programLines.append(line)
        outArr = []

        instructions = {}

        for line in programLines:
            byteCode, flags, step = getInfoFromAddr(eepromAddr)
            outByte = 0x00
            for i, op in operations[eepromIndex].items():
                outByte |= (1 - op.activeVoltage) << op.pin
            
            currOpList = []
            currInstr = None
            if byteCode in instructions:
                currInstr = instructions[byteCode]
                if type(currInstr) is dict:
                    currInstr = currInstr[flags]
            else:
                currInstr = instructions["DEFAULT"]
            
            if currInstr is not None and len(currInstr.operations) > step:
                opList = currInstr.operations[step]
                for op in opList:
                    if op.eeprom == eepromIndex:
                        outByte &= ~(0x01 << op.pin)
                        outByte |= op.activeVoltage << op.pin
            
            outArr.append(outByte)

        with open(outputFileName, "wb") as outFile:
            outFile.write(bytes(outArr))
            outFile.close()
        

            

    except KeyboardInterrupt:
        print()