#!/usr/bin/env python2.7

import urllib2
import os
from os import listdir
from os.path import isfile, join
import random
import datetime
#import string
import sys
try:
	import pyaudio
	import wave
except:
	print "Ooops ... no pyaudio or wave ... Say will try SoX"
import glob
import platform
#http://glowingpython.blogspot.com/2012/11/text-to-speech-with-correct-intonation.html

#change working dir to script folder
if len(os.path.split(sys.argv[0])[0]) > 0:
	os.chdir(os.path.split(sys.argv[0])[0])

replacementsdict = {'.exclamationmark': '!', '.apostrophe': "'", '.questionmark': '?', '.comma': ',', '.colon': ':'}

picfiles = [os.path.abspath(file) for file in glob.glob('*/*/pics/*.*')]
soundfiles = [os.path.abspath(file) for file in glob.glob('*/*/sounds/*.*')]
comparepicfiles = [file[:file.rindex(".")] for file in picfiles]
comparesoundfiles =[file.replace("speech_google.ogg","").replace("speech_google.wav","").replace("/sounds/","/pics/") for file in soundfiles]
print len(picfiles)
print len(soundfiles)
print len(comparepicfiles)
print len(comparesoundfiles)

compared = [os.path.split(file) for file in comparepicfiles if file not in comparesoundfiles]

google_translate_url = 'http://translate.google.com/translate_tts'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)')]

for dirpath, sentence in compared:
	outputdir = dirpath.replace("/pics","/sounds/")
	sentence_corrected = sentence#.replace(".questionmark","?")
	for sym in [sym for sym in replacementsdict.keys() if sym in sentence_corrected]:
		sentence_corrected = sentence_corrected.replace(sym,replacementsdict[sym])
	response = opener.open(google_translate_url+'?q='+sentence_corrected.replace(' ','%20')+'&tl=en')
	ofp = open(outputdir+sentence+'speech_google.mp3','wb')
	ofp.write(response.read())
	ofp.close()
	if platform.system() == 'Linux':
		os.system('avconv -i '+'"'+str(outputdir+sentence)+'speech_google.mp3" -acodec libvorbis '+'"'+str(outputdir+sentence)+'speech_google.ogg"') #on Linux
	else:
		os.system("afconvert -f 'WAVE' -d I16@44100 " + "'"+str(outputdir+sentence)+"speech_google.mp3'") #on a mac
	os.system('rm '+'"'+str(outputdir+sentence)+'speech_google.mp3"')
	print outputdir	
	print sentence


print "\n \
How to use:\n \
Save pictures to pics folder. Name them exactly what you want the text to be.\n \
Use .questionmark, .comma in the name instead of ? or , etc. -- files cannot have a ? in the name\n \
Run sound_download.py to get audio for text from Google Translate TTS API (unofficial).\n"

# try to import pygame module
try:
	import pygame as pg
	from pygame.locals import *
	import pg._view
except:
	print "RosettaTable depends on the pygame module. Please install pygame."


#start the show
pg.mixer.pre_init(16000, -16, 1, 4096)
pg.init()
pg.mixer.init()
pg.event.set_allowed(None)
pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN])
#Get Date
now = datetime.datetime.now()
current_year = now.year
current_month = now.month
current_day = now.day
date = str(current_month) + "/" + str(current_day) + "/" + str(current_year)

#adjust mac volume
try:
	os.system('osascript -e "set volume input volume 90"')
	os.system('osascript -e "set volume output volume 60"')
except:
	print "Please adjust your microphone volume."
#display variables
red = (255, 0, 0)
green = (0, 255, 0)
blue = (15, 15, 255)
yellow = (255, 255, 0)
gray = (101,111,117)
white = (255,255,255)
black = (0,0,0)
background_colour = white

score = 0
incorrectscore = 0
trycount = 0
original_length = 0
completeddict = {}
buttonresult = False
# create the basic window/screen and a title/caption
screen = pg.display.set_mode((0,0)) #full sized window mode pg.FULLSCREEN
screen.fill(background_colour)
size = screen.get_size()
w = size[0]
h = size[1]
pg.display.set_caption("RosettaTablet")
font = "DidactGothic.ttf"
myfont = pg.font.Font(font, 50)
mysmallfont = pg.font.Font(font, 40)

#correct/wrong sounds and pics
sound = pg.mixer.Sound('rails.wav')
wrong_sound = pg.mixer.Sound('CymbalCrash.wav')
correct_sound = pg.mixer.Sound('GuitarStrum.wav')
correctpic = pg.image.load("correct.png").convert_alpha()
wrongpic = pg.image.load("wrong.png").convert_alpha()
micpic = pg.image.load("mic.png").convert_alpha()

# show the whole thing
pg.display.flip()

def display_word(word):
	myfont = pg.font.Font(font, 40)
	label = myfont.render(word, 1, black)
	labelwidth = label.get_rect()[2]
	space_available = screen.get_size()[0] - quitbuttonbox[2] - 100
	space_indicies = []
	for pos, letter in enumerate(word):
		if letter == " ":
			space_indicies.append(pos)
	space_indicies.reverse()
	line1 = word
	line2 = ""
	while labelwidth > space_available:
		line1 = word[:space_indicies[0]]
		line2 = word[space_indicies[0]:]
		line1_render = myfont.render(line1, 1, black)
		line2_render = myfont.render(line2, 1, black)
		labelwidth = line1_render.get_rect()[2]
		space_indicies.pop(0)
	else:
		line1_render = myfont.render(line1, 1, black)
		line2_render = myfont.render(line2, 1, black)
	screen.blit(line1_render, (100, 0))
	screen.blit(line2_render, (100, 41))

def recordinput():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 5
	global WAVE_OUTPUT_FILENAME
	WAVE_OUTPUT_FILENAME = "/tmp/input.wav"
	p = pyaudio.PyAudio()
	stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = CHUNK)
	print("* recording")
	frames = []
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)
	print("* done recording")
	stream.stop_stream()
	stream.close()
	p.terminate()
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

def playinput():
	CHUNK = 1024
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
	data = wf.readframes(CHUNK)
	while data != '':
		stream.write(data)
		data = wf.readframes(CHUNK)
	stream.stop_stream()
	stream.close()
	p.terminate()

def getbestratio(boxheight,boxwidth,picheight,picwidth):
	height_ratio = float(boxheight) / float(picheight)
	width_ratio = float(boxwidth) / float(picwidth)
	picwidth *= min(width_ratio, height_ratio)
	picheight *= min(width_ratio, height_ratio)
	return int(picwidth), int(picheight)

def displayactivitychoice():
	global buttonresult
	screen.fill(background_colour)
	label1 = mysmallfont.render("Listen", 2, black)
	label2 = mysmallfont.render("Say", 2, black)
	listenlabel = screen.blit(label1,[200,(h/2)-100])
	saylabel = screen.blit(label2,[w-200,(h/2)-100])
	drawmainbutton(200,h/2)
	drawpronunciationbutton(w-200,h/2)
	#drawquitbutton()
	drawmenubutton()
	pg.display.flip()
	looping = True
	while looping:
		for event in pg.event.get():
			# exit conditions --> windows titlebar x click
			if event.type == pg.QUIT:
				raise SystemExit
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				pos = pg.mouse.get_pos()
				if mainbutton.collidepoint(pos) or listenlabel.collidepoint(pos):
					buttonresult = "mainlesson"
					looping = False
					break
				if pronunciationbutton.collidepoint(pos) or saylabel.collidepoint(pos):
					buttonresult = "pronunciation"
					looping = False
					break
				if menubutton.collidepoint(pos):
					looping = False
					break
				#if quitbutton.collidepoint(pos):
				#	raise SystemExit
				#	break

def drawmainbutton(x,y):
	global mainbuttonpic, mainbutton
	mainbuttonpic = pg.image.load("pictures.png").convert_alpha()
	mainbutton = screen.blit(mainbuttonpic, [x,y])

def drawpronunciationbutton(x,y):
	global pronunciationbuttonpic, pronunciationbutton
	pronunciationbuttonpic = pg.image.load("mic.png")#.convert_alpha()
	pronunciationbutton = screen.blit(pronunciationbuttonpic, [x,y])

def drawquitbutton():
	global quitbuttontext,quitbuttonbox,quitbutton
	quitbuttontext = mysmallfont.render("Quit", 2, black)
	quitbuttonbox = pg.draw.rect(screen,white,((w-quitbuttontext.get_rect()[2])-3,0,quitbuttontext.get_width()+6,quitbuttontext.get_height()+6),0)
	quitbutton = screen.blit(quitbuttontext, [w-quitbuttontext.get_rect()[2]-3,0])

def drawmenubutton():
	global menubuttontext,menubuttonbox,menubutton
	menubuttontext = mysmallfont.render("Menu", 2, black)
	menubuttonbox = pg.draw.rect(screen,white,(w-menubuttontext.get_width()-3,0,menubuttontext.get_width()+6,menubuttontext.get_height()+6),0)
	menubutton = screen.blit(menubuttontext, [w-menubuttontext.get_rect()[2]-3,0])

def drawnextbutton():
	global nextbuttontext,nextbuttonbox,nextbutton
	nextbuttontext = mysmallfont.render("Next", 2, black)
	nextbuttonbox = pg.draw.rect(screen,white,((w-nextbuttontext.get_rect()[2])-3,0,nextbuttontext.get_width()+6,nextbuttontext.get_height()+6),0)
	nextbutton = screen.blit(nextbuttontext, [(w-nextbuttontext.get_rect()[2])/2,h-nextbuttontext.get_rect()[1]-200])


def drawlessonstructure():
	global choicebox1, choicebox2, choicebox3,choicebox4, soundbutton, label
	screen = pg.display.set_mode((0,0)) #full sized window mode
	screen.fill(background_colour)
	size = screen.get_size()
	w = size[0]
	h = size[1]
	pg.display.set_caption("RosettaTablet")
	myfont = pg.font.Font(font, 50)
	mymedfont = pg.font.Font(font, 30)
	mysmallfont = pg.font.Font(font, 40)
	scorelabel = mymedfont.render("Score: " + str(score), 2, black)
	boxsize = scorelabel.get_rect()
	scoreXpos = (w - boxsize[2])-30
	scoreYpos = quitbuttonbox[3]
	screen.blit(scorelabel,[scoreXpos,scoreYpos])
	titlebox = pg.draw.rect(screen, black, (0,0,w,100), 3)
	choicebox1 = pg.draw.rect(screen, black, (0,100,(w)/2,(h-200)/2), 3)
	choicebox2 = pg.draw.rect(screen, black, (w/2,100,(w)/2,(h-200)/2), 3)
	choicebox3 = pg.draw.rect(screen, black, (0,((h-200)/2)+100,(w)/2,(h-200)/2), 3)
	choicebox4 = pg.draw.rect(screen, black, (w/2,((h-200)/2)+100,(w)/2,(h-200)/2), 3)
	soundpic = pg.image.load('sound.png')
	soundbutton = screen.blit(soundpic, (0,0))
	pg.display.flip()

def pronunciationpractice(lesson):
	global pronunciationbuttonpic, pronunciationbutton, menupushed
	menupushed = False
	screen.fill(background_colour)
	soundpic = pg.image.load('sound.png')
	recorddot = pg.image.load('recorddot.png')
	drawnextbutton()
	drawpronunciationbutton(w-200,h/2)
	#lesson = "emotions" #temporary lesson variable before getting sreen picked
	listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in lesson/pics/ folder
	original_length = len(listofpics)
	random.shuffle(listofpics) #shuffle order of lesson
	picpath = unit + "/" + lesson+"/pics/"
	soundpath = unit + "/" + lesson+"/sounds/"
	count_originals = 0
	for pic in listofpics:
		screen.fill(background_colour)
		soundbutton = screen.blit(soundpic, (0,0))
		drawnextbutton()
		drawpronunciationbutton(w-200,h/2)
		answer = pic
		word = answer[:answer.rindex(".")]
		word_display = word#.replace(".questionmark","?")
		for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
			word_display = word_display.replace(sym,replacementsdict[sym])
		try:
			wordsound = pg.mixer.music.load(soundpath+word+"speech_google.ogg")
		except:
			wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
		display_word(word_display)
		drawquitbutton()
		#drawmenubutton()
		picimage = pg.image.load(picpath + pic)
		picimage = pg.transform.smoothscale(picimage, getbestratio(screen.get_size()[1]-300,screen.get_size()[0]-300,float(picimage.get_size()[1]),float(picimage.get_size()[0]))) #(screenheight, screenwidht, picheight, picwidth)
		screen.blit(picimage,[5,100])
		#play word sound
		pg.display.flip()
		pg.mixer.music.play(0)
		#Figure out what to do with click event handler
		looping = True
		while looping:
			for event in pg.event.get():
				# exit conditions --> windows titlebar x click
				if event.type == pg.QUIT:
					raise SystemExit
				if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
					pos = pg.mouse.get_pos()
					if soundbutton.collidepoint(pos): #Sound button is pressed
						pg.mixer.music.play(0)
					if pronunciationbutton.collidepoint(pos):
						pg.draw.rect(screen,background_colour,(w-200,h/2,80,80),0)
						pronunciationbuttonpic = pg.image.load("recorddot.png").convert_alpha()
						pronunciationbutton = screen.blit(pronunciationbuttonpic, [w-200,h/2])
						pg.display.update()
						try:
							recordinput()
						except:
							os.system("rec -c 2 /tmp/voice.aiff trim 0 00:05")
						pg.draw.rect(screen,background_colour,(w-200,h/2,80,80),0)
						drawpronunciationbutton(w-200,h/2)
						pg.display.update()
						pg.mixer.music.play(0)
						pg.time.wait(1000)
						try:
							playinput()
						except:
							output = pg.mixer.music.load("/tmp/input.wav")
							pg.mixer.music.play(0)
							os.system("play /tmp/voice.aiff")
					if quitbutton.collidepoint(pos):
						raise SystemExit
					if nextbutton.collidepoint(pos):
						looping = False
						break
def mainlesson(lesson):
	global scorelabel, score, incorrectscore, trycount, original_length, missed, menupushed
	menupushed = False
	missed = []
	score = 0
	incorrectscore = 0
	#lesson = "emotions" #temporary lesson variable before getting screen picked
	listofpics = [f for f in listdir(unit + "/" + lesson+"/pics/") if isfile(join(unit + "/" + lesson+"/pics/",f))] #pictures in unit/lesson/pics/ folder
	original_length = len(listofpics)
	random.shuffle(listofpics) #shuffle order of lesson
	picpath = unit + "/" + lesson+"/pics/"
	soundpath = unit + "/" + lesson+"/sounds/"
	count_originals = 0
	for pic in listofpics:
		trycount = 0
		count_originals += 1
		drawlessonstructure()
		answer = pic
		word = answer[:answer.rindex(".")]
		word_display = word#.replace(".questionmark","?")
		for sym in [sym for sym in replacementsdict.keys() if sym in word_display]:
			word_display = word_display.replace(sym,replacementsdict[sym])
		try:
			wordsound = pg.mixer.music.load(soundpath+word+"speech_google.ogg")
		except:
			wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
		choices = ["","","",""] 
		choices[0] = answer #choiceX = answer ... we don't know which choice number it is
		#if choices[0] gets clicked and trycount == 0, add to score, move to next pic
		#if [choices[1],choices[2], choices[3]] get clicked, trycount += 1, play word again, wait for click, append to end of list?
		choices[1] = random.choice([x for x in listofpics if x != choices[0]])
		choices[2] = random.choice([x for x in listofpics if x not in [choices[0],choices[1]]])
		choices[3] = random.choice([x for x in listofpics if x not in [choices[0],choices[1],choices[2]]])
		#Load pictures, scale and match to choiceboxes surfaces
		randomindex = [0,1,2,3]
		random.shuffle(randomindex)#mixing up the placement of the answer
		choice1 = choices[randomindex[0]]
		choice2 = choices[randomindex[1]]
		choice3 = choices[randomindex[2]]
		choice4 = choices[randomindex[3]]
		pic1 = pg.image.load(picpath+choice1)
		pic2 = pg.image.load(picpath+choice2)
		pic3 = pg.image.load(picpath+choice3)
		pic4 = pg.image.load(picpath+choice4)
		pics = [pic1,pic2,pic3,pic4]
		#scale pictures to max size without stretching
		pic1 = pg.transform.smoothscale(pic1, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic1.get_size()[1]),float(pic1.get_size()[0])))
		pic2 = pg.transform.smoothscale(pic2, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic2.get_size()[1]),float(pic2.get_size()[0])))
		pic3 = pg.transform.smoothscale(pic3, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic3.get_size()[1]),float(pic3.get_size()[0])))
		pic4 = pg.transform.smoothscale(pic4, getbestratio((float(choicebox1[3])),float(choicebox1[2]),float(pic4.get_size()[1]),float(pic4.get_size()[0])))
		#match to choiceboxes surfaces
		surf1 = pg.Surface.blit(screen,pic1,choicebox1)
		surf2 = pg.Surface.blit(screen,pic2,choicebox2)
		surf3 = pg.Surface.blit(screen,pic3,choicebox3)
		surf4 = pg.Surface.blit(screen,pic4,choicebox4)
		pics = [pic1,pic2,pic3,pic4]
		surfs = [surf1,surf2,surf3,surf4]	
		display_word(word_display)
		drawmenubutton()
		#play word sound
		pg.display.flip()
		pg.mixer.music.play(0)
		#Figure out what to do with click event handler
		looping = True
		while looping:
			for event in pg.event.get():
				# exit conditions --> windows titlebar x click
				if event.type == pg.QUIT:
					raise SystemExit
				if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
					pos = pg.mouse.get_pos()
					if soundbutton.collidepoint(pos): #Sound button is pressed
						pg.mixer.music.play(0)
					#Wrong answer is clicked
					elif surfs[randomindex.index(1)].collidepoint(pos) or surfs[randomindex.index(2)].collidepoint(pos) or surfs[randomindex.index(3)].collidepoint(pos):
						screen.blit(wrongpic,[(w-wrongpic.get_rect()[2]-150),0])
						pg.display.flip()
						missed.append(word_display)
						wrong_sound.play()
						pg.mixer.music.play(0)
						trycount += 1
					#Right answer is clicked
					elif surfs[randomindex.index(0)].collidepoint(pos):
						correct_sound.play()
						screen.fill(background_colour)
						try:
							wordsound = pg.mixer.music.load(soundpath+word+"speech_google.ogg")
						except:
							wordsound = pg.mixer.music.load(soundpath+word+"speech_google.wav")
						display_word(word_display)
						screen.blit(pics[randomindex.index(0)],[(w - pics[randomindex.index(0)].get_rect()[2])/2,(h- pics[randomindex.index(0)].get_rect()[1])/2])
						pg.display.flip()
						pg.mixer.music.play(0)
						pg.time.wait(1500)
						looping = False
						break
					elif menubutton.collidepoint(pos):
						looping = False
						menupushed = True
						break
		if menupushed == True:
			break
		if trycount == 0 and count_originals <= original_length:
			score +=1
		elif trycount > 0:
			incorrectscore += 1
			listofpics.append(pic) #review picture if you got it wrong

	#display score screen after for loop is finished
def displayscore(lesson):
	global scorelabel,w,h, score,incorrectscore, completeddict
	print set(missed)
	screen.fill(white)
	datebox = pg.draw.rect(screen, black, (0,100,(w)/4,100), 3)
	unitbox = pg.draw.rect(screen, black, ((w)/4,100,(w)/4,100), 3)
	lessonbox = pg.draw.rect(screen, black, ((w)/2,100,(w)/4,100), 3)
	scorebox = pg.draw.rect(screen, black, (3*(w)/4,100,(w)/4,100), 3)
	datelabel = mysmallfont.render(str(date), 2, black)
	columnlabels = [mysmallfont.render("Date: ", 2, black),mysmallfont.render("Unit: ", 2, black),mysmallfont.render("Lesson: ", 2, black),mysmallfont.render("Score: ", 2, black)]
	for column in columnlabels:
		dist = (w/4)*(columnlabels.index(column))
		screen.blit(column, [dist+10,50])
	boxtexts = [mysmallfont.render(str(date), 2, black),mysmallfont.render(unit, 2, black),mysmallfont.render(lesson, 2, black),mysmallfont.render(str(int((float(score) / float(original_length))*100))+" %", 2, black)]
	for box in boxtexts:
		dist = (w/4)*(boxtexts.index(box))
		screen.blit(box, [dist+10,100])
	chooselessonbuttontext = mysmallfont.render("Choose a lesson", 2, black)
	chooselessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(chooselessonbuttontext.get_rect()[2]/2)-3,h-200-3,chooselessonbuttontext.get_width()+6,chooselessonbuttontext.get_height()+6),0)
	chooselessonbutton = screen.blit(chooselessonbuttontext, [(w/2)-(chooselessonbuttontext.get_rect()[2]/2),h-200])
	repeatlessonbuttontext = mysmallfont.render("Repeat", 2, black)
	repeatlessonbuttonbox = pg.draw.rect(screen,gray,((w/2)-(repeatlessonbuttontext.get_rect()[2]/2)-3,h-200-3-65,repeatlessonbuttontext.get_width()+6,repeatlessonbuttontext.get_height()+6),0)
	repeatlessonbutton = screen.blit(repeatlessonbuttontext, [(w/2)-(repeatlessonbuttontext.get_rect()[2]/2),h-200-65])
	repeatpic = pg.image.load("repeat.png").convert_alpha()
	pencilpic = pg.image.load("pencil.png").convert_alpha()
	screen.blit(pencilpic, [w/2,h/2])
	rep = screen.blit(repeatpic, [repeatlessonbuttonbox[0]-75,repeatlessonbuttonbox[1]-3])
	drawquitbutton()
	pg.display.flip()
	completeddict[lesson] = int((float(score) / float(original_length))*100)
	looping = True
	while looping:
		for event in pg.event.get():
			# exit conditions --> windows titlebar x click
			if event.type == pg.QUIT:
				raise SystemExit
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				pos = pg.mouse.get_pos()
				if quitbutton.collidepoint(pos):
					raise SystemExit
				if repeatlessonbuttonbox.collidepoint(pos) or rep.collidepoint(pos):
					mainlesson(lesson)
					displayscore(lesson)
				if chooselessonbuttonbox.collidepoint(pos):
					looping = False
					break
				
#display Lessons Menu
def unitmenu():
	global completeddict, buttonresult
	screen = pg.display.set_mode((0,0)) #full sized window mode
	screen.fill(background_colour)
	size = screen.get_size()
	w = size[0]
	h = size[1]
	pg.display.set_caption("RosettaTablet")
	myfont = pg.font.Font(font, 50)#formerly SysFont
	mysmallfont = pg.font.Font(font, 40)
	global unit
	uniton = True
	screen.fill(background_colour)
	listoffolders = [f for f in listdir("./") if isfile(join("./",f)) == False]
	listoffolders.remove("examplelesson") #remove blank lesson from menu
	listoffolders.remove("exampleunit")
	listoffolders.remove("Test")
	listoffolderlables = [screen.blit(mysmallfont.render(str(listoffolders.index(folder)+1)+". "+folder.title(), 1, black),[20,45*listoffolders.index(folder)]) for folder in listoffolders]
	drawquitbutton()
	pg.display.flip()
	while uniton:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				raise SystemExit
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				pos = pg.mouse.get_pos()
				if quitbutton.collidepoint(pos):
					raise SystemExit
				for folder in listoffolderlables:
					if folder.collidepoint(pos):
						unit = listoffolders[listoffolderlables.index(folder)]
						print unit
						lessonmenu(unit)
						pg.display.quit
						return unit
def lessonmenu(unit):
	global completeddict, buttonresult,lessonon
	screen = pg.display.set_mode((0,0)) #full sized window mode
	screen.fill(background_colour)
	size = screen.get_size()
	w = size[0]
	h = size[1]
	pg.display.set_caption("RosettaTablet")
	myfont = pg.font.Font(font, 50)
	mysmallfont = pg.font.Font(font, 40)
	global lesson
	lessonon = True
	screen.fill(background_colour)
	mysmallfont = pg.font.Font(font, 40)
	listoffolders = [f for f in listdir("./"+unit) if isfile(join("./"+unit,f)) == False]
	listoffolders.remove("examplelesson") #remove blank lesson from menu
	listoffolderlables = [screen.blit(mysmallfont.render(str(listoffolders.index(folder)+1)+". "+folder.title(), 1, black),[20,45*listoffolders.index(folder)]) for folder in listoffolders]
	#drawquitbutton()
	drawmenubutton()
	pg.display.flip()
	completedlessons = completeddict.keys()
	print "Completed Lessons:",completedlessons
	while lessonon:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				raise SystemExit
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				pos = pg.mouse.get_pos()
				#if quitbutton.collidepoint(pos):
				#	raise SystemExit
				if menubutton.collidepoint(pos):
					lessonon = False
					break
				for folder in listoffolderlables:
					if folder.collidepoint(pos):
						lesson = listoffolders[listoffolderlables.index(folder)]
						print lesson
						displayactivitychoice()
						pg.display.quit
						return lesson

#pronunciationpractice("emotions")
while True:
	unitmenu()
	if lessonon == True:
		if buttonresult == "mainlesson":
			mainlesson(lesson)
			if menupushed == False:
				displayscore(lesson)
		elif buttonresult == "pronunciation":
			pronunciationpractice(lesson)
			if menupushed == True:
				unitmenu()
		else:
			unitmenu()
	else:
		unitmenu()
