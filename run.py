
from helper import contar_numeros, get_numeros
from matcher import Matcher
import pandas as pd
import json 
import spacy
NLP = spacy.load("es_core_news_lg")


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

MATCHER = Matcher()
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


def procesar_resultados(predichos):
    for variable, esperada in zip(predichos, list(row[1:])):
        predicho= predichos[variable]
        if predicho == "" and esperada == "":
            METRICAS[variable]["tn"]+=1
        else:
            if variable in ["direccion","fot", "medidas", "barrio"]:
                correcta= NLP(predicho.lower()).similarity(NLP(esperada.lower())) == 1
            elif variable in [ "irregular", "esquina", "pileta"]:
                correcta= predicho != "" and predicho == esperada
                
            elif variable == "frentes":
                if esperada == "":
                    correcta = False
                elif not predicho:
                    correcta = True if predichos["esquina"] and esperada == 2 else False
                else:
                    correcta = predicho == int(esperada) 

            if correcta: 
                METRICAS[variable]["tp"]+=1
            else:
                METRICAS[variable]["error"].append({
                    "contexto": row["descripcion"],
                    "respuesta_predicha": predicho,
                    "respuesta_esperada": esperada
                })
                if predicho == "" and esperada != "":
                    METRICAS[variable]["fn"]+=1
                elif (esperada == "" and predicho != "") or (esperada!=predicho):
                    METRICAS[variable]["fp"]+=1

def descubrir_nuevos(predichos: dict):
    if predichos["irregular"]== "":
        predichos["irregular"]= True if contar_numeros(predichos["medidas"]) > 2 else ""

    if predichos["esquina"]:
        predichos["frentes"]= 2

if __name__ == "__main__":
    input = pd.read_csv('ground_truth_75.csv', sep = '|')
    input = input.fillna("")

    for index, row in input.iterrows():
        predichos = MATCHER.get_pairs(row['descripcion'])
        descubrir_nuevos(predichos)
        procesar_resultados(predichos)
        calcular_performance_por_variable()
    with open('resultados.json', 'w', encoding="utf8") as fp:
        json.dump(METRICAS, fp, ensure_ascii=False)