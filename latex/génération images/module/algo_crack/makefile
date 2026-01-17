# =====================
# Configuration
# =====================

TARGET ?= linux   # linux ou windows

INC_DIR = include
SRC_DIR = .
OBJ_DIR = build
BIN_DIR = .

SOURCES = $(wildcard $(SRC_DIR)/*.c)

# =====================
# Plateforme
# =====================

ifeq ($(TARGET),windows)
    CC = x86_64-w64-mingw32-gcc
    LD = x86_64-w64-mingw32-gcc

    EXEC = force_brute.exe

    CFLAGS = -Wall -Wextra -O2 -std=c99 \
             -D_FORTIFY_SOURCE=0 \
             -U_FORTIFY_SOURCE \
             -D__USE_MINGW_ANSI_STDIO=1

    LDFLAGS = -lmsvcrt
else
    CC = gcc
    EXEC = force_brute
    CFLAGS = -Wall -Wextra -O2 -std=c99
    LDFLAGS = -lm
endif

OBJECTS = $(SOURCES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

# =====================
# Règles
# =====================

all: $(BIN_DIR)/$(EXEC)

$(BIN_DIR)/$(EXEC): $(OBJECTS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)/force_brute $(BIN_DIR)/force_brute.exe

.PHONY: all clean
