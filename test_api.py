import requests
import base64

headers={
    'Authorization': 'Bearer {}'.format('<token>')
}

def getMe():
    r = requests.get('http://127.0.0.1:8080/api/users/me', headers=headers)
    print(r.text)

def getItems():
    r = requests.get('http://127.0.0.1:8080/api/items', headers=headers)
    print(r.text)

def createItem():
    with open('map.png', 'rb') as f:
        encImage = base64.b64encode(f.read()).decode('utf-8')

    with open('d.html', 'rb') as f:
        encFile = base64.b64encode(f.read()).decode('utf-8')

    r = requests.post('http://127.0.0.1:8080/api/items/create',
                      headers=headers,
                      json={
                        'name': 'test',
                        'about': 'lalala',
                        'amount': 10000,
                        'content': 'hi',
                        'categoryName': 'services',
                        'subCategoryId': 1,
                        'image': encImage,
                        'contentFile': encFile,
                        'extension': 'html'
                    }
    )
    print(r.text)