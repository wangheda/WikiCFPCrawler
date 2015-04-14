#!/bin/bash

count=46000

if [ $# -gt 0 ]; then
	count=$1
fi

./download.sh $count
./extract.sh

