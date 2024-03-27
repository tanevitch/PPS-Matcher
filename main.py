import json
import re
import spacy
from spacy.matcher import Matcher, DependencyMatcher
import pandas as pd
from spacy import displacy
import copy

NLP = spacy.load('es_core_news_lg')

#-----------------------------------------------------------
# DEPENDENCY MATCHER
#-----------------------------------------------------------
dep_matcher= DependencyMatcher(NLP.vocab)
fot = [
        [
            {'RIGHT_ID': 'fot', 'RIGHT_ATTRS': {'LOWER': {'IN':['fot', 'f.o.t']}}},
            {'LEFT_ID': 'fot', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
        ]
]
frentes = [
    [
        {'RIGHT_ID': 'frentes', 'RIGHT_ATTRS': {'LOWER': {'IN':['frente', 'frentes']}}}, 
        {'LEFT_ID': 'frentes', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': {"IN": ['nummod', 'amod']}}} 
    ],
    [
        {'RIGHT_ID': 'frentes', 'RIGHT_ATTRS': {'LOWER': 'salida'}},
        {'LEFT_ID': 'frentes', 'REL_OP': '>', 'RIGHT_ID': 'calles', 'RIGHT_ATTRS': {'DEP': 'obl'}}, 
        {'LEFT_ID': 'calles', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
    ]
]
dep_matcher.add('frentes', patterns=frentes)
dep_matcher.add('fot', patterns=fot)

#-----------------------------------------------------------
# MATCHER
#-----------------------------------------------------------
matcher = Matcher(NLP.vocab)

dir_interseccion = [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': {'IN': ['PROPN', 'NUM']}, 'OP': '+'},  
    {'LOWER': {"IN": ["y", "esquina", "esq.", "e"]}},  
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

matcher.add('medidas', [[
    {'LIKE_NUM': True}, 
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
    {'LOWER': 'x'}, 
    {'LIKE_NUM': True},
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
    {'LOWER': 'x', 'OP': '?'}, 
    {'LIKE_NUM': True, 'OP': '?'},
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
    {'LOWER': 'x', 'OP': '?'}, 
    {'LIKE_NUM': True, 'OP': '?'},
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
],
[   
    {'LIKE_NUM': True},
    {'LOWER': {'IN': ['m', 'mts', 'metros']}, "OP": "?"},
    {"LOWER": "de", "OP": "?"},
    {'LOWER': 'frente'},
    {'LOWER': {'IN': ['por', 'x', 'y']}, "OP": "?"},
    {'LIKE_NUM': True},
    {'LOWER': {'IN': ['m', 'mts', 'metros']}, "OP": "?"},
    {"LOWER": "de", "OP": "?"},
    {'LOWER': 'fondo'}
]])
matcher.add('DIR_NRO', [ [
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'},  
    {'POS': 'PROPN', 'OP': '+'},  
    {'LOWER': 'al', "OP": "?"}, 
    {'LIKE_NUM': True}    
],
[
    {'LOWER': {'IN': ['calle', 'avenida', 'av', 'diagonal', 'diag']}, 'OP':'?'},   
    {'TEXT': '.', 'OP':'?'}, 
    {'POS': 'PROPN', 'OP': '+'},  
    {'LOWER': 'n'}, 
    {'TEXT': '°'}, 
    {'LIKE_NUM': True}    
]])
matcher.add('DIR_INTERSECCION', [dir_interseccion])
matcher.add('DIR_ENTRE', [dir_entre])
matcher.add('DIR_LOTE', [[
    {'LOWER': 'lote'},
    {'POS': {'IN': ['NUM', 'PROPN']}}
]])
matcher.add('pileta', [[
    {'LOWER': {'IN': ['piscina', 'pileta']}}, 
]])
matcher.add('esquina', [[
    {'LOWER': 'esquina'}, 
]])
matcher.add('irregular', [[
    {'LEMMA': 'irregular'}
],
[
   {'LOWER': {'IN': ['lote', 'forma']}},
   {'POS': 'ADJ'}
]])
matcher.add('fot', [[
    {'LOWER': {'IN':['fot', 'f.o.t']}},
    {'LOWER':  {'IN':['res', 'residencial', 'comercial', 'com', 'industrial']}, "OP": "?"},
    {"IS_PUNCT": True, "OP":"?"},
    {"LIKE_NUM": True}
]])
matcher.add('barrio', [[
    {"LOWER": {'IN': ['estancia', 'barrio', 'country', 'club']}},
    {'POS':"PROPN", "OP": "+"}
]])

# ---------------------------------------
# Metricas
# ---------------------------------------
METRICAS = {
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


def matches(doc):
    prev_result = {
        'medidas': [],
        'DIR_NRO': [],
        'DIR_INTERSECCION': [],
        'DIR_ENTRE': [],
        'DIR_LOTE': [],
        'fot': [],
        'irregular': [],
        'pileta': [],
        'barrio': [],
        'esquina': [],
        'frentes': []
    }
    matches_locales= copy.deepcopy(prev_result)

    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_span = doc[start:end]
        prev_result[NLP.vocab.strings[match_id]].append(matched_span.text)
    for lista in prev_result:
        if prev_result[lista]:
            if lista=="fot":
                elegido= " ".join(prev_result[lista])
            else:
                elegido= max(prev_result[lista], key=len)
            matches_locales[lista].append(elegido)
    return matches_locales

def matches_dep(doc):
    prev_result = {
        'medidas': [],
        'DIR_NRO': [],
        'DIR_INTERSECCION': [],
        'DIR_ENTRE': [],
        'DIR_LOTE': [],
        'fot': [],
        'irregular': [],
        'pileta': [],
        'barrio': [],
        'esquina': [],
        'frentes': []
    }
    matches_dep = dep_matcher(doc)
    for match_id, token_ids in matches_dep:
        palabra= []
        for token_id in sorted(token_ids):
            token = doc[token_id]
            palabra.append(token.text)
        prev_result[NLP.vocab.strings[match_id]].append(' '.join(palabra))
    return prev_result

def merge(dic1, dic2):
    for clave, valores in dic1.items():
        if clave in dic2:
            dic2[clave].extend(valores)
        else:
            dic2[clave] = valores
    return dic2

# Si hay un match de dir interseccion y dir entre, donde el dir interseccion es substring del dir entre, se deja el dir entre
def clear_inter_entre(result):
    for interseccion in result.get('DIR_INTERSECCION', []):
        for entre in result.get('DIR_ENTRE', []):
            if interseccion in entre:
                result['DIR_INTERSECCION'].remove(interseccion)
    return result


def calcular_performance_por_variable():
    for variable, valores in METRICAS.items():
        tp = valores["tp"]
        fp = valores["fp"]
        fn = valores["fn"]

        precision = tp / (tp + fp) if (tp+fp)>0 else 0
        recall = tp / (tp + fn) if (tp+fn)>0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision+recall) >0 else 0

        METRICAS[variable]["p"] = precision
        METRICAS[variable]["r"] = recall
        METRICAS[variable]["f1"] = f1_score

def post_procesamiento(result: dict[list]):
    for variable in result.keys():
        if type(result[variable]) != bool:
            prediccion= str(result[variable]).strip()
            prediccion= " ".join(token.text for token in NLP(prediccion) if not token.is_punct)
            result[variable]= prediccion
    return result

def contiene_dos(texto):
    patron = re.compile(r'\b(dos|doble|2)\b', re.IGNORECASE)
    coincidencias = patron.findall(texto)
    return bool(coincidencias)

def contiene_tres(texto):
    patron = re.compile(r'\b(tres|triple|3)\b', re.IGNORECASE)
    coincidencias = patron.findall(texto)
    return bool(coincidencias)

def procesar_frentes(frentes_predichos):
    for match in frentes_predichos:
        contiene_2= contiene_dos(match.lower())
        if contiene_2:
            return 2
        else: 
            contiene_3= contiene_tres(match.lower())
            if contiene_3:
                return 3
    else:
        return 1


def procesar_irregular(predichos):
    for predicho in predichos:
        if "irregular" in predicho.lower(): 
            return True
        patron = re.compile(r'\b(triangular|martillo|trapecio)\b', re.IGNORECASE)
        coincidencias = patron.findall(predicho)
        if bool(coincidencias):
            return True 
    else:
        return ""
    
def contar_numeros(cadena):
    numeros = re.findall(r'\b\d+(?:[.,]\d+)?\b', cadena)
    numeros_sin_duplicados = set(numeros)
    return len(numeros_sin_duplicados)


def procesar_matches(predichos):
    matches_direccion_todos=predichos["DIR_ENTRE"]+predichos["DIR_INTERSECCION"]+predichos["DIR_NRO"]+predichos["DIR_LOTE"]
    result = {
        'direccion': max(matches_direccion_todos, key=len) if matches_direccion_todos else "",
        'fot': max(predichos["fot"], key=len) if predichos["fot"] else "",
        'irregular': procesar_irregular(predichos["irregular"]) if len(predichos["irregular"])>0 else "",
        'medidas': max(predichos["medidas"], key=len) if predichos["medidas"] else "",
        'esquina': True if len(predichos["esquina"])>0 else "",
        'barrio': max(predichos["barrio"], key=len) if predichos["barrio"] else "",
        'frentes': procesar_frentes(predichos["frentes"]) if predichos["frentes"] else "",
        'pileta': True if len(predichos["pileta"])>0 else "",
    }
    result= post_procesamiento(result)
    for variable, esperada in zip(result, list(row[1:])):
        rta= result[variable]
        if rta == "" and esperada == "":
            METRICAS[variable]["tn"]+=1
        else:
            if variable == "fot":
                esperada= ' '.join([token.text for token in NLP(esperada) if not token.is_punct])
                rta= ' '.join([token.text for token in NLP(rta) if not token.is_punct])

            if variable in ["direccion","fot", "medidas", "barrio"]:
                correcta= NLP(rta.lower()).similarity(NLP(esperada.lower())) == 1
            elif variable in [ "irregular", "esquina", "pileta"]:
                correcta= rta != "" and rta == esperada
                if variable == "irregular" and rta == "":
                    correcta =  contar_numeros(result["medidas"]) > 2
            elif variable == "frentes":
                if esperada == "":
                    correcta = False
                elif not rta:
                    correcta = True if result["esquina"] and esperada == 2 else False
                else:
                    correcta = procesar_frentes(rta) == int(esperada) 

            if correcta: 
                METRICAS[variable]["tp"]+=1
            else:
                METRICAS[variable]["error"].append({
                    "contexto": row["descripcion"],
                    "respuesta_predicha": rta,
                    "respuesta_esperada": esperada
                })
                if rta == "" and esperada != "":
                    METRICAS[variable]["fn"]+=1
                elif (esperada == "" and rta != "") or (esperada!=rta):
                    METRICAS[variable]["fp"]+=1
 
def obtener_matches(doc):
    return clear_inter_entre(merge(matches_dep(doc), matches(doc)))

if __name__ == "__main__":
    input = pd.read_csv('ground_truth_75.csv', sep = '|')
    input = input.fillna("")

    for index, row in input.iterrows():
        predichos = obtener_matches(NLP(row['descripcion']))
        procesar_matches(predichos)
        calcular_performance_por_variable()
    with open('resultados2.json', 'w', encoding="utf8") as fp:
        json.dump(METRICAS, fp, ensure_ascii=False)






