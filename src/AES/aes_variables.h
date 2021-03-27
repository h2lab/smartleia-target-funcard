#ifndef _AES_VARIABLE_H
#define _AES_VARIABLE_H

// Useful definitions
#define UCHAR   unsigned char
#define p_UCHAR unsigned char*


// global variables
#define AESKeySize                 16
#define AESInputSize               16
#define AESOutputSize              16
#define AESMaskSize                18 // 1 mask per state byte + 1 sbox input mask + 1 sbox output mask

// global variables for the input/output of AES128
UCHAR secret       [AESKeySize];
UCHAR input        [AESInputSize];
UCHAR mask         [AESMaskSize];

#endif
