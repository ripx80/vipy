#!/bin/bash

IFST=$IF;
IFS=$'\n'
t=0
for i in $(ls | sort -n)
  do 
  test "$i" == 't.sh' && continue
  ((t++))
  if [ $t -lt 10 ]
    then
  	new=$(echo $i | sed "s/Friends\.S1[0-9]E[0-9][0-9]/0$t\ -/g")
  else
  	new=$(echo $i | sed "s/Friends\.S1[0-9]E[0-9][0-9]/$t\ -/g")
fi  
  new=$(echo $new | sed "s/\./\ /g" | sed "s/\ German\ DVDRiP\ XviD-ARCHiV\ avi/\.avi/g")
  mv "$i" "$new"
echo $new
 done
IFS=$IFST
exit 0
