#include "HeartRate5.h"
#include <Wire.h>
#include <Arduino.h>

// Constructor
HeartRate5::HeartRate5(uint8_t address) {}


#define DIAGNOSIS       0x00

//PRPCT ( timer counter )
#define PRPCT            0x1D   /**< Bits 0-15 for writing counter value      */

//Timer Module enable / NUMAV ( # of times to sample and average )
#define TIM_NUMAV        0x1E

#define TIA_GAINS1       0x21

//TIA Gains 2
#define TIA_GAINS2       0x20

//LED1 Start / End
#define LED1_ST          0x03
#define LED1_END         0x04

//Sample LED1 Start / End
#define SMPL_LED1_ST     0x07
#define SMPL_LED1_END    0x08

//LED1 Convert Start / End
#define LED1_CONV_ST     0x11
#define LED1_CONV_END    0x12

//Sample Ambient 1 Start / End
#define SMPL_AMB1_ST     0x0B
#define SMPL_AMB1_END    0x0C

//Ambient 1 Convert Start / End
#define AMB1_CONV_ST     0x13
#define AMB1_CONV_END    0x14

//LED2 Start / End
#define LED2_ST          0x09
#define LED2_END         0x0A

//Sample LED2 Start / End
#define SMPL_LED2_ST     0x01
#define SMPL_LED2_END    0x02

//LED2 Convert Start / End
#define LED2_CONV_ST     0x0D
#define LED2_CONV_END    0x0E

//Sample Ambient 2 ( or LED3 ) Start / End
#define SMPL_LED3_ST     0x05
#define SMPL_LED3_END    0x06

//Ambient 2 ( or LED3 ) Convert Start / End
#define LED3_CONV_ST     0x0F
#define LED3_CONV_END    0x10

//ADC Reset Phase 0 Start / End
#define ADC_RST_P0_ST    0x15
#define ADC_RST_P0_END   0x16

//ADC Reset Phase 1 Start / End
#define ADC_RST_P1_ST    0x17
#define ADC_RST_P1_END   0x18

//ADC Reset Phase 2 Start / End
#define ADC_RST_P2_ST    0x19
#define ADC_RST_P2_END   0x1A

//ADC Reset Phase 3 Start / End
#define ADC_RST_P3_ST    0x1B
#define ADC_RST_P3_END   0x1C

//LED Current Control
#define LED_CONFIG       0x22

#define SETTINGS          0x23  /**< Settings Address */

 //Clockout Settings
#define CLKOUT            0x29  /**< Clockout Address */

  //LED1 Output Value
#define LED1VAL           0x2C  /**< LED1 Output code in twos complement      */

//LED2 Output Value
#define LED2VAL           0x2A  /**< LED2 Output code in twos complement      */

//LED3 or Ambient 2 Value
#define LED3VAL           0x2B  /**< LED3 / Ambient 2 value in twos complement*/

//Ambient 1 Value
#define ALED1VAL          0x2D  /**< Ambient 1 value in twos complement       */

//LED1-Ambient 1 Value
#define LED1_ALED1VAL     0x2F  /**< LED1-ambient1 in twos complement         */

//LED2-Ambient 2 Value
#define LED2_ALED2VAL     0x2E  /**< LED2-ambient2 in twos complement         */

//Diagnostics Flag
#define PD_SHORT_FLAG     0x30  /**< 0: No short across PD 1: Short across PD */

//PD disconnect / INP, INN settings / EXT clock Division settings
#define PD_INP_EXT        0x31
#define PD_DISCONNECT        2  /**< Disconnects PD signals (INP, INM)        */
#define ENABLE_INPUT_SHORT   5  /**< INP, INN are shorted to VCM when TIA dwn */
#define CLKDIV_EXTMODE       0  /**< Ext Clock Div Ration bits 0-2            */

  //PDN_CYCLE Start / End
#define PDNCYCLESTC       0x32  /**< Bits 0-15                                */
#define PDNCYCLEENDC      0x33  /**< Bits 0-15                                */

//Programmable Start / End time for ADC_RDY replacement
#define PROG_TG_STC       0x34  /**< Bits 0-15 Define Start Time              */
#define PROG_TG_ENDC      0x35  /**< Bits 0-15 Define End Time                */

//LED3C Start / End
#define LED3LEDSTC        0x36  /**< LED3 Start, if not used set to 0         */
#define LED3LEDENDC       0x37  /**< LED3 End, if not used set to 0           */
//PRF Clock Division settings
#define CLKDIV_PRF        0x39  /**< Clock Division Ratio for timing engine   */

  //DAC Settings
#define DAC_SETTING       0x3A  /**< DAC Settings Address                     */
#define POL_OFFDAC_LED2     19  /**< Polarity for LED2                        */
#define I_OFFDAC_LED2       15  /**< Setting for LED2                         */
#define POL_OFFDAC_AMB1     14  /**< Polarity for Ambient 1                   */
#define I_OFFDAC_AMB1       10  /**< Setting for Ambient 1                    */
#define POL_OFFDAC_LED1      9  /**< Polarity for LED1                        */
#define I_OFFDAC_LED1        5  /**< Setting for LED1                         */
#define POL_OFFDAC_LED3      4  /**< Polarity for LED3                        */
#define I_OFFDAC_LED3        0  /**< Setting for LED3                         */

// Initialize I2C
void HeartRate5::begin() {
    Wire.begin();
}

// Read a 24-bit register value
uint32_t HeartRate5::readRegister(uint8_t regAddr) {
    uint8_t hr_storage[3];  // Storage for the 3 bytes read
    uint32_t returnValue = 0;

    // Start I2C transmission to the device
    Wire.beginTransmission(HR5_ADDR);  // HR5_ADDR should be the I2C address of the sensor
    Wire.write(regAddr);  // Specify the register to read from
    if (Wire.endTransmission(false) != 0) {
#ifdef DEBUG
        Serial.println("I2C Error: Error during transmission");
#endif
        return 0xFFFFFFFF;  // Error value indicating failed read
}

    // Request 3 bytes from the register
    Wire.requestFrom(HR5_ADDR, (uint8_t)3);
    if (Wire.available() == 3) {
        hr_storage[0] = Wire.read();
        hr_storage[1] = Wire.read();
        hr_storage[2] = Wire.read();

        // Combine the 3 bytes into a 24-bit value
        returnValue = (uint32_t)hr_storage[0] << 16 | (uint32_t)hr_storage[1] << 8 | hr_storage[2];

        // Check if the value is negative in 24-bit two's complement format
        if (returnValue & 0x800000) {
            returnValue |= 0xFF000000;  // Sign-extend to 32-bit
        }
    }
    else {
#ifdef DEBUG
        Serial.println("Error: Not enough bytes available");
#endif
        return 0xFFFFFFFF;  // Error value indicating failed read
        }

    return returnValue;  // Return the 24-bit value read from the register
    }


// Write a 24-bit value to a register
void HeartRate5::writeRegister(uint8_t regAddr, uint32_t data) {
    Wire.beginTransmission(0x58);
    Wire.write(regAddr);
    Wire.write((data >> 16) & 0xFF);
    Wire.write((data >> 8) & 0xFF);
    Wire.write(data & 0xFF);
    Wire.endTransmission();
}

// Calculate the register value from the current in mA
uint32_t HeartRate5::calculateRegisterValue(float current_mA) {
    if (current_mA < 0 || current_mA > 50) {
        // Handle invalid current values
        return 0;
    }
    return static_cast<uint8_t>(current_mA / 0.8);
}

// Set LED current
void HeartRate5::setLEDCurrent(int led1Current, int led2Current, int led3Current) {
    uint32_t regValue = 0;

    // Ensure current values are within valid range (0-63)
    led1Current = constrain(led1Current, 0, 63);
    led2Current = constrain(led2Current, 0, 63);
    led3Current = constrain(led3Current, 0, 63);

    // Set LED currents
    regValue |= (led3Current << 12); // ILED3
    regValue |= (led2Current << 6);  // ILED2
    regValue |= (led1Current << 0);  // ILED1

    // Write to Register 22h
    writeRegister(0x22, regValue);
}

// Read sensor values
bool HeartRate5::readSensor(uint32_t& led2Value, uint32_t& led1Value, uint32_t& led3Value) {
    uint32_t led2Raw = readRegister(HR5_REG2AH);  // Correct register for LED2 value
    uint32_t led3Raw = readRegister(HR5_REG2BH);  // Correct register for LED3 value
    uint32_t led1Raw = readRegister(HR5_REG2CH);  // Correct register for LED1 value

    if (led2Raw == 0xFFFFFFFF || led1Raw == 0xFFFFFFFF || led3Raw == 0xFFFFFFFF) {
        return false;  // Return false if any read operation failed
    }

    led2Value = (uint32_t)(led2Raw & 0xFFFFFF);
    led1Value = (uint32_t)(led1Raw & 0xFFFFFF);
    led3Value = (uint32_t)(led3Raw & 0xFFFFFF);
    return true;
}

// Initialize the sensor with default settings
void HeartRate5::init() {
    writeRegister(0x00, 0x000000);
    writeRegister(0x01, 0x000050);
    writeRegister(0x02, 0x00018F);
    writeRegister(0x03, 0x000320);
    writeRegister(0x04, 0x0004AF);
    writeRegister(0x05, 0x0001E0);
    writeRegister(0x06, 0x00031F);
    writeRegister(0x07, 0x000370);
    writeRegister(0x08, 0x0004AF);
    writeRegister(0x09, 0x000000);
    writeRegister(0x0A, 0x00018F);
    writeRegister(0x0B, 0x0004FF);
    writeRegister(0x0C, 0x00063E);
    writeRegister(0x0D, 0x000198);
    writeRegister(0x0E, 0x0005BB);
    writeRegister(0x0F, 0x0005C4);
    writeRegister(0x10, 0x0009E7);
    writeRegister(0x11, 0x0009F0);
    writeRegister(0x12, 0x000E13);
    writeRegister(0x13, 0x000E1C);
    writeRegister(0x14, 0x00123F);
    writeRegister(0x15, 0x000191);
    writeRegister(0x16, 0x000197);
    writeRegister(0x17, 0x0005BD);
    writeRegister(0x18, 0x0005C3);
    writeRegister(0x19, 0x0009E9);
    writeRegister(0x1A, 0x0009EF);
    writeRegister(0x1B, 0x000E15);
    writeRegister(0x1C, 0x000E1B);
    writeRegister(0x1D, 0x009C3E);
    writeRegister(0x1E, 0x000103);
    writeRegister(0x20, 0x008003);
    writeRegister(0x21, 0x000003);
    writeRegister(0x22, 0x01B6D9);
    writeRegister(0x23, 0x104218);
    writeRegister(0x29, 0x000000);
    writeRegister(0x31, 0x000000);
    writeRegister(0x32, 0x00155F);
    writeRegister(0x33, 0x00991E);
    writeRegister(0x34, 0x000000);
    writeRegister(0x35, 0x000000);
    writeRegister(0x36, 0x000190);
    writeRegister(0x37, 0x00031F);
    writeRegister(0x39, 0x000000);
    writeRegister(0x3A, 0x000000);
}

// Set TIA settings (Gain and Bandwidth)
void HeartRate5::setTIASettings(uint8_t gain, uint8_t cf, bool enableSeparate, uint8_t gainSep, uint8_t cfSep) {
    uint8_t regValue = 0;
    gain = constrain(gain, 0, 7);
    cf = constrain(cf, 0, 7);
    // Set the TIA_GAIN and TIA_CF values
    regValue |= (gain & 0x07);       // Bits 2-0 for TIA_GAIN
    regValue |= ((cf & 0x07) << 3);  // Bits 5-3 for TIA_CF

    // Write to Register 21h (TIA settings)
    writeRegister(0x21, regValue);

    if (enableSeparate) {
        // Enable the EN_SEP_GAIN bit to allow separate settings
        uint32_t enSepValue = readRegister(0x21);
        enSepValue |= (1 << 6); // Assuming bit 6 is EN_SEP_GAIN
        writeRegister(0x21, enSepValue);

        // Set separate gain and Cf settings for the second phase
        uint8_t regSepValue = 0;
        regSepValue |= (gainSep & 0x07);       // Bits 2-0 for TIA_GAIN_SEP
        regSepValue |= ((cfSep & 0x07) << 3);  // Bits 5-3 for TIA_CF_SEP

        // Write to TIA_GAIN_SEP and TIA_CF_SEP register (assumed to be 0x22 for this example)
        writeRegister(0x22, regSepValue);
    }
}
// Set Gain for the TIA
void HeartRate5::setGain(uint8_t newGain) {
    uint32_t regValue = readRegister(0x21);

    if (regValue == 0xFFFFFFFF) {
        Serial.println("Error: Failed to read register 0x21");
        return;
    }

    // Mask the lower 3 bits (assuming they control gain) to clear old gain bits
    regValue &= ~0x07;

    // Set the new gain value, only considering the lower 3 bits
    regValue |= (newGain & 0x07);

    // Write the updated register value back to the device
    writeRegister(0x21, regValue);
}

// Configure the AFE4404 for a 125 Hz sampling rate

void HeartRate5::configureSamplingRate(int rate) {
    // Check the rate parameter and adjust register values accordingly
    if (rate == 125) {
        // Configure for 125 Hz sampling rate
        writeRegister(0x1D, 31999); // PRPCT register value for 125 Hz
        writeRegister(0x39, 1);     // CLKDIV_PRF value for 125 Hz (division by 16)
    }
    else if (rate == 250) {
        // Configure for 250 Hz sampling rate
        writeRegister(0x1D, 15999); // PRPCT register value for 250 Hz
        writeRegister(0x39, 0);     // CLKDIV_PRF value for 250 Hz (division by 8)
    }
    else {
        Serial.println("Error: Unsupported sampling rate");
        return;
    }

    Serial.print("Sampling rate set to ");
    Serial.print(rate);
    Serial.println(" Hz.");
}

// Enable the programmable timing interrupt
void HeartRate5::enableProgrammableTimingInterrupt(uint16_t startCount, uint16_t endCount) {
    // Step 1: Enable the programmable timing engine signal
    uint32_t regValue = readRegister(TIA_GAINS1); // Read the current value of the TIA_GAINS1 register
    if (regValue != 0xFFFFFFFF) { // Ensure the register read was successful
        regValue |= (1 << 8); // Set bit 8 (PROG_TG_EN) to enable programmable timing
        writeRegister(TIA_GAINS1, regValue); // Write back the updated value
    }

    // Step 2: Set the start time for the programmable timing engine
    writeRegister(PROG_TG_STC, startCount); // Set the PROG_TG_STC register

    // Step 3: Set the end time for the programmable timing engine
    writeRegister(PROG_TG_ENDC, endCount); // Set the PROG_TG_ENDC register
}
void HeartRate5::enableAdcReadyInterrupt(uint8_t interruptPin) {
    pinMode(interruptPin, INPUT);
    attachInterrupt(digitalPinToInterrupt(interruptPin), onAdcReady, RISING);
}
