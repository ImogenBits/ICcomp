

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

ALUADD = [                        ALU0, Fin]
ALUADC = [                  ALU1      , Fin]
ALUSUB = [                  ALU1, ALU0, Fin]
ALUSBB = [            ALU2            , Fin]
ALUINR = [            ALU2,       ALU0, Fin]
ALUINC = [            ALU2, ALU1      , Fin]
ALUDCR = [            ALU2, ALU1, ALU0, Fin]
ALUDCB = [      ALU3                  , Fin]
ALUAND = [      ALU3,             ALU0, Fin]
ALUOR  = [      ALU3,       ALU1      , Fin]
ALUXOR = [      ALU3,       ALU1, ALU0, Fin]
ALUCMA = [      ALU3, ALU2           , Fin]
ALUCMC = [      ALU3, ALU2,       ALU0, Fin]
ALUSTC = [      ALU3, ALU2, ALU1      , Fin]
ALURRC = [      ALU3, ALU2, ALU1, ALU0, Fin]
ALURAL = [ALU4                        , Fin]
ALURAR = [ALU4,                   ALU0, Fin]

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
    def __init__(self, operations, isRegular = true, flags = 0xF0, byteCode = nextInstruction, name = ""):
        if len(self) > 2^5:
            raise Exception("Instruction {} has too many steps!".format(byteCode))
        if byteCode == nextInstruction:
            nextInstruction += 1
        self.flags = flags
        self.byteCode = byteCode
        self.name = name
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

#Control Logic

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

initFlagsZero = Instruction(initFlagsZeroOpList, False, 0x0F, 0, name = "INIT")
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF1, 0, name = "INIT")
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF2, 0, name = "INIT")
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF4, 0, name = "INIT")
initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0xF8, 0, name = "INIT")

#Data Transfer

#MOV r1, r2
MOVr1r2 = {}
for r1 in registers:
    for r2 in registers:
        MOVr1r2[r1][r2] = Instruction([[ro(r1, "out"), ro(r2, "in")]], name = "MOV {}, {}".format(r1, r2))

#MOV M, r
MOVMr = {}
for r in registers:
    MOVMr[r] = Instruction([[Lout, MARLin],
                            [Hout, MARHin],
                            [RAMout, ro(r, "in")]], name = "MOV M, {}".format(r))

#MOV r, M
MOVrM = {}
for r in registers:
    MOVrM[r] = Instruction([[Lout, MARLin],
                            [Hout, MARHin],
                            [ro(r, "out"), RAMin]], name = "MOV {}, M".format(r))

#MVI data, r
MVIdatar = {}
for r in registers:
    MVIdatar[r] = Instruction([[PCLout, MARLin],
                               [PCHout, MARHin],
                               [RAMout, ro(r, "in"), CE]], name = "MVI data, {}".format(r))

#MVI data, M
MVIdataM = Instruction([[PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, TMPin, CE],
                        [Lout, MARLin],
                        [Hout, MARHin],
                        [ALUout, RAMin]], name = "MVI data, M")

#LXI data, rp
LXIdatarp = {}
for rp in registerPairs:
    LXIdatarp[rp] = Instruction([[PCLout, MARLin],
                                 [PCHout, MARHin],
                                 [RAMout, ro(rp[1], "in"), CE],
                                 [PCLout, MARLin],
                                 [PCHout, MARHin],
                                 [RAMout, ro(rp[0], "in"), CE]], name = "LXI data, {}".format(rp))

#LDA addr
LDAaddr = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin, CE],
                       [PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, MARHin, CE],
                       [ALUout, MARLin],
                       [RAMout, Ain]], name = "LDA addr")

#STA addr
STAaddr = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin, CE],
                       [PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, MARHin, CE],
                       [ALUout, MARLin],
                       [Aout, RAMin]], name = "STA addr")

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
                        [ALUout, MARLin] + ALUINR,
                        [MARHout, TMPin],
                        [ALUout, MARHin] + ALUINC,
                        [RAMout, Hin]], name = "LDHL addr")

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
                        [ALUout, MARLin] + ALUINR,
                        [MARHout, TMPin],
                        [ALUout, MARHin] + ALUINC,
                        [Hout, RAMin]], name = "STHL addr")


#LDAX rp
LDAXrp = {}
for rp in registerPairs:
    LDAXrp[rp] = Instruction([[ro(rp[1], "out"), MARLin],
                              [ro(rp[0], "out"), MARHin],
                              [RAMout, Ain]], name = "LDAX {}".format(rp))

#STAX rp
STAXrp = {}
for rp in registerPairs:
    STAXrp[rp] = Instruction([[ro(rp[1], "out"), MARLin],
                              [ro(rp[0], "out"), MARHin],
                              [Aout, RAMin]], name = "STAX {}".format(rp))

#XCHG
XCHG = Instruction([[Lout, TMPin],
                    [Eout, Lin],
                    [ALUout, Ein],
                    [Hout, TMPin],
                    [Dout, Hin],
                    [ALUout, Din]], name = "XCHG")

#Arithmetic

#ADD r
ADDr = {}
for r in registers:
    ADDr = Instruction([[ro(r, "out"), TMPin],
                        [ALUout, Ain] + ALUADD], name = "ADD {}".format(r))

#Add M
ADDM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUADD], name = "ADD M")

#ADC r
ADCr = {}
for r in registers:
    ADCr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUADC], name = "ADC {}".format(r))

#ADC M
ADCM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain,  ALUADC]], name = "ADC M")

#ADI data
ADIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUADD], name = "ADI data")

#ACI data
ACIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUADC], name = "ACI data")

#DAD rp
DADrp = {}
for rp in registerPairs:
    DADrp[rp] = Instruction([[Lout, Ain],
                             [ro(rp[1], "out"), TMPin],
                             [Aout, Lin] + ALUADD,
                             [Hout, Ain],
                             [ro(rp[0], "out"), TMPin],
                             [Aout, Hin] + ALUADC], name = "DAD {}".format(rp))

#SUB r
SUBr = {}
for r in registers:
    SUBr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUSUB], name = "SUB {}".format(r))

#SUB M
SUBM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUSUB], name = "SUB M")

#SBB r
SBBr = {}
for r in registers:
    SBBr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUSBB], name = "SBB {}".format(r))

#SBB M
SBBM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUSBB], name = "SBB M")

#SUI data
SUIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUSUB], name = "SUI data")

#SBI data
SBIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUSBB], name = "SBI data")

#INR r
INRr = {}
for r in registers:
    INRr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, ro(r, "in")] + ALUINR], name = "INR {}".format(r))

#INR M
INRM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, RAMin] + ALUINR], name = "INR M")

#DCR r
DCRr = {}
for r in registers:
    DCRr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, ro(r, "in")] + ALUDCR], name = "DCR {}".format(r))

#DCR M
DCRM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, RAMin] + ALUDCR], name = "DCR M")

#INX rp
INXrp = {}
for rp in registerPairs:
    INXrp[rp] = Instruction([[ro(rp[1], "out"), TMPin],
                             [ALUout, ro(rp[1], "in")] + ALUINR,
                             [ro(rp[0], "out"), TMPin],
                             [ALUout, ro(rp[0], "in")] + ALUINC], name = "INX {}".format(rp))

#DCX rp
DCXrp = {}
for rp in registerPairs:
    DCXrp[rp] = Instruction([[ro(rp[1], "out"), TMPin],
                             [ALUout, ro(rp[1], "in")] + ALUDCR,
                             [ro(rp[0], "out"), TMPin],
                             [ALUout, ro(rp[0], "in")] + ALUDCB], name = "DCX {}".format(rp))

#ANA r
ANAr = {}
for r in registers:
    ANAr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUAND], name = "ANA {}".format(r))

#ANA M
ANAM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUAND], name = "ANA M")

#ANIdata
ANIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUAND], name = "ANI data")

#ORA r
ORAr = {}
for r in registers:
    ORAr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUOR], name = "ORA {}".format(r))

#ORA M
ORAM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUOR], name = "ORA M")

#ORI data
ORIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUOR], name = "ORI data")

#XRA r
XRAr = {}
for r in registers:
    XRAr[r] = Instruction([[ro(r, "out"), TMPin],
                           [ALUout, Ain] + ALUXOR], name = "XRA {}".format(r))

#XRA M
XRAM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],
                    [ALUout, Ain] + ALUXOR], name = "XRA M")

#XRI data
XRIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [ALUout, Ain] + ALUXOR], name = "XRI data")

#CMA
CMA = Instruction([[ALUout, Ain] + ALUCMA], name = "CMA")

#CMC
CMC = Instruction([[] + ALUCMC], name = "CMC")

#STC
STC = Instruction([[] + ALUSTC], name = "STC")

#CMP r
CMPr = {}
for r in registers:
    CMPr[r] = Instruction([[ro(r, "out"), TMPin],
                           [] + ALUSUB], name = "CMP {}".format(r))

#CMP M
CMPM = Instruction([[Lout, MARLin],
                    [Hout, MARHin],
                    [RAMout, TMPin],], name = "CMP M")

#CPI data
CPIdata = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],], name = "CPI data")

#RRC
RRC = Instruction([[ALUout, Ain] + ALURRC], name = "RRC")

#RAL
RAL = Instruction([[ALUout, Ain] + ALURAL], name = "RAL")

#RAR
RAR = Instruction([[ALUout, Ain] + ALURAR], name = "RAR")

#Branch instructions

#JMP addr
JMPaddr = Instruction([[PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, TMPin,  CE],
                       [PCLout, MARLin],
                       [PCHout, MARHin],
                       [RAMout, PCHin],
                       [ALUout, PCLin]], name = "JMP addr")

#JZ addr
#JNZ addr
#JC addr
#JNC addr
#JP addr
#JM addr
#JPE addr
#JPO addr
conditionals = {"Z", "NZ", "C", "NC", "P", "M", "PE", "PO"}
Jcond = {}
for i in range(len(conditionals)):
    isSet = ~(i & 0x01)
    flagNum = int(i / 2)
    flag = (isSet << flagNum) | (0x01 << flagNum)
    byteCode = Instruction.byteCode
    Jcond[conditionals[i]] = Instruction([], flags = flag, byteCode = byteCode, name = "J" + conditionals[i] + " addr")
    Jcond[conditionals[i]] = Instruction([], flags = flag & 0x0F, byteCode = byteCode, name = "J" + conditionals[i] + " addr")












































































if __name__ == '__main__':
    try:
        


    except KeyboardInterrupt:
        print()
    except:
        import traceback
        traceback.print_exc()