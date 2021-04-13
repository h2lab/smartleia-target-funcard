#include <config.h>

;       .arch   at90s8515
        .arch   atmega16
; TRIG PIN C4 is PB5
TRIG_PIN_C4=5
; TRIG PIN C4 is PB7
TRIG_PIN_C8=7
PINB=0x16
DDRB=0x17
PORTB=0x18
        .text
        .global trig_high_c4, trig_low_c4, trig_high_c8, trig_low_c8

trig_low_c4:
        ; Set OUT direction
        sbi             DDRB, TRIG_PIN_C4
	; Signal low
	cbi             PORTB, TRIG_PIN_C4
	ret

trig_high_c4:
        ; Set OUT direction
        sbi             DDRB, TRIG_PIN_C4
	; Signal low
	sbi             PORTB, TRIG_PIN_C4
	ret

trig_low_c8:
        ; Set OUT direction
        sbi             DDRB, TRIG_PIN_C8
	; Signal low
	cbi             PORTB, TRIG_PIN_C8
	ret

trig_high_c8:
        ; Set OUT direction
        sbi             DDRB, TRIG_PIN_C8
	; Signal low
	sbi             PORTB, TRIG_PIN_C8
	ret

