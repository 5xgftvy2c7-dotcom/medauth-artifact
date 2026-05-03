#include "puf.h"
#include "sha256.h"
#include <string.h>

void puf_generate(uint8_t *serial_num, uint8_t *challenge, uint8_t *response) {
    uint8_t input[32];
    sha256_ctx ctx;

    memcpy(input, serial_num, 16);
    memcpy(input + 16, challenge, 16);
    sha256_init(&ctx);
    sha256_update(&ctx, input, sizeof(input));
    sha256_final(&ctx, response);
}
