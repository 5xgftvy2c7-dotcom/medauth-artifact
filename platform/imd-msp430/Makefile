CC ?= gcc
RUNS ?= 100
CFLAGS ?= -O0 -Wall -Wextra -std=c99 -DRUNS=$(RUNS)
LDFLAGS ?= -lm
TARGET = imd_microbenchmark
SRCS = microbenchmark_main.c crypto_primitives.c sha256.c puf.c zkp.c ecc_p256.c aes128.c
OBJS = $(SRCS:.c=.o)

.PHONY: all clean msp430

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

msp430:
	$(MAKE) CC=msp430-elf-gcc TARGET=imd_microbenchmark.elf CFLAGS="-mmcu=msp430fr5994 -O0 -Wall -Wextra -std=c99 -DRUNS=$(RUNS)" LDFLAGS="-mmcu=msp430fr5994 -lm"

clean:
	rm -f $(OBJS) $(TARGET) imd_microbenchmark.elf
