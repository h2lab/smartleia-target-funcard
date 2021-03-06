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
direct access through `/dev/ttyACMx` with the toggle `USE_LEIA=True` as an environment variable, or using PCSC daemon either through a regular smart card reader
(or LEIA in PCSC relay mode) by using the toggle `USE_LEIA=False` as an environment variable:

```
$ USE_LEIA=False python3 pin_timing_attacks.py 
[+]??Using PCSC reader
...
$ USE_LEIA=True python3 pin_timing_attacks.py 
[+]??Using LEIA raw access
...
```


The`script-AES128-enc.py` tests AES-128 encryption and decryption APDUs: this can be a basis to mount some side-channel attacks on an unprotected
AES (NOTE: although some APDUs setting masks are present, these are not used and are here for future evolutions).

The `pin_timing_attacks.py` extracts a secret PIN from the programmed funcard using a **timing attack** that exploits the dummy algorithm
used to check the PIN. In order for this attack to succeed, a timing oracle is needed. Since such a timing oracle exploits variations
of less than milliseconds, a proper time measurement for APDUs is necessary. This script shows that LEIA's [timing feature](https://h2lab.github.io/smartleia.github.io/c/test.html#timers)
can be of use here: a regular smart card reader is not able to extract the secret (at least with the basic approach used using LEIA). You
can test LEIA's timing extraction with the `USE_LEIA=True`, and PCSC based (using a regular reader or LEIA in PCSC mode) using the
`USE_LEIA=False` toggle. The first one should extract the secret PIN successfully, while the second will not succeed.


# Handling the ATMega8515 internal triggers

For additional measurement precision, two dedicated triggers have been implemented in the ATMega8515 firmware
on the ISO7816-2 pins C4 and C8 (see the figure below). Beware that the C8 pin is shared with LEIA's onboard own
trigger.

These two pins are unused by the ISO7816-3 layer, and since they are connected to internal
pins of the ATMega8515 (PB5 and PB7), we can use them without perturbing the APDU communication with a reader (either
LEIA or any reader).

Two modes are proposed. In the first mode, the pins C4 and C8 are set high just before executing the AES, and set low after its execution.
In the second mode, the pins C4 and C8 are toggled at each AES round in order to isolate on the scope each round for a better
focus on the points of interest. You can play around with the ``trig_high_c4/8()``, ``trig_low_c4/8()`` and ``trig_inv_c4/8()`` functions
calls inside the AES (it is safe to call them from C and assembly).

```
      -------------+------------- 
     |   C1        |         C5  | 
     |             |             | 
     +-------\     |     /-------+ 
     |   C2   +----+    +    C6  | 
     |        |         |        | 
     +--------|         |--------+ 
     |   C3   |         |    C7  | 
     |        +----+----+        | 
     +-------/     |     \-------+ 
     |   C4=TRIG1  |    C8=TRIG2 | 
     |             |             | 
      -------------+------------- 
```

By default, the internal triggers are not active. You can specifically activate each one of them using the `00 20 00 00 02 XX YY` APDU
(class `0x00` and instruction `0x20`, with P1 and P2 set to `0x00` and two bytes data). `XX=0x01` will activate the
first trigger mode on C4 (trig C4 high when AES begins, low after). `XX=0x02` will activate the second trigger mode on C4
(toggle C4 at each AES round). `XX=0x00` will deactivate the trigger on C4. The same logic holds independently for the second
pin C8 using the valye `YY`.

You can get the actual current values of the triggers modes with the `00 21 00 00 02` APDU, getting two bytes from the card
representing the current mode on C4 and C8 respectively.

**WARNING:** using the internal trigger **C8** can perturb LEIA's own trigger set through the dedicated
trigger strategies. So use this internal trigger **with care** and if you know what you are doing!

# Licenses

SOSSE source codes are released under GPL v2 License. AVR-Crypto-Lib source code is released under GPL v3 License.
Our specific source codes for aes are released under the BSD License. See the LICENSE file in each source folder for more information. 


