#! /usr/bin/python3
import os
import sys
from collections import defaultdict
import math

def get_bigram_trigram_count_dict(count_file):
	bigram_count = defaultdict(int)
	trigram_count = defaultdict(int)

	l = count_file.readline()
	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# count N-GRAM TAG1 TAG2 TAG3 
			fields = line.split(" ")
			if fields[1] == "2-GRAM":
				bigram_count[(fields[2], fields[3])] += int(fields[0])
			elif fields[1] == "3-GRAM":
				trigram_count[(fields[2], fields[3], fields[4])] += int(fields[0])

		l = count_file.readline()

	return bigram_count, trigram_count

def calculate(input_file, output_file, bigram_count, trigram_count):
	l = input_file.readline()
	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# TAG1 TAG2 TAG3
			fields = line.split(" ")
			tri = (fields[0], fields[1], fields[2])
			bi = (fields[0], fields[1])
			score = math.log2(float(trigram_count[tri]) / float(bigram_count[bi]))
			output_file.write(line + " " + str(score) + "\n")

		l = input_file.readline()

if __name__ == "__main__":
	if not os.path.exists("./ner_train_rare.dat"):
		os.system("python3 4_1.py")

	if not os.path.exists("./ner_rare.counts"):
		os.system("python3 count_freqs3.py ner_train_rare.dat > ner_rare.counts")

	try:
		count_file = open("./ner_rare.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_rare.counts.\n")
		sys.exit(1)

	bigram_count, trigram_count = get_bigram_trigram_count_dict(count_file)
	#print(bigram_count)
	#print(trigram_count)

	try:
		input_file = open("./trigrams.txt","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./trigrams.txt.\n")
		sys.exit(1)

	try:
		output_file = open("./5_1.txt", "w")
	except IOError:
		sys.stderr.write("ERROR: Cannot write outputfile ./5_1.txt.\n")
		sys.exit(1)

	calculate(input_file, output_file, bigram_count, trigram_count)