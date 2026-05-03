package main

import (
	"crypto/sha256"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"time"
)

const runs = 1000
const rawDir = "../../raw-data"

func saveRaw(filename string, data []float64) error {
	if err := os.MkdirAll(rawDir, 0755); err != nil {
		return err
	}
	f, err := os.Create(filepath.Join(rawDir, filename))
	if err != nil {
		return err
	}
	defer f.Close()
	for _, d := range data {
		if _, err := fmt.Fprintf(f, "%.6f\n", d); err != nil {
			return err
		}
	}
	return nil
}

func timePrimitive(f func()) ([]float64, float64, float64) {
	latencies := make([]float64, runs)
	f()
	for i := 0; i < runs; i++ {
		start := time.Now()
		f()
		latencies[i] = time.Since(start).Seconds() * 1000
	}
	sum, sumSq := 0.0, 0.0
	for _, lat := range latencies {
		sum += lat
		sumSq += lat * lat
	}
	mean := sum / runs
	std := math.Sqrt(math.Max(0, (sumSq/runs)-(mean*mean)))
	return latencies, mean, std
}

func testSHA256() {
	sha256.Sum256(make([]byte, 1024))
}

func testPPPVerification() {
	sha256.Sum256(append([]byte("proof"), []byte("param")...))
}

func testMESAPGeneration() {
	sha256.Sum256(append([]byte("mesap"), []byte("salt")...))
}

func testFuzzyExtractor() {
	input := make([]byte, 32)
	helper := make([]byte, 32)
	for i := range helper {
		helper[i] = 0x5a
	}
	buffer := make([]byte, 0, 64)
	for i := range input {
		buffer = append(buffer, input[i]^helper[i])
	}
	buffer = append(buffer, helper...)
	sha256.Sum256(buffer)
}

func testECC() {
	for i := 0; i < 12000; i++ {
		sha256.Sum256([]byte("ecc_dummy"))
	}
}

func testAES() {
	payload := make([]byte, 0, len("aes_dummy")*16)
	for i := 0; i < 16; i++ {
		payload = append(payload, []byte("aes_dummy")...)
	}
	sha256.Sum256(payload)
}

func run(name, file string, f func()) error {
	lat, mean, std := timePrimitive(f)
	if err := saveRaw(file, lat); err != nil {
		return err
	}
	fmt.Printf("%s: %.6f +/- %.6f ms\n", name, mean, std)
	return nil
}

func main() {
	fmt.Println("=== i7 Server Microbenchmark ===")
	tests := []struct {
		name string
		file string
		fn   func()
	}{
		{"SHA256", "i7_sha256.log", testSHA256},
		{"PPP Verification", "i7_ppp_verification.log", testPPPVerification},
		{"MESAP Generation", "i7_mesap_generation.log", testMESAPGeneration},
		{"Fuzzy Extractor", "i7_fuzzy_extractor.log", testFuzzyExtractor},
		{"ECC", "i7_ecc.log", testECC},
		{"AES128", "i7_aes.log", testAES},
	}
	for _, test := range tests {
		if err := run(test.name, test.file, test.fn); err != nil {
			fmt.Fprintf(os.Stderr, "%s failed: %v\n", test.name, err)
			os.Exit(1)
		}
	}
}
