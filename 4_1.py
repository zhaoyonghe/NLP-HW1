#! /usr/bin/python3
import os
import sys
import time
from collections import defaultdict
import rare_words_utils as rwutils

if __name__ == "__main__":
	start_time = time.time()

	rwutils.generate_files(True)

	end_time = time.time()
	print("Running time: " + str(end_time - start_time) + " seconds.")