from simplify import get_df, tokenize
from json import dump
# import px
import plotly.express as px
# from nlp.clusterer import tokenize_and_stem

def dict_to_js(dict, title):
    with open(f'{title}.js', 'w+', encoding='utf-8') as f:
        out = f'var {title} = JSON.parse(`{str({k: v for k, v in dict.items()})}`);'
        out = out.replace('\'', '"')
        f.write(out)

''' pass tokenized description and query '''
def contains(description, query):
    if len(query) == 1:
        description = set(description)  # O(d)
        for synonym in query:  # O(m)
            if synonym in description:
                return True
        return False
    else:
        for i in range(len(description) - len(query) + 1):  # O(dn)
            found = True
            for w in range(len(query)):
                if description[i + w] not in query[w]:
                    found = False
                    break
            if found:
                return True
        return False

def query_index(index, query):
    query = tokenize(query)
    scores = {}
    matches_in_vid = {}
    for word in query:
        video_scores = index[word]
        for vid, score in video_scores.items():
            if vid not in scores:
                scores[vid] = 1
                matches_in_vid[vid] = 0
            scores[vid] *= (1 + 10 * score)
            matches_in_vid[vid] += 1
    for vid in matches_in_vid:
        scores[vid] *= 2 ** (2 * (matches_in_vid[vid]) / (len(query)))
    scores = {k: v for k, v in sorted(scores.items(), key=lambda i: i[1], reverse=True)}
    # take the top 300 results and search the raw text
    # check for n-grams in title where each n-gram multiplies score by 2**n
    # check for n-grams in desc where each n-gram multiplies score by n
    # ngrams first, then n, then n-1grams, then n-1
    # also need constant time lookup of video parms from ID
    # for vid, score in scores.items()[:300]:
    # if contains()
    return scores

def add_text_field(text, tf, idf, metadata, field_weight=1):
    words = tokenize(text)
    for word in words:
        if word not in tf:
            tf[word] = 0
            if word not in metadata['doc_freq']:
                metadata['doc_freq'][word] = 0
            metadata['doc_freq'][word] += 1
        if word not in idf:
            idf[word] = 0
        tf[word] += field_weight
        idf[word] += 1
        metadata['tokens_parsed'] += 1


def add_BM25F(title, desc, tf, idf, metadata):
    # tf is term frequency
    # idf is inverse document frequency
    add_text_field(title, tf, idf, metadata, field_weight=100)
    add_text_field(desc, tf, idf, metadata, field_weight=1)
    metadata['documents_parsed'] += 1

def letters(string):
    return ''.join([s for s in string if s.isalpha()])

def index_pairs(id, tokens, index):
    for token in tokens:
        t = ' ' + letters(token) + ' '
        for i in range(len(t) - 1):
            pair = t[i:i + 2]
            if pair not in index:
                index[pair] = set()
            index[pair].add(id)

def query_pairs(query_tokens, index):
    pairs = set()
    for token in query_tokens:
        t = ' ' + letters(token) + ' '
        for i in range(len(t) - 1):
            pair = t[i:i + 2]
            pairs.add(pair)
    pairs = list(pairs)
    matching_videos = None
    for pair in pairs:
        if pair in index:
            if matching_videos is None:
                matching_videos = list(index[pair])
            else:
                new = []
                for video in matching_videos:
                    if video in index[pair]:
                        new.append(video)
                matching_videos = new
    return matching_videos
# TODO: incorperate stars and tags into index ratings
def index(df):
    # unique_words = {}
    index = {}
    pairs = {}
    term_feq = {}
    idf = {}  # contains uninverted document frequencies
    metadata = {
        'tokens_parsed': 0,
        'documents_parsed': 0,
        'doc_freq': {},
    }
    for i, row in enumerate(df[['id', 'title', 'desc']].itertuples()):
        print(f'\rAdding tf-idf tokens from video {i}/{len(df)}', end='')
        try:
            tf = {}
            add_BM25F(row.title, row.desc, tf, idf, metadata)
            index_pairs(row.id, tokenize(row.desc), pairs)
            index_pairs(row.id, tokenize(row.title), pairs)
            term_feq[row.id] = tf
        except AttributeError as e:
            pass
    pairs = {k: v for k, v in pairs.items() if len(v) < len(df) * 3 // 2}
    for i, video_id in enumerate(term_feq):
        print(f'\rIndexing video {i}/{len(term_feq)}', end='')
        tf = term_feq[video_id]
        for word in tf:
            if word not in index:
                index[word] = {}
            index[word][video_id] = round(tf[word] / idf[word], 4)
            # for prev, curr in zip(words, words[1:]):
            #     pair = (prev, curr)
            #     if pair not in unique_pairs:
            #         unique_pairs[pair] = 0
            #     unique_pairs[pair] += 1
    # {k: v for k, v in sorted(unique_pairs.items(), key=lambda i: i[1], reverse=True)}
    # sort all videos by word score (not actually needed)
    print()
    # for i, word in enumerate(index):
    #     print(f'\rSorting index of word {i}/{len(index)}', end='')
    #     index[word] = {k: v for k, v in sorted(index[word].items(), key=lambda i: i[1], reverse=True)}

    # code to plot the dist of word freqs
    # x = list(range(1, len(df) + 1))
    # y = [0] * len(df)
    # for word, count in metadata['doc_freq'].items():
    #     y[count] += 1
    # fig = px.scatter(x=x,y=y, trendline='ols')
    # fig.show()
    return index, pairs

df = get_df()
index, pairs = index(df)
# dict_to_js(index, 'index')
with open('index.js', 'w+', encoding='utf-8') as f:
    out = 'var index = new Set(["' + '\",\"'.join([w for w in index.keys()]) + '"])'
    out = out.replace('\'', '"')
    f.write(out)
pairs = {k: list(v) for k, v in pairs.items()}
print('dumping index')

for word, scores in list(index.items()):
    try:
        with open(f'./distributed_index/{word}.json', 'w+') as f:
            dump(scores, f)
    except:
        print('failed on: ' + word)
# with open('index.json', 'w+') as f:
#     dump(index, f)
# with open('pairs.json', 'w+') as f:
#     dump(pairs, f)

# print(len(query_pairs(tokenize('lesbian'), pairs)))
# print(len(query_pairs(tokenize('horny sex'), pairs)))
# print(len(query_pairs(tokenize('big dick'), pairs)))
# print(len(query_pairs(tokenize('watch the'), pairs)))
# print(len(query_pairs(tokenize('girlfriend camera'), pairs)))
# print(len(query_pairs(tokenize('naked girl'), pairs)))
# print()

# TODO: add tags and studio and stars to index
