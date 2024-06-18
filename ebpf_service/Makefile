CC = gcc         # Compiler to use (GCC)
CFLAGS = -Wall   # Compiler flags (add -g for debugging)
TARGET = hello    # Name of the executable

all: $(TARGET)   # Default target: build the executable

$(TARGET): hello.c
	$(CC) $(CFLAGS) -o $(TARGET) hello.c

clean:           # Target to clean up
	rm -f $(TARGET) *.o