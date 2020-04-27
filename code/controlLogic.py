

operations = {}
class Operation:
    def __init__(self, eeprom, pin, activeVoltage = False):
        self.eeprom = eeprom
        self.pin = pin
        self.activeVoltage = activeVoltage
        if eeprom not in operations.keys():
            operations[eeprom] = {}
        if pin not in operations[eeprom].keys():
            operations[eeprom][pin] = self
        else:
            raise Exception("Assinging operation to already assinged pin.")


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

Bin = Operation(0, 2)
Cin = Operation(0, 1)
Bout = Operation(0, 0)
Cout = Operation(0, 7)
Din = Operation(0, 6)
Ein = Operation(0, 5)
Dout = Operation(0, 4)
Eout = Operation(0, 3)

ALUADD = [                        ALU0]
ALUADC = [                  ALU1      ]
ALUSUB = [                  ALU1, ALU0]
ALUSBB = [            ALU2            ]
ALUINR = [            ALU2,       ALU0]
ALUINC = [            ALU2, ALU1      ]
ALUDCR = [            ALU2, ALU1, ALU0]
ALUDCB = [      ALU3                  ]
ALUAND = [      ALU3,             ALU0]
ALUOR  = [      ALU3,       ALU1      ]
ALUXOR = [      ALU3,       ALU1, ALU0]
ALUCMA = [      ALU3, ALU2,           ]
ALUCMC = [      ALU3, ALU2,       ALU0]
ALUSTC = [      ALU3, ALU2, ALU1      ]
ALURRC = [      ALU3, ALU2, ALU1, ALU0]
ALURAL = [ALU4,                       ]
ALURAR = [ALU4,                   ALU0]

#registers
registers = ["A", "B", "C", "D", "E", "H", "L"]
registerPairs = [("B", "C"), ("D", "E"), ("H", "L"), ("SPH", "SPL")]
def ro(r, dir):
    return globals()[r + dir]

#standard operations most instructions perform
fetchCycle = [
    [PCLout, MARLin],
    [PCHout, MARHin],
    [STRout, IRin, CE]
]
postInstrCycle = [
    [STCR]
]    

def doesMaskFit(flags, mask, relevancyMask):
    result = 0
    for i in range(4):
        if relevancyMask & (0x01 << i):
            result = result | (~(flags ^ mask) & (0x01 << i))
        else:
            result = result | (0x01 << i)
    return result == 0x0F

instructions = {}
class Instruction:
    nextInstruction = 0
    def __init__(self, operations, isRegular = true, flags = 0xF0, byteCode = nextInstruction):
        if len(self) > 2^5:
            raise Exception("Instruction {} has too many steps!".format(byteCode))
        if byteCode == nextInstruction:
            nextInstruction += 1
        self.flags = flags
        self.byteCode = byteCode
        if isRegular:
            self.operations = fetchCycle + operations + postInstrCycle
        else:
            self.operations = operations
        
        if flags & 0x0F:
            if byteCode in instructions.keys():
                if type(instructions[byteCode]) is not dict:
                    raise Exception("Instruction {} has already been assigned!".format(byteCode))
            else:
                instructions[byteCode] = {}
            
            for i in range(2^4):
                if doesMaskFit(i, flags & 0xF0, flags & 0x0F):
                    if i in instructions[byteCode].keys():
                        raise Exception("Instruction {} with flag {:2X} has already been assigned!".format(byteCode, flags))
                    else:
                        instructions[byteCode][i] = self
        else:
            if byteCode in instructions.keys():
                raise Exception("Instruction {} has already been assigned!".format(byteCode))
            else:
                instructions[byteCode] = self

    def __len__(self):
        return len(self.operations)


#Instruction definitons

#INIT
initFlagsZeroOpList = [
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin],
    [ALUout, MARLin, STALin] + ALUINR,
    [STRout, RAMin, IRin],
    [STCR]
]
initFlagsZeroOpList = ([[]] * (len(fetchCycle) + 1)) + initFlagsZeroOpList
initFlagsNonZeroOpList = ([[HLTset]] * (len(fetchCycle) + 1)) + initFlagsZeroOpList

initFlagsZero = Instruction(initFlagsZeroOpList, False, 0x0F, 0)
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF1, 0)
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF2, 0)
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF4, 0)
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF8, 0)

#MOV r1, r2
MOVr1r2 = {}
for r1 in registers:
    for r2 in registers:
        MOVr1r2[r1][r2] = Instruction([[ro(r1, "out"), ro(r2, "in")]])

#MOV M, r
MOVMr = {}
for r in registers:
    MOVMr[r] = Instruction([[Lout, MARLin],
                            [Hout, MARHin],
                            [RAMout, ro(r, "in")]])

#MOV r, M
MOVrM = {}
for r in registers:
    MOVrM[r] = Instruction([[Lout, MARLin],
                            [Hout, MARHin],
                            [ro(r, "out"), RAMin]])

#MVI data, r
MVIdatar = {}
for r in registers:
    MVIdatar[r] = Instruction([[PCLout, MARLin],
                               [PCHout, MARHin],
                               [RAMout, ro(r, "in"), CE]])

#MVI data, M
MVIdataM = Instruction([[PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, TMPin, CE],
                        [Lout, MARLin],
                        [Hout, MARHin],
                        [ALUout, RAMin]])

#LXI data, rp
LXIdatarp = {}
for rp in registerPairs:
    LXIdatarp[rp] = Instruction([[PCLout, MARLin],
                                 [PCHout, MARHin],
                                 [RAMout, ro(rp[1], "in"), CE],
                                 [PCLout, MARLin],
                                 [PCHout, MARHin],
                                 [RAMout, ro(rp[0], "in"), CE]])

#LDA addr
LDAaddr = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin, CE],
                       [PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, MARHin, CE],
                       [ALUout, MARLin],
                       [RAMout, Ain]])

#STA addr
STAaddr = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin, CE],
                       [PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, MARHin, CE],
                       [ALUout, MARLin],
                       [Aout, RAMin]])

#LDHL addr
LDHLaddr = Instruction([[PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, TMPin, CE],
                        [PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, MARHin, CE],
                        [ALUout, MARLin],
                        [RAMout, Lin],
                        [MARLout, TMPin],
                        [ALUout, MARLin, ALUINR],
                        [MARHout, TMPin],
                        [ALUout, MARHin, ALUINC],
                        [RAMout, Hin]])

#STHL addr
STHLaddr = Instruction([[PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, TMPin, CE],
                        [PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, MARHin, CE],
                        [ALUout, MARLin],
                        [Lout, RAMin],
                        [MARLout, TMPin],
                        [ALUout, MARLin, ALUINR],
                        [MARHout, TMPin],
                        [ALUout, MARHin, ALUINC],
                        [Hout, RAMin]])


#LDAX rp
LDAXrp = {}
for rp in registerPairs:
    LDAXrp[rp] = Instruction([[ro(rp[1], "out"), MARLin],
                              [ro(rp[0], "out"), MARHin],
                              [RAMout, Ain]])

#STAX rp
STAXrp = {}
for rp in registerPairs:
    STAXrp[rp] = Instruction([[ro(rp[1], "out"), MARLin],
                              [ro(rp[0], "out"), MARHin],
                              [Aout, RAMin]])

#XCHG
XCHG = Instruction([[Lout, TMPin],
                    [Eout, Lin],
                    [ALUout, Ein],
                    [Hout, TMPin],
                    [Dout, Hin],
                    [ALUout, Din]])

#ADD r
ADDr = Instruction([[rout, TMPin],
                    [ALUout, Ain, ALUADD]])

#Add M
ADDM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain, ALUADD]])




























if __name__ == '__main__':
    try:
        


    except KeyboardInterrupt:
        print()
    except:
        import traceback
        traceback.print_exc()