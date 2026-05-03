#include "crypto_primitives.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef RUNS
#define RUNS 100
#endif

#define SERIAL_NUM_LEN 16
#define CHALLENGE_LEN 16
#define RESPONSE_LEN 32

static FILE *open_log(const char *name) {
    char path[128];
    snprintf(path, sizeof(path), "../../raw-data/imd_%s.log", name);
    FILE *log = fopen(path, "w");
    if (log == NULL) {
        perror(path);
        exit(1);
    }
    return log;
}

static void test_primitive(const char *name, void (*func)(void)) {
    FILE *log = open_log(name);
    double latency[RUNS];
    double sum = 0.0;
    double sum_sq = 0.0;

    func();
    for (int i = 0; i < RUNS; i++) {
        start_timer();
        func();
        latency[i] = cycles_to_ms(stop_timer());
        fprintf(log, "%.6f\n", latency[i]);
        sum += latency[i];
        sum_sq += latency[i] * latency[i];
    }

    fclose(log);
    double mean = sum / RUNS;
    double variance = (sum_sq / RUNS) - (mean * mean);
    double stddev = sqrt(variance < 0 ? 0 : variance);
    printf("[IMD] %s: %.4f +/- %.4f ms\n", name, mean, stddev);
}

static uint8_t input_1kb[1024] = {0};
static uint8_t sha256_out[32] = {0};
static void test_sha256(void) { sha256_1kb(input_1kb, sha256_out); }

static uint8_t serial_num[SERIAL_NUM_LEN] = {0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0x0C,0x0D,0x0E,0x0F,0x10};
static uint8_t challenge[CHALLENGE_LEN] = {0};
static uint8_t puf_out[RESPONSE_LEN] = {0};
static void test_puf(void) { puf_simulate(serial_num, challenge, puf_out); }

static uint8_t fuzzy_input[32] = {0};
static uint8_t fuzzy_helper[32] = {0};
static uint8_t fuzzy_key[32] = {0};
static void test_fuzzy_extractor(void) { fuzzy_extractor(fuzzy_input, fuzzy_helper, fuzzy_key); }

static uint8_t ppp_secret[32] = {0};
static uint8_t ppp_proof[64] = {0};
static void test_ppp_proof(void) { ppp_proof_generation(ppp_secret, ppp_proof); }

static uint8_t mesap_proof[64] = {0};
static uint8_t mesap_param[32] = {0};
static uint8_t mesap_res[1] = {0};
static void test_mesap_verification(void) { mesap_proof_verification(mesap_proof, mesap_param, mesap_res); }

static uint8_t imdpp_secret[32] = {0};
static uint8_t imdpp_proof[64] = {0};
static void test_imdpp_proof(void) { imdpp_proof_generation(imdpp_secret, imdpp_proof); }

static uint8_t ecc_priv[32] = {0};
static uint8_t ecc_base[64] = {0};
static uint8_t ecc_res[64] = {0};
static void test_ecc(void) { ecc_p256_point_mult(ecc_priv, ecc_base, ecc_res); }

static uint8_t aes_plain[16] = {0};
static uint8_t aes_key[16] = {0};
static uint8_t aes_cipher[16] = {0};
static void test_aes(void) { aes128_encrypt(aes_plain, aes_key, aes_cipher); }

int main(void) {
    test_primitive("sha256", test_sha256);
    test_primitive("puf", test_puf);
    test_primitive("fuzzy_extractor", test_fuzzy_extractor);
    test_primitive("ppp_proof", test_ppp_proof);
    test_primitive("mesap_verification", test_mesap_verification);
    test_primitive("imdpp_proof", test_imdpp_proof);
    test_primitive("ecc", test_ecc);
    test_primitive("aes", test_aes);
    return 0;
}
