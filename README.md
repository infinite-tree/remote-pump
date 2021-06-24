# ESP32 irrigation pump webserver

Features:
   - webserver to turn pump on and off
   - set length to run pump
   - read pump status from external opt-coupler

## Hardware Assumptions

You're running an ESP32. We use [this WROVER one](https://www.aliexpress.com/item/4000064597840.html?spm=a2g0s.9042311.0.0.70504c4dpiaF4W)

You have a powerful enough relay/contactor to flip on your "pump". We use these:
  -  [380V 25A relay](https://www.amazon.com/gp/product/B074FT4VXB)

You have some kind of feedback telling you if the power if on or off:
  - [220V AC Detection board](https://www.aliexpress.com/item/32828199766.html). Note we use a 10k pull-up resistor and the output is inverted. 



## Building & Installing


### MicroPython Environment Installation

Download [micropython (spiram-idf4) here](https://micropython.org/download/esp32/)

```
sudo apt get install esptool
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0x1000 ./micro-python/esp32spiram-idf4-20191220-v1.12.bin
```


### Installing the Python code

```
pip3 install adafruit-ampy --upgrade
ampy --port /dev/ttyUSB0 put config.py /config.py
ampy --port /dev/ttyUSB0 put www /www
ampy --port /dev/ttyUSB0 put /MicroWebSrv2/MicroWebSrv2 /MicroWebSrv2
ampy --port /dev/ttyUSB0 put main.py /main.py
```

