#ifndef CRYPTO_PRIMITIVES_H
#define CRYPTO_PRIMITIVES_H

#include <stdint.h>

uint64_t get_cycle_count(void);
void start_timer(void);
uint64_t stop_timer(void);
double cycles_to_ms(uint64_t cycles);

void sha256_1kb(uint8_t *input, uint8_t *output);
void puf_simulate(uint8_t *serial_num, uint8_t *challenge, uint8_t *response);
void fuzzy_extractor(uint8_t *input, uint8_t *helper, uint8_t *key);
void ppp_proof_generation(uint8_t *secret, uint8_t *proof);
void mesap_proof_verification(uint8_t *proof, uint8_t *public_param, uint8_t *result);
void imdpp_proof_generation(uint8_t *secret, uint8_t *proof);
void ecc_p256_point_mult(uint8_t *private_key, uint8_t *base_point, uint8_t *result);
void aes128_encrypt(uint8_t *plaintext, uint8_t *key, uint8_t *ciphertext);

#endif
