#!/bin/sh

# Run iostat until stoped with Ctrl-C

while [ 1 ]; do
	iostat -x
	sleep 3
done
