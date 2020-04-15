#include "SerialTransfer.h"
SerialTransfer myTransfer;

typedef struct {
	uint32_t instruction;
	uint32_t pageNum;
	uint32_t len;
	byte data[128];
} Data;

//Data pin mapping
//					D0, D1, D2...            ...D7
static int DQ[8] = {47, 48, 49, 35, 34, 33, 32, 31};
//Address pin mapping
//					A0, A1, A2...                                       ...A14, A15, A16
static int A[17] = {46, 45, 44, 43, 42, 41, 40, 39, 25, 26, 29, 27, 38, 24, 23, 37, 36};
static int WE = 22;
static int OE = 28;
static int CE = 30;

//           D0, D1, D2...            ...D7
int IO[8] = {47, 48, 49, 35, 34, 33, 32, 31};
//                A0, A1, A2...                                       ...A14, A15, A16
int adress[17] = {46, 45, 44, 43, 42, 41, 40, 39, 25, 26, 29, 27, 38, 24, 23, 37, 36};

void declarePins() {
  for (int i = 0; i < 8; i++) {
    pinMode(DQ[i], OUTPUT);
  }
  for(int i = 0; i < 17; i++) {
    pinMode(A[i], OUTPUT);
  }
  pinMode(WE, OUTPUT);
  pinMode(OE, OUTPUT);
  pinMode(CE, OUTPUT);
  digitalWrite(OE, HIGH);
  digitalWrite(WE, HIGH);
  digitalWrite(CE, LOW);
  

}

byte readFromAddress(long adr) {
  digitalWrite(WE, HIGH);
  for(int i = 0; i < 17; i++) {
    if(adr % 2 == 0) {
      digitalWrite(A[i], LOW);
    }
    else {
      digitalWrite(A[i], HIGH);
    }
    adr = adr >> 1;
  }
  for (int i = 0; i < 8; i++) {
    digitalWrite(DQ[i], LOW);
    pinMode(DQ[i], INPUT);
  }
  digitalWrite(OE, LOW);
  delayMicroseconds(1);
  byte value = 0;
  for (int i = 7; i >= 0; i--) {
    value = (value << 1) + digitalRead(DQ[i]);
  }
  digitalWrite(OE, HIGH);
  for (int i = 0; i < 8; i++) {
    pinMode(DQ[i], OUTPUT);
  }
  return value;
}

void writeAddress(long address, byte value) {
	for(int j = 0; j < 7; j++) {
		digitalWrite(A[j], address & 1);
		address >>= 1;
	}

	for(int j = 0; j < 8; j++) {
		digitalWrite(DQ[j], value & 1);
		value >>= 1;
	}

	digitalWrite(WE, LOW);
	delayMicroseconds(5);
	digitalWrite(WE, HIGH);
	delayMicroseconds(5);
}


/*void writePage(uint32_t pageNum, byte values[128]) {
	long startAdr = pageNum * 128;
	for (int i = 0; i < 128; i ++) {
		long adr = startAdr + i;
		for(int j = 0; j < 7; j++) {
			digitalWrite(A[j], adr & 1);
			adr = adr >> 1;
		}

		byte currValue = values[i];
		for(int j = 0; j < 8; j++) {
			digitalWrite(DQ[j], currValue & 1);
			currValue = currValue >> 1;
		}
		//delay(1000);
		digitalWrite(WE, LOW);
		//delay(1000);
		delayMicroseconds(5);
		digitalWrite(WE, HIGH);
		delayMicroseconds(5);
	}
	delay(11);
}*/

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

void writePage(Data pageData) {
	byte dataArray[128];
	for (int i = 0; i < pageData.len; i++) {
		dataArray[i] = pageData.data[i];
	}
	for (int i = pageData.len; i < 128; i++) {
		dataArray[i] = 0x00;
	}
	writePage(pageData.pageNum * 128, dataArray);
}

void readPage(Data &data) {
	data.len = 128;
	for (long i = 0; i < data.len; i++) {
		data.data[i] = readFromAddress((long) (data.pageNum * 128) + i);
	}
}

void disableDataProtect() {
	writeAddress(0x5555, 0xAA);
	writeAddress(0x2AAA, 0x55);
	writeAddress(0x5555, 0x80);
	writeAddress(0x5555, 0xAA);
	writeAddress(0x2AAA, 0x55);
	writeAddress(0x5555, 0x20);
	delay(100);
}

void setup() {
	declarePins();
	Serial.begin(9600);
	delay(10);
}

void loop() {
}