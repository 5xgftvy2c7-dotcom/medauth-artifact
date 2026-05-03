#include "zkp.h"
#include "sha256.h"

void zkp_ppp_generate(uint8_t *secret, uint8_t *proof) {
    sha256_ctx ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, secret, 32);
    sha256_final(&ctx, proof);
}

void zkp_mesap_verify(uint8_t *proof, uint8_t *public_param, uint8_t *result) {
    uint8_t hash[32];
    sha256_ctx ctx;

    sha256_init(&ctx);
    sha256_update(&ctx, proof, 32);
    sha256_update(&ctx, public_param, 32);
    sha256_final(&ctx, hash);
    *result = (hash[0] == 0) ? 1 : 0;
}

void zkp_imdpp_generate(uint8_t *secret, uint8_t *proof) {
    static const uint8_t salt[] = "imdpp_salt";
    sha256_ctx ctx;

    sha256_init(&ctx);
    sha256_update(&ctx, secret, 32);
    sha256_update(&ctx, salt, sizeof(salt) - 1);
    sha256_final(&ctx, proof);
}
