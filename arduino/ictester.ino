#define AND_BTN_PIN A5
#define NOR_BTN_PIN A2


#define RED_LED_PIN A4
#define GRN_LED_PIN A3
#define DEBOUNCE_DELAY 150

unsigned long lastMillis = 0;



unsigned norResultMatrix[4][3] = {
  { 0, 0, 1 },
  { 0, 1, 0 },
  { 1, 0, 0 },
  { 1, 1, 0 }
};


unsigned andResultMatrix[4][3] = {
  { 0, 0, 0 },
  { 0, 1, 0 },
  { 1, 0, 0 },
  { 1, 1, 1 }
};



void setup()
{
  Serial.begin(9600); 
  pinMode(AND_BTN_PIN, INPUT);
  pinMode(NOR_BTN_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GRN_LED_PIN, OUTPUT);
  
  turnLEDsOff();
  resetPins();
}

void resetPins(void)
{
  for(int i = 2; i <= 13; i++)
    pinMode(i, INPUT);
}

void initPositiveFourGateTest(void)
{
  pinMode(2, INPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, INPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, INPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, INPUT);
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
}

void initNegativeFourGateTest(void)
{
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, INPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, INPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, INPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(13, INPUT);
}

bool testTwoInputGate(unsigned testCase[4][3], unsigned a, unsigned b, unsigned y)
{
  bool result = true;
  
  for(int i = 0; i < 4; i++)
  {
    digitalWrite(a, testCase[i][0]);
	digitalWrite(b, testCase[i][1]);
  	result = result & (digitalRead(y) == testCase[i][2]);
  }
  
  return result;
}

bool doFourGateTest(unsigned testCase[4][3], bool positive)
{
  bool result = true;
  unsigned long delayTime = 1000; // 500 milliseconds delay
  
  if(positive)
  {
    initPositiveFourGateTest();
    result = result & testTwoInputGate(testCase, 13, 12, 11);
    delay(delayTime);
    
    result = result & testTwoInputGate(testCase, 10, 9, 8);
    delay(delayTime);
    
    result = result & testTwoInputGate(testCase, 7, 6, 5);
    delay(delayTime);
    
    result = result & testTwoInputGate(testCase, 4, 3, 2);
    delay(delayTime);
    
  }
  else
  {
    initNegativeFourGateTest();
    result = result & testTwoInputGate(testCase, 2, 3, 4);
    delay(delayTime);
   
    result = result & testTwoInputGate(testCase, 5, 6, 7);
    delay(delayTime);
    
    result = result & testTwoInputGate(testCase, 8, 9, 10);
    delay(delayTime);
   
    result = result & testTwoInputGate(testCase, 11, 12, 13);
    delay(delayTime);
    
  }
  
  resetPins();
  
  
  return result;
}

void turnLEDsOff(void)
{
  digitalWrite(GRN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
}

void displayTestResult(bool success)
{
  digitalWrite(GRN_LED_PIN, success);
  digitalWrite(RED_LED_PIN, !success);
}

void loop()
{
  unsigned long currentMillis = millis();
  
  if(currentMillis - lastMillis > DEBOUNCE_DELAY)
  {
    if(Serial.available() > 0) // Check if data is available to read
    {
      String command = Serial.readString(); // Read the incoming data

      if(command.startsWith("AND")) // Check if the command is "AND"
        displayTestResult(doFourGateTest(andResultMatrix, true));
      else if(command.startsWith("NOR")) // Check if the command is "OR"
        displayTestResult(doFourGateTest(norResultMatrix, true));
      else if(command.startsWith("END")) // Check if the command is "END"
      {
        turnLEDsOff(); // Turn off the LEDs
        Serial.println("Test disconnected."); // Print a message to the Serial Monitor
      }
    }

    lastMillis = currentMillis;
  }
}