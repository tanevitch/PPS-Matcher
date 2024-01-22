import re
import spacy
from spacy.matcher import Matcher
import pandas as pd

nlp = spacy.load("es_core_news_lg")

matcher = Matcher(nlp.vocab)

dimension = [{"LIKE_NUM": True}, {"LOWER": "x"}, {"LIKE_NUM": True}]
dir_nro = [
    {"POS": "PROPN", "OP": "+"},  
    {"LOWER": "al"},       
    {"LIKE_NUM": True}    
]
dir_interseccion = [
    {"POS": "PROPN", "OP": "+"},  
    {"LOWER": "y"},       
    {"POS": "PROPN", "OP": "+"},       
    {"LIKE_NUM": True, "OP": "?"}   
]


dir_entre = [
    {"LIKE_NUM": True},   
    {"LOWER": "e/"},
    {"LIKE_NUM": True},
    {"LOWER": "y", "OP":"?"},    
    {"LIKE_NUM": True, "OP": "?"}
]

matcher.add("DIMENSION", [dimension])
matcher.add("DIR_ALTURA", [dir_nro])
matcher.add("DIR_INTERSECCION", [dir_interseccion])
matcher.add("DIR_INTERSECCION", [dir_entre])


def add_spaces(match):
    dimension = match.group(1)
    if ' x ' not in dimension and ' X ' not in dimension:
        return dimension.replace('x', ' x ').replace('X', ' X ')
    else:
        return dimension

def add_spaces2(match):
    dimension= match.group(0)
    return dimension.replace("e/", "e/ ")

def normalizar_direccion(text):   
    dimension_regex = re.compile(r'(\b\d+(?:,\d+)?\s?[xX]\s?\d+(?:,\d+)?\b)')
    text= dimension_regex.sub(add_spaces, text)
    dimension_regex = re.compile(r'e/\d+')
    return dimension_regex.sub(add_spaces2, text)
        
input = pd.read_csv('input.csv', sep = '|')
for index, row in input.iterrows():
    texto= normalizar_direccion(row["descripcion"])
    doc = nlp(texto)
    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_span = doc[start:end]
        print(matched_span.text)



