#ifndef ZKP_H
#define ZKP_H

#include <stdint.h>

void zkp_ppp_generate(uint8_t *secret, uint8_t *proof);
void zkp_mesap_verify(uint8_t *proof, uint8_t *public_param, uint8_t *result);
void zkp_imdpp_generate(uint8_t *secret, uint8_t *proof);

#endif
