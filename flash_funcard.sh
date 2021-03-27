#!/usr/bin/env bash

echo "[+] Compiling"
cd src && make && cd -

echo "[+] Going to flasher mod"
python3 go_flasher.py

sleep 3

avrdude -p m8515 -c avrisp2 -P /dev/ttyACM0 -U flash:w:`ls src/build/aes*.hex`:i -U eeprom:w:`ls src/build/eedata*.hex`:i

echo "[+] Please restart your LEIA board to go back to nominal mode!"
echo "    Press enter when OK"
read aa
