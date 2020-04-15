int IO[8] = {47, 48, 49, 35, 34, 33, 32, 31};
int adress[17] = {46, 45, 44, 43, 42, 41, 40, 39, 25, 26, 29, 27, 38, 24, 23, 37, 36};
int WE = 22;
int OE = 28;
int CE = 30;
int eeprom = 0;

void declarePins() {
  for (int i = 0; i < 8; i++) {
    pinMode(IO[i], OUTPUT);
  }
  for(int i = 0; i < 17; i++) {
    pinMode(adress[i], OUTPUT);
  }
  digitalWrite(OE, HIGH);
  digitalWrite(WE, HIGH);
  digitalWrite(CE, HIGH);
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



void setup() {
  declarePins();
  Serial.begin(9600);
  delay(10);

  // Program data bytes


  // Read and print out the contents of the EERPROM
  Serial.println("Reading EEPROM");
  printContents();
    

}

void loop() {
  // put your main code here, to run repeatedly:

}
