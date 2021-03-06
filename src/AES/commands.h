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
	\brief Command declarations.

	The documentation of the commands is on the main page of the doxygen
	documentation.

	$Id: commands.h,v 1.15 2002/12/22 15:42:55 m Exp $
*/
#include <types.h>

#ifndef SOSSE_COMMANDS_H
#define SOSSE_COMMANDS_H

#define CLA_PROP			0x00	//!< CLA byte: Proprietary

#define INS_WRITE			0xaa	//!< INS byte: Write EEPROM
#define INS_READ			0xbb	//!< INS byte: Read EEPROM

#define INS_SET_KEY			0x11	//!< INS byte: set key
#define INS_GET_KEY			0x15	//!< INS byte: get key
#define INS_SET_INPUT			0x12	//!< INS byte: set input
#define INS_GET_INPUT			0x16	//!< INS byte: get input

#define INS_SET_DIR			0x17	//!< INS byte: set direction
#define INS_SET_TYPE			0x18	//!< INS byte: set key type

#define INS_SET_MASK			0x19	//!< INS byte: set masks
#define INS_GET_MASK			0x1a	//!< INS byte: get masks

#define INS_AES128_GO			0x14	//!< INS byte: launch AES operation

#define INS_GET_OUTPUT			0x13	//!< INS byte: get output

#define INS_GET_RESPONSE		0xC0	//!< INS byte: get response

#define INS_SELECT			0xA4	//!< INS byte: select applet

#define INS_CHECK_PIN			0x1b	//!< INS byte: check pin

#ifdef WITH_AES_TRIG
#define INS_CONF_TRIG			0x20    //!<INS byte: configure trigger mode
#define INS_GET_TRIG			0x21    //!<INS byte: get trigger mode
#endif

/*! \brief Valid data in response array. Invalid if zero. */
extern iu8 resplen;

/*! \brief Write EEPROM. (Test command)
*/
void cmd_write( void );
/*! \brief Read EEPROM. (Test command)
*/
void cmd_read( void );

/*! \brief Set the secret key in RAM.
*/
void cmd_set_key( void );

/*! \brief Get the secret key stored in RAM.
*/
void cmd_get_key( void );

/*! \brief Set the cipher input in RAM.
*/
void cmd_set_input( void );

/*! \brief Get the cipher input stored in RAM.
*/
void cmd_get_input( void );

/*! \brief Set the masks values in RAM.
*/
void cmd_set_mask( void );

/*! \brief Get the mask values stored in RAM.
*/
void cmd_get_mask( void );

/*! \brief Launch AES-128 encryption or decryption.
*/
void cmd_aes128_go( void );

/*! \brief Get the cipher output stored in RAM.
*/
void cmd_get_output( void );


void cmd_set_dir( void );

void cmd_set_type( void );

void cmd_select( void );

void cmd_check_pin( void );

/*! \brief Get Response.
*/
void cmd_getResponse( void );

#ifdef WITH_AES_TRIG
void cmd_conf_trig(void);
void cmd_get_trig(void);
#endif

#endif /* SOSSE_COMMANDS_H */
