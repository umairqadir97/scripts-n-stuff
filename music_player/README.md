Readme file for the music player I use - Lucas Rountree

\####################  
\# OLD SCHOOL TITLE \#  
\####################

###Set up steps
*note, this was all done on Ubuntu 17.10 - please adjust for your Linux flavor*

# copy pasta for apt dependencies
sudo apt install -f ffmpeg cmus libfftw3-dev libncursesw5-dev libpulse-dev g++ make

# copy pasta to install the image viewer and cli visualizer
wget https://github.com/stefanhaustein/TerminalImageViewer/archive/master.zip && \
mv master.zip TerminalImageViewer-master.zip && \
unzip TerminalImageViewer-master.zip && \
cd TerminalImageViewer-master/src/main/cpp && make && sudo make install && \
cd ~ && \
rm -rf TerminalImageViewer-master* && \
wget https://github.com/dpayne/cli-visualizer/archive/master.zip && \
unzip master.zip && \
rm -f master.zip && \
cd cli-visualizer-master/ && \
./install.sh && \
cd ~

# Set up scripts and alias'
mkdir ${HOME}/bin
cp music_player.sh ${HOME}/bin/
mkdir ${HOME}/.config/cmus/plugins
cp display_art.sh ${HOME}/.config/cmus/plugins/
vim .bashrc -> alias play='exec bash bin/music_player.sh'
(or whatever you want the alias to be)
Now just open a terminal window and run your alias to start the player

# customize the visualizer! Read more here: https://github.com/dpayne/cli-visualizer#cli-visualizer
config file is: .config/vis/config
colors directory is: .config/vis/colors
check the "./vis/" directory for color scheme files.
Here are some custom color schemes I made:
*.config/vis/colors/retro*
gradient=true
#15CBEF
#FF55E9
#FF7FEF
#FF84E7
#FFFFFF

*.config/vis/colors/matrix
gradient=true
#006600
#80FF00
#FFFFFF

*.config/vis/colors/laser
gradient=true
#FF9999
#FF0000
#990000
#660000
#FF0099

Now update the following line in the config file to match below:
colors.scheme=retro,matrix,laser,rgb,rainbow,basic_colors

# Enjoy free music!
https://trevorsomething.bandcamp.com/album/trevor-something-does-not-exist
then in cmus main window (press 1), do:
:add Music
(Music = whatever directory your music is stored in- if this is not ${HOME}/Music, please update the variables in both scripts.)

cmus tutorial https://github.com/cmus/cmus/blob/master/Doc/cmus-tutorial.txt
