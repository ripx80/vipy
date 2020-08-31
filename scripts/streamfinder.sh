#!/bin/bash
SIFS=$IFS
IFS=$(echo -en "\n\b")

for i in $(ls)
 do
	if [[ $(ffmpeg -i "$i" 2>&1 | grep 'Stream' | wc -l) >2 ]]
		then
			echo "Found more than two Streams in : $i"
	fi
done

IFS=$SIFS
exit 0
