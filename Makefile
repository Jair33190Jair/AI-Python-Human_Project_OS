# Shared file-format converters. Callable from any project:
#   make -f ~/.claude/Makefile csv-to-xlsx CSV=path/to/file.csv
LIB := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))lib/
PYTHON_BIN := $(LIB).venv/bin/python3

.PHONY: csv-to-xlsx xlsx-to-pdf csv-to-pdf

# Convert a CSV to XLSX with the same name, overwriting if present.
csv-to-xlsx:
	$(PYTHON_BIN) $(LIB)csv_to_xlsx.py "$(CSV)"

# Convert an XLSX to PDF with the same name, overwriting if present.
xlsx-to-pdf:
	$(LIB)xlsx_to_pdf.py "$(XLSX)"

# Convert a CSV straight to a landscape PDF with the same name, overwriting if present.
csv-to-pdf:
	$(PYTHON_BIN) $(LIB)csv_to_pdf.py "$(CSV)"
