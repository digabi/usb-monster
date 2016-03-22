#!/bin/sh

# Run iostat until stoped with Ctrl-C

while [ 1 ]; do
	iostat -x -m 2 10
done
