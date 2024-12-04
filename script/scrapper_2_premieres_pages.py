from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import random
import datetime
from statistics import mean

class ScrapingPagesJaunes():
# Etape 1 : Se rendre sur l'url
dr = webdriver.Chrome()
url = WEBPAGE_PAGEJAUNE
dr.get(url)

dr.implicitly_wait(20)

# Etape 2 : Fermer la pop-up d'arrivee
button_accept = dr.find_element(By.ID, u"didomi-notice-agree-button")
actions_accept = ActionChains(dr)
actions_accept.move_to_element(button_accept)
actions_accept.click(button_accept)
actions_accept.perform()

dr.implicitly_wait(20)

# Etape 3 : Boucler sur les pages
## Etape 3.1 : Scrapper le contenu de la page
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
                                             columns=['Nom', 'Adresse', 'TelephoneAnnonceur', 'TelephoneContact', 'ID_PJ', 'Note', 'Nombre_Avis'])
    return df_contenu_page

## Etape 3.2: Passer a la page suivante
def next_page(dr):
    button = dr.find_element(By.ID, u"pagination-next")
    actions = ActionChains(dr)
    actions.move_to_element(button)
    actions.click(button)
    actions.perform()
    dr.implicitly_wait(20)

def nb_pages(dr):
    soup = BeautifulSoup(dr.page_source, "html.parser")
    count = soup.find("span", id="SEL-compteur")
    return int(count.text.split("/",1)[1].split()[0])

def boucler_N_premieres_pages(dr , n):
    dr.get(url)
    df_contenu_total = scraping_page(dr)
    pages = nb_pages(dr)
    print("Avancement : 1 / {} pages".format(pages))
    for i in range(2,n+1):
        time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
        if i > n:
            continue
        next_page(dr)
        url_suivant = dr.current_url
        dr.get(url_suivant)
        df_contenu_page = scraping_page(dr)
        df_contenu_total = pd.concat([df_contenu_total, df_contenu_page], ignore_index=True)
        print("Avancement : {} / {} pages".format(i, pages))
    return df_contenu_total

def boucler_toutes_pages(dr):
    dr.get(url)
    df_contenu_total = scraping_page(dr)
    pages = nb_pages(dr)
    print("Avancement : 1 / {} pages // Temps restant estime : {}".format(pages, str(datetime.timedelta(seconds=pages*mean([5, 8])))))
    for i in range(2,pages+1):
        time.sleep(random.uniform(5, 8))  # Délai aléatoire entre 10 et 30 secondes
        if i > pages:
            continue
        next_page(dr)
        url_suivant = dr.current_url
        dr.get(url_suivant)
        df_contenu_page = scraping_page(dr)
        df_contenu_total = pd.concat([df_contenu_total, df_contenu_page], ignore_index=True)
        print("Avancement : {} / {} pages // Temps restant estime : {}".format(i, pages, str(datetime.timedelta(seconds=(pages-i)*mean([5, 8])))))
    return df_contenu_total

# Etape finale : scrapper les N premieres pages
#df_contenu_N_pages = boucler_N_premieres_pages(dr, 2)
boucler_toutes_pages = boucler_toutes_pages(dr)
boucler_toutes_pages.to_csv("/output/liste_entreprises.csv", sep=";", encoding="utf-8")