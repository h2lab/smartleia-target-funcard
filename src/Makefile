###############################################################################
# Makefile for the project maskedAES
###############################################################################

#ARCH=at90s2323
#ARCH=at90s8515
#ARCH=at90s8535
#ARCH=atmega161
#ARCH=atmega163
ARCH=atmega8515

CC=avr-gcc -mmcu=$(ARCH)
AS=avr-as 
OBJCOPY=avr-objcopy
SIZE=avr-size

SOSSE_CFLAGS+=-Wall -mcall-prologues -fpack-struct -O0 -funsigned-char -funsigned-bitfields -fshort-enums -DCONF_WITH_TESTCMDS=1 -DWITH_AES_TRIG
SOSSE_ASFLAGS=-Wall

AES_CFLAGS+=-Wall -mcall-prologues -fpack-struct -Os -funsigned-char -funsigned-bitfields -fshort-enums -DAVRCRYPTOLIB -DWITH_AES_TRIG
AES_ASFLAGS=-Wall

DATE=`date +'%d%m%y-%H%M%S'`

BUILD_DIR = build
SOSSE_DIR = SOSSE
AES_DIR = AES

all: clean sosse aes eedata

clean: sosse_clean aes_clean eedata_clean


###### SOSSE ##################################################################
# SOSSE OS objects compilation
SOSSE_SRC =  $(wildcard $(SOSSE_DIR)/*.c)
SOSSE_SRC += $(wildcard $(SOSSE_DIR)/*.S)
SOSSE_SRC += $(wildcard $(SOSSE_DIR)/*.s)

SOSSE_OBJ =  $(patsubst %.c, %.o, $(wildcard $(SOSSE_DIR)/*.c))
SOSSE_OBJ += $(patsubst %.S, %.o, $(wildcard $(SOSSE_DIR)/*.S))
SOSSE_OBJ += $(patsubst %.s, %.o, $(wildcard $(SOSSE_DIR)/*.s))

$(SOSSE_DIR)/%.o: $(SOSSE_DIR)/%.c
	$(CC) $(SOSSE_CFLAGS) -I$(SOSSE_DIR) -c $< -o $@

$(SOSSE_DIR)/%.o: $(SOSSE_DIR)/%.S
	$(CC) $(SOSSE_CFLAGS) -I$(SOSSE_DIR) -c $< -o $@

$(SOSSE_DIR)/%.o: $(SOSSE_DIR)/%.s
	$(AS) $(SOSSE_ASFLAGS) -I$(SOSSE_DIR) $< -o $@

sosse: $(SOSSE_OBJ)

sosse_clean:
	@rm -f $(SOSSE_DIR)/*.o
	@rm -f $(SOSSE_DIR)/*.map

###### AES ##################################################################
# AES objects compilation
AES_SRC =  $(wildcard $(AES_DIR)/*.c)
AES_SRC += $(wildcard $(AES_DIR)/*.S)
# AVR cryptolib
AES_SRC += $(wildcard $(AES_DIR)/avrcryptolib/aes/*.c)
AES_SRC += $(wildcard $(AES_DIR)/avrcryptolib/aes/*.S)

AES_OBJ =  $(patsubst %.c, %.o, $(wildcard $(AES_DIR)/*.c))
AES_OBJ += $(patsubst %.S, %.o, $(wildcard $(AES_DIR)/*.S))
AES_OBJ += $(patsubst %.c, %.o, $(wildcard $(AES_DIR)/avrcryptolib/aes/*.c))
AES_OBJ += $(patsubst %.S, %.o, $(wildcard $(AES_DIR)/avrcryptolib/aes/*.S))

AES_BIN = aes

$(AES_DIR)/%.o: $(AES_DIR)/%.c
	$(CC) $(AES_CFLAGS) -I$(SOSSE_DIR) -I$(AES_DIR) -c $< -o $@

$(AES_DIR)/%.o: $(AES_DIR)/%.S
	$(CC) $(AES_CFLAGS) -I$(SOSSE_DIR) -I$(AES_DIR) -c $< -o $@

aes: $(AES_OBJ) sosse
	@mkdir -p $(BUILD_DIR)
	$(CC) -Wl,-Map,$(SOSSE_DIR)/sosse.map -o $(BUILD_DIR)/$(AES_BIN) $(filter-out $(SOSSE_DIR)/eedata.o, $(SOSSE_OBJ)) $(AES_OBJ)
	$(SIZE) $(BUILD_DIR)/$(AES_BIN)
	$(OBJCOPY) -O binary $(BUILD_DIR)/$(AES_BIN) $(BUILD_DIR)/$(AES_BIN).bin
	$(OBJCOPY) -O ihex $(BUILD_DIR)/$(AES_BIN) $(BUILD_DIR)/$(AES_BIN).hex
	$(OBJCOPY) -O ihex $(BUILD_DIR)/$(AES_BIN) $(BUILD_DIR)/$(AES_BIN)-$(DATE).hex
	@rm -f $(BUILD_DIR)/$(AES_BIN).bin $(BUILD_DIR)/$(AES_BIN).hex

aes_clean:
	@rm -f $(AES_DIR)/*.o
	@rm -f $(AES_DIR)/avrcryptolib/aes/*.o
	@rm -f $(BUILD_DIR)/$(AES_BIN)*

###### EEDATA #################################################################
EEDATA_SRC = $(SOSSE_DIR)/eedata.S
EEDATA_BIN = eedata

eedata:
	$(CC) $(SOSSE_ASFLAGS) -c -o $(BUILD_DIR)/$(EEDATA_BIN) -I$(SOSSE_DIR) -DDAY=0x`date +%d` -DMONTH=0x`date +%m` -DYEAR=0x`date +%y` $(EEDATA_SRC)
	$(OBJCOPY) -O binary $(BUILD_DIR)/$(EEDATA_BIN) $(BUILD_DIR)/$(EEDATA_BIN).bin
	$(OBJCOPY) -O ihex $(BUILD_DIR)/$(EEDATA_BIN) $(BUILD_DIR)/$(EEDATA_BIN).hex
	$(OBJCOPY) -O ihex $(BUILD_DIR)/$(EEDATA_BIN) $(BUILD_DIR)/$(EEDATA_BIN)-$(DATE).hex
	@rm -f $(BUILD_DIR)/$(EEDATA_BIN).bin $(BUILD_DIR)/$(EEDATA_BIN).hex

eedata_clean:
	@rm -f $(BUILD_DIR)/$(EEDATA_BIN)*
