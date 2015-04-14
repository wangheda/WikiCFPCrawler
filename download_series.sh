#!/bin/bash

mkdir -p www.wikicfp.com/cfp/program
for i in $(grep -o "/cfp/program?id=[[:digit:]]*" www.wikicfp.com/cfp/series/* | grep -o "[[:digit:]]*" | sort -n); do
	wget -O "www.wikicfp.com/cfp/program/$i" "http://www.wikicfp.com/cfp/program?id=$i"
	sleep 1
done
	
