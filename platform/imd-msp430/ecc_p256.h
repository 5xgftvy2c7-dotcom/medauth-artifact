#ifndef ECC_P256_H
#define ECC_P256_H

#include <stdint.h>

void ecc_p256_mult(uint8_t *private_key, uint8_t *base_point, uint8_t *result);

#endif
