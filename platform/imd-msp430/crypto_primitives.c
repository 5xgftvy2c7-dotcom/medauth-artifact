#include "crypto_primitives.h"
#include "aes128.h"
#include "ecc_p256.h"
#include "puf.h"
#include "sha256.h"
#include "zkp.h"
#include <time.h>

static clock_t timer_start;
static uint64_t last_cycles;

uint64_t get_cycle_count(void) {
    return last_cycles;
}

void start_timer(void) {
    timer_start = clock();
}

uint64_t stop_timer(void) {
    clock_t elapsed = clock() - timer_start;
    last_cycles = (uint64_t)(((double)elapsed * 16000000.0) / (double)CLOCKS_PER_SEC);
    return last_cycles;
}

double cycles_to_ms(uint64_t cycles) {
    return (double)cycles / 16000.0;
}

void sha256_1kb(uint8_t *input, uint8_t *output) {
    sha256_ctx ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, input, 1024);
    sha256_final(&ctx, output);
}

void puf_simulate(uint8_t *serial_num, uint8_t *challenge, uint8_t *response) {
    puf_generate(serial_num, challenge, response);
}

void fuzzy_extractor(uint8_t *input, uint8_t *helper, uint8_t *key) {
    uint8_t buffer[64];
    sha256_ctx ctx;

    for (int i = 0; i < 32; i++) {
        buffer[i] = input[i] ^ helper[i];
        buffer[i + 32] = helper[i];
    }
    sha256_init(&ctx);
    sha256_update(&ctx, buffer, sizeof(buffer));
    sha256_final(&ctx, key);
}

void ppp_proof_generation(uint8_t *secret, uint8_t *proof) {
    zkp_ppp_generate(secret, proof);
}

void mesap_proof_verification(uint8_t *proof, uint8_t *public_param, uint8_t *result) {
    zkp_mesap_verify(proof, public_param, result);
}

void imdpp_proof_generation(uint8_t *secret, uint8_t *proof) {
    zkp_imdpp_generate(secret, proof);
}

void ecc_p256_point_mult(uint8_t *private_key, uint8_t *base_point, uint8_t *result) {
    ecc_p256_mult(private_key, base_point, result);
}

void aes128_encrypt(uint8_t *plaintext, uint8_t *key, uint8_t *ciphertext) {
    aes128_enc(plaintext, key, ciphertext);
}
