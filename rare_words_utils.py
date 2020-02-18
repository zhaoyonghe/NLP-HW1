import os
import sys
from collections import defaultdict
import re

RARE = "_RARE_"

# other rare classes
FIR_CAP = "_FIR_CAP_"
ALL_CAP = "_ALL_CAP_" # not useful
ALL_NUM = "_ALL_NUM_" # not useful
CAP_PER = "_CAP_PER_" # not useful

PUR_DIG = "_PUR_DIG_"

TWO_DIG = "_TWO_DIG_" # not useful
FOUR_DIG = "_FOUR_DIG_" # not useful

DIG_CHA = "_DIG_CHA_" # not useful


RARE_CLASSES = [RARE, FIR_CAP, CAP_PER, ALL_NUM, DIG_CHA]


def is_all_num(word):
	return re.match("^\\+?\\-?\\d(\\d|\\.|\\-|\\+|,|/)+$", word)

def is_fir_cap(word):
	return word[0].isupper() and not re.match("^[A-Z]+\\+?\\-?\\d(\\d|\\.|\\-|\\+|,|/)+$", word)

def is_cap_per(word):
	return re.match("^[A-Z]\\.", word)

def is_dig_cha(word):
	return re.match("^[A-Z]+\\+?\\-?\\d(\\d|\\.|\\-|\\+|,|/)+$", word)

def get_rare_class(word, pure_rare = True):
	if pure_rare:
		return RARE
	else:
		if is_all_num(word):
			return ALL_NUM
		elif is_fir_cap(word):
			return FIR_CAP
		else:
			return RARE

# return value:
# key: rare word itself
# value: the class of that rare word
def get_rare_words_dict(count_file, pure_rare = True):
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

	rare_words = {}
	for (k, v) in words_count.items():
		if v < 5:
			rare_words[k] = get_rare_class(k, pure_rare)

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
			if word in rare_words.keys():
				output_file.write(rare_words[word] + " " + ne_tag + "\n")
			else:
				output_file.write(line + "\n")
		else:
			output_file.write("\n")
                       
		l = input_file.readline()

def generate_files(pure_rare):
	if not os.path.exists("./ner.counts"):
		print("Generating ./ner.counts...")
		os.system("python3 count_freqs3.py ner_train.dat > ner.counts")

	try:
		count_file = open("./ner.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner.counts.\n")
		sys.exit(1)

	rare_words = get_rare_words_dict(count_file, pure_rare)
	#print(rare_words)

	try:
		input_file = open("./ner_train.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_train.dat.\n")
		sys.exit(1)

	output_file = None
	if pure_rare:
		try:
			print("Generating ./ner_train_rare.dat...")
			output_file = open("./ner_train_rare.dat", "w")
		except IOError:
			sys.stderr.write("ERROR: Cannot write outputfile ./ner_train_rare.dat.\n")
			sys.exit(1)
	else:
		try:
			print("Generating ./ner_train_multirare.dat...")
			output_file = open("./ner_train_multirare.dat", "w")
		except IOError:
			sys.stderr.write("ERROR: Cannot write outputfile ./ner_train_multirare.dat.\n")
			sys.exit(1)

	replace_rare_words(input_file, output_file, rare_words)