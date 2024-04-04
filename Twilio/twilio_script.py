import os
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PHONE_NUMBER,API_KEY_WAPI
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
from funciones_df import request_wapi,get_forecast,create_df_info_lluvia,create_df_inf_add,send_message,get_date

# Ciudad del que enviará el estado del tiempo
query = 'Lima'
api_key = API_KEY_WAPI

input_date= get_date()
response = request_wapi(api_key,query)

datos = []

for i in tqdm(range(24),colour = 'blue'):
    datos.append(get_forecast(response,i))


df_rain = create_df_info_lluvia(datos)
df_info_ad = create_df_inf_add(datos)

# Send Message
message_id = send_message(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,input_date,df_rain,df_info_ad,query)

print('Mensaje Enviado con exito ' + message_id)
