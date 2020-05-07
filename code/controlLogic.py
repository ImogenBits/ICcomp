import sys

operations = {}
class Operation:
    def __init__(self, eeprom, pin, activeVoltage = 0):
        self.eeprom = eeprom
        self.pin = pin
        self.activeVoltage = activeVoltage
        if eeprom not in operations:
            operations[eeprom] = {}
        if pin not in operations[eeprom]:
            operations[eeprom][pin] = self
        else:
            raise Exception("Assinging operation to already assinged pin.")


#list of operations
ALU4 = Operation(5, 2, 1)
ALU3 = Operation(5, 1, 1)
ALU2 = Operation(5, 0, 1)
ALU1 = Operation(5, 7, 1)
ALU0 = Operation(5, 6, 1)
TMPin = Operation(5, 5)
ALUout = Operation(5, 4)
FinSel = Operation(5, 3, 1)

Fin = Operation(4, 2)
Fout = Operation(4, 1)
Ain = Operation(4, 0)
Aout = Operation(4, 7)
MARHin = Operation(4, 6)
MARLin = Operation(4, 5)
MARHout =  Operation(4, 4)
MARLout = Operation(4, 3)

RAMin = Operation(3, 2, 1)
RAMout = Operation(3, 1)
STAHin = Operation(3, 0)
STALin = Operation(3, 7)
STAHout = Operation(3, 6)
STALout = Operation(3, 5)
STRin = Operation(3, 4, 1)
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
CE = Operation(1, 6, 1)
IRin = Operation(1, 5)
STCR = Operation(1, 4, 1)
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
ALUCMA = [      ALU3, ALU2            , Fin]
ALUCMC = [      ALU3, ALU2,       ALU0, Fin]
ALUSTC = [      ALU3, ALU2, ALU1      , Fin]
ALURRC = [      ALU3, ALU2, ALU1, ALU0, Fin]
ALURAL = [ALU4                        , Fin]
ALURAR = [ALU4,                   ALU0, Fin]

#registers
registers = ["A", "B", "C", "D", "E", "H", "L"]
registerPairs = [("B", "C", "BC"), ("D", "E", "DE"), ("H", "L", "HL"), ("SPH", "SPL", "SP")]
def ro(r, dir):
    return globals()[r + dir]

#standard operations most instructions perform
fetchCycle = [
    [PCLout, MARLin],
    [PCHout, MARHin],
    [RAMout, IRin, CE]
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
    maxNumOperations = 2**5
    def __init__(self, operations, isRegular = True, flags = 0xF0, byteCode = None, name = ""):
        if isRegular:
            self.operations = fetchCycle + operations + postInstrCycle
        else:
            self.operations = operations
        if len(self.operations) > Instruction.maxNumOperations:
            raise Exception("Instruction {} ({:h}) has too many steps!".format(name, byteCode))
        if byteCode == None:
            byteCode = Instruction.nextInstruction
        if byteCode == Instruction.nextInstruction:
            Instruction.nextInstruction += 1
        self.flags = flags
        self.byteCode = byteCode
        self.name = name
        
        if flags & 0x0F:
            if byteCode in instructions:
                if type(instructions[byteCode]) is not dict:
                    raise Exception("Instruction {} has already been assigned!".format(byteCode))
            else:
                instructions[byteCode] = {}
            
            for i in range(2**4):
                if doesMaskFit(i, (flags & 0xF0) >> 4, flags & 0x0F):
                    if i in instructions[byteCode]:
                        raise Exception("Instruction {} with flag {:02X} has already been assigned!".format(byteCode, flags))
                    else:
                        instructions[byteCode][i] = self
        else:
            if byteCode in instructions:
                raise Exception("Instruction {} has already been assigned!".format(byteCode))
            else:
                instructions[byteCode] = self

    def __len__(self):
        return len(self.operations)

    def __str__(self):
        return self.name


#Instruction definitons
#Control Logic
def createControlLogicInstructions():
    #INIT
    initOpList = [
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin],
        [ALUout, MARLin, STALin, TMPin] + ALUINR[:-1],
        [STRout, RAMin, IRin],
        [STCR]
    ]
    initFlagsZeroOpList = ([[]] * (len(fetchCycle) + 1)) + initOpList
    initFlagsNonZeroOpList = ([[HLTset]] * (len(fetchCycle) + 1)) + initOpList

    initFlagsZero = Instruction(initFlagsZeroOpList, False, 0x0F, 0, name = "INIT")
    initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0x11, 0, name = "INIT")
    initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0x23, 0, name = "INIT")
    initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0x47, 0, name = "INIT")
    initFlagsNonZero = Instruction(initFlagsNonZeroOpList, False, 0x8F, 0, name = "INIT")

    #INIT2
    init2OpList = fetchCycle.copy()
    for i in range(Instruction.maxNumOperations - len(init2OpList)):
        init2OpList += [[STCR]]
    init2 = Instruction(init2OpList, False, name = "INIT2")
    #DEFAULT
    default = Instruction([[]], name = "DEFAULT", byteCode = "DEFAULT")

#Data Transfer
def createDataTransferInstructions():
    #MOV r1, r2
    MOVr1r2 = {}
    for r1 in registers:
        MOVr1r2[r1] = {}
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
                                    [RAMout, ro(rp[0], "in"), CE]], name = "LXI data, {}".format(rp[2]))

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
                                [RAMout, Ain]], name = "LDAX {}".format(rp[2]))

    #STAX rp
    STAXrp = {}
    for rp in registerPairs:
        STAXrp[rp] = Instruction([[ro(rp[1], "out"), MARLin],
                                [ro(rp[0], "out"), MARHin],
                                [Aout, RAMin]], name = "STAX {}".format(rp[2]))

    #XCHG
    XCHG = Instruction([[Lout, TMPin],
                        [Eout, Lin],
                        [ALUout, Ein],
                        [Hout, TMPin],
                        [Dout, Hin],
                        [ALUout, Din]], name = "XCHG")

#Arithmetic
def createArithmeticInstructions():
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
                        [ALUout, Ain] + ALUADC], name = "ADC M")

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
                                [Aout, Hin] + ALUADC], name = "DAD {}".format(rp[2]))

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
                                [ALUout, ro(rp[0], "in")] + ALUINC], name = "INX {}".format(rp[2]))

    #DCX rp
    DCXrp = {}
    for rp in registerPairs:
        DCXrp[rp] = Instruction([[ro(rp[1], "out"), TMPin],
                                [ALUout, ro(rp[1], "in")] + ALUDCR,
                                [ro(rp[0], "out"), TMPin],
                                [ALUout, ro(rp[0], "in")] + ALUDCB], name = "DCX {}".format(rp[2]))

#Logic
def createLogicInstructions():
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
def createBranchInstructions():
    #JMP addr
    JMPaddr = Instruction([[PCLout, MARLin],
                        [PCHout, MARHin],
                        [RAMout, TMPin, CE],
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
    conditionals = ["C", "NC", "PE", "PO", "Z", "NZ", "P", "M"]
    Jcond = {}
    for i in range(len(conditionals)):
        isSet = ~i & 0x01
        flagNum = int(i / 2)
        flag = (isSet << (flagNum + 4)) | (0x01 << flagNum)
        restFlag = (~flag & 0xF0) | (flag & 0x0F)
        byteCode = Instruction.nextInstruction
        Jcond[conditionals[i]] = Instruction([[PCLout, MARLin],
                                            [PCHout, MARHin],
                                            [RAMout, TMPin, CE],
                                            [PCLout, MARLin],
                                            [PCHout, MARHin],
                                            [RAMout, PCHin],
                                            [ALUout, PCLin]], flags = flag, byteCode = byteCode, name = "J" + conditionals[i] + " addr")
        Jcond[conditionals[i]] = Instruction([], flags = restFlag, byteCode = byteCode, name = "J" + conditionals[i] + " addr")

    #CALL addr
    CALLaddr = Instruction([[SPLout, TMPin],
                            [ALUout, MARLin] + ALUDCR,
                            [SPHout, TMPin],
                            [ALUout, MARHin] + ALUDCB,
                            [PCHout, RAMin],
                            [MARLout, TMPin],
                            [ALUout, MARLin, SPLin] + ALUDCR,
                            [MARHout, TMPin],
                            [ALUout, MARHin, SPHin] + ALUDCB,
                            [PCLout, RAMin],
                            [PCLout, MARLin],
                            [PCHout, MARHin],
                            [RAMout, TMPin, CE],
                            [PCLout, MARLin],
                            [PCHout, MARHin],
                            [RAMout, PCHin, CE],
                            [ALUout, PCLin]], name = "CALL addr")

    #RET
    RET = Instruction([[SPLout, MARLin],
                    [SPHout, MARHin],
                    [RAMout, PCLin],
                    [MARLout, TMPin],
                    [ALUout, MARLin] + ALUINR,
                    [MARHout, TMPin],
                    [ALUout, MARHin] + ALUINC,
                    [RAMout, PCHin],
                    [MARLout, TMPin],
                    [ALUout, SPLin] + ALUINR,
                    [MARHout, TMPin],
                    [ALUout, SPHin] + ALUINC], name = "RET")

#Stack and Machine Control
def createStackAndMachineControlInstructions():
    #PUSH rp
    PUSHrp = {}
    for rp in registerPairs:
        PUSHrp[rp] = Instruction([[SPLout, TMPin],
                                [ALUout, MARLin] + ALUDCR,
                                [SPHout, TMPin],
                                [ALUout, MARHin] + ALUDCB,
                                [ro(rp[0], "out"), RAMin],
                                [MARLout, TMPin],
                                [ALUout, MARLin,  SPLin] + ALUDCR,
                                [MARHout, TMPin],
                                [ALUout, MARHin,  SPHin] + ALUDCB,
                                [ro(rp[1], "out"), RAMin]], name = "PUSH {}".format(rp[2]))

    #PUSH PSW
    PUSHPSW = Instruction([[SPLout, TMPin],
                        [ALUout, MARLin] + ALUDCR,
                        [SPHout, TMPin],
                        [ALUout, MARHin] + ALUDCB,
                        [Aout, RAMin],
                        [MARLout, TMPin],
                        [ALUout, MARLin,  SPLin] + ALUDCR,
                        [MARHout, TMPin],
                        [ALUout, MARHin,  SPHin] + ALUDCB,
                        [Fout, RAMin]], name = "PUSH PSW")

    #POP rp
    POPrp = {}
    for rp in registerPairs:
        POPrp[rp] = Instruction([[SPLout, MARLin],
                                [SPHout, MARHin],
                                [RAMout, ro(rp[1], "in")],
                                [MARLout, TMPin],
                                [ALUout, MARLin] + ALUINR,
                                [MARHout, TMPin],
                                [ALUout, MARHin] + ALUINC,
                                [RAMout, ro(rp[0], "in")],
                                [MARLout, TMPin],
                                [ALUout, SPLin] + ALUINR,
                                [MARHout, TMPin],
                                [ALUout, SPHin] + ALUINC],  name = "POP {}".format(rp[2]))

    #POP PSW
    POPPSW = Instruction([[SPLout, MARLin],
                        [SPHout, MARHin],
                        [RAMout, Fin, FinSel],
                        [MARLout, TMPin],
                        [ALUout, MARLin] + ALUINR,
                        [MARHout, TMPin],
                        [ALUout, MARHin] + ALUINC,
                        [RAMout, Ain],
                        [MARLout, TMPin],
                        [ALUout, SPLin] + ALUINR,
                        [MARHout, TMPin],
                        [ALUout, SPHin] + ALUINC], name = "POP PSW")

    #SPAI data
    SPAIdata = Instruction([[PCLout, MARLin],
                            [PCHout, MARHin],
                            [RAMout, Ain, CE],
                            [SPLout, TMPin],
                            [ALUout, SPLin] + ALUADD,
                            [SPHout, TMPin],
                            [ALUout, SPHin] + ALUINC], name = "SPAI data")

    #SPSI data
    SPSIdata = Instruction([[PCLout, MARLin],
                            [PCHout, MARHin],
                            [RAMout, Ain, CE],
                            [SPLout, TMPin],
                            [ALUout, SPLin] + ALUSUB,
                            [SPHout, TMPin],
                            [ALUout, SPHin] + ALUDCB], name = "SPSI data")

    #XTHL
    XTHL = Instruction([[SPLout, MARLin],
                        [SPHout, MARHin],
                        [RAMout, TMPin],
                        [Lout, RAMin],
                        [ALUout, Lin],
                        [MARLout, TMPin],
                        [ALUout, MARLin] + ALUINR,
                        [MARHout, TMPin],
                        [ALUout, MARHin] + ALUINC,
                        [RAMout, TMPin],
                        [Hout, RAMin],
                        [ALUout, Hin]], name = "XRHL")

    #SPHL
    SPHL = Instruction([[Lout, SPLin],
                        [Hout, SPHin]], name = "SPHL")

    #HLT
    HLT = Instruction([[HLTset]], name = "HLT")

    #NOP
    NOP = Instruction([], name = "NOP")

def createInstructions():
    createControlLogicInstructions()
    createDataTransferInstructions()
    createArithmeticInstructions()
    createLogicInstructions()
    createBranchInstructions()
    createStackAndMachineControlInstructions()

def getInstructionsAsString():
    outStr = ""
    for i in range(2**8):
        if i in instructions:
            currInstr = instructions[i]
            if type(currInstr) is dict:
                currInstr = currInstr[0]
            outStr += "{:02X} | {}\n".format(i, currInstr)
    return outStr

def getInfoFromAddr(addr):
    pins = [
        ("IR", 7),
        ("IR", 6),
        ("F", 3),
        ("F", 2),
        ("F", 1),
        ("F", 0),
        ("CNT", 0),
        ("CNT", 1),
        ("IR", 2),
        ("IR", 3),
        ("IR", 5),
        ("IR", 4),
        ("CNT", 2),
        ("IR", 1),
        ("IR", 0),
        ("CNT", 3),
        ("CNT", 4)
    ]
    byteCode, flags, count = 0, 0, 0
    for i in range(len(pins)):
        register, pinNum = pins[i]
        currBit = (addr >> i) & 0x01
        if register == "IR":
            byteCode |= currBit << pinNum
        elif register == "F":
            flags |= currBit << pinNum
        elif register == "CNT":
            count |= currBit << pinNum
        else:
            raise Exception("Unsupported pinout!")
    return byteCode, flags, count

if __name__ == '__main__':
    try:
        command = None
        if len(sys.argv) <= 1 or sys.argv[1].isnumeric():
            command = "eeprom"
        else:
            command = sys.argv[1]
        
        if command == "eeprom":
            eepromIndex = int(sys.argv[1]) if len(sys.argv) > 1 else 5
            fileName = sys.argv[2] if len(sys.argv) > 2 else "ControlLogic{}".format(eepromIndex)

            outFile = open(fileName, "wb")
            createInstructions()
            outArr = []

            for eepromAddr in range(2**17):
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
            outFile.write(bytes(outArr))
            outFile.close()
        elif command == "instrList":
            outFileName = sys.argv[2] if len(sys.argv) > 2 else "instructionList.txt"
            with open(outFileName, "w") as outFile:
                createInstructions()
                outFile.write(getInstructionsAsString())
                outFile.close()

            

    except KeyboardInterrupt:
        print()