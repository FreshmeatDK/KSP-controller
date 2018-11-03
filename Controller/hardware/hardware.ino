/*
Name:       hardware.ino
Created:	03-11-2018
Author:     LORIEN\Jesper
*/

#include <Keypad.h>
#include <Wire.h>
#include <SPI.h>
#include <FastLED.h>
#include <LedControl.h>
#include <NewLiquidCrystal/LiquidCrystal_I2C.h>


//I2C adresses
#define RTCADR 0x68


// pin definitions

// PWR for gauges
#define CHARGE 4
#define MONO 5
#define SPEED 6
#define ALT 7
// 74hc165
#define SS1 46
#define CLKI 48
// CD4021
#define SS2 45
#define CLK 27
#define DTA 25
// FastLed
#define LEDPIN 23
// LedControl
#define LCCLK 43
#define LCCS 39
#define LCDATA 41
//Joystick buttons
#define JOY1BTN 50
#define JOY2BTN 42
#define JOY2FWD 38
#define JOY2BCK 40

// analog pins
#define TRIMYAW 2
#define TRIMPITCH 3
#define TRIMROLL 1
#define TRIMENGINE 0
#define JOY1X 4
#define JOY1Y 5 
#define JOY1Z 6
#define THROTTLE 7
#define JOY2X 8
#define JOY2Y 9 


// number of units attached
#define NUMLC 3
#define NUMLEDS 36
#define NUMIC1 4
#define NUMIC2 1

//vars
byte second = 0, minute, hour = 0, dayOfWeek, dayOfMonth, month, year; // bytes to hold RT clock
char key; // keypress buffer
char cmdStr[19]; // command string to pass
byte cmdStrIndex = 0; //current lenght of cmdStr
int trimY, trimP, trimR, trimE;

char keys[5][8] = {
	{ '7', '8', '9', '-', ',', '.', 'S', 'M' },
{ '4', '5', '6', 'c', 'v', 'V', 'P', 'R' },
{ '1', '2', '3', 91, 93, 'B', 'I', 'O' },
{ '0', '*', '#', 'm', 'T', 'B', 'N', 'A' },
{ 'W', 's', 'x', 'q', 'v', 'r', 'g', 'G' }
};
byte rowPins[5] = { 35, 33, 31, 29, 37 };
byte colPins[8] = { 26, 24, 22, 30, 28, 32, 34, 36 };


// objects
CRGB leds[NUMLEDS]; // Array of WS2811
byte dataIn[NUMIC1 + NUMIC2]; // Byte array of spi inputs
byte dataOld[NUMIC1 + NUMIC2]; //testing array
LedControl lc = LedControl(LCDATA, LCCLK, LCCS, NUMLC);
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);  // set the LCD address to 0x27 
LiquidCrystal_I2C lcd2(0x23, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);  // set the LCD address to 0x23
Keypad keymain(makeKeymap(keys), rowPins, colPins, 5, 8);


void setup()
{
	Serial.begin(9600);

	// Meter init
	pinMode(CHARGE, OUTPUT);
	analogWrite(CHARGE, 0);
	pinMode(MONO, OUTPUT);
	analogWrite(MONO, 0);
	pinMode(SPEED, OUTPUT);
	analogWrite(SPEED, 0);
	pinMode(ALT, OUTPUT);
	analogWrite(ALT, 0);

	//Joystick init
	pinMode(JOY1BTN, INPUT);
	pinMode(JOY2BTN, INPUT);
	pinMode(JOY2FWD, INPUT);
	pinMode(JOY2BCK, INPUT);

	// LCD init
	lcd.begin(20, 4);
	lcd.backlight();

	lcd2.begin(20, 4);
	lcd2.backlight();


	// SPI init
	SPI.begin();
	pinMode(SS1, OUTPUT);
	pinMode(SS2, OUTPUT);

	pinMode(CLKI, OUTPUT);
	pinMode(CLK, OUTPUT);
	pinMode(DTA, INPUT);


	//LED strip init
	FastLED.addLeds<NEOPIXEL, LEDPIN>(leds, NUMLEDS);

	//7seg LED init
	for (int i = 0; i < NUMLC; i++)
	{
		lc.shutdown(i, false);
		lc.setIntensity(i, 1);
		lc.clearDisplay(i);
	}
}


void loop()
{
	testTrim();
	testSPI();
	toggles();
	printTime();
	chkKeypad();
	execCmd();
}

