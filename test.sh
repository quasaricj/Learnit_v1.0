#!/bin/bash
xclock &
sleep 2
xwd -display :99 -root -out clock.xwd
convert clock.xwd clock.png
