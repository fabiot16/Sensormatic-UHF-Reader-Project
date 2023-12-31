# RFID UHF Reader for PicoW and ESP32

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## RFID UHF Reader with API Integration

This RFID UHF reader project is designed to read RFID tags within a specified range and manage their data in real-time. It operates as follows:

- Tags are read by the RFID reader.
- If the tag is not in the internal table, it gets sent to the API and registered internaly
- If X (debounce timer) seconds have gone by since the tag was last sent, its data is sent to the API and table updated.
- Tags not read within the last Y (clear timer) seconds are automatically removed from the internal table.

### Features

- Real-time data handling.
- Automatic tag expiration.
- Seamless API integration.
- Customizable timing intervals (debounce and clear).

### Use Cases

- **Attendance Tracking**: Automate attendance tracking, sending data to an attendance database only when students are in close proximity to the reader.

- **Inventory Control**: Enable real-time inventory control by sending updates to a central inventory system only when items are scanned recently.

- **Access Control**: Grant access to authorized personnel when their RFID tags are within range, ensuring security and efficiency.

- **Resource Management**: Manage resources, such as equipment or vehicles, by tracking their presence and sending updates when needed.

## Hardware

- For PicoW, used [SB Components UHF Reader](https://github.com/sbcshop/UHF_Reader_Pico_W_Software)
- For ESP32, used ESP32 WROVER not tested and not finished
- For LLRP used Zebras's FX9600 RFID reader with AN 720 Antena

## Software Setup

### PicoW
  - For Visual Studio
    - Install Visual Studio Code and PyMakr extension
    - Firmware comes pre-installed, but if needed, do it as described in [SB Components UHF Reader](https://github.com/sbcshop/UHF_Reader_Pico_W_Software).
    - Create and configure your own OTA Updater as discribed in [rdehuyss's Micropython OTA Updater](https://github.com/rdehuyss/micropython-ota-updater) or simply disable it by commenting connectToWifiAndUpdate().
    - Open PyMakr's tab on Visual Studio
    - On devices, click the lightning to connect, folder to open the board's explorer end terminal to start a terminal
    
    ![clicks](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/clicks.jpg)
    
    - In config.py declare the API variables
    - Copy 'app' folder and main.py to the board
    - CTRL+D To soft reboot and run the code (Sometimes the board bugs and it is needed to press the reset button (Number 9) shown in the image)
    
    ![reset](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/reset.jpg)

  - For Thonny
    - Open Thonny and configure the connection by clicking on the bottom right corner
   
    ![thonny](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/thonny.jpg)

    ![connect](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/connect.jpg)
    
    - Open the files you want to import with Thonny and edit them as you wish
    - To import them to the board, on File, presse Save as, an choose Pico W
   
    ![save](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/save.jpg)
      
    - You can also run the program directly on Thonny with the board connected
   
    ![run](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/run.jpg)

- If there is not a confirmation that the connection was successfull after 10 seconds, press the reset button.

> [!WARNING]
> Everytime you press the reset button, there is a need to reconnect the board on PyMakr

### LLRP
- Install Python
- In config.py declare the API variables

### ESP32 (C++) UNTESTED
- Install ESP32 Arduino library
- In config.cpp declare the API variables
- Upload the code to the board

## Usage

### PicoW
  - Power On
    - If it can't connect to a WiFi, it will open a config portal AP for you to set it up. Connect to it on your phone or pc (SSID = WifiManager, Password = password) and go to 192.168.4.1.
    
    ![index](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/index.jpg)

    - Once in the config page, you can configure WiFi and the RFID timmers if needed.
   
    ![ssids](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/ssids.jpg)
    ![rfid](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/rfid.jpg)
    - After you're done, press Exit.
   
    ![configured](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/configured.jpg)
  
  - After connection is made
    - If enabled, it will try to update OTA and then start just like in the video
   
    https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/assets/114235594/b0b616d7-ea5d-4fa6-a7ff-aaedc6f76064

    - API Receiving
    
    https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/assets/114235594/be996d8c-62bd-4874-99c7-1e6f7c176721

  If you want to update any setting while it is running, you can just press the button and it will set up the config portal and AP once again.

  ![config](https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/blob/main/images/config.jpg)

### LLRP
  - Connect the reader to the network
  - Run main.py

### ESP32
  - Not finished and not tested

## Demo
  
  https://github.com/fabiot16/Sensormatic-UHF-Reader-Project/assets/114235594/3267a211-2700-4701-b6fd-79b52c281e62

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting
  Micropython is very unstable with PicoW, soft reset usually causes bugs so its better to full reset
  WiFi in PicoW seems to be a little bit weak
  
## References
  [SB Components UHF Reader](https://github.com/sbcshop/UHF_Reader_Pico_W_Software)
  
  [rdehuyss's Micropython OTA Updater](https://github.com/rdehuyss/micropython-ota-updater)
  
  [esitarski's pyllrp](https://github.com/esitarski/pyllrp)
  
  [Micropython docs](https://docs.micropython.org/en/latest/)
  
## Future Work
  Use ESP32 module instead of PicoW to improve WiFi performance and threading

## Acknowledgments

  I would like to thank to Sensormatic and [@lasoares](https://github.com/lasoares) for providing me with the hardware, guidance and the opportunity to learn and grow as a software developer during this internship.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
