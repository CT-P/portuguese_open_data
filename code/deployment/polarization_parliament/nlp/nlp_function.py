#imports python package
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import os
import datetime
import re
import string
from collections import Counter

import nltk
from nltk.corpus import stopwords


def check_dialog(text_):
    pat="(?:</p><p>.*?\(.*?\): —)"
    match=re.findall(pat, text_)
    if match is None :
        return 'no_dialog'
    else:
        for m in match:
            
            return m

def extract_dialog(full_text,characters_for_name):    
    if full_text is None:
        return None
    else:
        dialogs=[(m.start(0), m.end(0)) for m in re.finditer('</p><p></p><p>(.+?): —', full_text)]
        out=[]
        if len(dialogs)==1:
            out.append(full_text[dialogs[0][1]-characters_for_name:])
        if len(dialogs)>1:
            for i in range(0, len(dialogs)-1):
                out.append(full_text[dialogs[i][1]-characters_for_name:dialogs[i+1][0]])
            out.append(full_text[dialogs[len(dialogs)-1][1]-50:])
        return out

    
def extract_party_name(dialogs):
    if dialogs is None:
        return None
    else:
        res=[]
        for i in dialogs:
                    positions=[(m.start(0), m.end(0)) for m in re.finditer('\((.+?)\): —', i)]
                    if len(positions)==0:
                        res.append(['No','No'])
                    else:
                        party=re.findall('\((.+?)\)',i)
                        name_aux=i[positions[0][1]-50:positions[0][1]]
                        name=re.sub(r'\b\w{1,2}\b', '', name_aux).replace('.','').replace ('()','').replace('  ','').replace('<','').replace('>','').replace('/','').replace(': —','')
                        if len(party)>0:
                            party=party[0]
                        res.append([party,name])
        return res

def add_speech_next_page(df):
    for pi in range(1,df.page.max()+1):
        if len(df[df.page==pi].speech.values[0])>0:
            speeches=df[df.page==pi].speech.values[0]
            if '</noscript>' in speeches[-1]:
                
                for n in range(1,df.page.max()-pi):
                    if ': —' in df[df.page==pi+n].text_1.values[0]:
                        
                        in_=df[df.page==pi+n].text_1.values[0].find(': —')
                        df[df.page==pi].speech.values[0][-1]=df[df.page==pi].speech.values[0][-1]+' '+str(df[df.page==pi+n].text_1.values[0][0:in_])
                        
                        break
                    else:
                        
                        df[df.page==pi].speech.values[0][-1]=df[df.page==pi].speech.values[0][-1]+' '+str(df[df.page==pi+n].text_1.values[0])
    return df


#defining the function to remove punctuation
def remove_punctuation(text):
  if(type(text)==float):
    return text
  ans=""  
  for i in text:     
    if i not in string.punctuation:
      ans+=i    
  return ans

def normlizeTokens(tokenLst, stopwordLst = None, stemmer = None):
    #We can use a generator here as we just need to iterate over it

    #Lowering the case and removing non-words
    workingIter = (w.lower() for w in tokenLst if w.isalpha())

    #Now we can use the semmer, if provided
    if stemmer is not None:
        workingIter = (stemmer.stem(w) for w in workingIter)
         
    #And remove the stopwords
    if stopwordLst is not None:
        workingIter = (w for w in workingIter if w not in stopwordLst)
    #We will return a list with the stopwords removed
    return list(workingIter)

def generate_N_grams(text,ngram=1):
  words=[word for word in text]  
  temp=zip(*[words[i:] for i in range(0,ngram)])
  ans=[' '.join(ngram) for ngram in temp]
  return ans


def rem(x, names_deputies,parties_ ):
    ans=[]
    dd=names_deputies+parties_
    ddf=np.append(dd,np.array(['sr.as','srs.','presidente','es.a','sr.ª','srº','sr']))
    for i in x.split(' '):
        #print(i)
        if i not in ddf:
            #print(i)
            ans.append(i)

    return ' '.join(ans)

def remove_accents(raw_text):
    """Removes common accent characters.

    Our goal is to brute force login mechanisms, and I work primary with
    companies deploying Engligh-language systems. From my experience, user
    accounts tend to be created without special accented characters. This
    function tries to swap those out for standard Engligh alphabet.
    """

    raw_text = re.sub(u"[àáâãäå]", 'a', raw_text)
    raw_text = re.sub(u"[èéêë]", 'e', raw_text)
    raw_text = re.sub(u"[ìíîï]", 'i', raw_text)
    raw_text = re.sub(u"[òóôõö]", 'o', raw_text)
    raw_text = re.sub(u"[ùúûü]", 'u', raw_text)
    raw_text = re.sub(u"[ç]", 'c', raw_text)

    return raw_text

def add_zeros(int_):
    if len(str(int_))<2:
        return '00'+str(int_)
    if len(str(int_))<3:
        return '0'+str(int_)
    if len(str(int_))==3:
        return str(int_)

def remove_punctuation(df_frame):
    df_frame['no_punct']= df_frame['no_punct'].apply(lambda x:remove_accents(x))
    return df_frame

def remove_names_in_speech(df_frame,names_deputies,parties_):
    df_frame['speech1']=df_frame['no_punct'].apply(lambda x:rem(x, names_deputies,parties_ ) )
    return df_frame

def create_tokens(df_frame):
    nltk.download('stopwords')
    stop_words_nltk = nltk.corpus.stopwords.words('portuguese')

    df_frame['tokenized_text'] = df_frame['speech1'].apply(lambda x: nltk.word_tokenize(x))
    df_frame['normalized_tokens'] = df_frame['tokenized_text'].apply(lambda x: normlizeTokens(x, stopwordLst = stop_words_nltk, stemmer = None))
    df_frame['normalized_tokens_count'] = df_frame['normalized_tokens'].apply(lambda x: len(x))
    return df_frame

def create_grams(df_frame, n):
    df_frame['tri_grams'] = df_frame['normalized_tokens'].apply(lambda x: generate_N_grams(x,n))
    return df_frame



def create_200r(df_mainf):
    indexes_no_applause=[n for n,x in enumerate(df_mainf.phrase) if 'aplausos' not in x]
    df_mainf=df_mainf.iloc[indexes_no_applause]

    tri_final = df_mainf[0:200].append(df_mainf[-200:], ignore_index=True)
    return tri_final

def add_url_finaldf(df_final200,declaracoes2):
    tri_final=df_final200
    tri_final['reference'] = [[]] * tri_final.shape[0]
    tri_final=tri_final.reset_index()
    for n,x in enumerate(tri_final.phrase):
        a=[i.count(x) for i in declaracoes2.tri_grams]
        indexes=np.where(np.array(a) >= 3)[0]
        list_links=[]
        for i in indexes:
            number=add_zeros(declaracoes2.iloc[i].number ) 
            legislature=declaracoes2.iloc[i].legislatura 
            session=declaracoes2.iloc[i].session 
            date=datetime.datetime.strptime(declaracoes2.iloc[i].date , '%d/%m/%Y').strftime('%Y-%m-%d')
            url_=f'https://debates.parlamento.pt/catalogo/r3/dar/01/{legislature}/{session}/{number}/{date}' 
            list_links.append(url_)
        if list_links==[]:
            list_links=['does not appear more than 3 times']
    
        tri_final['reference'][n]=list_links
    return tri_final