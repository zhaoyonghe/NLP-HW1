#! /usr/bin/python3
import os
import sys
import time
from collections import defaultdict
import math

# temp = [("PER", "I-PER"),("ORG", "I-ORG"),("LOC", "I-LOC"),("ISC", "I-MISC"),("O","O")]

def get_two_dicts_one_set(count_file):
	# key: tag, value: count of that tag
	tag_to_count = defaultdict(int)

	# key: (tag, word), value: count of that (tag, word) pair
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
				tag_to_count[fields[2]] += int(fields[0])
				tag_word_to_count[(fields[2], fields[3])] += int(fields[0])

		l = count_file.readline()

	temp = ["I-PER", "I-ORG", "I-LOC", "I-MISC", "B-PER", "B-ORG", "B-LOC", "B-MISC", "O"]
	temp = [tag for tag in temp if tag_to_count[tag] != 0]

	return tag_to_count, tag_word_to_count, words, temp

def predict(words_file, tag_to_count, tag_word_to_count, words, predict_file, temp):
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
				w = "_RARE_"

			ma = 0
			predicted_tag = ""			
			for tag in temp:
				e = tag_word_to_count[(tag, w)] / tag_to_count[tag]
				if e > ma:
					ma = e
					predicted_tag = tag				

			predict_file.write(word + " " + predicted_tag + " " + str(math.log2(ma)) + "\n") 
		else:
			predict_file.write("\n")
		l = words_file.readline()	

if __name__ == "__main__":
	start_time = time.time()

	if not os.path.exists("./ner_train_rare.dat"):
		rwutils.generate_files(True)

	if not os.path.exists("./ner_rare.counts"):
		print("Generating ner_rare.counts...")
		os.system("python3 count_freqs3.py ner_train_rare.dat > ner_rare.counts")

	try:
		count_file = open("./ner_rare.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_rare.counts.\n")
		sys.exit(1)

	tag_to_count, tag_word_to_count, words, temp = get_two_dicts_one_set(count_file)
	#print(tag_to_count)
	#print(tag_word_to_count)
	#print(temp)

	try:
		words_file = open("./ner_dev.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_dev.dat.\n")
		sys.exit(1)

	try:
		print("Generating ./4_2_diff.txt...")
		predict_file = open("./4_2_diff.txt","w")
	except IOError:
		sys.stderr.write("ERROR: Cannot write outputfile ./4_2_diff.txt.\n")
		sys.exit(1)

	predict(words_file, tag_to_count, tag_word_to_count, words, predict_file, temp)
	# rare words will always get the same prediction
	
	end_time = time.time()
	print("Running time: " + str(end_time - start_time) + " seconds.")