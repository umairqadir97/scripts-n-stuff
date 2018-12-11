#! /bin/bash

# 2018, Lucas Rountree, lredvtree@gmail.com

# This will open cmus, a visualizer, and an album art viewer.
# Requires the following dependencies: ffmpeg cmus libfftw3-dev libncursesw5-dev libpulse-dev xorg(or x plugins for wayland)
# Currently, only works with the following terminals: rxvt-unicode and gnome-terminal. Updated the if statement below to add lines for whatever terminal you want to use.
# Also the cli-visualizer:
# wget https://github.com/dpayne/cli-visualizer/archive/master.zip .
# unzip master.zip
# cd cli-visualizer-master
# ./install.sh

# Check dependencies
echo "Checking dependencies..."
DEP_LIST=(ffmpeg cmus libfftw3-dev libncursesw5-dev libpulse-dev xorg)
for PACKAGE in ${DEP_LIST[@]}; do
  if [ "$(dpkg-query -s "${PACKAGE}" | grep "Status: install ok installed")" ]; then
    echo -e "\e[93m${PACKAGE} installed!\e[0m"
  else
    echo -e "\e[91m${PACKAGE} NOT installed, run:"
    echo -e "apt-get install -f ${PACKAGE}"
    echo -e "quitting...\e[0m"
    exit
  fi
done
if [ "$(tput colors)" != "256" ]; then
  echo -e "\e[91mTerminal is not set to display 256 colors!
quitting...\e[0m"
  exit
fi
if ! [ "$(grep 'exec(' /etc/alternatives/x-terminal-emulator | grep "gnome-terminal\|urxvt")" ]; then
  echo -e "\e[91mYou do not appear to be using gnome-terminal or urxvt.
Please install, or reconfigure music-player to use your terminal emulator of choice.
quitting...\e[0m"
  exit
fi

# Set variables
CMUS_Version="$(cmus --version | grep "cmus" | awk '{print $2}')"
#Term_Font="xft:LiberationMono:size=10:antialias=true"
Working_Directory="${HOME}/.config/cmus/plugins"

# Get variables
#Monitor_Array="($(xrandr --current --query --verbose | grep -w connected | awk -F '(' '{print $1}' | awk '{print $NF}' | ))"
Primary_Monitor="$(xrandr --screen 0 -q | grep -w 'connected.*primary' | awk '{print $1}')"
Primary_Monitor_Geometry="$(xrandr --screen 0 -q | grep -w "${Primary_Monitor}" | awk '{print $4}')"
Primary_Size="$(echo "${Primary_Monitor_Geometry}" | awk -F '+' '{print $1}')"
Primary_Width="$(echo "${Primary_Size}" | awk -F 'x' '{print $1}')"
Primary_Height="$(echo "${Primary_Size}" | awk -F 'x' '{print $2}')"
Primary_Location="$(echo "${Primary_Monitor_Geometry}" | awk -F '+' '{print $2,$3}' | sed 's/ /+/')"
Primary_X="$(echo "${Primary_Location}" | awk -F '+' '{print $1}')"
Primary_Y="$(echo "${Primary_Location}" | awk -F '+' '{print $2}')"
Active_Window_ID="$(xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)" | awk '{print $5}')"
Font_Geometry="$(xprop -id "${Active_Window_ID}" | grep "program specified resize increment:" | awk -F ': ' '{print $2}')"
Font_Width="$(echo "${Font_Geometry}" | awk '{print $1}')"
Font_Height="$(echo "${Font_Geometry}" | awk '{print $3}')"
#Window_Geometry="$(xwininfo -id "${Active_Window_ID}" | grep geometry | awk '{print $2}')"
#Window_Corners="$(xwininfo -id "${Active_Window_ID}" | grep Corners | awk '{print $2,$3,$4,$5}')"
Pixel_Width="$(("${Primary_Width}" / "${Font_Width}"))"
Line_Height="$((${Primary_Height} / "${Font_Height}"))"
Half_Pixel_Width="$((("${Pixel_Width}" / 2) - 2))"
Half_Line_Height="$((("${Line_Height}" / 2) - 2))"

# Window Geometry
CMUS_Geometry="${Half_Pixel_Width}x${Line_Height}+${Primary_Location}"
VIS_Geometry="${Half_Pixel_Width}x${Half_Line_Height}+$(("${Primary_X}" + ("${Primary_Width}" / 2)))+${Primary_Y}"
ART_Geometry="${Half_Pixel_Width}x${Half_Line_Height}+$(("${Primary_X}" + ("${Primary_Width}" / 2)))+$(("${Primary_Y}" + ("${Primary_Height}" / 2)))"

# Identify terminal and open windows
unset -v Terminal_Name
Terminal_Name="$(ps h -q $PPID | awk '{print $NF}')"
if [ "$(echo "${Terminal_Name}" | grep "gnome-terminal")" ]; then
  gnome-terminal --hide-menubar --geometry="${VIS_Geometry}" -t "CMUS VISUALIZER" -- vis
  gnome-terminal --working-directory="${Working_Directory}" --hide-menubar --geometry="${ART_Geometry}" -t "ALBUM ART" -- bash display_art.sh
  gnome-terminal --hide-menubar --geometry="${CMUS_Geometry}" -t "CMUS ${CMUS_Version}" -- cmus
elif [ "$(echo "${Terminal_Name}" | grep "urxvt")" ]; then
  urxvt -g "${VIS_Geometry}" -sb -vb -T "CMUS VISUALIZER" -e bash -c "vis" &
  urxvt -g "${ART_Geometry}" -cd "${Working_Directory}" -sb -vb -T "ALBUM ART" -e bash -c "bash display_art.sh" &
  urxvt -g "${CMUS_Geometry}" -sb -vb -T "CMUS ${CMUS_Version}" -e bash -c "cmus"
else
  echo "Terminal could not be identified!
Quitting!"
  exit
fi

# test
#echo "CMUS_Version: ${CMUS_Version}
#Working_Directory: ${Working_Directory}
#Primary Monitor: ${Primary_Monitor}
#Primary_Monitor_Geometry: ${Primary_Monitor_Geometry}
#Primary_Size: ${Primary_Size}
#Primary_Width: ${Primary_Width}
#Primary_Height: ${Primary_Height}
#Primary_Location: ${Primary_Location}
#Primary_X: ${Primary_X}
#Primary_Y: ${Primary_Y}
#Active_Window_ID: ${Active_Window_ID}
#Font_Geometry: ${Font_Geometry}
#Font_Width: ${Font_Width}
#Font_Height: ${Font_Height}
#Pixel_Width: ${Pixel_Width}
#Line_Height: ${Line_Height}
#Half_Pixel_Width: ${Half_Pixel_Width}
#Half_Line_Height: ${Half_Line_Height}
#CMUS_Geometry: ${CMUS_Geometry}
#VIS_Geometry: ${VIS_Geometry}
#ART_Geometry: ${ART_Geometry}
"
