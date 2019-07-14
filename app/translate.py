import json, uuid
import requests
from flask_babel import _
from app import app

def translate(text, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    headers = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [
        { 'Text' : single_text } for single_text in text  
    ]
    base_url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    query_params = '&to={}'.format(dest_language)
    endpoint_url = base_url + query_params
    r = requests.post(endpoint_url, headers=headers, json=body)
    if r.status_code != 200:
        print _('Translation API response code: '), r.status_code
        print _('The requested text to translate was: '), text
        print _('The requested translation destination language was: '), dest_language
        return _('Error: the translation service failed.')
    response_json = r.json()
    return [single_text_results['translations'][0]['text'] for single_text_results in response_json]
