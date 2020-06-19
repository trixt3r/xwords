from collections import namedtuple
word_info_t=namedtuple("word_info_t",["nature","api","genre","nbr","lex","anto","hypo","syno","desinences", "mot"],defaults=[
"","","",[],[],[],[],[],""])
desinences_t=namedtuple("desinences_t",['ms','mp','fs','fp','rad'],defaults=['','','','',''])
word_t=namedtuple("word_t", ["ort", "api"])
