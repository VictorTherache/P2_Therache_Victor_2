try:
    import requests
    import sys
    from bs4 import BeautifulSoup
    from scrap_one_book import get_title, put_book_info_in_csv, get_book_info, download_book_image
    import csv
    import os.path
    from os import path
except ModuleNotFoundError as e:
    print("\nCertains modules sont manquants, veuillez taper 'pip install -r"
          " requirements.txt' pour les installer\n")
    raise SystemExit(e)


def split_url(url): # Change the url so it can be iterated
    """
    Return a url that can be used for iteration
    """
    url = url.split('index') 
    url = url[0] + 'page-1.html'
    url = url.split('page-')
    url = f"{url[0]}page-1.html"
    return url


def get_nbr_of_pages(url):
    """
    Return the number of a category's pages
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    nbr = soup.find('ul', {'class': 'pager'})
    if(nbr):
        nbr = nbr.find('li', {'class': 'current'})
        nbr = int(nbr.text.strip()[-1:])  # Keep the integer in the string
        return nbr


def get_category(url):
    """
    Return an array of all categories, used to check if a file already exists
    """
    category_array = []
    response = requests.get(url)
    if(response.ok):
        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.find('ul', {'class': 'nav-list'})
        links = links.find_all('a')
        for link in links:
            category_array.append(link.text.strip())
        return category_array


def get_books_url(url):
    """
    Return an array of all books url of a category
    """
    url_array = []
    nbr_pages = get_nbr_of_pages(url) 
    if(nbr_pages == None):
        nbr_pages = 1
    formatted_url = split_url(url)
    formatted_url = formatted_url.split('page')
    for i in range(1, int(nbr_pages) + 1):
        if nbr_pages != 1:
            join_url = formatted_url[0] + 'page-' + str(i) + '.html'
        else: 
            join_url = url
        response = requests.get(join_url)
        if(response.ok):
          soup = BeautifulSoup(response.text, 'lxml')
          table = soup.find('ol', {'class': 'row'})
          rows = table.find_all('a', href=True)
          for row in rows:
              if row.text:
                  url_array.append(
                      "http://books.toscrape.com/catalogue/" 
                       + row['href'].strip('../'))
    return url_array


def put_books_info_in_csv(url):
    """
    Put all the books informations of a category in a csv
    """
    books_urls = get_books_url(url)
    for url in books_urls:
        put_book_info_in_csv(url)
        download_book_image(url)


if __name__ == '__main__':
    try:
        url = sys.argv[1]
        category_array = get_category(url)
        for category in category_array:
            if os.path.exists(f"{category}.csv"):
                os.remove(f"{category}.csv")
        put_books_info_in_csv(url)
        print('\n**** Success ****\n')
    except IndexError:
        print('Veuillez entrer un url en tant que paramètre')
    except requests.exceptions.RequestException as e: 
        print('\nErreur de connection, veuillez vérifier votre connection internet ou rentrer un URL valide\n')
        raise SystemExit(e)
    except (AttributeError, TypeError) as e:
        print("Veuillez rentrer une url valide, ex : 'https://books.toscrape.com/catalogue/category/books/romance_8/page-1.html'")
    except (KeyboardInterrupt) as e:
        print('Programme arreté')


    