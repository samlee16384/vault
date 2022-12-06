import pandas as pd
import re 

def tokenize(text):
    for c in ['`', '-', '’', '‘', '\'']:
        text = text.replace(c, '')
    for c in ['.', '/', ',', ')', '…', '(', ':', '?', '!', '“', '”', ';', '-', '’', '‘', '\'', '\"', '\r', '\t', '\n']:
        text = text.replace(c, ' ')
    tokens = text.lower().split(' ')
    tokens = [t for t in tokens if t != '']
    return tokens

def get_df():
    df = pd.read_csv('video_data.csv')
    df = df[df['video'].notnull()]
    df['description_A'] = df['description_A'].fillna('')
    df['description_B'] = df['description_B'].fillna('')
    df['desc'] = df['description_A'] + ' ' + df['description_B']
    df = df.drop(['Unnamed: 0', 'description_A', 'description_B', 'affiliate_link', 'affiliate_image_desc'], axis=1)
    df['affiliate_image'] = df['affiliate_image'].fillna('')
    df = df.sort_values('n_comments', ascending=False)
    # df['title'] = df['title'].apply(lambda x: tokenize(x))
    # df['desc'] = df['desc'].apply(lambda x: tokenize(x))
    print('Data loaded')
    df['tags'] = (df['tags'].apply(lambda x: x.replace('\'', "")))
    df['stars'] = (df['stars'].apply(lambda x: x.replace('\'', "")))
    return df

def cleanRawStr(s):
    s = s.replace('\'', '"')
    s = s.replace('\\r', ' ')
    s = s.replace('\\n', ' ')
    s = s.replace('<br/>', ' ')
    s = s.replace('\\x92', '’')
    s = s.replace('\\u200b', '’')
    s = s.replace('`', '’')
    s = re.sub('<a.*?</a>', '', s)
    return s

def cleanStr(s):
    s = s.replace('\r', ' ')
    s = s.replace('\n', ' ')
    s = s.replace('<br/>', ' ')
    s = s.replace('\x92', '’')
    s = s.replace('\u200b', '’')
    s = s.replace('\u2033', '"')
    s = s.replace('\u0443', 'u')
    s = s.replace('`', '’')
    s = re.sub('<a.*?</a>', '', s)
    return s

df = get_df()

for index, row in df.iterrows():
    try:
        with open(f'./distributed_desc/{row["id"]}.txt', 'w+', encoding="utf-8") as f:
            f.write(cleanStr(row['desc']))
    except:
        print('failed on: ' + str(index))

df = df.drop(['desc'], axis=1)
with open('db.js', 'w+', encoding='utf-8') as f:
    string = "var db = ["

    json_content = ','.join([str(l) for l in (df.values.tolist())])
    
    string += cleanRawStr(json_content)
    string += "]"

    f.write(string)

# STOP = {'those', 'own', '’ve', 'yourselves', 'around', 'been', 'alone', 'off', 'am', 'then', 'other', 'can', 'regarding', 'hereafter', 'front', 'too', 'used', 'wherein', '‘ll', 'doing', 'everything', 'up', 'onto', 'never', 'either', 'how', 'before', 'anyway', 'since', 'through', 'amount', 'now', 'was', 'have', 'into', 'because', 'not', 'therefore', 'they', 'n’t', 'even', 'whom', 'it', 'see', 'somewhere', 'thereupon', 'nothing', 'whereas', 'much', 'whenever', 'seem', 'until', 'whereby', 'at', 'also', 'some', 'last', 'than', 'get', 'already', 'our', 'once', 'will', 'noone', "'m", 'that', 'what', 'thus', 'no', 'myself', 'out', 'next', 'whatever', 'although', 'though', 'which', 'would', 'therein', 'nor', 'somehow', 'whereupon', 'besides', 'whoever', 'ourselves', 'few', 'did', 'without', 'third', 'anything', 'against', 'while', 'if', 'however', 'when', 'may', 'ours', 'done', 'seems', 'else', 'call', 'perhaps', 'had', 'nevertheless', 'where', 'otherwise', 'still', 'within', 'its', 'for', 'elsewhere', 'throughout', 'of', 'others', 'show', '’s', 'anywhere', 'anyhow', 'as', 'are', 'the', 'hence', 'something', 'hereby', 'nowhere', 'latterly', 'say', 'does', 'neither', 'go', 'put', 'their', 'by', 'namely', 'could', 'unless', 'itself', 'is', 'whereafter', 'thereby', 'such', 'both', 'become', 'whole', 'who', 'yourself', 'every', 'thru', 'except', 'very', 'several', 'among', 'being', 'be', 'mine', 'further', 'n‘t', 'here', 'during', 'why', 'with', 'just', "'s", 'becomes', '’ll', 'about', 'a', 'using', 'seeming', "'d", "'ll", "'re", 'due', 'wherever', 'beforehand', 'becoming', 'might', 'amongst', 'my', 'thence', 'thereafter', 'almost', 'least', 'someone', 'often', 'from', 'keep', 'or', '‘m', 'nobody', 'sometime', 'across', '‘s', '’re', 'only', 'via', 'name', 'eight', 'three', 'back', 'to', 'all', 'became', 'move', 'formerly', 'so', 'i', 'whence', 'herein', 'more', 'after', 'themselves', 'you', 'above', 'them', 'your', 'made', 'indeed', 'most', 'everywhere', 'but', 'must', 'along', 'beside', 'anyone', 'full', 'has', 'yours', 'whose', 'seemed', 'sometimes', 'should', 'over', 'take', 'each', 'same', 'rather', 'really', 'latter', 'and', 'ca', 'hereupon', 'part', 'per', 'ever', '‘re', 'enough', "n't", 'again', '‘d', 'us', 'yet', 'moreover', 'mostly', 'one', 'meanwhile', 'whither', 'there', 'toward', '’m', "'ve", '’d', 'give', 'do', 'an', 'quite', 'these', 'everyone', 'towards', 'this', 'cannot', 'afterwards', 'beyond', 'make', 'were', 'whether', 'well', 'another', 'upon', 'any', 'none', 'various', 're', 'less', '‘ve'}



# big boobs
# small boobs
# big ass
# teen
# young
# big dick
# shaved
# oiled
# sister
# mom (mom, mother)
# step (sister + mom)
# step
# 69
# https://www.pornhub.com/insights/yir-2021

# also fix tags like anal, lesbian, threesome, orgy by checking for the words in the desc


# [(' '.join(k),v) for k,v in sorted_uniques.items() if k[1] == 'girl']


# {
#     ''Teen'': ['teen', 'teenage', 'college', '18-year-old'],
#     'Tight Pussy': small,
#     ''Shaved'': ['shaved', 'bald', 'trimmed']
# }

# tits, girlfriende, blonde, slut, babe, horny, cowgirl, spread, dripping, panties, clit, asshole, ass, bubble, brunette, naughty, sister, lesbian, milf, doggy, crazy, college, blowjob, step, teens, amatuer, stepmom, moaning, stepsisterm, boobs, petite, titties, masturbating, hardcore, threesome, daughter, stepdaughter, squirting, creamy, babes, shower, anal, moans, doggie, whore, busty, saliva, natural, wet, deep, missionary, cum, innocnent/shy, virgin
# big tits, reverse cowgirl, bubble butt

#
#
#
#
# throbbing, hard, errect
# moaning, moan, moans


