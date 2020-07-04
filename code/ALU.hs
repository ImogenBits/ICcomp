import Data.Bits
import qualified Data.Map as Map
import System.Environment
import Data.Maybe
import System.IO
import qualified Data.ByteString as BS


main :: IO ()
main = do
    args <- getArgs
    let epr = parseArgs args
    handle <- openBinaryFile ("EEPROMfiles/Alu" ++ show epr) WriteMode
    let res = BS.pack $ map (fromIntegral . valueAtAddr epr) [0..2^17]
    BS.hPut handle res

parseArgs :: [String] -> Eeprom
parseArgs ["MSB"] = MSB
parseArgs ["LSB"] = LSB
parseArgs _ = MSB


type InstrName = String
type InstrCode = Int
type Address = Int
type DQVal = Int
type AVal = Int
type TmpVal = Int
type FlagVal = Int
type AluFunc = Regs -> (Maybe DQVal, Maybe FlagVal)


data Regs = Regs
    { aReg :: AVal
    , tReg :: TmpVal
    , fReg :: FlagVal
    } deriving (Show)


data Eeprom = MSB | LSB deriving (Show)


data Instr = Instr
    { instrName :: InstrName
    , instrCode :: InstrCode
    , msbFunc :: AluFunc
    , lsbFunc :: AluFunc
    }

mkInstr :: InstrName -> InstrCode -> (Regs-> DQVal) -> Instr
mkInstr n c f = Instr n c (toAluFunc MSB f) (toAluFunc LSB f)

instrFunc :: Eeprom -> Instr -> AluFunc
instrFunc MSB = msbFunc
instrFunc LSB = lsbFunc

instance Show Instr where
    show (Instr n c f1 f2) = show c ++ ": " ++ n


cFlag = 0
pFlag = 1
zFlag = 2
sFlag = 3


defaultInstr = Instr "PASS" 0 lam lam
    where
        lam (Regs a t f) = (Just t, Just 0)
instrList =
    [ defaultInstr
    , mkInstr "ADD"  1 (\(Regs a t f) -> a + t) 
    , mkInstr "ADC"  2 (\(Regs a t f) -> a + t + extractBit f cFlag) 
    , mkInstr "SUB"  3 (\(Regs a t f) -> a - t) 
    , mkInstr "SBB"  4 (\(Regs a t f) -> a - t - extractBit f cFlag) 
    , mkInstr "INR"  5 (\(Regs a t f) -> t + 1) 
    , mkInstr "INC"  6 (\(Regs a t f) -> t + extractBit f cFlag) 
    , mkInstr "DCR"  7 (\(Regs a t f) -> t - 1) 
    , mkInstr "DCB"  8 (\(Regs a t f) -> t - extractBit f cFlag) 
    , mkInstr "AND"  9 (\(Regs a t f) -> a .&. t) 
    , mkInstr "OR"  10 (\(Regs a t f) -> a .|. t) 
    , mkInstr "XOR" 11 (\(Regs a t f) -> a `xor` t) 
    , mkInstr "CMA" 12 (\(Regs a t f) -> complement a) 
    , Instr   "CMC" 13 (\(Regs a t f) -> (Nothing, Just (complementBit f cFlag))) (\regs -> (Nothing, Just (fReg regs)))
    , Instr   "STC" 14 (\(Regs a t f) -> (Nothing, Just (setBit f cFlag))) (\regs -> (Nothing, Just (fReg regs)))
    , mkInstr "RRC" 15 (\(Regs a t f) -> rrc a f) 
    , mkInstr "RAL" 16 (\(Regs a t f) -> ral a f) 
    , mkInstr "RAR" 17 (\(Regs a t f) -> rar a f) 
    ]
instrMap = Map.fromList $ map (\i -> (instrCode i, i)) instrList

rrc :: AVal -> FlagVal -> AVal
rrc a f = a -- !Need to actually implement this

ral :: AVal -> FlagVal -> AVal
ral a f = shift a 1 .|. extractBit f cFlag -- ! Pretty sure this is wrong

rar :: AVal -> FlagVal -> AVal
rar a f = a -- !Need to actually implement this


toAluFunc :: Eeprom -> (Regs -> DQVal) -> AluFunc
toAluFunc epr func = newFunc
    where
        newFunc regs = (Just dq, Just $ flags epr dq (fReg regs))
            where
                dq = func regs

flags :: Eeprom -> DQVal -> FlagVal -> FlagVal
flags LSB d f =
    shiftExtract res 4 sFlag .|.
    if res == 0 then bit zFlag else 0 .|.
    if popCount res `mod` 2 == 0 then bit pFlag else 0 .|.
    shiftExtract d 5 cFlag
        where
            res = d .&. 0xF
flags MSB d f =
    shiftExtract res 4 sFlag .|.
    if res == 0 && testBit f zFlag then bit zFlag else 0 .|.
    if popCount res `mod` 2 == 0 && not (testBit f pFlag) then bit pFlag else 0 .|.
    shiftExtract d 5 cFlag
        where
            res = d .&. 0xF

extractBit :: Bits a => a -> Int -> Int
extractBit = (.) fromEnum . testBit

shiftExtract :: Bits a => a -> Int -> Int-> Int
shiftExtract a i =  shift (extractBit a i)

instrFuncFromCode :: Eeprom -> InstrCode -> AluFunc
instrFuncFromCode epr c =
    case Map.lookup c instrMap of
        Just instr -> instrFunc epr instr
        Nothing -> instrFunc epr defaultInstr

valueAtAddr :: Eeprom -> Address -> Int
valueAtAddr epr adr = applyPinout epr outPins $ combineRegs $ dqFromAddr epr adr
    where
        dqFromAddr epr addr = instrFuncFromCode epr c reg
            where
                reg = regFromAddr epr addr
                c = codeFromAddr epr addr
        combineRegs = collapse (fromMaybe 0)
            where
                collapse f (a, b) =
                    f a .|. shift (f b) 4


-- in "reverse" order, [0, 1, 2, 3,...]
data Pinout = Pinout
    { aPins :: [Int]
    , tmpPins :: [Int]
    , codePins :: [Int]
    , flagPins :: [Int]
    , outPins :: [Int]
    }

msbPinout = Pinout
    { aPins = [9, 8, 13, 14]
    , tmpPins = [2, 3, 4, 5]
    , codePins = [6, 7, 12, 15, 16]
    , flagPins = [1, 0, 10, 11]
    , outPins = [2, 1, 0, 7, 3, 4, 6, 5]
    }
lsbPinout = Pinout
    { aPins = [14, 13, 8, 9]
    , tmpPins = [6, 7, 12, 15]
    , codePins = [0, 1, 10, 11]
    , flagPins = [16, 5, 4, 3, 2]
    , outPins = [2, 1, 0, 3, 4, 5, 6, 7]
    }

applyPinout :: Eeprom -> (Pinout -> [Int]) -> Int -> Int
applyPinout epr pins addr =
    foldl (.|.) 0 $ zipWith f lst [0..]
        where
            f = shiftExtract addr
            lst = pins $ pinout epr

pinout :: Eeprom -> Pinout
pinout MSB = msbPinout
pinout LSB = lsbPinout


regFromAddr :: Eeprom -> Address -> Regs
regFromAddr epr addr = Regs a tmp flag
    where
        a = applyPinout epr aPins addr
        tmp = applyPinout epr tmpPins addr
        flag = applyPinout epr flagPins addr

codeFromAddr :: Eeprom -> Address -> Int
codeFromAddr epr = applyPinout epr codePins