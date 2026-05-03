#ifndef PUF_H
#define PUF_H

#include <stdint.h>

void puf_generate(uint8_t *serial_num, uint8_t *challenge, uint8_t *response);

#endif
