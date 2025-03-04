# TOBB ETÜ ELE495 - Capstone Project

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgements](#acknowledgements)

## Introduction
Radio Frequency (RF) signal localization represents a critical technological challenge with applications spanning emergency response, military operations, and wireless communication research. The aim of this project is to develop an autonomous RF transmitter localization system using a Software-Defined Radio (SDR) platform. The system utilizes a Raspberry Pi, RTL-SDR receiver, and a directional antenna to detect and navigate towards a continuous narrow-band RF signal source. Our capstone project, developed for the ELE495 course, introduces an innovative, low-cost solution for autonomous RF transmitter detection using Software-Defined Radio (SDR) technology.

## Features

- Hardware:
   - Raspberry Pi (Control Unit)(https://www.robotistan.com/raspberry-pi-4-4gb)

   - RTL-SDR Receiver (https://www.rtl-sdr.com/product/rtl-sdr-blog-v4-r828d-rtl2832u-1ppm-tcxo-sma-software-defined-radio-with-dipole-antenna/)

   - Directional Antenna

   - DC Motors

   - Motor Driver (L298N)

   - 4WD Robot Car (https://www.robotistan.com/bluetooth-controlled-robot-car-kits-for-arduino-1)
  

- Operating System and packages
   - Operating System: Raspberry Pi OS / Linux

   - Programming Language: Python 3.x

   - Required Libraries:

     - matplotlib

     - numpy

     - RTLSdr


- Applications
  
  - Autonomous RF Source Localization: The system can be used to detect and navigate towards an RF signal source without human intervention.

  - Search and Rescue Operations: Can assist in locating emergency beacons or lost communication devices in disaster scenarios.

  - Interference Detection: Helps identify and locate unauthorized or malfunctioning RF transmitters in communication networks.

  - Wireless Sensor Networks: Can be integrated into IoT systems for automated positioning of network nodes.

- Services 

  - Real-time Signal Processing: Uses RTL-SDR to continuously scan and analyze RF signals.

  - Remote Monitoring & Control: The system can be monitored and controlled through a GUI interface.

  - Data Logging: Logs signal strength and movement data for further analysis.

  - Algorithm Development: Can serve as a testbed for developing and improving RF localization algorithms.

## Installation
Download Raspberry Pi Imager from official website
```bash
wget https://downloads.raspberrypi.org/imager_latest
```
SD Card Configuration

  - Insert SD card into your computer
  
  - Select Raspberry Pi OS (64-bit) in Imager
  
  - Write OS image to SD card
  
  - Create SSH and Wi-Fi configuration files:

  - Create empty ssh file in boot partition
  
  - Create wpa_supplicant.conf with Wi-Fi credentials:
     
        country=US
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1

        network={
        ssid="YOUR_WIFI_NAME"
        psk="YOUR_WIFI_PASSWORD"
        key_mgmt=WPA-PSK
         }


2. Initial Raspberry Pi Connection

  - Insert configured SD card into Raspberry Pi

  - Connect Raspberry Pi to network

Find Raspberry Pi's IP address:

  - Use router interface
    
  - Use network scanning tools like nmap
  
  - Use arp -a command



3. SSH Connection

Open terminal
Connect via SSH:

        ssh pi@RASPBERRY_PI_IP_ADDRESS

Default password:         
          
        raspberry



4. System Update

Update package lists:

    sudo apt update

Upgrade installed packages:

    sudo apt upgrade


5. Install Project Dependencies

Install Git:

    sudo apt install git

Install Python dependencies:

    sudo apt install python3-pip

    pip3 install numpy matplotlib rtlsdr


6. Clone Project Repository

        git clone https://github.com/your-username/rf-transmitter-localization.git
   
        cd rf-transmitter-localization

Additional Setup Details

  - Ensure RTL-SDR is correctly connected
  - Configure GPIO for motor control
  - Set up directional antenna
## Usage
  - Start the car and ensure it is connected to the network
  - Connect to Rapberry pi using SSH on terminal
  - Navigate to project directory
  - Run main script:
      
        python3 main.py

## Screenshots
![image](https://github.com/user-attachments/assets/8e162eab-9a56-4048-8f6c-191700be4a43)






For a video demonstration, visit [here](
https://www.youtube.com/watch?v=3q8H3G9lvu0
).

## Acknowledgements
Special thanks to our supervisor Özlem Tuğfe Demir and the TOBB ETÜ Electrical and Electronics Engineering Department for their guidance.

Contributors:

[Selin Erdem](https://github.com/selinerdem2)

[Muhammed Çağrı Öz](https://github.com/muhammedcagrioz)

[Eray Naldöken](https://github.com/enaldoken)

[Lütfi Ertuğrul Bekmen](https://github.com/ErtBekmen)

Resources and tools:

[RTL-SDR Blog](https://www.rtl-sdr.com/v4/)

[IEEE Xplore](https://ieeexplore.ieee.org)


