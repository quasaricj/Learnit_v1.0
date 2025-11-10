#!/bin/bash
python3 course_app/ui/main_window.py &
sleep 5
# This is a bit of a hack, but we'll assume the upload dialog opens on top
# and the screenshot will capture it.
xwd -display :99 -root -out upload_dialog_screenshot.xwd
convert upload_dialog_screenshot.xwd upload_dialog_screenshot.png
killall python3
