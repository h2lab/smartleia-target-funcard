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

/*! @file
	\brief Commands.

	The documentation of the commands is on the main page of the doxygen
	documentation.

	$Id: commands.c,v 1.27 2003/03/30 12:42:21 m Exp $
*/

#include <hal.h>
#include <commands.h>
#include <config.h>
#include <log.h>
#include <stddef.h>
#include <string.h>
#include <sw.h>
#include <t0.h>
#include <tools.h>
#include <aes_variables.h>
#include <avrcryptolib/aes/aes-independant.h>

#ifdef __AVR__
#include <avr/io.h>
#endif /* __AVR__ */

/*! \brief Valid data in response array. Invalid if zero. */
iu8 resplen;
/*! \brief Data returned by Get Response command.

	The size of this array is the max. of sizeof(S_FINFO) and CRYPT_BLOCK_LEN.
*/
iu8 response[8];

#if CONF_WITH_TESTCMDS==1
void cmd_write( void )
{
	iu8 b, i;

	if( t0_testP3( 0x00 ) ) {
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* TODO: check for eeprom range */
	/* ACK */
	t0_sendAck();


	/* Receive */
	for( i=0; i<header[4]; i++ ) {
		///* ~ACK */
		//t0_sendCAck();

		/* Data */
		b = hal_io_recByteT0();

		if( !hal_eeprom_write( ((iu16)header[2]<<8)+header[3]+i, &b, 1 ) ) return;
	}

	sw_set( SW_OK );
}
#endif /* CONF_WITH_TESTCMDS==1 */

#if CONF_WITH_TESTCMDS==1
void cmd_read( void )
{
	iu16 i, max=header[4];
	iu8 b;

	/* TODO: check for eeprom range */

	/* ACK */
	t0_sendAck();

	if( !max ) max=256;
	for( i=0; i<max; i++ ) {
		if( !hal_eeprom_read( &b, (header[2]<<8)+header[3]+i, 1 ) ) return;

		/* Data */
		hal_io_sendByteT0( b );
	}

	/* SW */
	sw_set( SW_OK );
}
#endif /* CONF_WITH_TESTCMDS==1 */


/*! \brief Set the secret key in RAM.
*/
void cmd_set_key( void )
{
	
	if( t0_testP3( 0x00 ) ) {
		sw_set( SW_WRONG_LEN );
		return;
	}

	iu8 length=header[4];
	
	if(length>AESKeySize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	
	iu8 i, b;
	/* ACK */
	t0_sendAck();
	
	/* Receive */
	for( i=0; i<length; i++ ) {
		
		/* ~ACK */
		//t0_sendCAck();

		/* Data */
		b = hal_io_recByteT0();

		secret[i] = b;
	}
	
	/* ACK */
	//t0_sendAck();

	/* Initialize AES */
	aes_indep_init();
	
	/* Set key */
	aes_indep_key(secret);
	
	/* SW */
	sw_set( SW_OK );
}

/*! \brief Get the secret key stored in RAM.
*/
void cmd_get_key( void )
{
	iu16 i, length=header[4];
	iu8 b;
	
	if(length == 0){
		length = AESKeySize;
	}	
	if(length>AESKeySize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	for( i=0; i<length; i++ ) {
		b = secret[i];

		/* Data */
		hal_io_sendByteT0( b );
	}

	/* SW */
	sw_set( SW_OK );
}

/*! \brief Set the cipher input in RAM.
*/
void cmd_set_input( void )
{
	if( t0_testP3( 0x00 ) ) {
		sw_set( SW_WRONG_LEN );
		return;
	}

	iu8 length=header[4];
	
	if(length>AESInputSize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	
	iu8 i, b;
	/* ACK */
	t0_sendAck();
	
	/* Receive */
	for( i=0; i<length; i++ ) {
		
		/* ~ACK */
		//t0_sendCAck();

		/* Data */
		b = hal_io_recByteT0();

		input[i] = b;
	}
	
	/* ACK */
	//t0_sendAck();
	
	/* SW */
	sw_set( SW_OK );
}

/*! \brief Get the cipher input stored in RAM.
*/
void cmd_get_input( void )
{
	iu16 i, length=header[4];
	iu8 b;
	
	if(length == 0){
		length = AESInputSize;
	}
	if(length>AESInputSize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	for( i=0; i<length; i++ ) {
		b = input[i];

		/* Data */
		hal_io_sendByteT0( b );
	}

	/* SW */
	sw_set( SW_OK );
}

/*! \brief Set the masks values in RAM.
*/
void cmd_set_mask( void )
{
	
	if( t0_testP3( 0x00 ) ) {
		sw_set( SW_WRONG_LEN );
		return;
	}

	iu8 length=header[4];
	
	if(length>AESMaskSize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	
	iu8 i, b;
	/* ACK */
	t0_sendAck();
	
	/* Receive */
	for( i=0; i<length; i++ ) {
		
		/* ~ACK */
		//t0_sendCAck();

		/* Data */
		b = hal_io_recByteT0();

		mask[i] = b;
	}
	
	/* ACK */
	//t0_sendAck();
	
	/* SW */
	sw_set( SW_OK );
}

/*! \brief Get the mask values stored in RAM.
*/
void cmd_get_mask( void )
{
	iu16 i, length=header[4];
	iu8 b;

	if(length == 0){
		length = AESMaskSize;
	}
	if(length>AESMaskSize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	/* ACK */
	t0_sendAck();

	for( i=0; i<length; i++ ) {
		b = mask[i];

		/* Data */
		hal_io_sendByteT0( b );
	}

	/* SW */
	sw_set( SW_OK );
}


static iu8 dir = 0;
void cmd_set_dir(void)
{	
	iu16 length=header[4];
	if(length!=1){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	/* ACK */
	t0_sendAck();
	/* Receive */
	dir = hal_io_recByteT0() & 0x1;

	/* SW */
	sw_set( SW_OK );
}

void cmd_set_type(void)
{
	iu16 length=header[4];
	if(length!=1){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	/* ACK */
	t0_sendAck();

	/* SW */
	sw_set( SW_OK );
}

/*! \brief Launch AES-128 encryption or decryption
*/
void cmd_aes128_go( void )
{
        
	iu16 length=header[4];
	
	if(length!=0){ 
		sw_set( SW_WRONG_LEN );
		return;
	}
	if(dir == 0){
		aes_indep_enc(input);
	}
	else{
		aes_indep_dec(input);
	}

	/* ACK */
	//t0_sendAck();
	
	/* SW */
	sw_set( SW_OK );
}

/*! \brief Get the cipher output stored in RAM.
*/
void cmd_get_output( void )
{
	iu16 i, length=header[4];
	iu8 b;
	
	if(length == 0){
		length = AESOutputSize;
	}
	if(length>AESOutputSize){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	for( i=0; i<length; i++ ) {
		b = input[i];

		/* Data */
		hal_io_sendByteT0( b );
	}

	/* SW */
	sw_set( SW_OK );
}

void cmd_getResponse( void )
{
	iu8 i;

	if( resplen==0 ) {
		sw_set( SW_WRONG_CONDITION );
		return;
	}

	if( !t0_testP3( resplen ) ) {
		if( (header[4]>resplen) || (!header[4]) ) {
			sw_set( SW_WRONG_LE|resplen );
			return;
		}
		/* User want's not all data */
		resplen=header[4];
	}

	if( !t0_testP1P2( 0x0000 ) ) return;

	/* ACK */
	t0_sendAck();

	/* Data */
	for( i=0; i<resplen; i++ ) {
		hal_io_sendByteT0( response[i] );
	}

	sw_set( SW_OK );
}

void cmd_select( void )
{
	sw_set( SW_OK );
}

/*! \brief Check a static PIN.
*/
static iu8 PIN[] = "secret!";
static iu8 PIN_to_check[32] = { 0 };
void cmd_check_pin ( void )
{
	iu16 i, j, length=header[4];
	
	/* Check PIN size */
	if(length != sizeof(PIN)){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	/* Get the PIN to check */
	for( i=0; i<length; i++ ) {
		PIN_to_check[i] = hal_io_recByteT0();
	}

	/* Check the PIN */
	for ( i=0; i<length; i++ ) {
  		for(j = 0; j < 100; j++){ asm("nop");};
		if(PIN_to_check[i] != PIN[i]){
			sw_set ( SW_WRONG_LEN);
			return;
		}
	}
	/* SW */
	sw_set( SW_OK );
}

#ifdef WITH_AES_TRIG
extern unsigned char trig_activated;
void cmd_conf_trig(void)
{
	iu16 length=header[4];
	
	if(length!=1){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	/* Set trigger to value */
	trig_activated = hal_io_recByteT0();

	/* SW */
	sw_set( SW_OK );	
}

void cmd_get_trig(void)
{
	iu16 length=header[4];
	
	if(length!=1){ 
		sw_set( SW_WRONG_LEN );
		return;
	}

	/* ACK */
	t0_sendAck();

	/* Data */
	hal_io_sendByteT0( trig_activated );

	/* SW */
	sw_set( SW_OK );
}

#endif
