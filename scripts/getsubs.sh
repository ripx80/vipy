#!/bin/bash
for i in $(find round2 -name *.srt)
 do
	d=$(echo $i | cut -f2 -d\/) 
	mkdir -p subs/${d}
	cp $i subs/${d}
done

exit 0
