from string import ascii_uppercase
from sys import argv

def caesar_encrypt_letter(letter, key):
    letter_num = ord(letter) - ord('A')
    letter_num += key
    letter_num %= 26
    return chr(letter_num + ord('A'))

def caesar_encrypt_word(word, key):
    return ''.join(caesar_encrypt_letter(letter, key) if letter in ascii_uppercase else letter for letter in word )

print(caesar_encrypt_word(argv[1], int(argv[2])))
