#!/bin/bash
# Run the example tests

cd "$(dirname "$0")"
python3 test_examples.py
exit $?