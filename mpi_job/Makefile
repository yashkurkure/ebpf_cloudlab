SHELL := /bin/bash

# Set the C++ compiler
CXX = mpic++

# Set the compiler flags
CXXFLAGS = -std=c++11 -Wall -Wextra -pedantic -Werror -g

all: avg

avg: avg.cc
	@echo "Compiling avg.cc..."
	$(CXX) $(CXXFLAGS) -o avg avg.cc
	@echo "Done."

clean:
	@echo "Cleaning up..."
	rm avg
	@echo "Done."

cleanout:
	@echo "Cleaning up outputs..."
	rm *.out *.err
	@echo "Done."