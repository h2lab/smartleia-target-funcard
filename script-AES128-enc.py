#!/usr/bin/python

"""
This script shows how to communicate with the Masked AES on ATMega8515 smartcard chip.

"""



####################################################################################################
####################################################################################################
####################################################################################################
# import some libraries

from smartcard.System import readers
from smartcard.ATR import ATR
from smartcard.util import BinStringToHexList, HexListToBinString, toHexString, toBytes
from Crypto.Cipher import AES
from random import randint
import sys, os
import binascii

import smartleia as sl

USE_LEIA = os.getenv("USE_LEIA")
if USE_LEIA == "False":
	print("[+] Using PCSC reader")
	USE_LEIA = False
else:
	print("[+] Using LEIA raw access")
	USE_LEIA = True

####################################################################################################
####################################################################################################
####################################################################################################
# APDU commands for AES

### APDU command to Read/Write EEPROM
l_APDUSOSSEReadEEPROM  = [0x00, 0xaa]
l_APDUSOSSEWriteEEPROM = [0x00, 0xbb]

### APDU command to Set/Get AES Key
l_APDUSOSSESetKey = [0x00, 0x11]
l_APDUSOSSEGetKey = [0x00, 0x15]

### APDU command to Set/Get AES Input
l_APDUSOSSESetInput = [0x00, 0x12]
l_APDUSOSSEGetInput = [0x00, 0x16]

### APDU command to Set/Get AES Mask
l_APDUSOSSESetMask = [0x00, 0x19]
l_APDUSOSSEGetMask = [0x00, 0x1a]

### APDU command to Get AES Ouput
l_APDUSOSSEGetOutput = [0x00, 0x13]

### APDU command to launch AES encryption
l_APDUSOSSEAESEnc = [0x00, 0x14]

### APDU command to set DIR
l_APDUSOSSEAESSetDir = [0x00, 0x17]

### APDU command to set internal trigger
# 0x00 = no trigger, 0x01 = trig high on AES
# 0x02 = toggle trig every AES round
l_APDUSOSSEAESSetTrigMode = [0x00, 0x20]
l_APDUSOSSEAESGetTrigMode = [0x00, 0x21]


def set_trig_mode(trig_mode_c4=0x00, trig_mode_c8=0x00):
	print("Set Trig mode")
	# build complete Read APDU
	l_APDUSOSSEAESSetTrigMode_complete = []
	l_APDUSOSSEAESSetTrigMode_complete += l_APDUSOSSEAESSetTrigMode
	# unused P1
	l_APDUSOSSEAESSetTrigMode_complete.append(0)
	# unused P2
	l_APDUSOSSEAESSetTrigMode_complete.append(0)
	# Trig mode length
	l_APDUSOSSEAESSetTrigMode_complete.append(0x02)
	# Trig mode values (for C4 and C8 pins)
	l_APDUSOSSEAESSetTrigMode_complete.append(trig_mode_c4)
	l_APDUSOSSEAESSetTrigMode_complete.append(trig_mode_c8)
	
	print("send APDU: %s" % toHexString(l_APDUSOSSEAESSetTrigMode_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEAESSetTrigMode_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEAESSetTrigMode_complete)
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))

def get_trig_mode():
	print("Get Trig mode")
	# build complete Read APDU
	l_APDUSOSSEAESGetTrigMode_complete = []
	l_APDUSOSSEAESGetTrigMode_complete += l_APDUSOSSEAESGetTrigMode
	# unused P1
	l_APDUSOSSEAESGetTrigMode_complete.append(0)
	# unused P2
	l_APDUSOSSEAESGetTrigMode_complete.append(0)
	# Trig mode length
	l_APDUSOSSEAESGetTrigMode_complete.append(0x02)
	
	print("send APDU: %s" % toHexString(l_APDUSOSSEAESGetTrigMode_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEAESGetTrigMode_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEAESGetTrigMode_complete)
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	return response

def run_aes(l_secretKey,l_input,l_mask, direction=0):

	lengthKey  = len(l_secretKey)
	lengthInput= len(l_input)
	lengthMask = len(l_mask)
        
	print("Set Dir")
	# build complete Read APDU
	l_APDUSOSSESetDir_complete = []
	l_APDUSOSSESetDir_complete += l_APDUSOSSEAESSetDir
	# unused P1
	l_APDUSOSSESetDir_complete.append(0)
	# unused P2
	l_APDUSOSSESetDir_complete.append(0)
	# Dir length
	l_APDUSOSSESetDir_complete.append(0x01)
	# Dir value (encrypt or decrypt)
	l_APDUSOSSESetDir_complete.append(direction)

	print("send APDU: %s" % toHexString(l_APDUSOSSESetDir_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSESetDir_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSESetDir_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	##################################################
	# send Write Command
	print("Set Key")
	
	# build complete Read APDU
	l_APDUSOSSESetKey_complete = []
	l_APDUSOSSESetKey_complete += l_APDUSOSSESetKey 
	# unused P1
	l_APDUSOSSESetKey_complete.append(0)
	# unused P2
	l_APDUSOSSESetKey_complete.append(0)
	# key length
	l_APDUSOSSESetKey_complete.append(lengthKey)
	# key value
	l_APDUSOSSESetKey_complete += l_secretKey
	 
	# send Write APDU
	print("send APDU: %s" % toHexString(l_APDUSOSSESetKey_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSESetKey_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSESetKey_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Read Command
	print("Read Key")
	
	# build complete Read APDU
	l_APDUSOSSEGetKey_complete = []
	l_APDUSOSSEGetKey_complete += l_APDUSOSSEGetKey 
	# unused P1
	l_APDUSOSSEGetKey_complete.append(0)
	# unused P2
	l_APDUSOSSEGetKey_complete.append(0)
	# key length
	l_APDUSOSSEGetKey_complete.append(lengthKey)
	
	# send Read APDU
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEGetKey_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEGetKey_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Write Command
	print("Set Input")
	
	# build complete Read APDU
	l_APDUSOSSESetInput_complete = []
	l_APDUSOSSESetInput_complete += l_APDUSOSSESetInput 
	# unused P1
	l_APDUSOSSESetInput_complete.append(0)
	# unused P2
	l_APDUSOSSESetInput_complete.append(0)
	# input length
	l_APDUSOSSESetInput_complete.append(lengthInput)
	# input value
	l_APDUSOSSESetInput_complete += l_input
	 
	# send Write APDU
	print("send APDU: %s" % toHexString(l_APDUSOSSESetInput_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSESetInput_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSESetInput_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Read Command
	print("Read Input")
	
	# build complete Read APDU
	l_APDUSOSSEGetInput_complete = []
	l_APDUSOSSEGetInput_complete += l_APDUSOSSEGetInput 
	# unused P1
	l_APDUSOSSEGetInput_complete.append(0)
	# unused P2
	l_APDUSOSSEGetInput_complete.append(0)
	# input length
	l_APDUSOSSEGetInput_complete.append(lengthInput)
	
	# send Read APDU
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEGetInput_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEGetInput_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Write Command
	print("Set Mask")
	
	# build complete Read APDU
	l_APDUSOSSESetMask_complete = []
	l_APDUSOSSESetMask_complete += l_APDUSOSSESetMask 
	# unused P1
	l_APDUSOSSESetMask_complete.append(0)
	# unused P2
	l_APDUSOSSESetMask_complete.append(0)
	# mask length
	l_APDUSOSSESetMask_complete.append(lengthMask)
	# mask value
	l_APDUSOSSESetMask_complete += l_mask
	 
	# send Write APDU
	print("send APDU: %s" % toHexString(l_APDUSOSSESetMask_complete))
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSESetMask_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSESetMask_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Read Command
	print("Read Mask")
	
	# build complete Read APDU
	l_APDUSOSSEGetMask_complete = []
	l_APDUSOSSEGetMask_complete += l_APDUSOSSEGetMask 
	# unused P1
	l_APDUSOSSEGetMask_complete.append(0)
	# unused P2
	l_APDUSOSSEGetMask_complete.append(0)
	# mask length
	l_APDUSOSSEGetMask_complete.append(lengthMask)
	
	# send Read APDU
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEGetMask_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEGetMask_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Launch AES Command
	print("Launch AES 128")
	
	# build complete Read APDU
	l_APDUSOSSEAESEnc_complete = []
	l_APDUSOSSEAESEnc_complete += l_APDUSOSSEAESEnc 
	# unused P1
	l_APDUSOSSEAESEnc_complete.append(0)
	# unused P2
	l_APDUSOSSEAESEnc_complete.append(0)
	# unused P3
	l_APDUSOSSEAESEnc_complete.append(0)
	
	# send Read APDU
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEAESEnc_complete))
		response = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		response,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEAESEnc_complete)
	
	print("data: %s" % toHexString(response))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# send Read Command
	print("Read Output")
	
	# build complete Read APDU
	l_APDUSOSSEGetOutput_complete = []
	l_APDUSOSSEGetOutput_complete += l_APDUSOSSEGetOutput 
	# unused P1
	l_APDUSOSSEGetOutput_complete.append(0)
	# unused P2
	l_APDUSOSSEGetOutput_complete.append(0)
	# output length
	l_APDUSOSSEGetOutput_complete.append(lengthInput)
	
	# send Read APDU
	if USE_LEIA == True:
		r = reader.send_APDU(sl.create_APDU_from_bytes(l_APDUSOSSEGetOutput_complete))
		ciphertext = r.data
		sw1 = r.sw1
		sw2 = r.sw2
	else:
		ciphertext,sw1,sw2 = o_deviceConnection.transmit(l_APDUSOSSEGetOutput_complete)
	
	print("data: %s" % toHexString(ciphertext))
	print("sw  : %s" % toHexString([sw1]) + toHexString([sw2]))
	
	
	##################################################
	# check encryption
	
	# transform the key in binary string
	keyBinaryString = HexListToBinString(l_secretKey)
	
	# define size of key
	if sys.version_info.major == 3
		AES.key_size = (lengthKey,)
	else:
		AES.key_size = lengthKey
	
	# create an AES engine in ECB mode
	o_cryptoEngine = AES.new(bytes(l_secretKey), AES.MODE_ECB)
	
	# allocate memory for ciphertext2
	ciphertext2 = [0]*lengthInput
	
	# compute the expected ciphertext
	if direction == 0:
		ciphertext2 = o_cryptoEngine.encrypt(bytes(l_input))
	else:
		ciphertext2 = o_cryptoEngine.decrypt(bytes(l_input))
	
	# display
	print("\n")
	if direction == 0:
		print("--- AES128 encryption ---")
	else:
		print("--- AES128 decryption ---")
	print("plaintext : %s" % toHexString(l_input))
	print("key       : %s" % toHexString(l_secretKey))
	print("mask      : %s" % toHexString(l_mask))
	print("ciphertext: %s" % toHexString(ciphertext))
	out = ""
	for b in ciphertext2:
		out += ("%02X " % b)
	print("checking  : "+out)

	# check that ciphertext computed by the card is equal to ciphertext computed in Python
	if(bytes(ciphertext) == ciphertext2):
		print("operation ok :-)")
		print("\n")
		return 0
	else:
		print("operation ko :-(")
		print("\n")
		return 1

####################################################################################################
####################################################################################################
####################################################################################################
# example of a use of AES 128

##################################################
# open connection with the smartcard


if USE_LEIA == True:
        reader = sl.LEIA('/dev/ttyACM0')
        reader.configure_smartcard(sl.T.T0, negotiate_pts=False)
else:
	# get list of available smartcard reader(s)
	l_listReaders = readers()

	# by default the chosen reader is the first one in the reader list, 
	# in case this should be modified, the reader number can be given in 
	# a unique argument of the python script.
	readerNum = 0;
	if (len(sys.argv) == 2):
		readerNum = int(sys.argv[1]);
		# open a connection with the asked  smartcard reader
		o_deviceConnection = l_listReaders[readerNum].createConnection()
		# open a connection with the smartcard chip
		o_deviceConnection.connect()
	else:
		for readerNum in range(0, len(l_listReaders)):
			try:
				# open a connection with the first available smartcard reader answering
				o_deviceConnection = l_listReaders[readerNum].createConnection()
				# open a connection with the smartcard chip
				o_deviceConnection.connect()
			except:
				continue
			print("[+] Using reader %d" % readerNum)
			break


##################################################
# run the AES

# generate random inputs
l_secretKey = [0]*16
l_input     = [0]*16
l_mask      = [0]*18

for i in range(16):
    l_secretKey[i] = randint(0,255)
    l_input[i] = randint(0,255)
    l_mask[i] = randint(0,255)
l_mask[16] = randint(0,255)
l_mask[17] = randint(0,255)

# Optional: set the internal trig mode (0x01 or 0x02, 0x00 to disable)
# WARNING: this internal trig can of course perturb LEIA's own triggers
# set through the trigger strategy, so be careful when dealing with it.
#set_trig_mode(0x02, 0x02)
#get_trig_mode()
# run the aes
# Encrypt
run_aes(l_secretKey,l_input,l_mask,0)
# Decrypt
run_aes(l_secretKey,l_input,l_mask,1)

if USE_LEIA == False:
	##################################################
	# close connection with the smartcard
	o_deviceConnection.disconnect()
