import pandas as pd
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PHONE_NUMBER,API_KEY_WAPI
from datetime import datetime
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


# Funcion que retorna la fecha
def get_date():
    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")

    return input_date

# Función que retorna
def request_wapi(api_key,query):
    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=no&alerts=no'
    try :
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)

    return response

# Función que recorre y extrae los valores de interés del JSON - API
def get_forecast(response,i):
    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    tempe_cel = float(response['forecast']['forecastday'][0]['hour'][i]['temp_c'])
    tempe_fah=float(response['forecast']['forecastday'][0]['hour'][i]['temp_f'])
    por_humedad = float(response['forecast']['forecastday'][0]['hour'][i]['humidity']/100)
    por_nubosidad=float(response['forecast']['forecastday'][0]['hour'][i]['cloud']/100)
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    
    return fecha,hora,condicion,tempe_cel,tempe_fah,por_humedad,por_nubosidad,rain,prob_rain

# Función para crear el DF
def create_df_info_lluvia(data):

    # DF para que muestre si lloverá o no
    col = ['Fecha','Hora','Condicion','Temperatura_Cel','Temperatura_Fah','%_Humedad','%_Nubosidad','Lluvia','Prob_Lluvia']
    df_clima = pd.DataFrame(data,columns=col)
    df_clima = df_clima.sort_values(by = 'Hora',ascending = True)

    # Data cleaning
    df_clean = df_clima[(df_clima['Lluvia']==1) & (df_clima['Hora']>6) & (df_clima['Hora']<= 23)]
    df_rain = df_clean[['Hora','Condicion','Temperatura_Cel']]
    df_rain.set_index('Hora', inplace = True)
    
    return df_rain

def create_df_inf_add(data):
    # Información adicional del estado del tiempo
    col = ['Fecha','Hora','Condicion','Temperatura_Cel','Temperatura_Fah','%_Humedad','%_Nubosidad','Lluvia','Prob_Lluvia']
    df_clima = pd.DataFrame(data,columns=col)
    df_clima = df_clima.sort_values(by = 'Hora',ascending = True)

    # Obtener información
    df_info_ad = pd.DataFrame({
        '%Nubosidad': [round(df_clima['%_Nubosidad'].mean()*100, 0)],
        '%Humedad': [round(df_clima['%_Humedad'].mean()*100, 0)],
        'Temperatura': [round(df_clima['Temperatura_Cel'].mean(), 1)],
        'Condicion': [df_clima['Condicion'].mode()[0]]
    })
    df_info_ad = df_info_ad.reset_index(drop=True)
    return df_info_ad

# Función para mandar el MSJ
def send_message(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,input_date,df_rain,df_info_ad,query):

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    # En caso no haya datos en el DF
    if len(df_rain)==0:
        message = client.messages \
                    .create(
                        body='\nHola! \n\n\n El pronostico de lluvia hoy '+ input_date +' en ' + query +' es : \n\n\n ' + 'No hay probabilidad de Lluvia' + ' \n\n Información Adicional \n\n ' + str(df_info_ad.to_string(index=False)),
                        from_=PHONE_NUMBER,
                        to='+51963290272'
                    )
    # En el caso de que haya datos en el DF 
    else:
        message = client.messages \
                        .create(
                            body='\nHola! \n\n\n El pronostico de lluvia hoy '+ input_date +' en ' + query +' es : \n\n\n ' + str(df_rain) + ' \n\n Información Adicional \n\n ' + str(df_info_ad.to_string(index=False)),
                            from_=PHONE_NUMBER,
                            to='+51963290272'
                        )
    return message.sid
