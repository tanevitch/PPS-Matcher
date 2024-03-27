import json
import re
import spacy
from spacy.matcher import Matcher, DependencyMatcher
import pandas as pd
from spacy import displacy
import copy

NLP = spacy.load('es_core_news_lg')



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






