import spacy
from spacy import displacy
from spacy.matcher import Matcher, DependencyMatcher

nlp = spacy.load("es_core_news_lg")

doc=nlp("Se trata de un galpón de doble frente, ubicado sobre Av. De los Quilmes N° 1540/1550 a escasos metros del triangulo de Bernal, en zonificación R3  (permitiendo industrias de actividad inocua) de excelente acceso y de salida rápida a autopista Buenos Aires la Plata,diferentes puntos del conurbano como así también a Capital Federal.Galpón N° 1540:Implantado sobre dos lotes de terreno.En su primera mitad de 14,80 mts. x  mts. x 25,70 mts. Sup. Cubierta: 380,3.")

displacy.serve(doc)
frentes = [
    [
        {'RIGHT_ID': 'frentes', 'RIGHT_ATTRS': {'LOWER': {"IN": ['frentes', 'frente']}}}, 
        {'LEFT_ID': 'frentes', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': {"IN": ['nummod', 'amod']}}} 
    ]
]
dep_matcher= DependencyMatcher(nlp.vocab)
dep_matcher.add('FRENTES', patterns=frentes)

matches_dep = dep_matcher(doc)
for match_id, token_ids in matches_dep:
    palabra= []
    for token_id in sorted(token_ids):
        token = doc[token_id]
        palabra.append(token.text)
    print(nlp.vocab.strings[match_id], ' '.join(palabra))
