/*
	Simple Operating System for Smartcard Education
	Copyright (C) 2002  Matthias Bruestle <m@mbsks.franken.de>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

/* $Id: main.c,v 1.31 2002/12/24 13:33:11 m Exp $ */

/*! @file
	\brief main() function with command loop.
*/

#include <config.h>
#include <commands.h>
#include <sw.h>
#include <hal.h>
#include <t0.h>
#include <trig.h>

unsigned char trig_activated_c4 = 0;
unsigned char trig_level_c4 = 0;
void trig_inv_c4(void)
{
	if(trig_level_c4 == 0){
		trig_high_c4();
		trig_level_c4 = 1;
	}
	else{
		trig_low_c4();
		trig_level_c4 = 0;
	}
}

unsigned char trig_activated_c8 = 0;
unsigned char trig_level_c8 = 0;
void trig_inv_c8(void)
{
	if(trig_level_c8 == 0){
		trig_high_c8();
		trig_level_c8 = 1;
	}
	else{
		trig_low_c8();
		trig_level_c8 = 0;
	}
}


/*! \brief Main function containing command interpreter loop.

	At the end of the loop, sw is sent as the status word.

	This function does never return.
*/
int main( void )
{
	iu8 i, len, b;

	/* TODO: On error? */
	hal_init();

	/* Send ATR */
	/* TODO: Possible from EEPROM? */
	hal_io_sendByteT0( 0x3B );

	/* Low trig level by default */
	trig_low_c4();
	trig_low_c8();

#if CONF_WITH_LOGGING==1
	log_init();
#endif

	resplen = 0;

	if( !(hal_eeprom_read( &len, ATR_LEN_ADDR, 1 ) &&
		(len<=ATR_MAXLEN)) )
		for(;;) {}

	for( i=1; i<len; i++ ) {
		if( !hal_eeprom_read( &b, ATR_ADDR+i, 1 ) ) for(;;) {}
		hal_io_sendByteT0( b );
	}

	/* Command loop */
	for(;;) {
		for( i=0; i<5; i++ ) {
			header[i] = hal_io_recByteT0();
		}

#if CONF_WITH_TRNG==1
		hal_rnd_addEntropy();
#endif

		if( header[0] ==CLA_PROP ) {
			switch( header[1] ) {
#if CONF_WITH_TESTCMDS==1
			case INS_WRITE:
				cmd_write();
				break;
			case INS_READ:
				cmd_read();
				break;
#endif /* CONF_WITH_TESTCMDS==1 */
			case INS_SELECT:
				cmd_select();
				break;
			case INS_SET_KEY:
				cmd_set_key();
				break;
			case INS_GET_KEY:
				cmd_get_key();
				break;
			case INS_SET_INPUT:
				cmd_set_input();
				break;
			case INS_GET_INPUT:
				cmd_get_input();
				break;
			case INS_SET_MASK:
				cmd_set_mask();
				break;
			case INS_GET_MASK:
				cmd_get_mask();
				break;
			case INS_SET_DIR:
				cmd_set_dir();
				break;
			case INS_SET_TYPE:
				cmd_set_type();
				break;
			case INS_AES128_GO:
#ifdef WITH_AES_TRIG
				if(trig_activated_c4 >= 1){
					trig_high_c4();
				}
				if(trig_activated_c8 >= 1){
					trig_high_c8();
				}
#endif /* WITH_AES_TRIG */
				cmd_aes128_go();
#ifdef WITH_AES_TRIG
				if(trig_activated_c4 >= 1){
					trig_low_c4();
				}
				if(trig_activated_c8 >= 1){
					trig_low_c8();
				}
#endif /* WITH_AES_TRIG */
				break;
			case INS_GET_OUTPUT:
				cmd_get_output();
				break;
			case INS_CHECK_PIN:
				cmd_check_pin();
				break;
#ifdef WITH_AES_TRIG
			case INS_CONF_TRIG:
				/* Activate or desactivate the internal triggers */
				cmd_conf_trig();
				break;
			case INS_GET_TRIG:
				/* Get the current internal triggers state */
				cmd_get_trig();
				break;
#endif
			default:
				sw_set( SW_WRONG_INS );
			}
		} else {
			sw_set( SW_WRONG_CLA );
		}

#if CONF_WITH_TRNG==1
		hal_rnd_addEntropy();
#endif

		/* Return the SW in sw */
		t0_sendSw();
	}
}

