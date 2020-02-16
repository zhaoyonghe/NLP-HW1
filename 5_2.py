#! /usr/bin/python3

import sys
from collections import defaultdict
import math

def simple_word_iterator(words_file):
	"""
	Get an iterator object over the words file. The elements of the
	iterator contain string word. 
	Blank lines, indicating sentence boundaries return None.
	"""
	l = words_file.readline()
	while l:
		word = l.strip()
		if word: # Nonempty line
			yield word
		else: # Empty line
			yield None
		l = words_file.readline()

def sentence_iterator(word_iterator):
	"""
	Return an iterator object that yields one sentence at a time.
	Sentences are represented as lists of words.
	"""
	current_sentence = [] #Buffer for the current sentence
	for word in word_iterator:        
		if word == None:
			if current_sentence:  #Reached the end of a sentence
				yield current_sentence
				current_sentence = [] #Reset buffer
			else: # Got empty input stream
				sys.stderr.write("WARNING: Got empty input file/stream.\n")
				raise StopIteration
		else:
			current_sentence.append(word) #Add token to the buffer

	if current_sentence: # If the last line was blank, we're done
		yield current_sentence  #Otherwise when there is no more token # in the stream return the last sentence


def get_useful(count_file):
	T = defaultdict(list)
	#print(type(T))

	tag_to_count = defaultdict(int)
	tag_word_to_count = defaultdict(int)
	words = set()

	bigram_count = defaultdict(int)
	trigram_count = defaultdict(int)

	l = count_file.readline()

	while l:
		line = l.strip()
		if line: # Nonempty line
			# Extract information from line.
			# Available line has the format
			# count N-GRAM TAG1 TAG2 TAG3
			# word_count WORDTAG TAGTYPE word
			fields = line.split(" ")
			if fields[1] == "WORDTAG":
				T[fields[3]].append(fields[2])
				words.add(fields[3])
				tag_word_to_count[(fields[2], fields[3])] += int(fields[0])
			elif fields[1] == "3-GRAM":
				trigram_count[(fields[2], fields[3], fields[4])] += int(fields[0])
			elif fields[1] == "2-GRAM":
				bigram_count[(fields[2], fields[3])] += int(fields[0])
			elif fields[1] == "1-GRAM":
				tag_to_count[fields[2]] += int(fields[0])

		l = count_file.readline()

	words.add("_START_")
	T["_START_"].append("*")
	return bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T


class Tagging:
	def __init__(self, bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T):
		self.bigram_count = bigram_count
		self.trigram_count = trigram_count
		self.tag_to_count = tag_to_count
		self.tag_word_to_count = tag_word_to_count
		self.words = words
		self.T = T

	def viterbi(self, sentence):
		n = len(sentence)
		sent = ["_START_"]
		sent.extend(sentence)
		#print(sent)

		# pi[k][v][u] for trigram w, u, v => pi(k, u, v)
		pi = [{"*":[("*", 1.0)]}]
		for i in range(1, len(sent)):
			pi.append(defaultdict(list))

		res = [("", "")] * (n + 1)
		T_RARE_ = self.T["_RARE_"]

		bp = {}
		for k in range(1, len(sent)):
			#print(sent[k - 1])
			Txkm1 = T_RARE_
			if sent[k - 1] in self.words: 
				Txkm1 = self.T[sent[k - 1]]
				
			#print(Txkm1)
			for u in Txkm1:
				temp = pi[k - 1][u]

				Txk = T_RARE_
				xk = "_RARE_"
				if sent[k] in self.words: 
					Txk = self.T[sent[k]]
					xk = sent[k]				

				for v in Txk:
					ma = 0
					maw = "fuck"
					for (w, s) in temp:
						a = trigram_count[(w, u, v)]
						if a == 0: 
							continue
						b = bigram_count[(w, u)]
						if b == 0:
							continue
						c = tag_word_to_count[(v, xk)]
						d = tag_to_count[v]
						score = s * (float(a)/float(b)) * (float(c)/float(d))
						if score > ma:
							ma = score
							maw = w
					if ma > 0:
						pi[k][v].append((u, ma))
					bp[(k, u, v)] = maw

		yn = ""
		ynm1 = ""
		ma = 0
		for v, li in pi[n].items():
			for (u, score) in li:
				a = trigram_count[(u, v, "STOP")]
				if a == 0: 
					continue				
				b = bigram_count[(u, v)]
				if b == 0: 
					continue	
				if score * (float(a)/float(b)) > ma:
					ma = score
					yn = v
					ynm1 = u

		res[n] = (sent[n], yn)
		res[n - 1] = (sent[n - 1], ynm1)

		for k in range(n - 2, 0, -1):
			res[k] = (sent[k], bp[(k + 2, res[k + 1][1], res[k + 2][1])])

		return res[1:]

	def predict(self, input_file, output_file):
		#print(self.T)
		sent_iterator = sentence_iterator(simple_word_iterator(input_file))
		for sent in sent_iterator:
			res = self.viterbi(sent)
			for (word, tag) in res:
				#output_file.write(w + " " + str(math.log2(s)) + "\n")
				output_file.write(word + " " + tag + " -7\n")
			output_file.write("\n")
			#break

if __name__ == '__main__':
	try:
		count_file = open("./ner_rare.counts","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_rare.counts.\n")
		sys.exit(1)

	bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T = get_useful(count_file)
	
	tagging = Tagging(bigram_count, trigram_count, tag_to_count, tag_word_to_count, words, T)
	
	try:
		words_file = open("./ner_dev.dat","r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./ner_dev.dat.\n")
		sys.exit(1)

	try:
		predict_file = open("./5_2.txt","w")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile ./5_2.txt.\n")
		sys.exit(1)

	tagging.predict(words_file, predict_file)