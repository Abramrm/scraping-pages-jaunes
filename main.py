from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import random
import datetime
from statistics import mean
import os
from AdresseParser import AdresseParser
from secret import WEBPAGE_PAGEJAUNE


class ScrapingPagesJaunes:

    def __init__(self):
        self.dr = webdriver.Chrome()
        self.url = WEBPAGE_PAGEJAUNE
        self.dr.get(self.url)
        self.companies_list_file = ""
        self.companies_details = ""

    @staticmethod
    def scraping_page(dr):
        soup = BeautifulSoup(dr.page_source, "html.parser")
        liste = soup.find("ul", class_="bi-list")
        elements = liste.contents
        elements_clean = []
        for i in range(len(elements)):
            if elements[i].text != "\n":
                elements_clean.append(elements[i])
        contenu_page = {}
        id = 0
        for el in elements_clean:
            id += 1
            contenu_entreprise = []
            contenu_entreprise.append(el.h3.text)  # Nom
            contenu_entreprise.append(
                el.find("a", class_="pj-lb pj-link").contents[0].get_text().replace("\\n", "").strip())  # Adresse
            if el.find("span", class_="annonceur") != None:
                contenu_entreprise.append(el.find("span", class_="annonceur").get_text())  # Telephone_annonceur
            else:
                contenu_entreprise.append("")
            if el.find("div", class_="bi-fantomas") != None:
                bi_fantomas_div = el.find('div', class_='bi-fantomas')
                span_contents = [span.get_text(strip=True) for span in bi_fantomas_div.find_all('span')]
                contenu_entreprise.append(span_contents)  # Telephone_contact
            else:
                contenu_entreprise.append("")
            contenu_entreprise.append(el.get("id"))  # identifiant pages jeunes
            if el.find("span", class_="note_moyenne") != None:
                contenu_entreprise.append(el.find("span", class_="note_moyenne").get_text())  # note
            else:
                contenu_entreprise.append("")
            if el.find("span", class_="bi-rating") != None:
                contenu_entreprise.append(el.find("span", class_="bi-rating").get_text())  # nombre avis
            else:
                contenu_entreprise.append("")
            contenu_page[str(id)] = contenu_entreprise

        df_contenu_page = pd.DataFrame.from_dict(contenu_page, orient='index',
                                                 columns=['Nom', 'Adresse', 'TelephoneAnnonceur', 'TelephoneContact',
                                                          'ID_PJ', 'Note', 'Nombre_Avis'])
        return df_contenu_page

    def next_page(self):
        button = self.dr.find_element(By.ID, u"pagination-next")
        actions = ActionChains(self.dr)
        actions.move_to_element(button)
        actions.click(button)
        actions.perform()
        self.dr.implicitly_wait(20)

    def nb_pages(self):
        soup = BeautifulSoup(self.dr.page_source, "html.parser")
        count = soup.find("span", id="SEL-compteur")
        return int(count.text.split("/", 1)[1].split()[0])

    def boucler_n_premieres_pages(self, n):
        df_contenu_total = self.scraping_page(self.dr)
        pages = self.nb_pages()
        print("Avancement : 1 / {} pages".format(pages))
        for i in range(2, n + 1):
            time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
            if i > n:
                continue
            self.next_page()
            url_suivant = self.dr.current_url
            self.dr.get(url_suivant)
            df_contenu_page = self.scraping_page(self.dr)
            df_contenu_total = pd.concat([df_contenu_total, df_contenu_page], ignore_index=True)
            print("Avancement : {} / {} pages".format(i, pages))
        print("Les dimensions finales de la table sont de : {}".format(df_contenu_total.shape))
        return df_contenu_total

    def boucler_toutes_pages(self):
        df_contenu_total = self.scraping_page(self.dr)
        pages = self.nb_pages()
        print("Avancement : 1 / {} pages // Temps restant estimé : {}".format(pages, str(datetime.timedelta(
            seconds=pages * mean([5, 8])))))
        for i in range(2, pages + 1):
            time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
            if i > pages:
                continue
            self.next_page()
            url_suivant = self.dr.current_url
            self.dr.get(url_suivant)
            df_contenu_page = self.scraping_page(self.dr)
            df_contenu_total = pd.concat([df_contenu_total, df_contenu_page], ignore_index=True)
            print("Avancement : {} / {} pages // Temps restant estimé : {}".format(i, pages, str(datetime.timedelta(
                seconds=(pages - i) * mean([5, 8])))))
        print("Les dimensions finales de la table sont de : {}".format(df_contenu_total.shape))
        return df_contenu_total

    @staticmethod
    def create_output_folder():
        folder_path = "output/"
        if not os.path.exists(folder_path):
            # If it doesn't exist, create the folder
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created.")
        else:
            print(f"Folder '{folder_path}' already exists.")

    def save_list_n_premieres_companies(self, n):
        df = self.boucler_n_premieres_pages(n)
        self.create_output_folder()
        self.companies_list_file = "liste_{}_premieres_entreprises.csv".format(n)
        df.to_csv("output/{}".format(self.companies_list_file), sep=";", encoding="utf-8")

    def save_list_complete_companies(self):
        df = self.boucler_toutes_pages()
        self.create_output_folder()
        self.companies_list_file = "output/liste_entreprises.csv"
        df.to_csv("output/{}".format(self.companies_list_file), sep=";", encoding="utf-8")

    @staticmethod
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

    def recover_details(self):
        df = pd.read_csv("output/{}".format(self.companies_list_file), sep=";", encoding="utf-8")
        df['ID'] = df['ID_PJ'].str[4:]
        id_list = df['ID'].tolist()
        dr = webdriver.Chrome()
        df_contenu_total = pd.DataFrame(
            columns=['Id', 'Activite', 'SIREN', 'FormeJuridique', 'DateCrea', 'EffectifEntreprise', 'SIRET', 'NAF',
                     'EffectifEtab', 'TypoEtablissement'])
        compteur = 0
        for i in id_list:
            compteur += 1
            url = "https://www.pagesjaunes.fr/pros/" + i
            dr.get(url)
            soup = BeautifulSoup(dr.page_source, "html.parser")
            df_page = self.get_detail(i, soup)
            df_contenu_total = pd.concat([df_contenu_total, df_page], ignore_index=True)
            print("Avancement : {}/{}".format(compteur, len(id_list)))
            time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
        return df_contenu_total

    def save_details(self):
        df_page = self.recover_details()
        self.companies_details = "detailed_file.csv"
        df_page.to_csv("output/{}".format(self.companies_details), sep=";", encoding="utf-8")

    def join_informations(self):
        adr_parser = AdresseParser()
        dtype_entreprise = {'Nom': 'str', 'Adresse': 'str', 'TelephoneAnnonceur': 'str', 'TelephoneContact': 'str',
                            'ID_PJ': 'str', 'Note': 'str', 'Nombre_Avis': 'str'}
        dtype_details = {'Id': 'str', 'Activite': 'str', 'SIREN': 'str', 'FormeJuridique': 'str', 'DateCrea': 'str',
                         'EffectifEntreprise': 'str', 'SIRET': 'str', 'NAF': 'str', 'EffectifEtab': 'str',
                         'TypoEtablissement': 'str'}
        df_entreprises = pd.read_csv("output/{}".format(self.companies_list_file), sep=";", encoding="utf-8",
                                     dtype=dtype_entreprise)
        df_entreprises['Id'] = df_entreprises['ID_PJ'].astype('string').str[4:]
        del df_entreprises[df_entreprises.columns[0]]
        df_detail = pd.read_csv("output/{}".format(self.companies_details), sep=";", encoding="utf-8", dtype=dtype_details)
        df_detail['Id'] = df_detail['Id'].astype('string')
        del df_detail[df_detail.columns[0]]
        # df_entreprises["Numero"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['numero'])
        # df_entreprises["NomVoie"] = df_entreprises['Adresse'].apply(
        #     lambda x: '{} {}'.format(adr_parser.parse(x)['rue']['type'], adr_parser.parse(x)['rue']['nom']).strip())
        # df_entreprises["CP"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['code_postal'])
        # df_entreprises["Ville"] = df_entreprises['Adresse'].apply(lambda x: adr_parser.parse(x)['ville']['nom'])
        result = df_entreprises.merge(df_detail, on="Id", how='left')
        result['Web'] = "https://www.pagesjaunes.fr/pros/" + result["Id"]
        result['Nombre_Avis'] = result['Nombre_Avis'].str.replace('(', '').str.replace(')', '').str.replace('avis',
                                                                                                            '').str.strip()

        url_naf = 'https://www.insee.fr/fr/statistiques/fichier/8181066/Correspondances%20NAFrev2-NAF%202025%20-%20Table%20quasi-definitive%20-%20octobre%202024.xlsx'
        df_naf = pd.read_excel(url_naf, engine='openpyxl', header=1, usecols="A:B", names=['NAF', 'NAF_Detail'])
        df_naf['NAF'] = df_naf['NAF'].str.replace('.', '')
        df_naf = df_naf.drop_duplicates()
        result = result.merge(df_naf, on="NAF", how='left')

        url_formejur = r'https://www.insee.fr/fr/statistiques/fichier/2028129/cj_septembre_2022.xls'
        df_fj = pd.read_excel(url_formejur, engine='xlrd', header=3, usecols="A:B",
                              names=['FormeJuridique', 'FormeJuridique_Detail'], sheet_name='Niveau III',
                              dtype={'FormeJuridique': 'str', 'FormeJuridique_Detail': 'str'})

        result = result.merge(df_fj, on="FormeJuridique", how='left')
        result = result[
            ['Nom', 'Adresse', 'TelephoneAnnonceur', 'ID_PJ', 'SIREN', 'DateCrea', 'EffectifEntreprise', 'SIRET',
             'EffectifEtab', 'TypoEtablissement', 'NAF', 'NAF_Detail', 'FormeJuridique', 'FormeJuridique_Detail',
             'Web']]
        result = result.drop_duplicates()
        return result

    def save_completed_file(self):
        df = self.join_informations()
        df.to_csv("output/complete_file.csv", sep=";", encoding='mbcs')


if __name__ == "__main__":
    print("##### DEBUT SCRAPING #####")
    scrap = ScrapingPagesJaunes()
    scrap.save_list_n_premieres_companies(1)
    #scrap.save_list_complete_companies()
    scrap.save_details()
    scrap.save_completed_file()
    print("##### FIN SCRAPING #####")

# if __name__ == "__main__":
#     scrap = ScrapingPagesJaunes()
#     scrap.companies_details = "detailed_file.csv"
#     scrap.companies_list_file = "liste_1_premieres_entreprises.csv"
#     scrap.join_informations()
