int IO[8] = {32, 33, 34, 46, 45, 44, 43, 42};
int adress[15] = {31, 30, 29, 28, 27, 26, 25, 24, 37, 38, 41, 39, 23, 36, 22};
int WE = 35;
int OE = 40;

// 4-bit DEC decoder for common cathode 7-segment display
byte digits[] = { 0x77, 0x41, 0x6E, 0x6B, 0x59, 0x3B, 0x3F, 0x61, 0x7F, 0x7B};

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
  for (int base = 0; base <= 1023; base += 16) {
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




void setup() {
  declarePins();
  Serial.begin(9600);
  delay(10);

  // Erase entire EEPROM
 /* Serial.print("Erasing EEPROM");
  for (int address = 0; address <= 2047; address += 1) {
    writeEEPROM(address, 0xff);

    if (address % 64 == 0) {
      Serial.print(".");
    }
  }
  Serial.println(" done");
*/

  // Program data bytes
  Serial.print("Programming EEPROM");
  Serial.println("1");
  for (int address = 0; address < 256; address++) {
    writeEEPROM(address, digits[address % 10]);
  }
  Serial.println("10");
  for (int value = 0; value < 256; value++) {
    writeEEPROM(value + 256, digits[(value / 10) % 10]);
  }
  Serial.println("100");
  for (int value = 0; value < 256; value++) {
    writeEEPROM(value + 512, digits[(value / 100) % 10]);
  }
  Serial.println("1000");
  for (int value = 0; value < 256; value++) {
    writeEEPROM(value + 768, 0);
  }

  Serial.println("-1");
  for (int value = -128; value < 128; value++) {
    writeEEPROM(((byte) value) + 1024, digits[abs(value) % 10]);
  }
  Serial.println("-10");
  for (int value = -128; value < 128; value++) {
    writeEEPROM(((byte) value) + 1280, digits[abs(value / 10) % 10]);
  }
  Serial.println("-100");
  for (int value = -128; value < 128; value++) {
    writeEEPROM(((byte) value) + 1536, digits[abs(value / 100) % 10]);
  }
  Serial.println("-1000");
  for (int value = -128; value < 128; value++) {
    if (value < 0) {
      writeEEPROM(((byte) value) + 1792, 0x08);
    }
    else {
      writeEEPROM(((byte) value) + 1792, 0x00);
    }
  }
  
  Serial.println(" done");


  // Read and print out the contents of the EERPROM
  Serial.println("Reading EEPROM");
  printContents();
    

}

void loop() {
  // put your main code here, to run repeatedly:

}
