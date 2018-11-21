from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import numpy as np
import spacy
from spacy import displacy

Tokens = []
Sentences = []

nlp = spacy.load('de')

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

Doc_PATH = 'C:/Users/PagolPoka/Desktop/assignment4IR.pdf'
Doc_PATH_German = 'C:/Users/PagolPoka/Downloads/2_Geschäftsbeziehung_und_Bankvertrag.pdf'

text = convert_pdf_to_txt(Doc_PATH_German)
print("The text is: ", text)

print("**********************TOKENIZATION***********************************")
doc = nlp(text)




#This section deals with extraction of different features of each word [treated as token] and create a datastructure from it.
for token in doc:
    Tokens_Ftre = []

    letters = set(token.text)
    mixed = any(letter.islower() for letter in letters) and any(letter.isupper() for letter in letters)




    Tokens_Ftre.append(token.text)
    Tokens_Ftre.append(len(token.text))
    Tokens_Ftre.append(token.idx)
    if token.is_lower:
        Tokens_Ftre.append("LowerCase")
    elif token.is_upper:
        Tokens_Ftre.append("UpperCase")
    elif mixed:
        Tokens_Ftre.append("MixedCase")
    else:
        Tokens_Ftre.append(" ")
    Tokens_Ftre.append(token.pos_)

    if token.like_num:
        Tokens_Ftre.append("Number")
    elif token.is_punct:
        Tokens_Ftre.append("Punctuation")
    elif token.is_space:
        Tokens_Ftre.append("Space")
    else:
        Tokens_Ftre.append("Word")
    Tokens.append(Tokens_Ftre)


print("The token features are:    [Text, Lenght, Index, Orth, POS, Kind]")
print(" ")
print(Tokens)





#Sentence Splitter:

print("**********The Sectences are: ************")
print("  ")
for sent in doc.sents:
    print(" **Sent**: ")
    print(sent)
    Sentences.append(sent)



#Display the named entities in the text# .
displacy.serve(doc, style='ent')


