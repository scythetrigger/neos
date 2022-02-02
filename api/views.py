from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
import json

# csrf exemption required for external requests since Django requires csrf tokens
@csrf_exempt 

# create views here
def api(request):
    
    # validate request method
    if request.method == 'POST':
        jsonRequest = request.POST
        
    else:
        response = {'Error': 'POST is the only supported HTTP method.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    
    # validate request data
    if 'modFile' not in jsonRequest:
        response = {'Error': 'A .mod file is required.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    else:
        modFile = jsonRequest['modFile']
        
    if 'datFile' not in jsonRequest:
        response = {'Error': 'A .dat file is required.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    else:
        datFile = jsonRequest['datFile']
    
    if 'category' not in jsonRequest:
        response = {'Error': 'No problem category specified.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    else:
        category = jsonRequest['category']
    
    if 'solver' not in jsonRequest:
        response = {'Error': 'No problem solver specified.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    else:
        solver = jsonRequest['solver']
    
    if 'username' not in jsonRequest:
        username = 'neosAPI'
    else:
        username = jsonRequest['username']
        
    if 'password' not in jsonRequest:
        password = 'neosAPI'
    else:
        password = jsonRequest['password']
        
    if 'email' not in jsonRequest:
        email = 'neosAPI@domain.com'
    else:
        email = jsonRequest['email']
    
    
    
    # set runfile
    runFile = open('static/master.run', 'r').read()
        
    # initialize connection to neos
    sesh = requests.Session()
    url = 'https://auth.neos-server.org/public/api/login'
    payload = {
        'username': username,
        'password': password
        }
    response = sesh.post(url, data = payload)
    
    # send job to neos
    url = 'https://neos-server.org/neos/cgi-bin/nph-neos-solver.cgi'
    payload = {
        
        'field.1': modFile,
        'field.2': datFile,
        'field.3': runFile,
        'field.4': '',
        	  
        'email': email,
        'auto-fill': 'yes',
        'category': category,
        'solver': solver,
        'inputMethod': 'AMPL'
        
        }
    response = sesh.post(url, payload)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    try:
        tag = soup.find_all('meta')[1]
    except:
        response = {'Error': 'URL for solution not found, make sure category and solver are appropriate.'}
        jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
        return HttpResponse(jsonResponse, content_type = 'text/json')
    
    # retrieve results from NEOS
    url = tag['content'].split('URL=')[1]
    response = sesh.get(url)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    neosResults = soup.find('pre').text
    lines = neosResults.split('\n')
    
    # parse AMPL
    variables = {}
    data = lines[lines.index('---Start Variables---') + 1:lines.index('---End Variables---')]
    for datum in data:
        datum = datum.strip()
        name, value = datum.split('|')
        crumbs = name.split('[')
        name = crumbs[0]
        index = '[' + crumbs[1]
        if name not in variables.keys():
            variables[name] = {}
        variables[name][index] = float(value)
         
    objectives = {}
    data = lines[lines.index('---Start Objectives---') + 1:lines.index('---End Objectives---')]
    for datum in data:
        datum = datum.strip()
        name, value = datum.split('|')
        objectives[name] = float(value)
    
    response = {'variables': variables, 'objectives': objectives}
    jsonResponse = json.dumps(response, indent = 4, separators=(',', ':'))
    return HttpResponse(jsonResponse, content_type = 'text/json')













