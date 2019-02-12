#!/usr/bin/env python
"""
#######################################################
# Python Music Player
# By Benjamin Urquhart
# VERSION: 2.4.3

This player is designed to play music on a Raspberry Pi,
but can be used on Windows and OSX.
OSX support is limited.

Don't expect good documentation for a little while.
#######################################################
"""
version = '2.4'
revision = '3'
######################################################
import datetime
import urllib
import urllib2
import os
import sys
import string
import tarfile
from threading import Thread as Process
#from multiprocessing import Process
from time import sleep
from random import randint
try:
    import traceback
    import requests
except ImportError:
    pass
#####################################################
#connUser = False
threadUse = False
stop = False
skip = False
pause = False
play = False
debug = False
option = "n"
select = 0
current = ""
amount = 0
played = []
playlist = []
check = ""
width = 800
height = 600
console = False
text = ''
songNum = 1
kill = False
######################################################
#                                                    ############
print "Starting Python Music Player " + version + "." + revision #
#                                                    ############
######################################################
def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
######################################################
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)
######################################################
# The shutdown process
def shutdown():
    try:
        bcast("\n")
        bcast("Stopping...")
        pygame.mixer.music.stop()
        """
        try:
            conn.close()
            s.close()
        except:
            LogErr()
            pass
            """
        log("Shutdown success")
        log_file.close()
        pygame.quit()
        quit()
    except:
        log("An error occoured")
        LogErr()
        log_file.close()
        pygame.quit()
        quit()
######################################################
# Custom logging function
def log(string):
    try:
        if debug:
            print "[Debug]: " + string
	log_file.write("[Logger]: ")
        log_file.write(string)
        log_file.write("\n")
    except:
        pass
######################################################
def LogErr():
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log('')
        log(''.join(line for line in lines))
        if debug:
            bcast("[Error]: " + ''.join(line for line in lines), True)
    except:
        pass
######################################################
def bcast(string, err=False):
    try:
        if err:
            print string
        else:
            print "[Player]: " + string
        #conn.send(string)
        text = string
        #display(string, background, screen)
    except:
        pass
######################################################
def updater():
    log('Update requested; attempting...')
    if update == 0:
        bcast('No update found.')
        log('No update found')
    else:
        bcast('Attempting to retrive tarball...')
        try:
            log('Connecting to ' + url +'...')
            try:
                r = requests.get('http://' + url)
                status = r.status_code
            except:
                status = 200
                LogErr()
            if status == int(200):
                try:
                    filename = urllib.urlretrieve('http://' + url + '/python/downloads/player/music-player-' + str(ver) + '.tar.gz', 'music-player-' + str(ver) + '.tar.gz')
                except:
                    LogErr()
                    raise IOError
                bcast('Installing...')
                log('Download success')
                log('Will now attempt to install update')
                try:
                    mkdir('update')
                    os.rename("music-player-" + str(ver) + ".tar.gz", 'update/update.tar.gz')
                    os.chdir('update')
                    tar = tarfile.open("update.tar.gz")
                    tar.extractall()
                    tar.close()
                    os.remove('update.tar.gz')
                    os.chdir('..')
                    log('Success!')
                    bcast('Done!')
                    bcast("Move 'player.py' from the folder 'update' to: " + os.path.dirname(os.getcwd()))
                except:
                    LogErr()
                    bcast('Installation failed')
            else:
                bcast('Server is down')
                raise IOError
        except:
            LogErr()
            bcast('Download failed')
######################################################

# To control the player remotely (non-functional)

def server():
    try:
        import socket
        HOST = socket.gethostname()
        PORT = 9000
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            LogErr()
            try:
                s.close()
            except:
                LogErr()
                pass
        s.listen(2)
        print 'Started control server on ' + HOST + ':' + str(PORT)
    except:
        print "Couldn't create control server"
        LogErr()
######################################################
# Get news updates
def news():
    log("Getting news")
    try:
        news = urllib2.urlopen("http://" + url + "/news.txt")
        news = news.read()
        if news == '':
            bcast("No News")
            log("No News")
        else:
            bcast(news)
            log(news)
    except:
        LogErr()
        bcast("Couldn't get news updates", True)
######################################################
def control():
    threadUse = True
    option = ''
    option = raw_input('> ')
    try:
        option = option.replace("\n", '')
        option = option.lower()
        if option == 'quit' or option == 'stop':
            print "Use Control-C to quit"
            #stop = True
            #shutdown()
        elif option == 'skip':
            #skip = True
            pygame.mixer.music.stop()
        elif option == 'update':
            #update = True
            updater()
        # Play/Pause indev
        elif option == 'pause':
            #pause = True
            pygame.mixer.music.pause()
            bcast('Paused')
        elif option == 'play':
            #play = True
            pygame.mixer.music.play()
        elif option == '':
            option = ''
        elif option == 'debug':
            if debug == True:
                print "Debug mode disabled"
                debug = False
            elif debug == False:
                print "Debug mode enabled"
                debug = True
        elif option == "news":
            news()
        else:
            bcast("Invalid command: " + option)
    except:
        LogErr()
    sleep(0.1)
    threadUse = False
###################################################
def control2():
    try:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event == pygame.K_d:
                    print "Debug"
                    if debug:
                        debug = False
                    else:
                        debug = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_F11:
                    bcast("Pause")
                    if pause == True:
                        pygame.mixer.music.play()
                        pause = False
                    elif pause == False:
                        pygame.mixer.music.pause()
                        pause = True
                if event.key == pygame.K_u:
                    bcast("Update")
                    updater()
                if event.key == pygame.K_F12:
                    bcast("Skip")
                    pygame.mixer.music.stop()
                if event.key == pygame.K_F10 or event.key == pygame.K_q:
                    bcast("Quit")
                    shutdown()
    except:
        LogErr()
    sleep(0.2)
######################################################
mkdir('logs')
time = datetime.datetime.now()
try:
    log_file = open("./logs/" + str(time), "w+")
except:
    LogErr()
    bcast("Failed to create log")
######################################################
"""
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()
######################################################
def display(text):
    screen.fill((225, 225, 225))
    largeText = pygame.font.Font('freesansbold.ttf',115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((width/2),(height/2))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    pygame.display.flip()
"""
def display(text, background, screen):
    font = pygame.font.Font("freesansbold", 36)
    out = font.render(text, 1, (10, 10, 10))
    textpos = out.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(out, textpos)
    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
######################################################
#server()
######################################################
# Looking for pygame...
try:
    import pygame
    from pygame.locals import *
    #import Screen
except ImportError:
    LogErr()
    try:
        print "Downloading assets"
        log('Pygame missing; getting installer')
        osv = sys.platform
        if osv == 'win32':
            urllib.urlretrieve('https://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi', 'pygame-1.9.1.msi')
        elif osv == 'darwin':
            urllib.urlretrieve('https://pygame.org/ftp/pygame-1.9.1release-python.org-32bit-py2.7-macosx10.3.dmg', 'pygame-mac.dmg')
            log('Success!')
        elif osv == 'linux2' or 'cygwin':
            print 'You are using linux or cygwin'
            print "Use the command 'sudo pip install pygame' to download\nthe nessasary modules"
            log(osv + ' detected; pip installer recommended')
        else:
            print 'Unrecognized os: ' + osv
        try:
            urllib.urlretrieve('http://' + url + '/pygame.tar.gz', 'pygame.tar.gz')
            tar = tarfile.open("pygame.tar.gz")
            tar.extractall()
            tar.close()
            os.remove('pygame.tar.gz')
        except:
            LogErr()
            print "Failed to get assets"
            exit()
        print 'Please run the installer that has been dropped into the ' + os.path.dirname(os.getcwd()) + ' folder'
    except:
        print 'Failed to get assets'
        print "Please install the 'pygame' module manually at pygame.org"
        LogErr()
        shutdown()
    exit()
#######################################################
# Load pygame module
try:
    pygame.init()
    pygame.mixer.init()
    #pygame.font.init()
    log('Pygame initialized')
except:
    bcast("Couldn't run pygame.init()", True)
    log("pygame.init() failed")
    LogErr()
#######################################################
try:
    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--console" or arg == "-c":
		console = True
	    elif arg == "--verbose" or arg == "-v":
		debug = True
	    elif arg == "-f" or arg == "--file":
                pygame.init()
                try:
                    pygame.mixer.music.load(sys.argv[i+1])
                    print "Now Playing: " + sys.argv[i+1]
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        continue
                    kill = True
                except:
                    LogErr()
                    print "There was an error playing the file"
                    kill = True
	    elif arg == "-h" or arg == "--help":
		print 'Plays music in the "Music" folder within the current directory\n'
		print "Usage: " + sys.argv[0] + " [-hvc] [-f <filepath>]"
		print "Options: "
		print "\t -h, --help\t Displays this help text"
		print "\t -v, --verbose\t Displays extra information"
		print "\t -c, --console\t Disables Pygame screen (text-only mode)"
		print "\t -f, --file\t Plays the file at the filepath specified"
		print "\nExamples: \n\t " + sys.argv[0] + " -v -c -f /sample/file/path/foo.bar"
		print "\t " + sys.argv[0] + " -f foo.bar"
                kill = True
            i = i + 1
except:
    pass
if kill:
    exit()
######################################################
# Checking for updates...
url = "benjaminurquhart.me" # This wasn't the original URL - replaced for privacy
update = 0
try:
    log('Checking for updates...')
    log('Getting info from ' + url)
    ver = urllib2.urlopen('http://' + url + '/version.txt')
    rev = urllib2.urlopen('http://' + url + '/rev.txt')
    ver = ver.read()
    rev = rev.read()
    if float(ver) > float(version):
        log('Update found!')
        bcast("Python Music Player " + ver + " is availible")
        bcast("Type update at the prompt to download")
        update = 1
    elif float(ver) < float(version):
        log('Indev vesion in use')
        bcast('Indev version in use')
    elif int(rev) > int(revision) and float(ver) == float(version):
        log('New revision found!')
        bcast('Revision ' + str(rev) + ' is availible')
        bcast('Type update at the prompt to download')
        update = 1
    elif float(ver) == float(version):
        log('No update found')
        bcast('No update found')
except:
    bcast('Failed to check for updates', True)
    LogErr()
    log('Update check failed')
######################################################
mkdir('Music')
log("Player starting...")
news()
######################################################
try:
    if console == False:
        screen = pygame.display.set_mode((1000, 200))
        pygame.display.set_caption("Music Player")
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))
except:
    bcast("Display error, console mode active", True)
    log("Display error")
    LogErr()
    console = True
log("Player started")
# Check the Music folder for tracks
sound_data = os.listdir('./Music')
try:
    for i in sound_data:
        playlist.append(i)
    i = 0
    amount = len(playlist)
    log(str(amount) + " Songs found")
    if amount == 0:
        bcast('No music found!')
        shutdown()
    bcast("Number of songs: " + str(amount))
#######################################################
# Play the music
    while i != amount:
        select = randint(0, amount - 1)
        if option.lower() == "y":
            for i in song:
               current = i
            option = "n"
        else:
            current = playlist[select]
        #current = current.replace("\n", "")
        if current not in played:
# Try to load the track
            bcast("Now Playing: " + current + " (" + str(songNum) + " out of " + str(amount) + ")")
            log("Song " + str(songNum) + " out of " + str(amount))
            try:
                log("Loading '" + current + "'")
                pygame.mixer.music.load("./Music/" + current)
                log('Now Playing: ' + current)
            except:
                bcast("Couldn't play " + current)
#######################################################
# Play loaded track
            pygame.mixer.music.play()
# Take user input for controlling player
            while pygame.mixer.music.get_busy():
                if console == False:
                    #font = pygame.font.Font(None, 36)
                    #out = font.render(text, 1, (10, 10, 10))
                    #textpos = out.get_rect()
                    ##textpos.centerx = background.get_rect().centerx
                    screen.blit(background, (0, 0))
                    #pygame.display.flip()
                    control2()
                else:
                    t = Process(None, control())
                    t.daemon = False
                    t.start()
#######################################################
            if not current in played:
                played.append(current)
                i = i + 1
            sleep(0.2)
            songNum = songNum + 1
    bcast("All songs have been played!")
    log('All songs have been played')
    shutdown()
#######################################################
except:
    LogErr()
    shutdown()
