#!/bin/bash

# demonstration of accessing MetGet from a bash script
# needs the "jq" json processor to parse json files
set -u

if [  ${BASH_VERSION:0:1} -lt 4 ] ; then
	echo "Must run in Bash version >=4.\n"
	exit 1
fi

if ! command -v jq &> /dev/null
then
    echo "jq could not be found."
    exit
fi

#logfile="logfile.txt"

rm -rf filelist.json # $logfile

rename2fort=1
declare -A typemap
typemap[pre]=1
typemap[wnd]=2 

wait_interval=30  # seconds
maxtries=10
url="https://o4hrmumea3.execute-api.us-east-1.amazonaws.com/metget-stack01-development/build"
apikey="WVE8kbfs6naplUPp6lwnc81u5VUWuKGH1i484O8P"
returned_file="req.return"
H1="Content-Type: application/json"
H2="x-api-key: $apikey"
# this file will need to be templated and adjusted for real-time
uploadfile="rq.json"

echo "Checking for 'filename' in $uploadfile."
downloaded_filename=`jq '.filename' $uploadfile`
if [ $downloaded_filename == "null" ] ;then
    echo "Key for downloaded filename (filename) not found in $uploadfile. Terminal."
	exit 1
fi
echo "Checking for 'domains' in $uploadfile."
domains=`cat $uploadfile | jq '.domains'`
if [ "$domains" == "null" ] ;then
    echo "Key for domains (domains) not found in $uploadfile. Terminal."
    exit 1
fi
ndomains=`echo $domains | jq '. | length'`
echo "$ndomains domains in $uploadfile"

echo Sending post request to $url
echo curl -o $returned_file -X POST $url -d @"$uploadfile" -H "$H1" -H "$H2"  # > logfile.txt
curl -o $returned_file -X POST $url -d @"$uploadfile" -H "$H1" -H "$H2" > /dev/null  # > logfile.txt
if [ $? -ne 0 ]; then
	echo "post request failed. Terminal."
	exit 1
elif [ ! -e $returned_file ]; then 
	echo "$returned_file not found after curl/post.  Terminal."
	exit 1
fi
echo "Curl/post to $url successful."  

# get the url to ping
checkurl=`cat req.return | jq -r '.body.request_url'`
echo "Url to check is $checkurl"  # >> $logfile 2>&1

ntries=0
while true
do
	((ntries+=1)) 
	echo "Try # $ntries" 

	echo wget "$checkurl/filelist.json"
	wget "$checkurl/filelist.json"  # >> $logfile 2>&1
	if [ $? -eq 0 ]; then	
		echo "Found filelist.json at $checkurl"  # >> $logfile 2>&1
		break
	fi
	echo "filelist.json not found at $checkurl. Sleeping for $wait_interval secs ..."  # >> $logfile 2>&1
	if [ $ntries == $maxtries ] ; then
		echo "Max tries ($maxtries) reached.  Terminal."  # >> $logfile 2>&1
		exit 1
	fi
	sleep $wait_interval
	echo " "
done

echo "getting files to retrieve ..."  # >> $logfile 2>&1
files=`cat filelist.json  | jq '.output_files' | jq -r '.[]'`

echo "Retrieving $files" 
for f in $files; do
	fout="$f"
	if [ $rename2fort == 1 ] ; then
		ftype=`echo $f | awk -F. '{print $2}'`
		dom=`echo $f | awk -F_ '{print $3}' | awk -F. '{print $1}'` 
		lastdigit=`echo "$dom*2+${typemap[$ftype]}" | bc`
		fout="fort.22$lastdigit"
	fi
	echo "wgetting $f and writing to $fout ..."
	wget $checkurl/$f -O $fout > /dev/null # >> logfile.txt 
	if [ $? -ne 0 ] ; then
		echo "Download of $f failed. Continuing..."
	fi
	echo "$f written to $fout"
done


