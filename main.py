import json
import re
import spacy
from spacy.matcher import Matcher, DependencyMatcher
import pandas as pd
from spacy import displacy
import copy

nlp = spacy.load('es_core_news_lg')

#-----------------------------------------------------------
# DEPENDENCY MATCHER
#-----------------------------------------------------------
dep_matcher= DependencyMatcher(nlp.vocab)
fot = [
        [
            {'RIGHT_ID': 'fot', 'RIGHT_ATTRS': {'TEXT': {'IN':['FOT', 'fot', 'F.O.T', 'f.o.t', 'Fot', 'F.o.t']}}}, 
            {'LEFT_ID': 'fot', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
        ]
]
frentes = [
    [
        {'RIGHT_ID': 'frentes', 'RIGHT_ATTRS': {'LOWER': {"IN": ['frentes', 'frente']}}}, 
        {'LEFT_ID': 'frentes', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
    ]
]
dep_matcher.add('FRENTES', patterns=frentes)
dep_matcher.add('FOT', patterns=fot)

#-----------------------------------------------------------
# MATCHER
#-----------------------------------------------------------
matcher = Matcher(nlp.vocab)
esquina = [
    {'LOWER': 'esquina'}, 
]
pileta = [
    {'LOWER': {'IN': ['piscina', 'pileta']}}, 
]
dimension_x = [{'LIKE_NUM': True}, {'LOWER': 'x'}, {'LIKE_NUM': True}]

dimension_larga = [
    {'LIKE_NUM': True}, 
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
    {'LOWER': {"IN": ["x", "por", "y"]}},
    {'LIKE_NUM': True},
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
]


dir_altura = [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'},  
    {'POS': 'PROPN', 'OP': '+'},  
    {'LOWER': 'al', "OP": "?"}, 
    {'LIKE_NUM': True}    
]
dir_nro = [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': 'PROPN', 'OP': '+'},  
    {'LOWER': 'n'}, 
    {'TEXT': '°'}, 
    {'LIKE_NUM': True}    
]
dir_lote= [
    {'LOWER': 'lote'},
    {'LIKE_NUM': True},
    {'POS': 'PROPN', 'OP': '*'}, 
]
dir_interseccion = [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},  
    {'LOWER': {"IN": ["y", "esquina", "esq"]}},  
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'},      
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},     
]
dir_entre = [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},  
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},   
    {'LOWER': {'IN': ['e/', 'entre', 'e']}},
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},  
    {'LOWER': 'y'},    
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},  
]
irregular= [
    {'LOWER': 'irregular'}
]

fot=[
    {'TEXT': {'IN':['FOT', 'fot', 'F.O.T', 'f.o.t', 'Fot', 'F.o.t']}},
    {'LOWER':  {'IN':['res', 'residencial']}, "OP": "?"},
    {"IS_PUNCT": True, "OP":"?"},
    {"LIKE_NUM": True},
    {"IS_PUNCT": True, "OP":"?"},
    {'TEXT': {'IN':['FOT', 'fot', 'F.O.T', 'f.o.t', 'Fot', 'F.o.t']}, "OP": "?"},
    {'LOWER': {'IN':['comercial', 'com', 'industrial']}, "OP": "?"},
    {"IS_PUNCT": True, "OP":"?"},
    {"LIKE_NUM": True, "OP": "?"}
]

barrio= [
    {"LOWER": "barrio"},
    {'POS':"PROPN", "OP": "+"}
]

matcher.add('DIMENSION', [dimension_x, dimension_larga])
matcher.add('DIR_NRO', [dir_nro])
matcher.add('DIR_ALTURA', [dir_altura])
matcher.add('DIR_INTERSECCION', [dir_interseccion])
matcher.add('DIR_ENTRE', [dir_entre])
matcher.add('DIR_LOTE', [dir_lote])
matcher.add('PILETA', [pileta])
matcher.add('ESQUINA', [esquina])
matcher.add('IRREGULAR', [irregular])
matcher.add('FOT', [fot])
matcher.add('BARRIO', [barrio])


def add_spaces(match):
    dimension = match.group(1)
    if ' x ' not in dimension and ' X ' not in dimension:
        return dimension.replace('x', ' x ').replace('X', ' X ')
    else:
        return dimension

def add_spaces2(match):
    dimension= match.group(0)
    return dimension.replace('e/', 'e/ ')

def normalizar_dimensiones(text):   
    dimension_regex = re.compile(r'(\b\d+(?:,\d+)?\s?[xX]\s?\d+(?:,\d+)?\b)') 
    return dimension_regex.sub(add_spaces, text)
    
def normalizar_direccion(text):
    dimension_regex = re.compile(r'e/\d+')
    return dimension_regex.sub(add_spaces2, text)

result = {
    'DIMENSION': [],
    'DIR_ALTURA': [],
    'DIR_NRO': [],
    'DIR_INTERSECCION': [],
    'DIR_ENTRE': [],
    'DIR_LOTE': [],
    'FOT': [],
    'IRREGULAR': [],
    'PILETA': [],
    'BARRIO': [],
    'ESQUINA': [],
    'FRENTES': []
}

def matches(doc):
    prev_result = {
        'DIMENSION': [],
        'DIR_ALTURA': [],
        'DIR_NRO': [],
        'DIR_INTERSECCION': [],
        'DIR_ENTRE': [],
        'DIR_LOTE': [],
        'FOT': [],
        'IRREGULAR': [],
        'PILETA': [],
        'BARRIO': [],
        'ESQUINA': [],
        'FRENTES': []
    }
    matches_locales= copy.deepcopy(prev_result)

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
        'DIMENSION': [],
        'DIR_ALTURA': [],
        'DIR_NRO': [],
        'DIR_INTERSECCION': [],
        'DIR_ENTRE': [],
        'DIR_LOTE': [],
        'FOT': [],
        'IRREGULAR': [],
        'PILETA': [],
        'BARRIO': [],
        'ESQUINA': [],
        'FRENTES': []
    }
    matches_dep = dep_matcher(doc)
    for match_id, token_ids in matches_dep:
        palabra= []
        for token_id in sorted(token_ids):
            token = doc[token_id]
            palabra.append(token.text)
        result[nlp.vocab.strings[match_id]].append(' '.join(palabra))
        prev_result[nlp.vocab.strings[match_id]].append(' '.join(palabra))
    return prev_result

def merge(dic1, dic2):
    for clave, valores in dic1.items():
        if clave in dic2:
            dic2[clave].extend(valores)
        else:
            dic2[clave] = valores
    return dic2

def clear_inter_entre(result):
    for interseccion in result.get('DIR_INTERSECCION', []):
        for entre in result.get('DIR_ENTRE', []):
            if interseccion in entre:
                result['DIR_INTERSECCION'].remove(interseccion)
    return result

metricas = metricas = {
    "direccion": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "fot": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "irregular": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "medidas": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "esquina": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "barrio": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "frentes": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    },
    "pileta": {
        "tp": 0,
        "fp": 0,
        "fn": 0,
        "tn": 0,
        "p": 0.0,
        "r": 0.0,
        "f1": 0.0,
        "error": [
            
        ]
    }
}
input = pd.read_csv('ground_truth_75.csv', sep = '|')
input = input.fillna("")

for index, row in input.iterrows():
    texto= normalizar_direccion(row['descripcion'])
    texto= normalizar_dimensiones(texto)
    doc = nlp(texto)    
    predichos= merge(matches_dep(doc), matches(doc))
    predichos = clear_inter_entre(predichos)

    a=predichos["DIR_ENTRE"]+predichos["DIR_INTERSECCION"]+predichos["DIR_ALTURA"]+predichos["DIR_NRO"]+predichos["DIR_LOTE"]
    prev_result = {
        'DIRECCION': max(a, key=len) if a else "",
        'FOT': max(predichos["FOT"], key=len) if predichos["FOT"] else "",
        'IRREGULAR': max(predichos["IRREGULAR"], key=len) if predichos["IRREGULAR"] else "",
        'DIMENSION': max(predichos["DIMENSION"], key=len) if predichos["DIMENSION"] else "",
        'ESQUINA': max(predichos["ESQUINA"], key=len) if predichos["ESQUINA"] else "",
        'BARRIO': max(predichos["BARRIO"], key=len) if predichos["BARRIO"] else "",
        'FRENTES': max(predichos["FRENTES"], key=len) if predichos["FRENTES"] else "",
        'PILETA': max(predichos["PILETA"], key=len) if predichos["PILETA"] else "",
    }

    for respuesta, esperada, key_metrica in zip(prev_result, list(row[1:]), metricas):
        rta= prev_result[respuesta]
        if rta == "" and esperada == "":
            metricas[key_metrica]["tn"]+=1
        else:
            if key_metrica == "medidas":
                esperada= normalizar_dimensiones(esperada)
            if key_metrica == "fot":
                
                esperada= ' '.join([token.text for token in nlp(esperada) if not token.is_punct])
                rta= ' '.join([token.text for token in nlp(rta) if not token.is_punct])

            if key_metrica in ["direccion","fot", "medidas", "barrio", "frentes"]:
                correcta= nlp(rta).similarity(nlp(esperada)) > 0.9
            elif key_metrica in [ "irregular", "esquina", "pileta"]:
                correcta= rta != "" and esperada == True

            if correcta:
                metricas[key_metrica]["tp"]+=1
            else:
                metricas[key_metrica]["error"].append({
                    "contexto": row["descripcion"],
                    "respuesta_predicha": rta,
                    "respuesta_esperada": esperada
                })
                if rta == "" and esperada != "":
                    metricas[key_metrica]["fn"]+=1
                elif (esperada == "" and rta != ""):
                    metricas[key_metrica]["fp"]+=1
                elif esperada!=rta:
                    metricas[key_metrica]["tn"]+=1

for metrica, valores in metricas.items():
    tp = valores["tp"]
    fp = valores["fp"]
    fn = valores["fn"]

    if (tp + fp) > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0.0

    if (tp + fn) > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0.0

    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    metricas[metrica]["p"] = precision
    metricas[metrica]["r"] = recall
    metricas[metrica]["f1"] = f1_score

with open('resultados.json', 'w', encoding="utf8") as fp:
    json.dump(metricas, fp, ensure_ascii=False)




