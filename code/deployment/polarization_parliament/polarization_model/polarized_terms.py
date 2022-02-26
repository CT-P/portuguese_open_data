import pandas as pd
import numpy as np

import os
import datetime
import re
import string
from collections import Counter

right=[ 'PSD',  'CDS-PP', 'CH','IL','CDS']
left=[ 'PS', 'BE', 'PCP', 'PAN', 'PEV','L','CDU']


def create_frequency_table_grams(n_gram=1, indf=None):
    right=[ 'PSD',  'CDS-PP', 'CH','IL','CDS']
    left=[ 'PS', 'BE', 'PCP', 'PAN', 'PEV','L','CDU']
    grams_d={1: 'uni_grams', 2: 'bi_grams', 3: 'tri_grams'}
   

    r_grams=[item for sublist in indf[indf.party.isin(right)][grams_d[n_gram]] for item in sublist]
    l_grams=[item for sublist in indf[indf.party.isin(left)][grams_d[n_gram]] for item in sublist]

    total_counter = Counter([item for sublist in indf[grams_d[n_gram]] for item in sublist])
    right_counter = Counter(r_grams)
    left_counter = Counter(l_grams)

    df_all = pd.DataFrame.from_dict(total_counter, orient='index').reset_index()
    df_all.columns=['phrase','count']
    df_all['f_right']=[right_counter[x] for x in df_all.phrase]
    df_all['f_left']=[left_counter[x] for x in df_all.phrase]


    df_all['f_left_total']=sum(left_counter.values())
    df_all['f_right_total']=sum(right_counter.values())
    df_all['f_right_minus']=(df_all['f_right']- df_all['f_right_total'])/df_all['f_right_total']
    df_all['f_left_minus']=(df_all['f_left']- df_all['f_left_total'])/df_all['f_left_total']

    df_all['f_right_norm']=df_all['f_right']/df_all['f_right_total']
    df_all['f_left_norm']=df_all['f_left']/df_all['f_left_total']

    df_all['f_right_minus_norm']=df_all['f_right_minus']/df_all['f_right_total']
    df_all['f_left_minus_norm']=df_all['f_left_minus']/df_all['f_left_total']

    return df_all


def calculate_pearson(df_all):
    aa=df_all['f_right_norm']*df_all['f_left_minus_norm'] 
    bb=df_all['f_left_norm']*df_all['f_right_minus_norm']
    cc=aa-bb
    dd=cc*cc
    d11=df_all['f_right_norm']+df_all['f_left_norm']
    d22=df_all['f_right_norm']+df_all['f_right_minus_norm']
    d33=df_all['f_left_norm']+df_all['f_left_minus_norm']
    d44=df_all['f_right_minus_norm']+df_all['f_left_minus_norm']
    denom=d11*d22*d33*d44
    pp=dd/denom
    return pp

def create_phrase_partisanship(df):
    aa=df['f_right_norm']+df['f_left_norm']
    df['rho']=df['f_right_norm']/aa
    bb=1-df['f_right_norm']
    df['f_left_norm_scaled']=df['f_right_norm']/bb
    cc=1-df['f_left_norm']
    df['f_right_norm_scaled']=df['f_left_norm']/cc
    df['pi']=df['f_right_norm']*df['rho']
    df['pi_scaled']=(df['pi']/(1-df['f_right_norm']))+((1-df['pi'])/(1-df['f_left_norm']))

    df['gram_partisanship']= 0.5 * (1 - df['pi_scaled'] + 
                           (df['f_right_norm_scaled'] +  df['f_left_norm_scaled']) * df['rho'])
    return df

def create_polarization_correlation(df):
    
    aa=df['f_left_norm']*-1
    bb= df['f_right_norm']*1
    df['beta_polarization']=aa+bb

    return df

def apply_polarization_model(declaracoes2):
    dfg3=create_frequency_table_grams(n_gram=3, indf=declaracoes2)
    dfg3['pearson_quad']=calculate_pearson(dfg3)
    trigrams_table=dfg3[dfg3.pearson_quad>0]
    trigrams_table=create_phrase_partisanship(trigrams_table)
    trigrams_table=create_polarization_correlation(trigrams_table)
    final_df = trigrams_table.sort_values(by=['gram_partisanship'], ascending=False)
    return final_df