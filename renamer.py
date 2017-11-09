import sys
import os
import subprocess
from shutil import copy2
from dateutil.parser import parse
import argparse

folder = sys.argv[1]
albumformat = sys.argv[2]

created = False
year = ""
quality = ""
album = ""
performer = ""
output = ""

scriptpath = os.path.dirname(folder)

for filename in os.listdir(folder):
	ext = os.path.splitext(filename)[1]
	print("\nProcessing file: " + filename)
	if ext.lower() in [".mp3",".flac"]:
		print("Found audio file")
		if created == False:
			process = subprocess.Popen("mediainfo " + ' --Inform="General;%Album%,.,%Performer%,.,%Recorded_Date%,.,%Original/Released_Date%,.,%Released_Date%" ' + '"' + filename + '"', cwd=scriptpath, shell="true", stdout=subprocess.PIPE)
			out, err = process.communicate()
			
			try:
				out = out.decode()
			except AttributeError:
				pass
			params = out.split(",.,")
			if params[0] != "":
				album = params[0]
			else:
				album = "undefined"
			if params[1] != "":
				performer = params[1]
			else:
				performer = "undefined"
			if params[2] != "":
				year = str(parse(params[2], fuzzy=True).year)
			elif params[3] != "":
				year = str(parse(params[3], fuzzy=True).year)
			elif params[4] != "":
				year = str(parse(params[4], fuzzy=True).year)
			else:
				year = "undefined"
			 
			if ext.lower() == ".flac":
				quality = "FLAC"
			elif ext.lower() == ".mp3":
				process = subprocess.Popen("mediainfo " + ' --Inform="Audio;%BitRate%,.,%BitRate_Mode%,.,%Format_Version%" '+ '"' + filename + '"', cwd=scriptpath, shell="true", stdout=subprocess.PIPE)
				out, err = process.communicate()
				try:
					out = out.decode()
				except AttributeError:
					pass
				params = out.split(",.,")
				if params[1] == "CBR":
					quality = str((int(params[0])/1000))
				elif params[1] == "VBR":
					params[2] = str(params[2])
					version = [int(s) for s in params[2].split() if s.isdigit()]
					version[0] = str(version[0])
					quality = "V" + version[0]
				else:
					quality = "undefined"

			if quality != "" and year != "" and performer != "" and album != "":
				print("Got params for directory creation: ")
				print("Performer: " + performer)
				print("Album: " + album)
				print("Year: " + year)
				print("Quality: " + quality)
				output = performer + " - " + album + " [" + year + "] [" + albumformat + "] [" + quality + "]"
				if not os.path.isdir(output):
					print("Creating dir: " + output)
					os.makedirs(output)
				else:
					print("Dir " + output + " already exists")
				created = True

		process = subprocess.Popen("mediainfo " + ' --Inform="General;%Track/Position% - %Performer% - %Title%.%FileExtension%" ' + '"' + filename + '"', cwd=scriptpath, shell="true", stdout=subprocess.PIPE)
		out, err = process.communicate()
		  
		try:
			out = out.decode()
			print("Found invalid chars in metadata. Issue was fixed.")
		except AttributeError:
			pass

		if os.path.isdir(output):
			print("Creating new file: " + out.rstrip())
			copy2(folder + "/" + filename, output)
			os.rename(output + "/" + filename, output + "/" + out.rstrip())

