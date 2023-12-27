import openai
import os
from googletrans import Translator
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
import json
import sys
sys.path.append('..') 
from document_ocr import extract_text
load_dotenv()

deed = Blueprint('deed', __name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"

translator = Translator()


deployment_name = os.getenv("DEPLOYMENT2")

def is_english(text):
    return all(ord(char) < 128 for char in text)

def translate_ocr(extracted_text,lang):
    
#     prompt = f"""This is the land ownership document ROR;'s data. The given text is in '{lang}' language, translate it into english : {extracted_text}. If any value is not in roman script then tranliterate it from given language to roman script in english. Analyze the data. Then from the translated text extract only the below fields in english and answer in key:value pair format (IN JSON FORMAT) for example 
#     "name of the land owner" : "Dev seth",
#     "name of his/her mother/father/husband" : "some value"
#     the fields are:
#     - type of land portion (survey number/block number)
#     - plot number (in case of block)
#     - area
#     - name of the land owner
#     - name of his/her mother/father/husband 
#     - residential address
#     - each landowner's share
#     - Encumbrance/Charges
#     - Remarks (usually in the last colummn)
   
#    """
    prompt = f"""this data is from deed document (land ownership related document): {extracted_text}. Analyze the data Then from the text extract appropriate values for  following fields in english and answer in key:value pair format for eg.(key1:value1\nkey2:value2)  *****************IN JSON FORMAT***********:

    - First Party Details: name of his/her mother/father/husband and residential address.
    - Second Party Details: name of his/her mother/father/husband and residential address.
    - Property Address
    - Property Area
    - Boundaries
    - Registeration Number
    - Registration Date
    - Registar Office Details

    If any word in {lang} language please translate or transliterate it into english.
    
    Plese skip the key if it does not have any value.
    """


    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.2,
        messages=[{ "role": "user", "content": prompt}],
        max_tokens=500
      )
    answer=completion.choices[0].message.content
    return answer

def final_call(res,lang):
    
    prompt = f"""The given data is in {lang} language. Please transliterate this data into english and give json format:

    {res}

    """
  


    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.1,
        messages=[{ "role": "user", "content": prompt}],
        max_tokens=500
      )
    answer=completion.choices[0].message.content
    return answer

@deed.route('/api/deed_upload', methods=["POST"])
def ror_ocr():
    file = request.files["file"]
    lang = request.form['lang']

    print("lang = ",lang)
    file_name = file.filename
    
    extracted_text=extract_text(file,file_name,lang)
    print("Extracted Text: ",extracted_text, "length: ",len(extracted_text))
    if len(extracted_text) > 14000:
        # Split the text into two parts
        half_length = len(extracted_text) // 2
        first_half = extracted_text[:half_length]
        second_half = extracted_text[half_length:]

        # Get responses for each half
        response1 = translate_ocr(first_half, lang)
        response2 = translate_ocr(second_half, lang)

        # Combine the responses into a single JSON object
        data1 = json.loads(response1)
        data2 = json.loads(response2)

        combined_data = {**data1, **data2}  # Merge the dictionaries

        return json.dumps(combined_data)
    # translated_text = translator.translate(extracted_text, dest='en')
    response=translate_ocr(extracted_text,lang)
    print(response)
    eng_res = is_english(response)
    if not eng_res:
        print(eng_res)
        response = final_call(response,lang)
        print(response)
    try:
        json_data = json.loads(response)
        return json_data
    except :
        return ("Invalid output format")
  
   
   

