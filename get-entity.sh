#!/bin/bash
env_file='script.env'
if [ ! -r $env_file ]; then echo "ERR Could not find $env_file"; exit 1; fi
source $env_file

if [ "#$1" = "#" ]; then echo "Usage $0 <entity>"; exit 1; fi
entity="$1"
url="${APP_URL}/entity/${entity}"
hdr_out=`mktemp`

rsp=`curl -D $hdr_out -s "$url"`
e=$?; if [ $e -ne 0 ]; then echo "ERR Failed call to ${APP_URL}/world"; exit $e; fi

echo "$rsp" | jq >/dev/null 2>&1
e=$?
if [ $e -ne 0 ]
then 
    echo "ERR Response is not JSON"
    cat $hdr_out
    echo "$rsp"
    exit $e
else
    cat $hdr_out
    echo "$rsp" | jq
fi

rm $hdr_out
