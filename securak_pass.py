import hashlib
import multiprocessing
from time import time

import unidecode
import os
import logging

from multiprocessing import Queue, Process
from colorama import Fore as Fo
from numpy.ma.core import append

logging.basicConfig(filename="securak.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger("securac")

input_q = Queue(maxsize=1000)
processed_data_sum = [0]
lock = multiprocessing.Lock()
WORKER_NUMBER = 7
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
    counter = 0
    c3 = 0
    item = []
    start_time = time()
    for w1 in word_list:
        for w2 in word_list:
            print(f"preparing 2,5 mln data...")
            for w3 in word_list:
                c3 += 1
                if c3 % 50 == 0:
                    logger.info(f"{Fo.YELLOW}prepared 5 mln data...{Fo.RESET}")
                    lock.acquire()
                    # logger.info(f"{Fo.RED} total processed {processed_data_sum:,d} guesses{Fo.RESET}")
                    lock.release()
                for w4 in word_list:
                    guess = f"{w1}{w2}{w3}{w4}"
                    item.append(guess)
                    counter += 1
                    if counter % 100_000 == 0:
                        # logger.info(f"{Fo.YELLOW}worker: {worker_pid} time: {time() - start_time} prepared: {counter} guesses")
                        input_q.put(item)
                        logger.debug(f"{len(item)=}")
                        item.clear()
                        start_time = time()
    for _ in range(WORKER_NUMBER):
        input_q.put(None)


def worker(input_q, processed_data_sum):
    worker_pid = os.getpid()
    print("  Started worker no {}".format(worker_pid))
    n = 0
    # while not input_q.empty(): # This solution is invalid - not 100% certain
    timer = time()
    while True:
        n += 1
        # print("Input queue size: {}".format(input_q.qsize()))
        item = input_q.get()
        if item is None:
            break
        for guess in item:
            calculate(guess)
        logger.debug(f"{Fo.LIGHTBLUE_EX}{len(item)=}")
        lock.acquire()
        processed_data_sum[0] += len(item)
        logger.info(f"{Fo.CYAN} total processed {processed_data_sum[0]:,} guesses{Fo.RESET}")
        lock.release()

        if (time() - timer ) > 5:
            timer = time()
            logging.info(f"{Fo.GREEN}worker: {worker_pid} guessing: {int(n / 5 * len(item)):,d} per second, input_q: {input_q.qsize()}{Fo.RESET}")
            n = 0
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

    input_t = Process(target=input_worker, args=(input_q, word_list))
    # input_t_2 = Process(target=input_worker, args=(input_q, word_list[1000:2000]))
    # input_t_3 = Process(target=input_worker, args=(input_q, word_list[2000:]))

    print(f"Starting workers number: {WORKER_NUMBER}")
    for w in range(WORKER_NUMBER):
        t = Process(target=worker, args=(input_q, processed_data_sum))
        worker_processes.append(t)

    start_time = time()

    input_t.start()
    # input_t_2.start()
    # input_t_3.start()
    for t in worker_processes:
        t.start()

    for t in worker_processes:
        t.join()  # Wait for every worker to finish his job
    input_t.join()
    # input_t_2.join()
    # input_t_3.join()
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


