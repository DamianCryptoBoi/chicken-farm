#!/bin/sh

monkey -p com.google.android.youtube 1

sleep 5;

am start -a android.intent.action.VIEW "https://www.youtube.com/watch?v=I4EWvMFj37g&ab_channel=Fireship"

sleep 20;

### skip ads###

input tap 627 660

sleep 1;

input tap 627 660

sleep 1;

# input tap 690 793

# sleep 1;

# input tap 690 793

# sleep 1;

################

# input tap 100 1500

# sleep 10;

# input tap 40 570

# sleep 3;

# input tap 181 670

# sleep 3;

# ### skip ads###

# input tap 627 660

# sleep 1;

# input tap 627 660

# sleep 1;

# input tap 690 793

# sleep 1;

# input tap 690 793

# sleep 1;

# ################


# input tap 117 807

# sleep 10;

# input keyevent 4

# input tap 142 986

# sleep 3;

# ### skip ads###

# input tap 627 660

# sleep 1;

# input tap 627 660

# sleep 1;

# input tap 690 793

# sleep 1;

# input tap 690 793

# sleep 1;

# ################

# sleep 20;

# am force-stop com.google.android.youtube
