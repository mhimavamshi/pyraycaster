#!/bin/bash

{
	for file in *.py; do
	    echo "===== $file ====="
	    cat -n "$file"
	    echo
	done
} | wl-copy
# wl copy all the stdout

