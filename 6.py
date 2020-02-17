#! /usr/bin/python3
import os
import time
import sys
from collections import defaultdict
import math
import rare_words_utils as rwutils
import viterbi_utils as vitutils

if __name__ == '__main__':
	start_time = time.time()

	if not os.path.exists("./ner_train_multirare.dat"):
		rwutils.generate_files(False)

	if not os.path.exists("./ner_multirare.counts"):
		os.system("python3 count_freqs3.py ner_train_multirare.dat > ner_multirare.counts")
	
	try:
		count_file = open("./ner_multirare.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_multirare.counts.\n")
		sys.exit(1)

	bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T = vitutils.get_useful(count_file)
	
	tagging = vitutils.Tagging(bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T)
	
	try:
		words_file = open("./ner_dev.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_dev.dat.\n")
		sys.exit(1)

	try:
		predict_file = open("./6.txt","w")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./5_2.txt.\n")
		sys.exit(1)

	tagging.predict(words_file, predict_file, False)

	end_time = time.time()
	print("Running time: " + str(end_time - start_time))

	

