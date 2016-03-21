#!/bin/sh

# Sets default PulseAudio sink (==device)
SINK=$1

if [ "$SINK" = "" ]; then
	echo "Give sink number as parameter! Execute:"
	echo "   pactl list sinks"
	echo "to get all sinks (=audio devices)"

	exit 1
fi

pactl set-default-sink $SINK
pactl set-sink-mute $SINK 0
pactl set-sink-volume $SINK "100%"
