import hashlib
import multiprocessing
from time import time

import unidecode
import os
import logging

from multiprocessing import Queue, Process

logging.basicConfig(filename="securak.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger("securac")

input_q = Queue(maxsize=10000)
WORKER_NUMBER = 4
file_path = r"./words2.txt"


def get_word_list(file_path):
    with open(file_path, encoding="utf-8") as file:
        lines = [line.rstrip() for line in file]
        return lines


def calculate(item):
    hs = hashlib.sha256(item.encode('utf-8')).hexdigest()
    if hs == securak_expected_sha256:
        logger.info(f"password is {item}")
        print(f"password is {item}")
        exit()


def input_worker(input_q, word_list):
    worker_pid = os.getpid()
    print("  Started input worker no {}".format(worker_pid))
    for w1 in word_list:
        for w2 in word_list:
            print(f"preparing 2,5 mln data...")
            for w3 in word_list:
                for w4 in word_list:
                    guess = f"{w1}{w2}{w3}{w4}"
                    input_q.put(guess)
    for _ in range(WORKER_NUMBER):
        input_q.put(None)


def worker(input_q):
    worker_pid = os.getpid()
    print("  Started worker no {}".format(worker_pid))
    n = 0
    # while not input_q.empty(): # This solution is invalid - not 100% certain
    while True:
        # print("Input queue size: {}".format(input_q.qsize()))
        item = input_q.get()
        if item is None:
            break
        calculate(item)
        n += 1
        if n % 100000 == 0:
            logging.info(f"worker number: {worker_pid} guessing: {n}/{possible_pass_number}")
    print("    Finished worker no {}               ".format(worker_pid))


if __name__ == '__main__':
    word_list = get_word_list(file_path)
    # removing polish characters
    word_list = [unidecode.unidecode(w) for w in word_list]
    possible_pass_number = len(word_list) ** 4
    logger.info(f"{possible_pass_number} possible passwords")
    securak_expected_sha256 = "0a2551e134fca8fc124380498e7802f79576fac3291f855a6030225dd5839717"

    cpu_no = multiprocessing.cpu_count()
    print("Main program started.")
    print("Found {} cores in CPU.".format(cpu_no))

    worker_processes = []

    input_t = Process(target=input_worker, args=(input_q, word_list[:1000]))
    input_t_2 = Process(target=input_worker, args=(input_q, word_list[1000:2000]))
    input_t_3 = Process(target=input_worker, args=(input_q, word_list[2000:]))

    print(f"Starting workers number: {WORKER_NUMBER}")
    for w in range(WORKER_NUMBER):
        t = Process(target=worker, args=(input_q,))
        worker_processes.append(t)

    start_time = time()

    input_t.start()
    input_t_2.start()
    input_t_3.start()
    for t in worker_processes:
        t.start()

    for t in worker_processes:
        t.join()  # Wait for every worker to finish his job
    input_t.join()
    input_t_2.join()
    input_t_3.join()
    total_time = time() - start_time


    print("\nMain program finished.")










# can use numpy
# word_list = ["tak", "nie", "co", "to", "był", "on", "ona", "kot", "pies"]





# securak_expected_sha256 = "0a2551e134fca8fc124380498e7802f79576fac3291f855a6030225dd5839717"
# expected_sha256 = "2d6792e9b116dfc3b865736b6176e4128ec53677296d8205e197dcab2398dc9a"
# expected_sha256 = "9d81725285ce746d8af72433b01a98be6a64987991d1ff3aa4fa53496d2bf946"
# expected_sha256 = "14b7ddb92fa3537c052076c25e4c4f53daeb31271e483b77b8187d9eaddd116c"

# n = 0
# # start_with_word = 102_828_744
# start_with_word = 1
# for w1 in word_list:
#     for w2 in word_list:
#         for w3 in word_list:
#             for w4 in word_list:
#                 n += 1
#                 if n < start_with_word:
#                     continue
#                 if n % 100000 == 0:
#                     logging.info(f"guessing: {n}/{possible_pass_number} {w1}{w2}{w3}{w4}")
#                     print(f"guessing: {n}/{possible_pass_number} {w1}{w2}{w3}{w4}")
#                 # print(f"{n}/{possible_pass_number}")
#                 guess = f"{w1}{w2}{w3}{w4}"
#                 hs = hashlib.sha256(guess.encode('utf-8')).hexdigest()
#                 if hs == securak_expected_sha256:
#                     logger.info(f"password is {guess}")
#                     print(f"password is {guess}")
#                     exit()


