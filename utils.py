import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client.json"

import requests
import json

from pymongo import MongoClient
client=MongoClient("mongodb+srv://hitesh:lioneaters@cluster0-ktlow.mongodb.net/test?retryWrites=true&w=majority")

db=client.get_database('user_preferences')


import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "project-1-cd204"

MY_API_KEY="AIzaSyBQ27fB6HLMOlQLeNqsl2GQh_yIH1T8igs"

from gnewsclient import gnewsclient

client = gnewsclient.NewsClient(max_results=3)

def get_news(parameters):
    client.topic = parameters.get('news_type')
    client.language = parameters.get('language')
    client.location = parameters.get('geo-country','')
    return client.get_news()
    #return "1"

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg,session_id):
    response=detect_intent_from_text(msg,session_id)
    print(response.intent.display_name)
    if response.intent.display_name=="get_news":
        news = get_news(dict(response.parameters))
        news_str = 'Here is your news:'
        for row in news:
            news_str += "\n\n{}\n\n{}\n\n".format(row['title'],
                row['link'])
        return news_str
    elif response.intent.display_name=="get_places_info":
        url=f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={msg}&inputtype=textquery&fields=photos,price_level,rating,formatted_address,name,rating,opening_hours,geometry&key={MY_API_KEY}"
        respon=requests.get(url)
        text=json.loads(respon.text)
        print(text["status"])
        print(session_id)
        if text["status"]!="OK":
            return "some error occured"+text["status"]
        temp=text["candidates"][0]
        res="formatted_address :{}\n\n\n".format(temp["formatted_address"])
        res+="geometry:{}\n\n\n".format(temp["geometry"])
        records=db.preferences
        name=temp["name"]
        new_preference={
            "session_id":session_id,
            "name":name
        }
        records.find_one_and_delete({"session_id":session_id,"name":name})
        records.insert_one(new_preference)
        return res
    elif response.intent.display_name=="get_place_photos":
        url=f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={msg}&inputtype=textquery&fields=photos,price_level,rating,formatted_address,name,rating,opening_hours,geometry&key={MY_API_KEY}"
        respon=requests.get(url)
        text=json.loads(respon.text)
        if text["status"]!="OK":
            return "some error occured "+text["status"]
        temp=text["candidates"][0]
        temp2=temp["photos"]
        photo_reference=temp2[0]["photo_reference"]
        photo_url=f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&sensor=false&photoreference={photo_reference}&key={MY_API_KEY}"
        li=[]
        li.append(photo_url)
        return li
    elif response.intent.display_name=="get_preferences":
        records=db.preferences
        num=records.count_documents({"session_id":session_id})
        if num==0:
            return "no preferences found"
        else:
            c=list(records.find({"session_id":session_id}))
            ans=""
            for i in c:
                ans+=i["name"]+"\n"
            return ans
    else:
        return response.fulfillment_text




#response = detect_intent_from_text("show sports news in english", 12314)