COREDIR = ../
PYTHON = python3

CMD = PYTHONPATH=$(COREDIR) $(PYTHON)

ft245_sync_tb:
	$(CMD) ft245_sync_tb.py

ft245_async_tb:
	$(CMD) ft245_async_tb.py

core_tb:
	$(CMD) core_tb.py

example_designs:
	cd ../example_designs && $(PYTHON) make.py -t simple -p minispartan6 -Ob run False build-bitstream

all: ft245_sync_tb ft245_async_tb core_tb example_designs
