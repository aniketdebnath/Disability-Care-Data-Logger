#ifndef HeartRate5_h
#define HeartRate5_h

#include <Wire.h>
#include <Arduino.h>

// HeartRate5 Class Definition
class HeartRate5 {
public:
    // Registers
    static const uint8_t HR5_REG0H = 0x00;
    static const uint8_t HR5_REG1H = 0x01;  // LED2STC
    static const uint8_t HR5_REG2H = 0x02;  // LED2ENDC
    static const uint8_t HR5_REG3H = 0x03;  // LED1LEDSTC
    static const uint8_t HR5_REG4H = 0x04;  // LED1LEDENDC
    static const uint8_t HR5_REG5H = 0x05;  // ALED2STC/LED3STC
    static const uint8_t HR5_REG6H = 0x06;  // ALED2ENDC/LED3ENDC
    static const uint8_t HR5_REG7H = 0x07;  // LED1STC
    static const uint8_t HR5_REG8H = 0x08;  // LED1ENDC
    static const uint8_t HR5_REG9H = 0x09;  // LED2LEDSTC
    static const uint8_t HR5_REGAH = 0x0A;  // LED2LEDENDC
    static const uint8_t HR5_REGBH = 0x0B;  // ALED1STC
    static const uint8_t HR5_REGCH = 0x0C;  // ALED1ENDC
    static const uint8_t HR5_REGDH = 0x0D;  // LED2CONVST
    static const uint8_t HR5_REGEH = 0x0E;  // LED2CONVEND
    static const uint8_t HR5_REGFH = 0x0F;  // ALED2CONVST/LED3CONVST
    static const uint8_t HR5_REG10H = 0x10; // ALED2CONVEND/LED3CONVEND
    static const uint8_t HR5_REG11H = 0x11; // LED1CONVST
    static const uint8_t HR5_REG12H = 0x12; // LED1CONVEND
    static const uint8_t HR5_REG13H = 0x13; // ALED1CONVST
    static const uint8_t HR5_REG14H = 0x14; // ALED1CONVEND
    static const uint8_t HR5_REG15H = 0x15; // ADCRSTSTCT0
    static const uint8_t HR5_REG16H = 0x16; // ADCRSTENDCT0
    static const uint8_t HR5_REG17H = 0x17; // ADCRSTSTCT1
    static const uint8_t HR5_REG18H = 0x18; // ADCRSTENDCT1
    static const uint8_t HR5_REG19H = 0x19; // ADCRSTSTCT2
    static const uint8_t HR5_REG1AH = 0x1A; // ADCRSTENDCT2
    static const uint8_t HR5_REG1BH = 0x1B; // ADCRSTSTCT3
    static const uint8_t HR5_REG1CH = 0x1C; // ADCRSTENDCT3
    static const uint8_t HR5_REG1DH = 0x1D; // PRPCT
    static const uint8_t HR5_REG1EH = 0x1E; // Timer Control
    static const uint8_t HR5_REG20H = 0x20;
    static const uint8_t HR5_REG21H = 0x21;
    static const uint8_t HR5_REG22H = 0x22;
    static const uint8_t HR5_REG23H = 0x23;
    static const uint8_t HR5_REG29H = 0x29;
    static const uint8_t HR5_REG2AH = 0x2A; // LED2VAL
    static const uint8_t HR5_REG2BH = 0x2B; // ALED2VAL/LED3VAL
    static const uint8_t HR5_REG2CH = 0x2C; // LED1VAL
    static const uint8_t HR5_REG2DH = 0x2D; // ALED1VAL
    static const uint8_t HR5_REG2EH = 0x2E; // LED2-ALED2VAL
    static const uint8_t HR5_REG2FH = 0x2F; // LED1-ALED1VAL
    static const uint8_t HR5_REG31H = 0x31;
    static const uint8_t HR5_REG32H = 0x32;
    static const uint8_t HR5_REG33H = 0x33;
    static const uint8_t HR5_REG34H = 0x34;
    static const uint8_t HR5_REG35H = 0x35;
    static const uint8_t HR5_REG36H = 0x36;
    static const uint8_t HR5_REG37H = 0x37;
    static const uint8_t HR5_REG39H = 0x39;
    static const uint8_t HR5_REG3AH = 0x3A;
    static const uint8_t HR5_REG3DH = 0x3D;
    static const uint8_t HR5_REG3FH = 0x3F;
    static const uint8_t HR5_REG40H = 0x40;

    // Default I2C address
    static const uint8_t HR5_ADDR = 0x58;

    // Constructor
    HeartRate5(uint8_t address = HR5_ADDR);

    // Public methods
    void begin();
    void init();
    void setLedConfig(uint8_t led, float current_mA);
    void setTimingControls();  // Renamed for consistency
    bool readSensor(uint32_t& led2Value, uint32_t& led1Value, uint32_t& led3Value);
    void setLEDCurrent(int led1Current, int led2Current, int led3Current);
    void setTIASettings(uint8_t gain, uint8_t cf, bool enableSeparate = false, uint8_t gainSep = 0, uint8_t cfSep = 0);
    uint32_t calculateRegisterValue(float current_mA);
    void writeRegister(uint8_t regAddr, uint32_t data);
    void setGain(uint8_t gain);
    uint32_t readRegister(uint8_t regAddr);
    uint16_t calculateSpO2(uint32_t irData, uint32_t redData);
    void enableAdcReadyInterrupt(uint8_t interruptPin);
    // Reading values
    uint32_t getLed3Val();
    uint32_t getLed2Val();
    uint32_t getAled2Val();
    uint32_t getLed1Val();
    uint32_t getAled1Val();
    void enableProgrammableTimingInterrupt(uint16_t startCount, uint16_t endCount);
    // Function to configure the sensor for 125 Hz sampling
    void configureSamplingRate(int rate);
    void configureSamplingWithDecimation(uint32_t prfPeriod, uint8_t numAverages, uint8_t decimationFactor);

private:
    uint8_t _deviceAddress;

    void i2cWrite(uint8_t regAddr, uint8_t* data, uint8_t length);
    void i2cRead(uint8_t regAddr, uint8_t* data, uint8_t length);
    void resetDelay();
};

// Global flag for interrupt handling
extern volatile bool adcReadyFlag;

// Interrupt service routine (ISR)
void IRAM_ATTR onAdcReady();

#endif // HeartRate5_h
