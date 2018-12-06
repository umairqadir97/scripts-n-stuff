#! /bin/bash
# This script uses the application "tiv" to display album art images inside the terminal.
# You need 256 color enabled in the terminal for this to work.
# 2018, Lucas Rountree, lredvtree@gmail.com
# wget https://github.com/stefanhaustein/TerminalImageViewer/archive/master.zip
# cd TerminalImageViewer-master/src/main/cpp && make && sudo make install

DATE="$(/bin/date +%Y%m%d-%H%M%S)"
Log_File="${HOME}/.config/cmus/plugins/logs/art_display_${DATE}.log"
Music_Library="${HOME}/Music"
CMUS_PID=$(ps -A | grep cmus | awk '{print $1}')

#logme() {
#echo -e "[${DATE}]:  ${1}" >> "${Log_File}"
#[ "$2" ] && [ "$2" = "true" ] && echo "$1"
#}

#logme "## Starting display_art log ##"

if ! [ "${CMUS_PID}" ]; then
#  logme "CMUS not found running at start, waiting a few seconds before moving on..."
  sleep 2
  CMUS_PID=$(ps -A | grep cmus | awk '{print $1}')
fi

# Display Album Art
display_art() {
clear
unset -v Current_Artist
unset -v Current_Album
unset -v Get_Album_Directory
unset -v Album_Image_Name
unset -v Album_Image
Current_Artist="$(cmus-remote -Q 2>/dev/null | grep "tag artist " | cut -d ' ' -f 3-)"
Current_Album="$(cmus-remote -Q 2>/dev/null | grep "tag album " | cut -d ' ' -f 3-)"
#Get_Album_Directory="$(ls "${Music_Library}" 2>/dev/null | grep "${Current_Artist}" | grep "${Current_Album}")"
Get_Song="$(cmus-remote -Q | grep "file" | cut -d ' ' -f 2-)"
Get_Album_Directory="$(dirname "${Get_Song}")"
Album_Image_Name="$(ls "${Get_Album_Directory}" 2>/dev/null | grep ".jpg\|.jpeg\|.png")"
if [ "$(echo "${Album_Image_Name}" | wc -l)" -gt "1" ]; then
  Album_Image_Name="$(echo "${Album_Image_Name}" | grep "cover")"
fi
Album_Image="${Get_Album_Directory}/${Album_Image_Name}"
if ! [ "${Current_Artist}" ]; then
  unset -v Album_Image
  Current_Artist="UNFOUND"
  Album_Image="UNFOUND"
  Current_Album="UNFOUND"
fi
if [ -f "${Album_Image}" ]; then
#  Track_Number="$(cmus-remote -Q 2>/dev/null | grep "tag tracknumber" | cut -d ' ' -f 3)"
#  Current_Song="$(cmus-remote -Q 2>/dev/null | grep "tag title" | cut -d ' ' -f 3-)"
  tiv "${Album_Image}"
#  echo "${Current_Artist} - ${Current_Album} - ${Track_Number} ${Current_Song}"
  check_album
else
#  logme ">> No Album Image Found for album: [${Current_Album}] by: [${Current_Artist}]! <<" "true"
  echo "NO ALBUM IMAGE FOUND!
Current Artist: ${Current_Artist}
Current Album: ${Current_Album}
Album Directory: ${Get_Album_Directory}
Album Image Name: ${Album_Image_Name}
Album Image: ${Album_Image}

Albums in ${Music_Library} by ${Current_Artist}:
$(ls "${Music_Library}" | grep "${Current_Artist}")"
#  logme "Value for Album_Image: ${Album_Image}"
  check_album
fi
}

# Check Album
check_album() {
#Check_Album="$(cmus-remote -Q | grep "album " | awk -F 'album ' '{print $2}' 2>/dev/null)"
Check_Album="$(cmus-remote -Q 2>/dev/null | grep "tag album " | cut -d ' ' -f 3-)"
while [ "${Check_Album}" = "${Current_Album}" ]; do
  sleep 1
#  Check_Album="$(cmus-remote -Q | grep "album " | awk -F 'album ' '{print $2}' 2>/dev/null)"
  Check_Album="$(cmus-remote -Q 2>/dev/null | grep "tag album " | cut -d ' ' -f 3-)"
done
while [ -z "${Check_Album}" -a "${CMUS_PID}" ]; do
  sleep 1
  Check_Album="$(cmus-remote -Q 2>/dev/null | grep "tag album " | cut -d ' ' -f 3-)"
  CMUS_PID=$(ps -A | grep cmus | awk '{print $1}')
done
}

while [ "${CMUS_PID}" ]; do
#  logme "CMUS PID: ${CMUS_PID}, running art display."
  display_art
  CMUS_PID=$(ps -A | grep cmus | awk '{print $1}')
done
#logme "CMUS not running, quitting!"
Vis_PID="$(ps -A | grep vis | awk '{print $1}')"
if [ "${Vis_PID}" ]; then
  kill -9 "${Vis_PID}"
fi
exit
