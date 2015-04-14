#!/bin/bash

count=46000

if [ $# -gt 0 ]; then
	count=$1
fi

site=www.wikicfp.com
python download_list.py ${site} '/cfp/servlet/event.showcfp?eventid=%d' '/cfp/event/%d' 1 $count
for i in {A..Z}; do
	python download_list.py ${site} "/cfp/series?t=c&i=$i" "/cfp/series/$i"

done
./download_series.sh
tar czf ${site}.$(date +%Y%m%d).tar.gz ${site}/

