#!/usr/bin/python3
print("start")

import os
import tarfile
import tempfile
import shutil
from multiprocessing import Pool
import time
from datetime import datetime

BASE_DIR = "../../TrainingData"
COMPRESSED_DIR = f"{BASE_DIR}/compressed"
UNCOMPRESSED_DIR = f"{BASE_DIR}/uncompressed"
TEMP_DIR = f"{BASE_DIR}/temp"

# moved to its own storage: /scratch/hpc-prf-katapar/traing
os.makedirs(UNCOMPRESSED_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# (Probably not needed anymore)
def adjust_times(root_dir, timestamp):
	for root, dirs, files in os.walk(root_dir, topdown=False):
		for sub_dir in dirs:
			os.utime(os.path.join(root, sub_dir), (timestamp, timestamp))
		for file_name in files:
			os.utime(os.path.join(root, file_name), (timestamp, timestamp))

def process_file(file_name):
	if not file_name.endswith(".tgz"):
		return

	# Extract base name for directory (e.g., '2024-11-24' from '2024-11-24npzs.tgz')
	base_name = file_name.split("npzs")[0]
	dir_date = datetime.strptime(base_name, "%Y-%m-%d")
	timestamp = time.mktime(dir_date.timetuple())

	source_file_path = os.path.join(COMPRESSED_DIR, file_name)
	target_dir = os.path.join(UNCOMPRESSED_DIR, base_name)
	temp_dir = os.path.join(TEMP_DIR, base_name)

	if os.path.exists(target_dir):
		#print(f"Skipping {file_name}")
		return

	print(f"Extracting {file_name} to {temp_dir}")
	os.makedirs(temp_dir, exist_ok=True)
	try:
		with tarfile.open(source_file_path, 'r') as tar:
			for member in tar.getmembers():
				# Remove the topmost directory in the member's path (equals tgz file name)
				member.name = member.name.split('/', 1)[-1]  # Keep everything after the first '/'
				tar.extract(member, path=temp_dir, filter="data")
		time.sleep(10)

		# The shuffle script expects the last-modified timestamp of the dirs/files to correspond to their name. Fix this manually here.
		adjust_times(temp_dir, timestamp)
		time.sleep(10)

		# All done, move the result to production
		shutil.move(temp_dir, target_dir)
		os.utime(target_dir, (timestamp, timestamp))
		print(f"Moved {file_name} contents to {target_dir}")

	except Exception as e:
		# Incomplete download?!
		print(f"Failed to process {file_name}: {e}")
		return


if __name__ == "__main__":
	file_names = os.listdir(COMPRESSED_DIR)
	if 1111==1111:
		with Pool(50) as pool:
			results = pool.map(process_file, file_names)
	else:
		for f in file_names:
			process_file(f)

print("end")
