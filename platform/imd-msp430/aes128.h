#ifndef AES128_H
#define AES128_H

#include <stdint.h>

void aes128_enc(uint8_t *plaintext, uint8_t *key, uint8_t *ciphertext);

#endif
