
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import os



base_url = 'http://books.toscrape.com'
base_url_categorie ='http://books.toscrape.com/catalogue/category/books/travel_2/index.html'

element_a_exclure = ["Product Type", "Tax"]

chemin_utilisateur_image = "c:/Users/Mehdi/Desktop/Formation_Python_OC/Projet_2/images_livres"

chemin_utilisateur_livres = "C:/Users/Mehdi/Desktop/Formation_Python_OC/Projet_2/données_livres_par_catégorie/"


tous_les_produits_categorie = []

entete_produit = ['title', 'product_page_url', 'product_description', 'category', 'image_url','UPC', 'Price (excl. tax)', 'Price (incl. tax)', 'Availability', 'Number of reviews'] 

def trouver_infos(soup):
    return soup.find('div', class_='container-fluid page')

def extraire_element(element):
    if element is None:
        return "No informations"
    return element.text.strip()
    
    

def infos_liste(ul_liste):
    infos = ul_liste.findAll('li')
    return[info.text.strip() for info in infos]

def extraire_lien_image(article_div):
    image_div = article_div.find('div', class_='item active')
    lien_img = image_div.find('img')['src']
    url_img = urljoin(base_url, lien_img)
    return url_img


def extraire_detail_produit(table ,element_a_exclure, infos_produit):
    details = table.findAll('tr')

    for detail in details:
        titre_detail = detail.find('th')
        if titre_detail:
            titre = titre_detail.text.strip()
        if titre not in element_a_exclure:
            donnee_titre = detail.find('td')
            if donnee_titre:
                donnee = donnee_titre.text.strip()
                infos_produit.append(donnee)

def extraction_image(url_img, chemin_utilisateur):
    response = requests.get(url_img)
    if response.status_code == 200:
        num_image = url_img.split("/")[-1]
        chemin_dossier = chemin_utilisateur + '/' +num_image
        with open(chemin_dossier, 'wb') as f:
            f.write(response.content)
    

def ecriture_fichiers_livres(chemin_utilisateur_livres, entete_produit, tous_les_produits_categorie, categorie_livre):
    chemin_fichier = chemin_utilisateur_livres+categorie_livre+".csv"
    
    with open (chemin_fichier,'w',encoding='utf-8-sig', newline ='') as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(entete_produit)
        writer.writerows(tous_les_produits_categorie)
    

response = requests.get(base_url)
if response.status_code == 200:
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, features="html.parser")
    liste_liens_categories = []
    lien_categorie = soup.find('ul', class_='nav nav-list').find('ul').findAll('li')

    for categorie in lien_categorie:
        lien_cat = urljoin(base_url,categorie.find('a')['href'])
        liste_liens_categories.append(lien_cat)
  

    

liens_livres = []
infos_produit = []

for lien_categorie in liste_liens_categories:
    page_suivante = lien_categorie

    while page_suivante :
        response = requests.get(page_suivante)
        if response.status_code == 200:
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, features="html.parser")
            liens_livres_html = soup.find('ol' , class_= 'row').findAll('h3')
                
            for element in liens_livres_html:
                lien_livre = element.find('a')['href']
                lien = urljoin(base_url_categorie, lien_livre)
                liens_livres.append(lien)
            lien_next = soup.find('li', class_='next')
            if lien_next:
                lien_next = soup.find('li', class_='next').find('a')['href']
                lien_page_next = urljoin(lien_categorie,lien_next)
                page_suivante = lien_page_next
            else:
                break
            


        

    for lien in liens_livres:
        response = requests.get(lien)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, features="html.parser")
                
            infos_div = trouver_infos(soup)

            title_product = extraire_element(infos_div.find('div', class_= 'col-sm-6 product_main').find('h1'))

            description = extraire_element(infos_div.find('article', class_='product_page').find('p', class_ =False))

            ul_infos = infos_div.find('ul', class_ = 'breadcrumb')
            categorie_list = infos_liste(ul_infos)
            categorie_livre = categorie_list[2]

            image_url = extraire_lien_image(infos_div)

            table = soup.find('table', class_= 'table table-striped')

            infos_produit.append(title_product)
            infos_produit.append(lien)
            infos_produit.append(description)
            infos_produit.append(categorie_livre)
            infos_produit.append(image_url)

            extraire_detail_produit(table , element_a_exclure, infos_produit)
            extraction_image(image_url, chemin_utilisateur_image)
            tous_les_produits_categorie.append(infos_produit.copy())
            infos_produit.clear()
                
    liens_livres.clear()


    ecriture_fichiers_livres(chemin_utilisateur_livres, entete_produit,tous_les_produits_categorie, categorie_livre)
    tous_les_produits_categorie.clear()










