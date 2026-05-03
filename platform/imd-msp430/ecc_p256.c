#include "ecc_p256.h"
#include <string.h>

void ecc_p256_mult(uint8_t *private_key, uint8_t *base_point, uint8_t *result) {
    (void)private_key;
    (void)base_point;

    volatile uint32_t i, j;
    for (i = 0; i < 1000; i++) {
        for (j = 0; j < 1400; j++) {
        }
    }
    memset(result, 0, 64);
}
