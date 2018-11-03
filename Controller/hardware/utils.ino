void testReset()
{
	for (int i = 0; i < 1000; i++)
	{
		Serial.println(i);
		delay(100);
	}

}

void testKeypad()
{
	char key = keymain.getKey();

	if (key != NO_KEY) {
		Serial.println(key);
	}
}

void testMeters()
{
	int thrRead;
	thrRead = analogRead(THROTTLE) / 4;
	Serial.println(thrRead);
	analogWrite(CHARGE, thrRead);
	analogWrite(MONO, thrRead);
	analogWrite(SPEED, thrRead);
	analogWrite(ALT, thrRead);
}

void testJoy()
{
	int Joy1X, Joy1Y, Joy1Z, Joy2X, Joy2Y;
	Joy1X = analogRead(JOY1X);
	Joy1Y = analogRead(JOY1Y);
	Joy1Z = analogRead(JOY1Z);
	Joy2X = analogRead(JOY2X);
	Joy2Y = analogRead(JOY2Y);
	Serial.print("J1X ");
	Serial.print(Joy1X);
	Serial.print(" J1Y ");
	Serial.print(Joy1Y);
	Serial.print(" J1Z ");
	Serial.print(Joy1Z);
	Serial.print(" J1Btn ");
	Serial.println(digitalRead(JOY1BTN));
	Serial.print("J2X ");
	Serial.print(Joy2X);
	Serial.print(" J2Y ");
	Serial.print(Joy2Y);
	Serial.print(" J2F ");
	Serial.print(digitalRead(JOY2FWD));
	Serial.print(" J2B ");
	Serial.print(digitalRead(JOY2BCK));
	Serial.print(" J2Btn ");
	Serial.println(digitalRead(JOY2BTN));


	Serial.println(analogRead(THROTTLE));
	delay(1000);
}

void testLCD()
{

	readTime();
	lcd2.setCursor(0, 2);
	lcd2.print("Time: ");
	lcd2.print(hour);
	lcd2.print(":");
	if (minute < 10) lcd2.print("0");
	lcd2.print(minute);
	lcd2.print(":");
	if (second < 10) lcd2.print("0");
	lcd2.print(second);
	if ((hour > 21) && (minute > 44) || (hour > 22)) {
		lcd2.setCursor(5, 3);
		lcd2.print("Bedtime");
	}
}

void readTime()
{
	Wire.beginTransmission(RTCADR);
	Wire.write(0); // set DS3231 register pointer to 00h
	Wire.endTransmission();
	Wire.requestFrom(RTCADR, 3);
	// request three bytes of data from DS3231 starting from register 00h
	second = bcdToDec(Wire.read() & 0x7f);
	minute = bcdToDec(Wire.read());
	hour = bcdToDec(Wire.read() & 0x3f);
	/*Serial.print(hour);
	Serial.print(':');
	Serial.print(minute);
	Serial.print(':');
	Serial.println(second);
	Serial.println();*/
	//dayOfWeek = bcdToDec(Wire.read());
	//dayOfMonth = bcdToDec(Wire.read());
	//month = bcdToDec(Wire.read());
	//year = bcdToDec(Wire.read());
}

void killLC()
{
	for (int i = 0; i < NUMLC; i++)
	{
		for (int j = 0; j < 8; j++)
		{
			lc.setChar(i, j, '.', false);
			delay(50);
		}
	}
}

void testLC()
{
	for (int ad = 0; ad < NUMLC; ad++)
	{
		for (int val = 0; val < 10; val++)
		{
			for (int pos = 0; pos < 8; pos++)
			{
				lc.setDigit(ad, pos, val, false);
				delay(50);
				Serial.println(val);
			}
			delay(500);
		}
	}
}

void testTrim()
{
	int trYaw = 0, trPitch = 0, trRoll = 0, trEng = 0;

	static int trYO, trPO, trRO, trEO; //previous values of read variables
	static unsigned long timer; // time when display started
	bool change;

	trYaw = analogRead(TRIMYAW);
	trPitch = analogRead(TRIMPITCH);
	trRoll = analogRead(TRIMROLL);
	trEng = analogRead(TRIMENGINE);

	if ((trYaw < trYO - 7) || (trYaw > trYO + 7))
	{
		trimY = ((trYaw + 15) / -5) + 100;
		LCNum(2, trimY);
		trYO = trYaw;
		timer = millis();
	}

	if ((trPitch < trPO - 7) || (trPitch > trPO + 7))
	{
		trimP = ((trPitch + 15) / -5) + 100;
		LCNum(2, trimP);
		trPO = trPitch;
		timer = millis();
	}

	if ((trRoll < trRO - 7) || (trRoll > trRO + 7))
	{
		trimR = ((trRoll + 20) / -5) + 100;
		LCNum(2, trimR);
		trRO = trRoll;
		timer = millis();
	}

	if ((trEng < trEO - 10) || (trEng > trEO + 10))
	{
		trimE = constrain(map(trEng, 1010, 10, 0, 100), 0, 100);
		LCNum(2, trimE);
		trEO = trEng;
		timer = millis();
	}



	if (millis() - timer > 1000)
	{
		lc.clearDisplay(2);
	}

	/*Serial.print("Yaw: ");
	Serial.print(trYaw);
	Serial.print("  Pitch: ");
	Serial.print(trPitch);
	Serial.print("  Roll: ");
	Serial.print(trRoll);
	Serial.print("  Engine: ");
	Serial.println(trEng);
	*/

}

void testPin(int p)
{
	digitalWrite(p, HIGH);
	Serial.println('h');
	delay(2000);

	digitalWrite(p, LOW);
	Serial.println('l');
	delay(2000);

}

void testSPI()
{
	bool change = false;
	SPI.beginTransaction(SPISettings(6000000, MSBFIRST, SPI_MODE2));


	//Serial.println('r');
	delay(1);
	digitalWrite(SS1, HIGH);

	for (int i = 0; i < NUMIC1; i++)
	{
		digitalWrite(CLKI, LOW);
		dataIn[i] = SPI.transfer(0x00);
		digitalWrite(CLKI, HIGH);

	}
	digitalWrite(SS1, LOW);
	SPI.endTransaction();

	SPI.beginTransaction(SPISettings(3000000, MSBFIRST, SPI_MODE2));


	digitalWrite(SS2, LOW);
	delay(1);
	for (int i = NUMIC1; i < NUMIC1 + NUMIC2; i++)
	{
		dataIn[i] = shiftIn(DTA, CLK, MSBFIRST);
	}
	digitalWrite(SS2, HIGH);
	SPI.endTransaction();

	for (int i = 0; i < NUMIC1 + NUMIC2; i++)
	{
		if (dataIn[i] != dataOld[i])
		{
			change = true;
		}
	}
	if (change == true)
	{
		//printAllBytes();
	}

	for (int i = 0; i < NUMIC1 + NUMIC2; i++)
	{
		dataOld[i] = dataIn[i];
	}
	delay(11);
}

void printByte(byte data)
{
	char bit[8];
	for (int i = 7; i > -1; i--)
	{
		bit[i] = bitRead(data, i);
		Serial.print(bitRead(data, i));
		if (i == 4) Serial.print('|');
	}
}

void printAllBytes()
{
	for (int i = 0; i < NUMIC1 + NUMIC2; i++)
	{
		printByte(dataIn[i]);
		Serial.print(" | | ");
	}
	Serial.println();

}

void toggles()
{
	/*Picks out the relevant toggle of the dataIn bytes and change LED accordingly*/
	bool statusRead;
	//AG 1
	statusRead = (dataIn[1] & B00010000);
	statusLED(19, statusRead);

	//AG 2
	statusRead = (dataIn[1] & B00100000);
	statusLED(18, statusRead);

	//AG 3
	statusRead = (dataIn[2] & B00010000);
	statusLED(17, statusRead);

	//AG 4
	statusRead = (dataIn[2] & B00100000);
	statusLED(16, statusRead);

	//AG 5
	statusRead = (dataIn[2] & B01000000);
	statusLED(15, statusRead);

	//AG 6
	statusRead = (dataIn[2] & B10000000);
	statusLED(14, statusRead);

	//AG 7
	statusRead = (dataIn[2] & B00000001);
	statusLED(13, statusRead);

	//AG 8
	statusRead = (dataIn[2] & B00000010);
	statusLED(12, statusRead);

	//AG 9
	statusRead = (dataIn[2] & B00000100);
	statusLED(11, statusRead);

	//AG 10
	statusRead = (dataIn[2] & B00001000);
	statusLED(10, statusRead);

	//SAS
	statusRead = (dataIn[1] & B01000000);
	statusLED(0, statusRead);

	//RCS
	statusRead = (dataIn[1] & B10000000);
	statusLED(1, statusRead);

	//Gear
	statusRead = (dataIn[3] & B10000000);
	statusLED(2, statusRead);

	//Brakes
	statusRead = (dataIn[3] & B01000000);
	statusLED(3, statusRead);

	//Engine mode
	statusRead = (dataIn[3] & B00100000);
	statusLED(4, statusRead);

	//Lights
	statusRead = (dataIn[3] & B00010000);
	statusLED(5, statusRead);

	//Solar panels
	statusRead = (dataIn[3] & B00001000);
	statusLED(6, statusRead);

	//Radiators
	statusRead = (dataIn[3] & B00000100);
	statusLED(7, statusRead);

	//Cargo bays
	statusRead = (dataIn[3] & B00000010);
	statusLED(8, statusRead);

	//Reserve batteries
	statusRead = (dataIn[3] & B00000001);
	statusLED(9, statusRead);


	FastLED.show();
}

void rotSelectors()
{
	/*Detects status of rotary selectors for SAS mode, cam mode and panel mode*/

	word SASMode = 0, camMode = 0, panelMode = 0;

	SASMode = dataIn[1] >> 4;
	camMode = dataIn[0] & B00000111;
	panelMode = (dataIn[0] >> 3) & B00000111;

	Serial.print(SASMode);
	Serial.print(' ');
	Serial.print(camMode);
	Serial.print(' ');
	Serial.print(panelMode);
	Serial.println();
}

void testLED()
{
	for (int i = 0; i < NUMLEDS; i++)
	{
		singleLED(i);
		delay(100);
	}

}

void singleLED(int lednum)
{
	//Serial.println(lednum);
	for (int i = 0; i < NUMLEDS; i++)
	{
		if (i != lednum) leds[i] = CRGB::Black;
	}
	leds[lednum] = CRGB::Green;
	FastLED.show();
}

void statusLED(int lednum, bool status)
{
	if (status) leds[lednum] = 0x001100;
	else leds[lednum] = 0x110000;
}

void chkKeypad() {

	char key = keymain.getKey();
	if (key != NO_KEY) {
		if ((key == '#')) {
			cmdStr[cmdStrIndex - 1] = '\0';
			cmdStrIndex--;
			lcd2.setCursor(cmdStrIndex, 3);
			lcd2.print(" ");

		}
		if ((key != '#')) {
			cmdStr[cmdStrIndex] = key;
			cmdStrIndex++;
			Serial.println(key);
		}

		if (cmdStrIndex > 18) cmdStrIndex = 18;

	}
	lcd2.setCursor(0, 3);
	lcd2.print(cmdStr);
	if ((cmdStr[cmdStrIndex - 1] == '*') && (cmdStr[cmdStrIndex - 2] == '*')) {
		execCmd();
		lcd2.clear();
		for (int i = 0; i <= 18; i++) {
			cmdStr[i] = '\0';
		}
		cmdStrIndex = 0;
	}
}

void execCmd() {
	char action[2];
	char value[18];
	char tmpval[8];
	int actionN;

	if (cmdStr[2] == '*') {                      //if the string is of format xx*, int action = xx
		for (int i = 0; i < 2; i++) {
			action[i] = cmdStr[i];
		}
		action[2] = '\0';
		for (int i = 3; i < cmdStrIndex; i++) {   // int value is the value of rest of string
			value[i - 3] = cmdStr[i];
		}
		value[cmdStrIndex - 3] = '\0';

		actionN = atoi(action);
		switch (actionN) {
		case 91: // set time yy mm dd w hh mm ss
		{
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i];
			}
			tmpval[2] = '\0';
			year = (byte)atoi(tmpval);
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i + 2];
			}
			tmpval[2] = '\0';
			month = (byte)atoi(tmpval);
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i + 4];
			}
			tmpval[2] = '\0';
			dayOfMonth = (byte)atoi(tmpval);
			for (int i = 0; i < 1; i++) {
				tmpval[i] = value[i + 6];
			}
			tmpval[1] = '\0';
			dayOfWeek = (byte)atoi(tmpval);
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i + 7];
			}
			tmpval[2] = '\0';
			hour = (byte)atoi(tmpval);
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i + 9];
			}
			tmpval[2] = '\0';
			minute = (byte)atoi(tmpval);
			for (int i = 0; i < 2; i++) {
				tmpval[i] = value[i + 11];
			}
			tmpval[2] = '\0';
			second = (byte)atoi(tmpval);
			setTime(second, minute, hour, dayOfWeek, dayOfMonth, month, year);
			break; }
		case 92: { // clear indicators, todo clear alarms
			lcd.clear();
			lcd2.clear();
			break;
		}

		}


	}
}

void LCNum(int add, int16_t num)
{
	int pos;
	int dig[5];
	bool neg = false;
	bool first = false;
	if (num < 0)
	{
		neg = true;
		num = -1 * num;
	}
	for (char i = 0; i < 5; i++)
	{
		dig[i] = num % 10;
		num = num / 10;
	}
	lc.clearDisplay(add);

	for (int i = 4; i > -1; i--)
	{
		if ((dig[i] == 0) && ((first == true) || (i == 0)))
		{
			lc.setDigit(add, i, dig[i], false);
		}

		if ((dig[i] != 0) && (first == false))
		{
			if (neg == true)
			{
				lc.setChar(add, i + 1, '-', false);
			}

			first = true;
		}
		if ((dig[i] != 0) && (first == true))
		{
			lc.setDigit(add, i, dig[i], false);
		}


	}

}

void setTime(byte ssecond, byte sminute, byte shour, byte sdayOfWeek, byte sdayOfMonth, byte smonth, byte syear)
{
	// sets time and date data to DS3231
	Wire.beginTransmission(RTCADR);
	Wire.write(0); // set next input to start at the seconds register
	Wire.write(decToBcd(ssecond)); // set seconds
	Wire.write(decToBcd(sminute)); // set minutes
	Wire.write(decToBcd(shour)); // set hours
	Wire.write(decToBcd(sdayOfWeek)); // set day of week (1=Sunday, 7=Saturday)
	Wire.write(decToBcd(sdayOfMonth)); // set date (1 to 31)
	Wire.write(decToBcd(smonth)); // set month
	Wire.write(decToBcd(syear)); // set year (0 to 99)
	Wire.endTransmission();
}

void printTime()
{
	readTime();
	if (hour > 22)
	{
		if ((second % 2) == 0)
		{
			lc.setChar(0, 7, 'b', false);
		}
		else
		{
			lc.setChar(0, 7, ' ', false);
		}
	}
	if (hour > 9)
	{
		int ones = hour % 10;
		hour = hour / 10;
		lc.setDigit(0, 5, hour, false);
		lc.setDigit(0, 4, ones, true);
	}
	else
	{
		lc.setDigit(0, 5, 0, false);
		lc.setDigit(0, 4, hour, true);
	}
	if (minute > 9)
	{
		int ones = minute % 10;
		minute = minute / 10;
		lc.setDigit(0, 3, minute, false);
		lc.setDigit(0, 2, ones, true);
	}
	else
	{
		lc.setDigit(0, 3, 0, false);
		lc.setDigit(0, 2, minute, true);
	}
	if (second > 9)
	{
		int ones = second % 10;
		second = second / 10;
		lc.setDigit(0, 1, second, false);
		lc.setDigit(0, 0, ones, false);
	}
	else
	{
		lc.setDigit(0, 1, 0, false);
		lc.setDigit(0, 0, second, false);
	}
}

byte decToBcd(byte val)
{
	return((val / 10 * 16) + (val % 10));
}
// Convert binary coded decimal to normal decimal numbers
byte bcdToDec(byte val)
{
	return((val / 16 * 10) + (val % 16));
}

