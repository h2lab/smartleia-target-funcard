# Testing target

This repository contains an AVR implementation of an unprotected 128-bit key AES as well as a dummy PIN verification
algorithm for playing with the LEIA boards.

The implementations have been tested on a 
[WB Electronics 64 Kbit ATMega chipcard](http://www.infinityusb.com/default.asp?show=store&ProductGrp=8).

# Compilation

Go to the [src/](src/) folder and run ``make``. You must have `avr-gcc`, e.g. from [avr-gcc](https://gcc.gnu.org/wiki/avr-gcc), and the `avr-libc` installed on your PC: these are usually
packaged with popular distros such as Debian or Ubuntu.
Make should create ``aes-<DDMMYY>-<HHMMSS>.hex`` and ``eedata-<DDMMYY>-<HHMMSS>.hex`` in the [src/build/](src/build/) folder. 


# Loading in the ATMega8515 card

Load the files ``eedata.hex`` (in EEPROM int.) and ``aes-<DDMMYY>-<HHMMSS>.hex`` (in FLASH) in the ATMega8515 component. You can for instance use the [**Infinity USB Unlimited**](http://www.infinityusb.com/default.asp?show=store&ProductID=11) Reader and IDE from WB Electronics for this step.

If you have a **recent LEIA board with the flashing mode feature**, you can simply execute the local flashing script:

```
sh flash_funcard.sh
```
This will compile and push the firmware on the funcard inserted in your LEIA board.

# Using the testing scripts

Two test scripts are provided here: `script-AES128-enc.py` and `pin_timing_attacks.py`.

The testing scripts are mainly Python based, and have been tested with Python3. The **dependency requirements** for these scripts are:

  * The `smartleia` package in its **version v1.0.1-1 at least** (this contains a small fix for funcards usage through PCSC relay), available [here](https://github.com/h2lab/smartleia).
  * The `pyscard`, `numpy` and `crypto` packages, all available with `pip`.

Two test scripts are provided: `script-AES128-enc.py` and `pin_timing_attacks.py`. Each of these scripts can be used in two modes: using LEIA's
direct access through `/dev/ttyACMx` with the toggle `USE_LEIA=True` in the scripts, or using PCSC daemon either through a regular smart card reader
(or LEIA in PCSC relay mode) by using the toggle `USE_LEIA=False` in the scripts.

The`script-AES128-enc.py` tests AES-128 encryption and decryption APDUs: this can be a basis to mount some side-channel attacks on an unprotected
AES (NOTE: although some APDUs setting masks are present, these are not used and are here for future evolutions).

The `pin_timing_attacks.py` extracts a secret PIN from the programmed funcard using a **timing attack** that exploits the dummy algorithm
used to check the PIN. In order for this attack to succeed, a timing oracle is needed. Since such a timing oracle exploits variations
of less than milliseconds, a proper time measurement for APDUs is necessary. This script shows that LEIA's [timing feature](https://h2lab.github.io/smartleia.github.io/c/test.html#timers)
can be of use here: a regular smart card reader is not able to extract the secret (at least with the basic approach used using LEIA). You
can test LEIA's timing extraction with the `USE_LEIA=True`, and PCSC based (using a regular reader or LEIA in PCSC mode) using the
`USE_LEIA=False` toggle in the script. The first one should extract the secret PIN successfully, while the second will not succeed.



# Licenses

SOSSE source codes are released under GPL v2 License. AVR-Crypto-Lib source code is released under GPL v3 License.
Our specific source codes for aes are released under the BSD License. See the LICENSE file in each source folder for more information. 


