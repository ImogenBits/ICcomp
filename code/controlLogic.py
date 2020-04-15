class Operation:
    def __init__(self, eeprom, pin, activeVoltage = False):
        self.eeprom = eeprom
        self.pin = pin
        self.activeVoltage = activeVoltage

#list of operations
ALU4 = Operation(5, 2, True)
ALU3 = Operation(5, 1, True)
ALU2 = Operation(5, 0, True)
ALU1 = Operation(5, 7, True)
ALU0 = Operation(5, 6, True)
TMPin = Operation(5, 5)
ALUout = Operation(5, 4)
FinSel = Operation(5, 3, True)

Fin = Operation(4, 2)
Fout = Operation(4, 1)
Ain = Operation(4, 0)
Aout = Operation(4, 7)
MARHin = Operation(4, 6)
MARLin = Operation(4, 5)
MARHout =  Operation(4, 4)
MARLout = Operation(4, 3)

RAMin = Operation(3, 2, True)
RAMout = Operation(3, 1)
STAHin = Operation(3, 0)
STALin = Operation(3, 7)
STAHout = Operation(3, 6)
STALout = Operation(3, 5)
STRin = Operation(3, 4, True)
STRout = Operation(3, 3)

SPHin = Operation(2, 2)
SPLin = Operation(2, 1)
SPHout = Operation(2, 0)
SPLout = Operation(2, 7)
Hin = Operation(2, 6)
Lin = Operation(2, 5)
Hout = Operation(2, 4)
Lout = Operation(2, 3)

PCHin = Operation(1, 2)
PCLin = Operation(1, 1)
PCHout = Operation(1, 0)
PCLout = Operation(1, 7)
CE = Operation(1, 6, True)
IRin = Operation(1, 5)
STCR = Operation(1, 4, True)
HLTset = Operation(1, 3)

fetchCycle = [
    [PCLout, STALin],
    [PCHout, STAHin],
    [STRout, IRin, CE]
]
postInstrCycle = {
    [HLTset]
}

class Instruction:
    def __init__(self, name, byteCode, operations, isRegular = true):
        self.name = name
        self.byteCode = byteCode
        if isRegular:
            self.operations = fetchCycle + operations + postInstrCycle
        else:
            self.operations = operations
    def __len__(self):
        return len(self.operations)



if __name__ == '__main__':
    try:
        


    except KeyboardInterrupt:
        print()
    except:
        import traceback
        traceback.print_exc()