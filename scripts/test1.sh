#!/bin/sh

monkey -p com.google.android.youtube 1

sleep 3;

am start -a android.intent.action.VIEW -d "https://youtube.com/shorts/6sHFU_wvSjE?feature=share"