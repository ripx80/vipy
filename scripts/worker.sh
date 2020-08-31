#!/bin/bash
trap exit 2

SIFS=$IFS
IFS=$(echo -en "\n\b")
test -d ./broken || mkdir ./broken
for i in $(ls ./raw)
  do
	./video_project "./raw/${i}"
	if [[ $? != 0 ]]
	  then
		echo "ERROR: Worker has detect an unhandled error. Move this to broken"
		if [[ "$(ls -A ./tmp)" ]]
		  then
			i=${i:0:-4}
			test -d "./broken/$i" || mkdir "./broken/$i"
			mv ./tmp/* "./broken/$i"
		fi
	fi
done
IFS=$SIFS
