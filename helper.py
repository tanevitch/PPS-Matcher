import spacy
import re 

NLP = spacy.load("es_core_news_lg")

def clear_inter_entre(result):
    for interseccion in result.get('dir_interseccion', []):
        for entre in result.get('dir_entre', []):
            if interseccion in entre and interseccion in result["dir_interseccion"]:
                result['dir_interseccion'].remove(interseccion)
    return result

def procesar_direccion(predichos: list[list]):
    predichos= clear_inter_entre(predichos)
    matches_direccion_todos=predichos["dir_entre"]+predichos["dir_interseccion"]+predichos["dir_nro"]+predichos["dir_lote"]
    if matches_direccion_todos == []:
        return ""
    mejor_match= max(matches_direccion_todos, key=len)
    
    return re.sub(r'^\. ', '',mejor_match)

def procesar_fot(predichos: list):
    numeros = get_numeros(" ".join(predichos))
    if contar_numeros(" ".join(predichos)) == 1:
        return " ".join(set(numeros))
    else: 
        result = ". ".join(list(set(predichos)))
        result = result.replace("Res.", "residencial:")
        result = result.replace("Com.", "comercial:")
        result = result.replace("Fot", "FOT")
        return result


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
    
def get_numeros(cadena: str):
    return re.findall(r'\b\d+(?:[.,]\d+)?\b', cadena)
     

def contar_numeros(cadena):
    numeros = re.findall(r'\b\d+(?:[.,]\d+)?\b', cadena)
    numeros_sin_duplicados = set(numeros)
    return len(numeros_sin_duplicados)


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

def procesar_medidas(predichos: list):
    mejor_match = max(predichos, key=len)
    medidas = ""
    for numero in list(map(str, get_numeros(mejor_match))):
        medidas+= numero+" x "
    return medidas.rstrip(" x")

def procesar_barrio(predichos: list):
    return max(predichos, key=len)
    # return re.compile(re.escape("Barrio"), re.IGNORECASE).sub("", mejor_match).strip()