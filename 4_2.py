#! /usr/bin/python3
import os
import sys
from collections import defaultdict
import math
import rare_words_utils as rwutils

temp = [("PER", "I-PER"),("ORG", "I-ORG"),("LOC", "I-LOC"),("ISC", "I-MISC"),("O","O")]

def get_two_dicts_one_set(count_file):
	tag_to_count = defaultdict(int)
	tag_word_to_count = defaultdict(int)
	words = set()

	l = count_file.readline()
	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# word_count WORDTAG TAGTYPE word 
			fields = line.split(" ")
			if fields[1] == "WORDTAG":
				words.add(fields[3])
				if len(fields[2]) == 1:
					tag_to_count["O"] += int(fields[0])
					tag_word_to_count[("O", fields[3])] += int(fields[0])
				else:
					for (k, v) in temp:
						if fields[2][-3:] == k:
							tag_to_count[v] += int(fields[0])
							tag_word_to_count[(v, fields[3])] += int(fields[0])
							break            
		l = count_file.readline()

	return tag_to_count, tag_word_to_count, words

def predict(words_file, tag_to_count, tag_word_to_count, words, predict_file):
	l = words_file.readline()
	while l:
		word = l.strip()
		#print(word)
		if word: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# word_count WORDTAG TAGTYPE word 
			w = word
			if word not in words:
				w = rwutils.get_rare_class(word)

			ma = 0
			predicted_tag = ""			
			for (_, tag) in temp:
				e = tag_word_to_count[(tag, w)] / tag_to_count[tag]
				if e > ma:
					ma = e
					predicted_tag = tag				

			predict_file.write(word + " " + predicted_tag + " " + str(math.log2(ma)) + "\n") 
		else:
			predict_file.write("\n")
		l = words_file.readline()	

if __name__ == "__main__":
	if not os.path.exists("./ner_train_rare.dat"):
		print("Generating ner_train_rare.dat...")
		os.system("python3 4_1.py")

	if not os.path.exists("./ner_rare.counts"):
		print("Generating ner_rare.counts...")
		os.system("python3 count_freqs3.py ner_train_rare.dat > ner_rare.counts")

	try:
		count_file = open("./ner_rare.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_rare.counts.\n")
		sys.exit(1)

	tag_to_count, tag_word_to_count, words = get_two_dicts_one_set(count_file)
	#print(tag_to_count)
	#print(tag_word_to_count)

	try:
		words_file = open("./ner_dev.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_dev.dat.\n")
		sys.exit(1)

	try:
		predict_file = open("./4_2.txt","w")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./4_2.txt.\n")
		sys.exit(1)

	predict(words_file, tag_to_count, tag_word_to_count, words, predict_file)
	# print(tag_to_count)
	# rare words will always get the same prediction
