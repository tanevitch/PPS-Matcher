import spacy
from spacy import displacy
from spacy.matcher import Matcher, DependencyMatcher

nlp = spacy.load("es_core_news_lg")

doc=nlp("CASA SUCRE - BELGRANO R Casa sobre lote propio de doble frente (17.35 x 35) con balcones terraza, jardín, piscina, solárium y quincho con parrilla")
for token in doc:
    print(token.text, token.pos_, token.dep_)

# matcher= Matcher(nlp.vocab)
# matcher.add('FRENTES', patterns=[[
#     {'TEXT': {'IN':['fot', 'fot', 'F.O.T', 'FOT', 'f.o.t', 'fot', 'F.o.t']}},
#     {'LOWER':  {'IN':['res', 'residencial']}, "OP": "?"},
#     {"IS_PUNCT": True, "OP":"?"},
#     {"LIKE_NUM": True},
#     {"IS_PUNCT": True, "OP":"?"},
#     {'TEXT': {'IN':['fot', 'fot', 'F.O.T', 'FOT', 'f.o.t', 'fot', 'F.o.t']}, "OP": "?"},
#     {'LOWER': {'IN':['comercial', 'com', 'industrial']}, "OP": "?"},
#     {"IS_PUNCT": True, "OP":"?"},
#     {"LIKE_NUM": True, "OP": "?"}
# ]])

# matches = matcher(doc)
# for match_id, start, end in matches:
#     matched_span = doc[start:end]
#     print(nlp.vocab.strings[match_id], matched_span.text)

dep_matcher= DependencyMatcher(nlp.vocab)
fot = [
        [
            {'RIGHT_ID': 'fot', 'RIGHT_ATTRS': {'TEXT': {'IN':['FOT', 'fot', 'F.O.T', 'f.o.t', 'Fot', 'F.o.t']}}},
            {'LEFT_ID': 'fot', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
        ]
]
dep_matcher.add("fot", fot)
matches_dep = dep_matcher(doc)
for match_id, token_ids in matches_dep:
    palabra= []
    for token_id in sorted(token_ids):
        token = doc[token_id]
        palabra.append(token.text)
    print(nlp.vocab.strings[match_id], ' '.join(palabra))
