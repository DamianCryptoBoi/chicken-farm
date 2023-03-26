#!/bin/sh

# open youtube - auto swipe/wait for 1 mins - close youtube

monkey -p com.google.android.youtube 1
sleep 10;
# open shorts atb - depends on device resolution, change this
input tap 200 940
sleep 3;
end=$((SECONDS+60))

while [ $SECONDS -lt $end ]; do
    input swipe 270 800 270 200 200
    sleep $(( $RANDOM % 10 + 1 ))
done

am force-stop com.google.android.youtube

