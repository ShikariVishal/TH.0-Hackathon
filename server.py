import requests
import ipfshttpclient
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from translate import Translator

def translate(language,text):
    translator= Translator(to_lang=language)
    translation = translator.translate(text)
    return (translation)

app = flask.Flask(__name__)

app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

# maps md5hash to its englishLanguage
MD5Hashes = {}
structuredHashes = {}

def addNewHash(_englishHash, _language, _languageHash, _MD5Hash):
    MD5Hashes[_MD5Hash] = _englishHash
    structuredHashes[(_englishHash, _language)] = _languageHash

def checkMD5Hashes(_MD5Hash):
    if _MD5Hash in MD5Hashes.keys():
        return MD5Hashes[_MD5Hash]
    else:
        return 'Not Present'

def getLanguageHash(_englishHash, _language):
    if (_englishHash, _language) in structuredHashes.keys():
        return structuredHashes[(_englishHash, _language)]
    else:
        return 'Not Present'



def predict(input_text, language):
    # return "nicv"
    dest_lang =  language
    print(language)
    try:
        translator = Translator()
        translated_text = translator.translate(input_text, dest=dest_lang).text
        return translated_text
    except Exception as e:
        print("Error ==================================", e)

def downloadFromIPFS(hash):
    client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    return client.cat(hash)

def uploadToIPFS(data):
    file = {
        'file': data
    }
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=file)
    responseJson = response.json()
    hash = responseJson['Hash']
    return (hash)


@app.route('/MD5hash', methods=['POST'])
@cross_origin()
def home():
    # receiving json format

    # {
    #     'md5Hash': '',
    #     'requiredLanguage': ''
    # }
    content = request.get_json()
    englishHash = checkMD5Hashes(content['md5Hash'])
    
    if(englishHash == 'Not Present') :
        response = flask.jsonify({
            'ipfsHash' : '',
            'message': 'noHash'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    finalHash = getLanguageHash(englishHash, content['requiredLanguage'])
    if(finalHash == 'Not Present'):

        # Download english content
        client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
        englishData = client.cat(englishHash)

        # convert to required language
        # predictedData = predict(englishData, content['requiredLanguage'])
        predictedData = translate(content['requiredLanguage'], englishData)

        # upload to IPFS
        file = {
            'file': predictedData
        }
        response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=file)
        responseJson = response.json()
        hash = responseJson['Hash']

        # update in dictionary
        addNewHash(englishHash, content['requiredLanguage'], hash, content['md5Hash'])

        # send back data
        response = flask.jsonify({
            'ipfsHash' : hash,
            'message': 'finalHash'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    response = flask.jsonify({
        'ipfsHash' : finalHash,
        'message': 'finalHash'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

    # return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/newHash', methods=['POST'])
@cross_origin()
def newHash():
    print('in newHash')
    # receiving json format

    # {
    #     'IPFSHash': '',
    #     'requiredLanguage': '',
    #     'md5Hash': ''
    # }
    content = request.get_json()
    print(content)
    # download the data from ipfs
    client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    data = client.cat(content['IPFSHash'])

    # convert to english and required language
    lang = 'en' # detect(data)
    englishLang = ''
    englishHash = ''
    if lang == 'en':
        englishLang = data
        englishHash = content['IPFSHash']
    else:
        englishLang = predict(data, 'en')
    print("EnglishData = ", englishLang)
    data = data.decode("utf-8")
    requiredLang = translate(content['requiredLanguage'], data)
    print("required Lang = ", requiredLang)

    # upload english and required language to IPFS
    if(lang != 'en'):
        file = {
            'file': englishLang
        }
        response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=file)
        responseJson = response.json()
        englishHash = responseJson['Hash']
    
    file = {
        'file': requiredLang
    }
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=file)
    responseJson = response.json()
    requiredHash = responseJson['Hash']

    # update in dictionary
    addNewHash(englishHash, content['requiredLanguage'], requiredHash, content['md5Hash'])

    print(englishHash)
    print(structuredHashes[(englishHash, content['requiredLanguage'])])
    print(checkMD5Hashes(content['md5Hash']))

    # send back data
    response = flask.jsonify({
        'ipfsHash' : requiredHash,
        'message': 'finalHash'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


app.run()

