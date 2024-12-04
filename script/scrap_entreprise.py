from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import random
import datetime
from statistics import mean

def get_detail(entreprise_id, soup):
    contenu_page = {}
    contenu_page["Id"] = entreprise_id
    # ACTIVITE
    if soup.find('div', class_='zone-produits-presta-services-marques') != None:
        activite = soup.find('div', class_='zone-produits-presta-services-marques')
        activite_value = activite.get_text(separator='\n', strip=True)
        contenu_page["Activite"] = activite_value
    else:
        contenu_page["Activite"] = ""
    # INSEE
    ## Infos entreprise
    if soup.find('dl', class_='info-entreprise') != None:
        info_entreprise = soup.find('dl', class_='info-entreprise')
        ### SIREN
        if info_entreprise.find('dt', string="SIREN") != None:
            siren_dt = info_entreprise.find('dt', string="SIREN")
            siren_value = siren_dt.find_next('dd').strong.get_text(strip=True)
            contenu_page["SIREN"] = siren_value
        else:
            contenu_page["SIREN"] = ""
        ### Forme juridique
        if info_entreprise.find('dt', string="Forme juridique") != None:
            forme_jur = info_entreprise.find('dt', string="Forme juridique")
            fj_value = forme_jur.find_next('dd').strong.get_text(strip=True)
            contenu_page["FormeJuridique"] = fj_value
        else:
            contenu_page["FormeJuridique"] = ""
        ### Date creation
        if info_entreprise.find('dt', string="Création d'entreprise") != None:
            crea = info_entreprise.find('dt', string="Création d'entreprise")
            crea_value = crea.find_next('dd').strong.get_text(strip=True)
            contenu_page["DateCrea"] = crea_value
        else:
            contenu_page["DateCrea"] = ""
        ### Effectif de l'entreprise
        if info_entreprise.find('dt', string="Effectif de l'entreprise") != None:
            eff_ent = info_entreprise.find('dt', string="Effectif de l'entreprise")
            eff_ent_value = eff_ent.find_next('dd').strong.get_text(strip=True)
            contenu_page["EffectifEntreprise"] = eff_ent_value
        else:
            contenu_page["EffectifEntreprise"] = ""

    ## Infos
    if soup.find('dl', class_='info-etablissement') != None:
        info_etab = soup.find('dl', class_='info-etablissement')
        ### SIRET
        if info_etab.find('dt', string="SIRET") != None:
            siret_dt = info_etab.find('dt', string="SIRET")
            siret_value = siret_dt.find_next('dd').strong.get_text(strip=True)
            contenu_page["SIRET"] = siret_value
        else:
            contenu_page["SIRET"] = ""
        ### Code NAF
        if info_etab.find('dt', string="Code NAF") != None:
            naf = info_etab.find('dt', string="Code NAF")
            naf_value = naf.find_next('dd').strong.get_text(strip=True)
            contenu_page["NAF"] = naf_value
        else:
            contenu_page["NAF"] = ""
        ### Effectif de l'établissement
        if info_etab.find('dt', string="Effectif de l'établissement") != None:
            eff_etab = info_etab.find('dt', string="Effectif de l'établissement")
            eff_etab_value = eff_etab.find_next('dd').strong.get_text(strip=True)
            contenu_page["EffectifEtab"] = eff_etab_value
        else:
            contenu_page["EffectifEtab"] = ""
        ### Typologie de l'établissement
        if info_etab.find('dt', string="Typologie de l'établissement") != None:
            type = info_etab.find('dt', string="Typologie de l'établissement")
            type_value = type.find_next('dd').strong.get_text(strip=True)
            contenu_page["TypoEtablissement"] = type_value
        else:
            contenu_page["TypoEtablissement"] = ""

    df_page = pd.DataFrame(contenu_page, index=[0])
    return df_page

def recover_detail(id_list):
    dr = webdriver.Chrome()
    df_contenu_total = pd.DataFrame(columns=['Id', 'Activite','SIREN','FormeJuridique','DateCrea','EffectifEntreprise','SIRET','NAF', 'EffectifEtab', 'TypoEtablissement'])
    compteur = 0
    for i in id_list:
        compteur += 1
        url = "https://www.pagesjaunes.fr/pros/" + i
        dr.get(url)
        soup = BeautifulSoup(dr.page_source, "html.parser")
        df_page = get_detail(i, soup)
        df_contenu_total = pd.concat([df_contenu_total, df_page], ignore_index=True)
        print("Avancement : {}/{}".format(compteur, len(id_list)))
        time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
    return df_contenu_total

#df = pd.read_csv('df_contenu_N_pages.csv', sep=";", encoding="utf-8")
df = pd.read_csv('df_contenu_N_pages_corros.csv', sep=";", encoding="utf-8")
df['ID'] = df['ID_PJ'].str[4:]
id_list = df['ID'].tolist()
df_page = recover_detail(id_list)
df_page.to_csv("detail_carrosiers.csv", sep=";", encoding="utf-8")