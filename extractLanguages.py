#! /usr/bin/env python
from urllib import urlopen
from bs4 import BeautifulSoup
from textblob import TextBlob
import langid
import re
import wikipedia


#Open English/Spanish/French/Dutch/German/Thai/Assamese/German Files For Writing
lang_file = open("x_test.txt", "r")
en_file = open("english.txt", "a")
sp_file = open("spanish.txt", "a")
fr_file = open("french.txt", "a")
de_file = open("german.txt", "a")
pt_file = open("portuguese.txt", "a")
th_file = open("thai.txt", "a")
nl_file = open("dutch.txt", "a")
as_file = open("assamese.txt", "a")


#For Loop To Get Text Paragraphs From File
for line in lang_file:
    try:
        lang_res = langid.classify(line)[0]
    except:
        lang_res = "Zo"
        print("Skipped...")

    if lang_res == "en":
        en_file.write(line)
        en_file.write("\n")
    elif lang_res == "es":
        sp_file.write(line)
        sp_file.write("\n")
    elif lang_res == "fr":
        fr_file.write(line)
        fr_file.write("\n")
    elif lang_res == "de":
        de_file.write(line)
        de_file.write("\n")
    elif lang_res == "pt":
        pt_file.write(line)
        pt_file.write("\n")
    elif lang_res == "th":
        th_file.write(line)
        th_file.write("\n")
    elif lang_res == "nl":
        nl_file.write(line)
        nl_file.write("\n")
    elif lang_res == "as":
        as_file.write(line)
        nl_file.write("\n")

#link_file.close()
lang_file.close()
en_file.close()
sp_file.close()
fr_file.close()
de_file.close()
pt_file.close()
th_file.close()
nl_file.close()
as_file.close()
