import json
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
import joblib
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import nltk
import re

from nltk.stem.snowball import SnowballStemmer
# import nltk
# nltk.download('punkt')

stemmer = SnowballStemmer("english")

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z0-9]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters or numbrers (e.g. raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z0-9]', token):
            filtered_tokens.append(token)
    return filtered_tokens

def cluster(descriptions, titles, ids, num_clusters=5, stop_words='english', max_df=0.7, min_df=0.1, max_features=None, ngram_range=(1, 2), title_weight=2):
    if stop_words != 'english':
        stop_words = tokenize_and_stem(' '.join(stop_words))
    print('Initiating clustering')
    totalvocab_stemmed = []
    totalvocab_tokenized = []
    for i, desc in enumerate(descriptions):
        print(f'\rTokenizing and stemming description {i}/{len(descriptions)}', end='')
        allwords_stemmed = tokenize_and_stem(desc)  # for each item in 'synopses', tokenize/stem
        totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list

        allwords_tokenized = tokenize_only(desc)
        totalvocab_tokenized.extend(allwords_tokenized)

    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index=totalvocab_stemmed)

    print('\nPerforming tf-idf vectorization!')
    # define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=max_df, max_features=max_features,
                                       min_df=min_df, stop_words=stop_words,
                                       use_idf=True, tokenizer=tokenize_and_stem, ngram_range=ngram_range)

    new_descriptions = descriptions.copy()
    if title_weight > 0:
        for i in range(len(descriptions)):
            new_descriptions[i] = titles[i] + ' ' + new_descriptions[i]  # TODO: paste title w times to weight it by w
    tfidf_matrix = tfidf_vectorizer.fit_transform(new_descriptions)  # fit the vectorizer to synopses

    print(tfidf_matrix.shape)
    # TODO: convert to JSON with integer IDs
    tfidf_json = {}  # encode sparse matrix as json
    for row, id in zip(tfidf_matrix.toarray().tolist(), ids):
        id = int(id)
        tfidf_json[id] = {}
        for i, col in enumerate(row):
            if col != 0:
                tfidf_json[id][i] = col
    terms = tfidf_vectorizer.get_feature_names()
    with open('tfidf_json.json', 'w+') as f:
        json.dump({'terms': terms, 'data': tfidf_json}, f)
    df = pd.DataFrame(csr_matrix.todense(tfidf_matrix))
    csv_file = "tfidf_matrix.csv"
    df.to_csv(csv_file, index=False)

    dist = 1 - cosine_similarity(tfidf_matrix)

    km = KMeans(n_clusters=num_clusters)

    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()

    joblib.dump(km, 'doc_cluster.pkl')

    km = joblib.load('doc_cluster.pkl')
    clusters = km.labels_.tolist()

    films = {'title': titles, 'description': descriptions, 'cluster': clusters}

    frame = pd.DataFrame(films, index=[clusters], columns=['title', 'description', 'cluster'])

    frame['cluster'].value_counts()  # number of films per cluster (clusters from 0 to 4)

    print("Top terms per cluster:")
    print()
    # sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    for i in range(num_clusters):
        print("Cluster %d words:" % i, end='')

        for ind in order_centroids[i, :6]:  # replace 6 with n words per cluster
            print(' %s' % vocab_frame.loc[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'), end=',')
        print()  # add whitespace
        print()  # add whitespace

        print("Cluster %d titles:" % i, end='')
        for title in frame.loc[i]['title'].values.tolist()[:10]:
            print(' %s,' % title, end='')
        print()  # add whitespace
        print()  # add whitespace

    # convert two components as we're plotting points in a two-dimensional plane
    # "precomputed" because we provide a distance matrix
    # we will also specify `random_state` so the plot is reproducible.
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

    pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

    xs, ys = pos[:, 0], pos[:, 1]
    print()
    print()

    cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e'}

    # set up cluster names using a dict
    cluster_names = {0: '0',
                     1: '1',
                     2: '2',
                     3: '3',
                     4: '4'}

    # create data frame that has the result of the MDS plus the cluster numbers and titles
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles))

    # group by cluster
    groups = df.groupby('label')


    # set up plot
    fig, ax = plt.subplots(figsize=(17, 9))  # set size
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling

    # iterate through groups to layer the plot
    # note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
                label=cluster_names[name], color=cluster_colors[name],
                mec='none')
        ax.set_aspect('auto')
        ax.tick_params(axis='x',          # changes apply to the x-axis
                       which='both',      # both major and minor ticks are affected
                       bottom='off',      # ticks along the bottom edge are off
                       top='off',         # ticks along the top edge are off
                       labelbottom='off')
        ax.tick_params(axis='y',         # changes apply to the y-axis
                       which='both',      # both major and minor ticks are affected
                       left='off',      # ticks along the bottom edge are off
                       top='off',         # ticks along the top edge are off
                       labelleft='off')

    ax.legend(numpoints=1)  # show legend with only 1 point

    # add label in x,y position with the label as the film title
    # for i in range(len(df)):
    # ax.text(df.loc[i]['x'], df.loc[i]['y'], df.loc[i]['title'], size=8)

    plt.show()  # show the plot

'''
Suppose you are looking for an n-gram where each word has m synonyms
search_query is of the form [[w1.1, ... , w1.m],..., [wn.1, ... , wn.m]]
If description has length d and n = 1, we run in O(d + m)
For n > 1, we run in O(dn + nm)
'''
def contains_fuzzy(description, search_query):
    words = tokenize_and_stem(description)
    query = [set(tokenize_and_stem(' '.join(words))) for words in search_query] # O(nm)
    if len(query) == 1:
        words = set(words) # O(d)
        for synonym in query: # O(m)
            if synonym in words:
                return True
        return False
    else:
        for i in range(len(words) - len(query) + 1): # O(dn)
            found = True
            for w in range(len(query)):
                if words[i + w] not in query[w]:
                    found = False
                    break
            if found:
                return True
        return False

print()
