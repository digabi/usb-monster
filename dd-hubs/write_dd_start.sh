#!/bin/bash

# Determine path to write_dd.py
if [ -L $0 ]; then
	echo "is symlink"
	MY_PATH="`realpath \"$0\"`"
	MY_PATH="`dirname \"$MY_PATH\"`"
else
	MY_PATH="`dirname \"$0\"`"
	MY_PATH="`( cd \"$MY_PATH\" && pwd )`"
fi


filename=$(zenity --file-selection --title="Select Image File" --filename=./)
return_code=$?
echo "Return code: $return_code"
if [ "$return_code" == "0" ]; then
	python2 $MY_PATH/write_dd.py $filename
	# Make terminal sane (in case write_dd died violently)
	stty sane
else
	echo "Cancelled..."
fi

