#utilities_parlamient
import pandas as pd

def read_pre_text(file_name):

    declaracoes2 = pd.read_csv(file_name) #"speech_selected.csv"
    declaracoes2["no_punct"] = declaracoes2["speech"].str.replace('[^\w\s]','')
    declaracoes2["no_punct"] = declaracoes2["no_punct"].str.lower()
    declaracoes2=declaracoes2[~declaracoes2.no_punct.isna()]
    return declaracoes2

def load_deputies_names(file_name):
    deputies=pd.read_csv(file_name)#'deputies_2015_now.csv'
    names_deputies= deputies['nome'].str.lower().values
    parties_= deputies['partido'].str.lower().values
    return names_deputies, parties_

def load_data_legis(file_name):
    dates_df=pd.read_csv(file_name) #'datas_leg.csv'
    dates_df['number']=[int(x[-3:]) for x in dates_df['Número']]
    dates_df['number']=[int(x[-3:]) for x in dates_df['Número']]
    dates_df.columns=['Número', 'date', 'Publicação', 'N.º de Páginas', 'legislatura',
        'session', 'number']
    return dates_df
    
def clean_partiesnames(main_frame):

    main_frame.loc[main_frame["party"] == "PEN", "party"] = 'PAN'

    main_frame.loc[main_frame["party"] == "OS Verdes", "party"] = 'PEV'
    main_frame.loc[main_frame["party"] == "Os verdes", "party"] = 'PEV'
    main_frame.loc[main_frame["party"] == "Os Vedes", "party"] = 'PEV'
    main_frame.loc[main_frame["party"] == "Os Verdes", "party"] = 'PEV'
    main_frame.loc[main_frame["party"] == "s Verdes", "party"] = 'PEV'

    main_frame.loc[main_frame["party"] == "SD", "party"] = 'PSD'
    main_frame.loc[main_frame["party"] == "PD", "party"] = 'PSD'

    main_frame.loc[main_frame["party"] == "CDS", "party"] = 'CDS-PP'
    main_frame.loc[main_frame["party"] == "CSD-PP", "party"] = 'CDS-PP'
    main_frame.loc[main_frame["party"] == "CDS-P", "party"] = 'CDS-PP'

    main_frame.loc[main_frame["party"] == "PC", "party"] = 'PCP'
    main_frame.loc[main_frame["party"] == "CDU", "party"] = 'PCP'

    main_frame.loc[main_frame["party"] == "B E", "party"] = 'BE'
    main_frame.loc[main_frame["party"] == "Bloco de Esquerda", "party"] = 'BE'

    main_frame.loc[main_frame["party"] == "Partido Socialista", "party"] = 'PS' 

    partiesss=['PS', 'PSD', 'BE', 'PCP', 'CDS-PP', 'PAN', 'PEV','CH','IL','L']
    main_frame=main_frame[main_frame.party.isin(partiesss)]
    return main_frame #declarações2

def add_dates_main(df_main, df_dates):
    df_main=pd.merge(df_main,\
         df_dates[['legislatura',	'session'	,'number','date']], \
              how='left', left_on=['legislatura',	'session'	,'number'],\
                   right_on = ['legislatura',	'session'	,'number'])
    return df_main


def extract_president_names( df_main):
    presidents_secret=['idália salvador serrão','ana mesquita','nelson peralta','abel baptista','diogo leão','fernando negrão','helga correia','lina lopes','eduardo ferro rodrigues','maria da luz rosinha','duarte pacheco','rosa maria bastos albernaz','alberto martins','sandra pontedeira','jorge lacão','pedro alves', 'sandra pontedeira','emília santos','antónio carlos monteiro']


    df_main=df_main[~df_main.speaker.isin(presidents_secret)] 
    return df_main