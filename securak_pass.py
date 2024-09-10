import hashlib
import unidecode
import os
import logging

logging.basicConfig(filename="securak.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger("securac")


def get_word_list(file_path):
    with open(file_path, encoding="utf-8") as file:
        lines = [line.rstrip() for line in file]
        return lines

file_path = r"./words2.txt"

# can use numpy
word_list = ["tak", "nie", "co", "to", "był", "on", "ona", "kot", "pies"]
word_list = get_word_list(file_path)
print(word_list)
word_list = [unidecode.unidecode(w) for w in word_list]
print(word_list)

possible_pass_number = len(word_list) ** 4

logger.info(f"{possible_pass_number} possible passwords")


securak_expected_sha256 = "0a2551e134fca8fc124380498e7802f79576fac3291f855a6030225dd5839717"
expected_sha256 = "2d6792e9b116dfc3b865736b6176e4128ec53677296d8205e197dcab2398dc9a"
expected_sha256 = "9d81725285ce746d8af72433b01a98be6a64987991d1ff3aa4fa53496d2bf946"
expected_sha256 = "14b7ddb92fa3537c052076c25e4c4f53daeb31271e483b77b8187d9eaddd116c"

n = 0
# start_with_word = 102_828_744
start_with_word = 1
for w1 in word_list:
    for w2 in word_list:
        for w3 in word_list:
            for w4 in word_list:
                n += 1
                if n < start_with_word:
                    continue
                if n % 100000 == 0:
                    logging.info(f"guessing: {n}/{possible_pass_number} {w1}{w2}{w3}{w4}")
                    print(f"guessing: {n}/{possible_pass_number} {w1}{w2}{w3}{w4}")
                # print(f"{n}/{possible_pass_number}")
                guess = f"{w1}{w2}{w3}{w4}"
                hs = hashlib.sha256(guess.encode('utf-8')).hexdigest()
                if hs == securak_expected_sha256:
                    logger.info(f"password is {guess}")
                    print(f"password is {guess}")
                    exit()


