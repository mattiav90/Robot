.PHONY: go plot idx sim help

# Initialize the FLAGS variable.
FLAGS :=

# Extract extra arguments that are not go, plot, idx, sim, or help.
EXTRA_ARGS := $(filter-out go plot idx sim help,$(MAKECMDGOALS))

# If 'plot' is among the command-line goals, add the flag.
ifneq (,$(filter plot,$(MAKECMDGOALS)))
FLAGS += --plot True
endif

# If 'idx' is among the command-line goals, use the first extra argument as its value.
ifneq (,$(filter idx,$(MAKECMDGOALS)))
FLAGS += --idx $(firstword $(EXTRA_ARGS))
endif

# If 'sim' is among the command-line goals, add the flag.
ifneq (,$(filter sim,$(MAKECMDGOALS)))
FLAGS += --sim True
endif

go:
	python3 top.py $(FLAGS)

# Dummy targets to avoid errors.
plot:
	@:

idx:
	@:

sim:
	@:

help:
	@echo "Available commands:"
	@echo "  make go                 - Run 'python3 top.py' with specified flags."
	@echo "  make go plot            - Run 'python3 top.py --plot True'"
	@echo "  make go idx X           - Run 'python3 top.py --idx X' (replace X with your index value)"
	@echo "  make go sim             - Run 'python3 top.py --sim True'"
	@echo "  make help               - Display this help message"
