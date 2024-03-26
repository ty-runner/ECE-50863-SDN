from typing import List
import math
# Adapted from code by Zach Peats

# ======================================================================================================================
# Do not touch the client message class!
# ======================================================================================================================

# BBA-2 Implementation

class ClientMessage:
	"""
	This class will be filled out and passed to student_entrypoint for your algorithm.
	"""
	total_seconds_elapsed: float	  # The number of simulated seconds elapsed in this test
	previous_throughput: float		  # The measured throughput for the previous chunk in kB/s

	buffer_current_fill: float		    # The number of kB currently in the client buffer
	buffer_seconds_per_chunk: float     # Number of seconds that it takes the client to watch a chunk. Every
										# buffer_seconds_per_chunk, a chunk is consumed from the client buffer.
	buffer_seconds_until_empty: float   # The number of seconds of video left in the client buffer. A chunk must
										# be finished downloading before this time to avoid a rebuffer event.
	buffer_max_size: float              # The maximum size of the client buffer. If the client buffer is filled beyond
										# maximum, then download will be throttled until the buffer is no longer full

	# The quality bitrates are formatted as follows:
	#
	#   quality_levels is an integer reflecting the # of quality levels you may choose from.
	#
	#   quality_bitrates is a list of floats specifying the number of kilobytes the upcoming chunk is at each quality
	#   level. Quality level 2 always costs twice as much as quality level 1, quality level 3 is twice as big as 2, and
	#   so on.
	#       quality_bitrates[0] = kB cost for quality level 1
	#       quality_bitrates[1] = kB cost for quality level 2
	#       ...
	#
	#   upcoming_quality_bitrates is a list of quality_bitrates for future chunks. Each entry is a list of
	#   quality_bitrates that will be used for an upcoming chunk. Use this for algorithms that look forward multiple
	#   chunks in the future. Will shrink and eventually become empty as streaming approaches the end of the video.
	#       upcoming_quality_bitrates[0]: Will be used for quality_bitrates in the next student_entrypoint call
	#       upcoming_quality_bitrates[1]: Will be used for quality_bitrates in the student_entrypoint call after that
	#       ...
	#
	quality_levels: int
	quality_bitrates: List[float]
	upcoming_quality_bitrates: List[List[float]]

	# You may use these to tune your algorithm to each user case! Remember, you can and should change these in the
	# config files to simulate different clients!
	#
	#   User Quality of Experience =    (Average chunk quality) * (Quality Coefficient) +
	#                                   -(Number of changes in chunk quality) * (Variation Coefficient)
	#                                   -(Amount of time spent rebuffering) * (Rebuffering Coefficient)
	#
	#   *QoE is then divided by total number of chunks
	#
	quality_coefficient: float
	variation_coefficient: float
	rebuffering_coefficient: float
# ======================================================================================================================


# Your helper functions, variables, classes here. You may also write initialization routines to be called
# when this script is first imported and anything else you wish.

def determine_best_rate(client_message: ClientMessage, current_rate: int, calculated_rate: float):
	# If the buffer is full, increase the quality level.
	differences = {}
	for rate in range (client_message.quality_levels):
		difference = abs(client_message.quality_bitrates[rate] - calculated_rate)
		differences[rate] = difference
	min_rate = min(differences, key=differences.get)
	if min_rate > current_rate:
		print("Increasing rate")
	return min_rate

# def calc_chunk_size(client_message: ClientMessage, rate: int):
# 	# Total size = base chunk size * chunk size ratio * 2 ^ (quality level - 1)
# 	print(client_message.buffer_seconds_per_chunk)
# 	return client_message.buffer_seconds_per_chunk * 1 * 2 ** rate

last_rate = 0
last_buffer_occupancy = 0
def student_entrypoint(client_message: ClientMessage):
	"""
	Your mission, if you choose to accept it, is to build an algorithm for chunk bitrate selection that provides
	the best possible experience for users streaming from your service.

	Construct an algorithm below that selects a quality for a new chunk given the parameters in ClientMessage. Feel
	free to create any helper function, variables, or classes as you wish.

	Simulation does ~NOT~ run in real time. The code you write can be as slow and complicated as you wish without
	penalizing your results. Focus on picking good qualities!

	Also remember the config files are built for one particular client. You can (and should!) adjust the QoE metrics to
	see how it impacts the final user score. How do algorithms work with a client that really hates rebuffering? What
	about when the client doesn't care about variation? For what QoE coefficients does your algorithm work best, and
	for what coefficients does it fail?

	Args:
		client_message : ClientMessage holding the parameters for this chunk and current client state.

	:return: float Your quality choice. Must be one in the range [0 ... quality_levels - 1] inclusive.
	"""
	global last_rate
	global last_buffer_occupancy
	#BBA-0 Algo
	#print(f"Quality levels: {client_message.quality_bitrates}")
	#print(f"Previous throughput: {client_message.previous_throughput}")
	reservior = client_message.buffer_max_size * 0.375
	if client_message.buffer_seconds_until_empty >= client_message.buffer_max_size * 0.9:
		#steady state
		calc_chunk_size(client_message, last_rate)
		return 2
	elif client_message.buffer_seconds_until_empty < reservior:
		#startup
		return 0
	else:
		#transient state, linearly increase quality level f(B)
		#print(last_buffer_occupancy)
		#print(last_rate, client_message.previous_throughput)
		last_rate = determine_best_rate(client_message, last_rate, client_message.previous_throughput)
		#print(f"Last rate: {last_rate}")
		last_buffer_occupancy = client_message.buffer_seconds_until_empty
		return last_rate
	#return min(client_message.quality_levels - 1, client_message.quality_levels - 1)
