import ctypes
import hashlib
import logging
import multiprocessing
import os
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value
from time import sleep
from time import time

import unidecode
from colorama import Fore as Fo

logging.basicConfig(
    # filename="securak.log",
    # filemode='w',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger("securac")

input_q = Queue(maxsize=20)
processed_sum = Value(ctypes.c_longlong, 0)
WORKER_NUMBER = 7
ITEM_LENGTH = 20_000
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


def logging_worker(input_q: Queue, processed_sum: Value) -> None:
    timer_start = time()

    while True:
        logger.info(f"{Fo.LIGHTBLUE_EX}Input Queue size: {input_q.qsize()}{Fo.RESET}")
        with processed_sum.get_lock():
            logger.info(f"{Fo.LIGHTBLUE_EX}Processed sum: {processed_sum.value:,} in {time() - timer_start:.2f} seconds{Fo.RESET} ")
            logger.info(f"{Fo.LIGHTBLUE_EX}Processing speed: {int(processed_sum.value / (time() - timer_start)):,} per second{Fo.RESET}")
        sleep(3)


def input_worker(input_q: Queue, word_list: list[str], processed_sum: Value) -> None:
    worker_pid = os.getpid()
    world_list_length = len(word_list)
    print(f"  Started input worker no {worker_pid}")
    print(f"  World list length in input worker is: {world_list_length}")

    counter = 0
    item = []
    start_time = time()

    for w1 in word_list:
        for w2 in word_list:

            for w3 in word_list:
                for w4 in word_list:
                    guess = f"{w1}{w2}{w3}{w4}"
                    item.append(guess)
                    counter += 1
                    if counter % ITEM_LENGTH == 0:
                        input_q.put(item)
                        item = []
                    if counter % (200 * ITEM_LENGTH) == 0:
                        logger.info(f"{Fo.LIGHTYELLOW_EX}Added 200 items to Input Queue with length: {ITEM_LENGTH:,} each in {time() - start_time:.3f} seconds{Fo.RESET}")
                        start_time = time()

    for _ in range(WORKER_NUMBER):
        input_q.put(None)


def worker(input_q: Queue, processed_data_sum: Value):
    worker_pid = os.getpid()
    print("  Started worker no {}".format(worker_pid))
    n = 0
    timer = time()
    while True:
        items = input_q.get()
        if items is None:
            break
        for guess in items:
            calculate(guess)

        with processed_data_sum.get_lock():
            processed_data_sum.value += len(items)
            local_sum = processed_data_sum.value
        n += len(items)

        if (time() - timer) > 2:
            timer = time()
            logger.info(f"{Fo.CYAN}worker: {worker_pid} guessing: {int(n/2):,} per second, input_q: {input_q.qsize()}{Fo.RESET}")
            n = 0
    print("    Finished worker no {}               ".format(worker_pid))


if __name__ == '__main__':

    word_list = get_word_list(file_path)
    # removing polish characters
    word_list = [unidecode.unidecode(w) for w in word_list]
    possible_pass_number = len(word_list) ** 4
    logger.info(f"{possible_pass_number:,} possible passwords")
    securak_expected_sha256 = "0a2551e134fca8fc124380498e7802f79576fac3291f855a6030225dd5839717"

    cpu_no = multiprocessing.cpu_count()
    print("Main program started.")
    print("Found {} cores in CPU.".format(cpu_no))

    worker_processes = []

    logging_t = Process(target=logging_worker, args=(input_q, processed_sum))

    # input_t = Process(target=input_worker, args=(input_q, word_list, processed_sum))

    input_t_1 = Process(target=input_worker, args=(input_q, word_list[:1000], processed_sum))
    input_t_2 = Process(target=input_worker, args=(input_q, word_list[1000:2000], processed_sum))
    input_t_3 = Process(target=input_worker, args=(input_q, word_list[2000:], processed_sum))

    print(f"Starting workers number: {WORKER_NUMBER}")
    for w in range(WORKER_NUMBER):
        t = Process(target=worker, args=(input_q, processed_sum))
        worker_processes.append(t)

    start_time = time()

    logging_t.start()

    # input_t.start()
    input_t_1.start()
    input_t_2.start()
    input_t_3.start()
    for t in worker_processes:
        t.start()

    for t in worker_processes:
        t.join()  # Wait for every worker to finish his job
    # input_t.join()
    input_t_1.join()
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


