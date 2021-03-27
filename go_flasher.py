import smartleia as sl

try:
    reader = sl.LEIA('/dev/ttyACM0')
except:
    reader = sl.LEIA('/dev/ttyACM1')

# Go to flasher mode
reader.flasher()
