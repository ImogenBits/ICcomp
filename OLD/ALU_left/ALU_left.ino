#include <math.h>
//           D0, D1, D2...            ...D7
int IO[8] = {47, 48, 49, 35, 34, 33, 32, 31};
//                A0, A1, A2...                                       ...A14, A15, A16
int adress[17] = {46, 45, 44, 43, 42, 41, 40, 39, 25, 26, 29, 27, 38, 24, 23, 37, 36};
int WE = 22;
int OE = 28;
int CE = 30;

//            Pin0, Pin1, Pin2, Pin3, Pin4
long pinoutA[4] = {9, 8, 13, 14};
long pinoutTMP[4] = {2, 3, 4, 5};
long pinoutFin[4] = {1, 0, 10, 11};
long pinoutControl[5] = {6, 7, 12, 15, 16};

long pinoutBUS[4] = {2, 1, 0, 7};
long pinoutFout[4] = {3, 4, 6, 5};


int parity_even(unsigned x) {
    int parity = 0;
    while(x != 0) {
        parity ^= x;
        x >>= 1;
    }
    return !(parity & 0x1);
}

void declarePins() {
  for (int i = 0; i < 8; i++) {
    pinMode(IO[i], OUTPUT);
  }
  for(int i = 0; i < 17; i++) {
    pinMode(adress[i], OUTPUT);
  }
  pinMode(WE, OUTPUT);
  pinMode(OE, OUTPUT);
  pinMode(CE, OUTPUT);
  digitalWrite(OE, HIGH);
  digitalWrite(WE, HIGH);
  digitalWrite(CE, LOW);
  

}

byte readEEPROM(long adr) {
  digitalWrite(WE, HIGH);
  for(int i = 0; i < 17; i++) {
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
  delayMicroseconds(1);
  byte value = 0;
  for (int i = 7; i >= 0; i--) {
    value = (value << 1) + digitalRead(IO[i]);
  }
  digitalWrite(OE, HIGH);
  for (int i = 0; i < 8; i++) {
    pinMode(IO[i], OUTPUT);
  }
  return value;
}

void printContents() {
  for (int page = 0; page < 10; page++) {
    for (int base = 0; base < 128; base += 32) {
      byte data[32];
      for (int offset = 0; offset < 32; offset += 1) {
        data[offset] = readEEPROM(base + offset + (page * 128));
        delayMicroseconds(1);
      }

      char buf[120];
      sprintf(buf, "%03x:  %02x %02x %02x %02x %02x %02x %02x %02x  %02x %02x %02x %02x %02x %02x %02x %02x  %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
              base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
              data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15],
              data[16], data[17], data[18], data[19], data[20], data[21], data[22], data[23], data[24], data[25], data[26], data[27], data[28], data[29], data[30], data[31]);
      
      Serial.println(buf);
    }
    Serial.println("");
  }
}

void writePage(long startAdr, byte value[128]) {
  long adr = startAdr;
  for(int i = 0; i < 17; i++) {
    digitalWrite(adress[i], (adr & 1));
    adr = adr >> 1;
  }
  
  for (int i = 0; i < 128; i ++) {
    long adr = startAdr + i;
    for(int j = 0; j < 7; j++) {
      digitalWrite(adress[j], (adr & 1));
      adr = adr >> 1;
    }

    byte currValue = value[i];
    for(int j = 0; j < 8; j++) {
      if(currValue % 2 == 0) {
        digitalWrite(IO[j], LOW);
      } else {
        digitalWrite(IO[j], HIGH);
      }
      currValue = currValue >> 1;
    }
    digitalWrite(WE, LOW);
    delayMicroseconds(5);
    digitalWrite(WE, HIGH);
    delayMicroseconds(5);
  }
  delay(11);
}


unsigned char calcDataFromAddr(long addr){
  unsigned char A = 0, TMP = 0, Fin = 0, Control = 0;
  unsigned char BUS = 0, Fout = 0;
  unsigned char result = 0;
  bool SF = false, ZF = false, PF = false, CF = false;
  
  for(int j = 0; j < 4; j++){
    if(addr & ((long) 0x01 << (pinoutA[j]))){
      A += ((long) 0x01 << (j));
    }
  }
  for(int j = 0; j < 4; j++){
    if(addr & ((long) 0x01 << (pinoutTMP[j]))){
      TMP += ((long) 0x01 << (j));
    }
  }
  for(int j = 0; j < 4; j++){
    if(addr & ((long) 0x01 << (pinoutFin[j]))){
      Fin += ((long) 0x01 << (j));
    }
  }
  for(int j = 0; j < 5; j++){
    if(addr & ((long) 0x01 << (pinoutControl[j]))){
      Control += ((long) 0x01 << (j));
    }
  }

/*
  Serial.println(A, HEX);
  Serial.println(TMP, HEX);
  Serial.println(Fin, HEX);
  Serial.println(Control, HEX);*/
  
  
  switch(Control){
    case 1:
      result = A + TMP + (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 2:
      result = A + TMP + (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 3:
      result = A - TMP - (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 4:
      result = A - TMP - (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 5:
      result = TMP + (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 6:
      result = TMP + (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 7:
      result = TMP - (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 8:
      result = TMP - (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 9:
      result = A & TMP;
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 10:
      result = A | TMP;
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 11:
      result = A ^ TMP;
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 12:
      result = ~A;
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 13:
      result = 0;
      SF = Fin & 0x08;
      ZF = Fin & 0x04;
      PF = Fin & 0x02;
      CF = !(Fin & 0x01);
      break;
    case 14:
      result = 0;
      SF = Fin & 0x08;
      ZF = Fin & 0x04;
      PF = Fin & 0x02;
      CF = Fin & 0x01;
      break;
    case 15:
      result = (A >> 1) + ((Fin & 0x01) ? 0x08 : 0x00);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = Fin & 0x01;
      break;
    case 16:
      result = (A << 1) + (Fin & 0x01);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = result & 0x10;
      break;
    case 17:
      result = (A >> 1) + ((Fin & 0x04) ? 0x08 : 0x00);
      SF = result & 0x08;
      ZF = ((result & 0x0f) == 0) && (Fin & 0x04);
      PF = !parity_even(result & 0x0f) == !(Fin & 0x02);
      CF = Fin & 0x01;
      break;
    default:
      result = 0xff;
      SF = true;
      ZF = true;
      PF = true;
      CF = true;
  }


  //Calculates Fout and BUS
  Fout |= SF;
  Fout <<= 1;
  Fout |= ZF;
  Fout <<= 1;
  Fout |= PF;
  Fout <<= 1;
  Fout |= CF;
  for(int j = 0; j < 4; j++){
    if(Fout & (0x01 << j)){
      BUS += (0x01 << pinoutFout[j]);
    }
  }

  for(int j = 0; j < 4; j++){
    if(result & (0x01 << j)){
      BUS += (0x01 << pinoutBUS[j]);
    }
  }

/*
  char buf[30];
  sprintf(buf, "Fout: %02x  F: %01x%01x%01x%01x result: %02x", Fout, SF, ZF, PF, CF, result);
  Serial.println(buf);*/
  
  return BUS;
}


void setup() {
  declarePins();
  Serial.begin(9600);
  delay(10);
  Serial.println("Start");

/*
  long addr = 0x0664c;
  Serial.println(addr, HEX);
  Serial.println(calcDataFromAddr(addr), HEX);
  return;*/

  //write data
  long numPages = 3;
  unsigned char dataArray[128];
  
  for (long i = 0; i < numPages; i++) {
    Serial.println(i);
    unsigned char dataArray[128];
    for (long j = 0; j < 128; j++) {
      dataArray[j] = 0xBB;//calcDataFromAddr((long) (i * 128 + j));
    }
    writePage(i * 128, dataArray);
  }

  delay(1000);
  // Read and print out the contents of the EERPROM
  Serial.println("Reading EEPROM");
  printContents();
  
}

void loop() {
  // put your main code here, to run repeatedly:

}
