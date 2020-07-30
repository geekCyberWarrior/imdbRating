import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import selenium

url = 'https://www.imdb.com/chart/top/'
source_code = requests.get(url).text
soup = BeautifulSoup(source_code,'lxml')
rank = 0

def get_movie_list():
    movie_list = soup.find('tbody',class_='lister-list')
    movie_names = []
    for movie in movie_list.find_all('tr'):
        movie_name = movie.find('td',class_='titleColumn').a.text
        movie_names.append(movie_name)
    return movie_names

def get_movie_json(movie_name):
    global rank
    result = {'movieName' : movie_name}
    try:
        browser = webdriver.Firefox()
        browser.get(url)
        movie_name = browser.find_element_by_link_text(movie_name)
        mov_url = movie_name.get_attribute('href')
        source_code = requests.get(mov_url).text
    
    except selenium.common.exceptions.NoSuchElementException:
        browser.close()
        source_code = requests.get(url).text
        soup = BeautifulSoup(source_code,'lxml')
        source_code = soup.find_all('td',class_ = 'titleColumn')[rank].a['href']
        source_code = 'https://www.imdb.com' + source_code
        source_code = requests.get(source_code).text
        soup = BeautifulSoup(source_code,'lxml')
        branch = soup.find('div',{'id' : 'titleDetails'})
        movie_name = branch.find_all('div',class_ = 'txt-block')[3].text.split(': ')[1].split('See more')[0].strip()
        result = {'movieName' : movie_name}
        browser = webdriver.Firefox()
        browser.get(source_code)
        movie_name = browser.find_element_by_link_text(movie_name)

    except Exception:
        print(movie_name)
        return None
    finally:
        browser.close()
        soup = BeautifulSoup(source_code,'lxml')

        yearReleased = soup.find('span',{'id' : 'titleYear'}).a.text
        result['yearReleased'] = yearReleased
        movieRating = soup.find('div',class_ = 'imdbRating').div.strong.span.text
        result['Rating'] = movieRating
        duration = soup.find('div',class_ = 'subtext').time.text.strip()
        result['Duration'] = duration
        genres = []
        for genre in soup.find('div',class_ = 'subtext').find_all('a')[:-1]:
            genres.append(genre.text)
        result['Genres'] = genres
        movie_description = soup.find('div',class_ = 'summary_text').text.strip()
        result['Description'] = movie_description
        directors = []
        for director in soup.find('div',class_ = 'credit_summary_item').find_all('a'):
            directors.append(director.text)
        writers = []
        for writer in soup.find_all('div',class_ = 'credit_summary_item')[1].find_all('a'):
            writers.append(writer.text)
        result['Writers'] = writers
        stars = []
        for star in soup.find_all('div',class_ = 'credit_summary_item')[2].find_all('a')[:-1]:
            stars.append(star.text)
        result['Stars'] = stars
        rank+=1

    return result

movies = get_movie_list()
final_data = {'movies' : []}

'''
for i in movies:
    print(i)
'''
for movie in movies[:20]:
    res = get_movie_json(movie)
    if res:
        final_data['movies'].append(get_movie_json(movie))

with open('imdb_Results.json','w') as f:
    json.dump(final_data,f,indent=4)
