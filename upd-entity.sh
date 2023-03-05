#!/bin/bash
env_file='script.env'
if [ ! -r $env_file ]; then echo "ERR Could not find $env_file"; exit 1; fi
source $env_file

if [ "#$1" = "#" ]; then echo "Usage $0 <entity>"; exit 1; fi
entity="$1"
url="${APP_URL}/entity/${entity}"
hdr_out=`mktemp`

cnt_hdr='Content-Type: application/json'
cnt_body=`cat <<EOF
{ 
    "x": 2,
    "y": 3
}
EOF`
rsp=`curl -D $hdr_out -sX POST -H "$cnt_hdr" -d "$cnt_body" "$url"`
e=$?
if [ $e -ne 0 ]
then 
    echo "ERR Failed call to $url"
    cat $hdr_out
    echo "$rsp"
    exit $e
else
    cat $hdr_out
    echo "$rsp"
fi

rm $hdr_out

