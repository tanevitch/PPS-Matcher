import json
import re
import spacy
from spacy.matcher import Matcher, DependencyMatcher
import pandas as pd
from spacy import displacy

nlp = spacy.load("es_core_news_lg")

# doc=nlp("Se trata de un galpón de 3 frentes, ubicado sobre Av. 7 N° 1540/1550 a escasos metros del triangulo de Bernal, en zonificación R3  (permitiendo industrias de actividad inocua) de excelente acceso y de salida rápida a autopista Buenos Aires la Plata,diferentes puntos del conurbano como así también a Capital Federal.Galpón N° 1540:Implantado sobre dos lotes de terreno.En su primera mitad de 14,80 mts. x  mts. x 25,70 mts. Sup. Cubierta: 380,3.")
# for token in doc:
#     print(token.text, token.pos_, token.dep_)
# displacy.serve(doc, style="dep")

#-----------------------------------------------------------
# DEPENDENCY MATCHER
#-----------------------------------------------------------
dep_matcher= DependencyMatcher(nlp.vocab)
fot = [
    [
        {'RIGHT_ID': 'fot', 'RIGHT_ATTRS': {'TEXT': {"IN":["FOT", "fot", "F.O.T", "f.o.t", "Fot", "F.o.t"]}}}, 
        {'LEFT_ID': 'fot', 'REL_OP': '>', 'RIGHT_ID': 'num', "RIGHT_ATTRS": {'DEP': "nummod"}} 
    ]
]
frentes = [
    [
        {'RIGHT_ID': 'frentes', 'RIGHT_ATTRS': {'LOWER': "frentes"}}, 
        {'LEFT_ID': 'frentes', 'REL_OP': '>', 'RIGHT_ID': 'num', "RIGHT_ATTRS": {'DEP': "nummod"}} 
    ]
]
dep_matcher.add('FOT', patterns=fot)
dep_matcher.add('FRENTES', patterns=frentes)

#-----------------------------------------------------------
# MATCHER
#-----------------------------------------------------------
matcher = Matcher(nlp.vocab)
esquina = [
    {"LOWER": "esquina"}, 
]
pileta = [
    {"LOWER": {"IN": ["piscina", "pileta"]}}, 
]
dimension = [{"LIKE_NUM": True}, {"LOWER": "x"}, {"LIKE_NUM": True}]
dir_altura = [
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"},  
    {"POS": "PROPN", "OP": "+"},  
    {"LOWER": "al"}, 
    {"LIKE_NUM": True}    
]
dir_nro = [
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"}, 
    {"POS": "PROPN", "OP": "+"},  
    {"LOWER": "n"}, 
    {"TEXT": "°"}, 
    {"LIKE_NUM": True}    
]
dir_lote= [
    {"LOWER": "lote"},
    {"LIKE_NUM": True},
    {"POS": "PROPN", "OP": "*"}, 
]
dir_interseccion = [
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"}, 
    {"POS": {"IN": ["PROPN", "NUM"]}, "OP": "+"},  
    {"LOWER": "y"},  
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"},      
    {"POS": {"IN": ["PROPN", "NUM"]}, "OP": "+"},     
]
dir_entre = [
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},  
    {"TEXT": ".", "OP":"?"}, 
    {"POS": {"IN": ["PROPN", "NUM"]}, "OP": "+"},   
    {"LOWER": "e/"},
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"}, 
    {"POS": {"IN": ["PROPN", "NUM"]}, "OP": "+"},  
    {"LOWER": "y"},    
    {"LOWER": {"IN": ["calle", "avenida", "av", "diagonal", "diag"]}, "OP":"?"},   
    {"TEXT": ".", "OP":"?"}, 
    {"POS": {"IN": ["PROPN", "NUM"]}, "OP": "+"},  
]
matcher.add("DIMENSION", [dimension])
matcher.add("DIR_NRO", [dir_nro])
matcher.add("DIR_ALTURA", [dir_altura])
matcher.add("DIR_INTERSECCION", [dir_interseccion])
matcher.add("DIR_ENTRE", [dir_entre])
matcher.add("DIR_LOTE", [dir_lote])
matcher.add("PILETA", [pileta])
matcher.add("ESQUINA", [esquina])


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
    return dimension_regex.sub(add_spaces, text)
    
def normalizar_dimensiones(text):
    dimension_regex = re.compile(r'e/\d+')
    return dimension_regex.sub(add_spaces2, text)

result = {
    "DIMENSION": [],
    "DIR_ALTURA": [],
    "DIR_NRO": [],
    "DIR_INTERSECCION": [],
    "DIR_ENTRE": [],
    "DIR_LOTE": [],
    "FOT": [],
    "PILETA": [],
    "ESQUINA": [],
    "FRENTES": []
}

def matches(doc):
    prev_result = {
        "DIMENSION": [],
        "DIR_ALTURA": [],
        "DIR_NRO": [],
        "DIR_INTERSECCION": [],
        "DIR_ENTRE": [],
        "DIR_LOTE": [],
        "FOT": [],
        "PILETA": [],
        "ESQUINA": []
    }
    matches_locales= prev_result
    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_span = doc[start:end]
        prev_result[nlp.vocab.strings[match_id]].append(matched_span.text)
    for lista in prev_result:
        if prev_result[lista]:
            elegido= max(prev_result[lista], key=len)
            result[lista].append(elegido)
            matches_locales[lista].append(elegido)
    return matches_locales

def matches_dep(doc):
    prev_result = {
        "DIMENSION": [],
        "DIR_ALTURA": [],
        "DIR_NRO": [],
        "DIR_INTERSECCION": [],
        "DIR_ENTRE": [],
        "DIR_LOTE": [],
        "FOT": [],
        "PILETA": [],
        "ESQUINA": []
    }
    matches_dep = dep_matcher(doc)
    for match_id, token_ids in matches_dep:
        for token_id in token_ids:
            token = doc[token_id]
        result[nlp.vocab.strings[match_id]].append(token.text)
        prev_result[nlp.vocab.strings[match_id]].append(token.text)
    return prev_result

def merge(dic1, dic2):
    for clave, valores in dic1.items():
        if clave in dic2:
            dic2[clave].extend(valores)
        else:
            dic2[clave] = valores
    return dic1

input = pd.read_csv('input.csv', sep = '|')
for index, row in input.iterrows():
    texto= normalizar_direccion(row["descripcion"])
    texto= normalizar_dimensiones(texto)
    doc = nlp(texto)    
    predichos= merge(matches_dep(doc), matches(doc))
    
with open("resultado.json", "w", encoding="utf8") as outfile:
    json.dump(result, outfile, ensure_ascii=False)



