import requests,json
from models import *
def search_books_api(query):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q={}'.format(query))
    
    items=json.loads(response.text)['items']
    
    result=[]
    
    for item in items:
        # print('#'*100)
      
        author_list=item.get('volumeInfo',{}).get('authors')
        
        authors=''
        if author_list != None:
            for i,author in enumerate(author_list):
                if i>0:
                    authors+=', '
                authors+=author
            
        category_list=item.get('volumeInfo',{}).get('categories')
        categories=''
        
        if category_list != None:
            for i,category in enumerate(category_list):
                if i>0:
                    categories+=', '
                categories+=category
                
        description=item.get('volumeInfo').get('description','No description')
        
        #description=description[:100]+'...'
            
        image_link=item.get('volumeInfo',{}).get('imageLinks',{}).get('smallThumbnail')
        
        title=item.get('volumeInfo',{}).get('title')
        id=item.get('id',None)
        # print(title,' ',authors,' ',categories)
        # print(image_link)
        # print(description)
        # print('#'*100)
        result.append(Book(id,title,authors,categories,description,image_link))
        
    return result


def get_book_details(id):
    url = 'https://www.googleapis.com/books/v1/volumes/{}'.format(id)
    # print(url)
    response = requests.get(url)
    # print('res=',response.text)
    item = json.loads(response.text)
    # print('#'*100)
    
    author_list=item.get('volumeInfo',{}).get('authors')
    
    authors=''
    if author_list != None:
        for i,author in enumerate(author_list):
            if i>0:
                authors+=', '
            authors+=author
        
    category_list=item.get('volumeInfo',{}).get('categories')
    categories=''
    
    if category_list != None:
        for i,category in enumerate(category_list):
            if i>0:
                categories+=', '
            categories+=category

    description='No description'
    if item.get('volumeInfo'):
        if item.get('volumeInfo').get('description'):
            description=item.get('volumeInfo').get('description','No description')
        
           

   
        
    image_link=item.get('volumeInfo',{}).get('imageLinks',{}).get('smallThumbnail')
    
    title=item.get('volumeInfo',{}).get('title')
    id=item.get('id')
    print(title,' ',authors,' ',categories)
    print(image_link)
    print(description)

    print('='*100)
    return Book(id,title,authors,categories,description,image_link)
    
    