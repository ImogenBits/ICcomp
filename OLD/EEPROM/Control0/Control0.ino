t IO[8] = {32, 33, 34, 46, 45, 44, 43, 42};
int adress[15] = {31, 30, 29, 28, 27, 26, 25, 24, 37, 38, 41, 39, 23, 36, 22};
int WE = 35;
int OE = 40;
#define numEEPROM 2
byte fetch[numEEPROM][2] = {{0x04, 0x28}, {0x02, 0x01}}; //[EEPROM][Step]
int eeprom = 0;

void declarePins() {
  for (int i = 0; i < 8; i++) {
    pinMode(IO[i], OUTPUT);
  }
  for(int i = 0; i < 15; i++) {
    pinMode(adress[i], OUTPUT);
  }
  digitalWrite(OE, HIGH);
  digitalWrite(WE, HIGH);
  pinMode(WE, OUTPUT);
  pinMode(OE, OUTPUT);
  

}

void writeEEPROM(unsigned int adr, byte value) {
  for(int i = 0; i < 15; i++) {
    digitalWrite(adress[i], (adr & 1));
    adr = adr >> 1;
  }
  for(int i = 0; i < 8; i++) {
    if(value % 2 == 0) {
      digitalWrite(IO[i], LOW);
    }
    else {
      digitalWrite(IO[i], HIGH);
    }
    value = value >> 1;
  }
  
  digitalWrite(WE, LOW);
  delayMicroseconds(10);
  digitalWrite(WE, HIGH);
  delay(10);
  
}

byte readEEPROM(unsigned int adr) {
  for(int i = 0; i < 15; i++) {
    if(adr % 2 == 0) {
      digitalWrite(adress[i], LOW);
    }
    else {
      digitalWrite(adress[i], HIGH);
    }
    adr = adr >> 1;
  }
  for (int i = 0; i < 8; i++) {
    digitalWrite(IO[i], LOW);
    pinMode(IO[i], INPUT);
  }
  digitalWrite(OE, LOW);
  byte value = 0;
  for (int i = 7; i >= 0; i--) {
    value = (value << 1) + digitalRead(IO[i]);
  }
  digitalWrite(OE, HIGH);
  for (int i = 0; i < 8; i++) {
    pinMode(IO[i], INPUT);
  }
  return value;
}

void printContents() {
  for (int base = 0; base <= 256; base += 16) {
    byte data[16];
    for (int offset = 0; offset <= 15; offset += 1) {
      data[offset] = readEEPROM(base + offset);
    }

    char buf[80];
    sprintf(buf, "%03x:  %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
            base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
            data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15]);

    Serial.println(buf);
  }
}

void saveInstruction(int index, byte data[numEEPROM][3]) {
  writeEEPROM(index * 8, fetch[eeprom][0]);
  writeEEPROM((index * 8) + 1, fetch[eeprom][1]);
  for (int i = 0; i < 3; i++) {
    writeEEPROM((index * 8) + 2 + i, data[eeprom][i]);
  }
}




void setup() {
  declarePins();
  Serial.begin(9600);
  delay(10);

  // Erase entire EEPROM
  Serial.print("Erasing EEPROM");
  for (int address = 0; address <= 271; address += 1) {
    writeEEPROM(address, 0x00);

    if (address % 64 == 0) {
      Serial.print(".");
    }
  }
  Serial.println(" done");


  // Program data bytes


  
  byte instruct[16][numEEPROM][3] = {
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //LDA
    { {0x14, 0x48, 0x00},
      {0x00, 0x00, 0x00} },
    //ADD
    { {0x14, 0x08, 0x40},
      {0x00, 0x20, 0x08} },
    //SUB
    { {0x14, 0x08, 0x40},
      {0x00, 0x20, 0x18} },
    //SVA
    { {0x14, 0x82, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //
    { {0x00, 0x00, 0x00},
      {0x00, 0x00, 0x00} },
    //JMP
    { {0x10, 0x00, 0x00},
      {0x04, 0x00, 0x00} },
    //OUT
    { {0x80, 0x00, 0x00},
      {0x40, 0x00, 0x00} },
    //HLT
    { {0x01, 0x00, 0x00},
      {0x00, 0x00, 0x00} } 
  };
  
  for (int i = 0; i < 16; i++) {
    saveInstruction(i, instruct[i]);
  }
  

  // Read and print out the contents of the EERPROM
  Serial.println("Reading EEPROM");
  printContents();
    

}

void loop() {
  // put your main code here, to run repeatedly:

}
