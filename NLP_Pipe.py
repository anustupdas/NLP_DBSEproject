from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import numpy as np
import re
import spotlight
from datetime import date
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from dateutil.parser import parse
import PyPDF2
import os
import glob
import time





nlp = spacy.load('de')

Numerals = []
RuleList = []
SubRule =['gesetz1','gesetz2','gesetz3','gesetz4','gesetz5']



def extractText(file):
    pdfReader = PyPDF2.PdfFileReader(file)
    num_pages = pdfReader.getNumPages()
    count = 0
    text = ''
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        # print(pageObj.extractText())
        count += 1
        text += pageObj.extractText()
    return text

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


#This function checks weather a number is Roman Numeral ot not
def checkIfRomanNumeral(numeral):
    """Controls that the userinput only contains valid roman numerals"""
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I"]
    for letters in numeral:
        if letters not in validRomanNumerals:
            #print("Sorry that is not a valid roman numeral")
            return False
    return True


files = []
path = 'C:/Users/PagolPoka/Desktop/Docs'
Doc_PATH_German = 'C:/Users/PagolPoka/Downloads/2_Geschäftsbeziehung_und_Bankvertrag.pdf'

for filename in os.listdir(path):
    files.append(filename)

ticks = time.time()

print ("Number of ticks since 12:00am, January 1, 1970:", ticks)


counter = 0
for filename in glob.glob(os.path.join(path, '*.pdf')):

    output = 'Rulefile_' + files[counter] + '.txt'
    print (output)
    text = extractText(filename)

    print("The Content of the File is: ", text)

    print("**********************TOKENIZATION***********************************")
    doc = nlp(text)

    for token in doc:

        if checkIfRomanNumeral(token.text):
            Numerals.append(token.text)

    # Convert list to set and then back to list
    Numerals = list(set(Numerals))

    print(Numerals)

    matcher = Matcher(nlp.vocab)

    # **********************Rule: toc-chapter**********************
    IS_ROMAN = nlp.vocab.add_flag(lambda text: text in Numerals)
    IS_DASHPUNCT = nlp.vocab.add_flag(lambda text: text in ['-', '_'])
    IS_INHALT = nlp.vocab.add_flag(lambda text: text in ['Inhalt', 'Inhaltsübersicht'])
    IS_SINGLELETTER = nlp.vocab.add_flag(
        lambda text: text in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                              'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                              '0'])

    toc_chapterTop1 = [{'ORTH': "Kapitel"}, {IS_ROMAN: True}, {IS_DASHPUNCT: True, 'OP': '?'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '+'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '?'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '?'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '?'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '?'}]
    toc_chapterTop2 = [{'ORTH': "Kap"}, {'IS_PUNCT': True, 'ORTH': '.'}, {IS_ROMAN: True},
                       {IS_DASHPUNCT: True, 'OP': '?'},
                       {'LIKE_NUM': False, 'IS_PUNCT': False, IS_SINGLELETTER: False, IS_INHALT: False, 'OP': '+'}]

    matcher.add('toc-chapter', None, toc_chapterTop1)
    matcher.add('toc-chapter', None, toc_chapterTop2)

    # **************************************************************

    # **********************Rule: Reference**********************
    IS_OMITSIGN = nlp.vocab.add_flag(lambda text: text in ['(', ')', '\'', '/', ';', 'Rn', 'nach', 'gemäß'])

    ref_Extractor = [{'ORTH': "§", 'OP': '+'}, {IS_OMITSIGN: True, 'IS_TITLE': False, 'POS': 'VAFIN', 'OP': '!'},
                     {IS_OMITSIGN: False, 'IS_UPPER': False, 'OP': '?'},
                     {IS_OMITSIGN: False, 'IS_UPPER': False, 'OP': '?'},
                     {IS_OMITSIGN: False, 'IS_UPPER': False, 'OP': '?'},
                     {IS_OMITSIGN: False, 'IS_UPPER': False, 'OP': '?'},
                     {IS_OMITSIGN: False, 'IS_UPPER': False, 'OP': '?'}, {'IS_UPPER': True}]
    ref_Extractor2 = [{'ORTH': "Art"}, {'ORTH': "."}, {IS_OMITSIGN: True, 'POS': 'VAFIN', 'OP': '!'},
                      {'IS_UPPER': True, 'OP': '+'}]
    ref_Extractor3 = [{'ORTH': "Art"}, {'ORTH': "."}, {IS_OMITSIGN: True, 'POS': 'VAFIN', 'OP': '!'},
                      {'IS_UPPER': False, 'IS_LOWER': False, 'OP': '+'}]
    ref_Extractor4 = [{'LIKE_NUM': True, 'SHAPE': 'dddd'}, {'ORTH': "/"}, {'IS_UPPER': True}]
    ref_Extractor5 = [{'LIKE_NUM': True, 'SHAPE': 'dddd'}, {'POS': 'NUM'}, {'ORTH': "/"}, {'IS_UPPER': True}]
    ref_Extractor6 = [{'POS': 'NUM'}, {'ORTH': "/"}, {'POS': 'NUM'}, {'ORTH': "/"}, {'IS_UPPER': True}]

    matcher.add('gesetz1', None, ref_Extractor)
    matcher.add('gesetz2', None, ref_Extractor2)
    matcher.add('gesetz2', None, ref_Extractor3)
    matcher.add('gesetz3', None, ref_Extractor4)
    matcher.add('gesetz4', None, ref_Extractor5)
    matcher.add(' ', None, ref_Extractor5)
    # **************************************************************

    matches = matcher(doc)

    for match_id, start, end in matches:
        LocalRule = []
        string_id = nlp.vocab.strings[match_id]  # get string representation
        span = doc[start:end]  # the matched span

        try:
            annotations = spotlight.annotate('http://api.dbpedia-spotlight.org/de/annotate', span.text, confidence=0.9,
                                             support=10)
            # print("Dbpedia: ", annotations)
        except:
            annotations = ""
            # print ("Exception")

        LocalRule.append(span.text)
        LocalRule.append(str(start) + "-" + str(end))

        if string_id in SubRule:
            LocalRule.append("Reference")
            LocalRule.append(string_id)
        else:
            LocalRule.append(string_id)
            LocalRule.append(" ")

        LocalRule.append(annotations)

        RuleList.append(LocalRule)
        print("")
        print(string_id, start, end, span.text)

    print("The final Rules are: ")
    print(RuleList)

    for i in RuleList:
        # Logging
        with open(output, 'a') as f:
            print("", file=f)
            print("Rule", i, file=f)

    counter += 1

ticks1 = time.time()

print ("Number of ticks since 12:00am, January 1, 1970:", ticks1)


hours, rem = divmod(ticks1 - ticks, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

