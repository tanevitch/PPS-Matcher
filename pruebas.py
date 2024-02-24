import spacy
from spacy import displacy
from spacy.matcher import Matcher, DependencyMatcher

nlp = spacy.load("es_core_news_lg")

doc=nlp("Avenida Montevideo y 105. Lote de 8.66 x 26 mts.")
for token in doc:
    print(token.text, token.pos_, token.dep_)
displacy.serve(doc)
matcher= Matcher(nlp.vocab)
matcher.add('FRENTES', patterns=[[
    {'LIKE_NUM': True}, 
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
    {'LOWER': {"IN": ["x", "por", "y"]}},
    {'LIKE_NUM': True},
    {'LOWER': {"IN": ["mts","m","metros"]}, "OP":"?"},
]])

matches = matcher(doc)
for match_id, start, end in matches:
    matched_span = doc[start:end]
    print(nlp.vocab.strings[match_id], matched_span.text)

# dep_matcher= DependencyMatcher(nlp.vocab)
# fot = [
#         [
#             {'RIGHT_ID': 'fot', 'RIGHT_ATTRS': {'TEXT': {'IN':['FOT', 'fot', 'F.O.T', 'f.o.t', 'Fot', 'F.o.t']}}},
#             {'LEFT_ID': 'fot', 'REL_OP': '>', 'RIGHT_ID': 'num', 'RIGHT_ATTRS': {'DEP': 'nummod'}} 
#         ]
# ]
# dep_matcher.add("fot", fot)
# matches_dep = dep_matcher(doc)
# for match_id, token_ids in matches_dep:
#     palabra= []
#     for token_id in sorted(token_ids):
#         token = doc[token_id]
#         palabra.append(token.text)
#     print(nlp.vocab.strings[match_id], ' '.join(palabra))
