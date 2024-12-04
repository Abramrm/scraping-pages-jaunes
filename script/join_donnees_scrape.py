import pandas as pd
from AdresseParser import AdresseParser
adr_parser = AdresseParser()
dtype_entreprise = {'Nom':'str', 'Adresse':'str', 'TelephoneAnnonceur':'str', 'TelephoneContact':'str', 'ID_PJ':'str', 'Note':'str', 'Nombre_Avis':'str'}
dtype_details = {'Id':'str', 'Activite':'str','SIREN':'str','FormeJuridique':'str','DateCrea':'str','EffectifEntreprise':'str','SIRET':'str','NAF':'str', 'EffectifEtab':'str', 'TypoEtablissement':'str'}
df_entreprises = pd.read_csv('df_contenu_N_pages_correze.csv', sep=";", encoding="utf-8", dtype=dtype_entreprise)
df_entreprises['Id'] = df_entreprises['ID_PJ'].astype('string').str[4:]
del df_entreprises[df_entreprises.columns[0]]
df_detail = pd.read_csv('detail_correze.csv', sep=";", encoding="utf-8", dtype=dtype_details)
df_detail['Id'] = df_detail['Id'].astype('string')
del df_detail[df_detail.columns[0]]
df_entreprises["Numero"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['numero'])
df_entreprises["NomVoie"] = df_entreprises['Adresse'].apply(lambda x: '{} {}'.format(adr_parser.parse(x)['rue']['type'], adr_parser.parse(x)['rue']['nom']).strip())
df_entreprises["CP"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['code_postal'])
df_entreprises["Ville"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['ville']['nom'])
result = df_entreprises.merge(df_detail, on="Id", how='left')
result['Web'] = "https://www.pagesjaunes.fr/pros/" + result["Id"]
result['Nombre_Avis'] = result['Nombre_Avis'].str.replace('(', '').str.replace(')', '').str.replace('avis', '').str.strip()

url_naf = 'https://www.insee.fr/fr/statistiques/fichier/8181066/Correspondances%20NAFrev2-NAF%202025%20-%20Table%20quasi-definitive%20-%20octobre%202024.xlsx'
df_naf = pd.read_excel(url_naf, engine='openpyxl', header=1, usecols="A:B", names=['NAF', 'NAF_Detail'])
df_naf['NAF'] = df_naf['NAF'].str.replace('.', '')
df_naf = df_naf.drop_duplicates()
result = result.merge(df_naf, on="NAF", how='left')

url_formejur = r'https://www.insee.fr/fr/statistiques/fichier/2028129/cj_septembre_2022.xls'
df_fj = pd.read_excel(url_formejur, engine='xlrd', header=3, usecols="A:B", names=['FormeJuridique', 'FormeJuridique_Detail'], sheet_name='Niveau III', dtype={'FormeJuridique':'str', 'FormeJuridique_Detail':'str'})

result = result.merge(df_fj, on="FormeJuridique", how='left')

result = result[['Nom', 'Adresse', 'TelephoneAnnonceur', 'ID_PJ', 'SIREN', 'DateCrea', 'EffectifEntreprise', 'SIRET', 'EffectifEtab', 'TypoEtablissement', 'NAF', 'NAF_Detail', 'FormeJuridique', 'FormeJuridique_Detail', 'Web']]
result = result.drop_duplicates()
#result.to_csv("data_correze.csv", sep=";", encoding="utf-8")
result.to_csv("data_correze.csv", sep=";", encoding='mbcs')
