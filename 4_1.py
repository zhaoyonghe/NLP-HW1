#! /usr/bin/python3

import sys
from collections import defaultdict

def get_rare_words_set(count_file):
	words_count = defaultdict(int)

	l = count_file.readline()
	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# word_count WORDTAG TAGTYPE word 
			fields = line.split(" ")
			if fields[1] == "WORDTAG":
				words_count[fields[3]] += int(fields[0])                
		l = count_file.readline()

	rare_words = set()
	for (k, v) in words_count.items():
		if v < 5:
			rare_words.add(k)

	return rare_words


def replace_rare_words(input_file, output_file, rare_words):
	l = input_file.readline()
	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Each line has the format
			# word pos_tag phrase_tag ne_tag
			fields = line.split(" ")
			ne_tag = fields[-1]
			#phrase_tag = fields[-2] #Unused
			#pos_tag = fields[-3] #Unused
			word = " ".join(fields[:-1])
			if word in rare_words:
				output_file.write("_RARE_ " + ne_tag + "\n")
			else:
				output_file.write(line + "\n")
		else:
			output_file.write("\n")
                       
		l = input_file.readline()


if __name__ == "__main__":
	try:
		count_file = open("./ner.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner.counts.\n")
		sys.exit(1)

	rare_words = get_rare_words_set(count_file)

	try:
		input_file = open("./ner_train.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_train.dat.\n")
		sys.exit(1)

	try:
		output_file = open("./ner_train_rare.dat", "w")
	except IOError:
		sys.stderr.write("ERROR: Cannot write outputfile ./ner_train_rare.dat.\n")
		sys.exit(1)

	replace_rare_words(input_file, output_file, rare_words)
