# -*- coding: utf-8 -*-

import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import os
import pandas as pd


import re
from datetime import datetime
#import requests
import json
import urllib.request
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import math
from sklearn.model_selection import cross_val_score



def categorize_entrance_date(date):
    try:
        if pd.isnull(date) or date == 'לא צויין':
            return 'not_defined'
        elif date == 'גמיש' or date == 'גמיש ':
            return 'flexible'
        elif date == 'מיידי':
            return 'less_than_6 months'
        else:
            today = datetime.strptime('01/06/2023', '%d/%m/%Y')
            date1 = datetime.strptime(date, '%d/%m/%Y')
            difference = (date1 - today).days
            if difference<=180:
                return 'less_than_6 months'
            elif difference>365:
                return 'above_year'
            else:
                return 'months_6_12'
    except:
        return 'not_defined'
    
def classify_days(value):
    try:
        if pd.isnull(value):
            return ''
        elif value.isdigit():
            days = int(value)
            if days <= 30:
                return "between_0_30"
            elif days <= 60:
                return "between_30_60"
            else:
                return "more_than_60"
        else:
            return value
    except:
        return 'not_defined'
    
def classify_furniture(value):
    try:
        if value == 'לא צויין':
            return 1
        elif value == 'חלקי':
            return 1
        elif value == 'אין':
            return 0
        elif value == 'ללא':
            return 0
        elif value == 'מלא':
            return 2
        else:
            return 1
    except:
        return 1
        
    
def fill_area1(row):
    try:
        average_area_by_city_type = df.groupby(['City', 'type'])['Area'].mean()
        average_room_number_by_city_type = df.groupby(['City', 'type'])['room_number'].mean()
        city = row['City']
        house_type = row['type']
        if pd.isna(row['Area']):
            return row['room_number'] * (average_area_by_city_type[city, house_type] / average_room_number_by_city_type[city, house_type])
        else:
            return row['Area']
    except:
        return row['Area']

def fill_area2(row):
    try:
        average_area_by_city = df.groupby('City')['Area'].mean()
        average_room_number_by_city = df.groupby('City')['room_number'].mean()
        city = row['City']
        if pd.isna(row['Area']):
            return row['room_number'] * (average_area_by_city[city] / average_room_number_by_city[city])
        else:
            return row['Area']
    except:
        return row['Area']

def fill_room_number1(row):
    try:
        average_room_number_by_city_type = df.groupby(['City', 'type'])['room_number'].mean()
        average_area_by_city_type = df.groupby(['City', 'type'])['Area'].mean()
        city = row['City']
        house_type = row['type']
        if pd.isna(row['room_number']):
            return row['Area'] * (average_room_number_by_city_type[city, house_type] / average_area_by_city_type[city, house_type])
        else:
            return row['room_number']
    except:
        return row['room_number']

def fill_room_number2(row):
    try:
        average_room_number_by_city = df.groupby('City')['room_number'].mean()
        average_area_by_city = df.groupby('City')['Area'].mean()
        city = row['City']
        if pd.isna(row['room_number']):
            return row['Area'] * (average_room_number_by_city[city] / average_area_by_city[city])
        else:
            return row['room_number']
    except:
        return row['room_number']

def fill_room_number3(row):
    try:
        average_room_number = df['room_number'].mean()
        average_area = df['Area'].mean()
        if pd.isna(row['room_number']):
            return row['Area'] * (average_room_number / average_area)
        else:
            return row['room_number']
    except:
        return row['room_number']

    
def Distance_km(orign):
    serviceurl='https://maps.googleapis.com/maps/api/distancematrix/json?'
    parms = dict()
    parms['destinations'] = 'תל אביב'
    parms['origins'] = orign
    parms['key'] = "A.....A"
    try:
        url = serviceurl + urllib.parse.urlencode(parms)
    except:
        print('Enter your key')

    try:
        response = requests.get(url)
        if not response.status_code == 200:
            print("HTTP error",response.status_code)
        else:
            try:
                response_data = response.json()
                return response_data['rows'][0]['elements'][0]['distance']['value'] / 1000 # in km
            except:
                print("Response not in valid JSON format")
    except:
        print("Something went wrong with requests.get")
        
def clean(df):
    df.columns = df.columns.str.strip()
    if 'Unnamed: 23' in df.columns:
        df = df.drop('Unnamed: 23', axis=1)
    
    df['Area'].fillna('', inplace=True)
    df.loc[df['Area'].str.contains('1000'), 'Area'] = ''
    df['Area'] = df['Area'].str.replace(r'\D', '', regex=True)
    df['Area'] = df['Area'].apply(lambda x: int(x) if x else x)

    df['city_area'].fillna('', inplace=True)
    df["city_area"] = df["city_area"].str.replace('/', ' ')  # Replace slashes with spaces
    df.loc[df['city_area'].str.contains('None'), 'city_area'] = ''
    df["city_area"] = df["city_area"].str.replace('בשכונת', '') 
    df["city_area"] = df["city_area"].str.replace('-', '') 
    df["city_area"] = df["city_area"].str.strip()  # Remove leading and trailing spaces

    df['room_number'].fillna('', inplace=True)
    df['room_number'] = df['room_number'].str.replace(r'[\[\]"\-׳\']', '', regex=True)
    df['room_number'] = df['room_number'].str.replace(r'[א-ת]', '', regex=True)
    df["room_number"] = df["room_number"].str.strip()  # Remove leading and trailing spaces
    df['room_number'] = df['room_number'].apply(lambda x: float(x) if x else x)
    #df['room_number'] = df['room_number'].apply(room_num_big)
    
    df["City"] = df["City"].str.strip()
    df['City'] = df['City'].replace('נהרייה', 'נהריה')
    df['City'] = df['City'].replace('פתח-תקווה','פתח תקווה')
    df['City'] = df['City'].replace('באר-שבע','באר שבע')
    df['City'] = df['City'].replace('רחובות-ישראל','רחובות')
    df['City'] = df['City'].replace('הוד-השרון','הוד השרון')
    df['City'] = df['City'].replace('תל-אביב-יפו-ישראל','תל אביב')
    df['City'] = df['City'].replace('תל-אביב-יפו','תל אביב')



    df['condition'] = df['condition'].replace(['לא צויין', 'None','FALSE'], 'not_defined')
    df['condition'].fillna('', inplace=True)
    translation_dict = {
        'שמור': 'Well-maintained',
        'חדש': 'New',
        'משופץ': 'Renovated',
        'ישן': 'Old',
        'דורש שיפוץ': 'Needs renovation',
        'חדש מקבלן': 'New',
        '':'',
        'not_defined':'not_defined'
    }
    
    translation_dict2 = {
        'Well-maintained': 2,
        'New': 1,
        'Renovated': 3,
        'Old': 4,
        'Needs renovation': 5,
        'not_defined': 3,
    }
    def translate_condition(value):
        if value in translation_dict:
            return translation_dict[value]
        else:
            return 'not_defined'
    
    df['condition'] = df['condition'].apply(translate_condition)
    df['condition'] = df['condition'].replace(translation_dict2)
    
    df['entranceDate'] = df['entranceDate'].apply(categorize_entrance_date)
    
    df['furniture'] = df['furniture'].apply(classify_furniture)

    translation_dict = {
        'דירה': 'Apartment',
        'דירת גן': 'Garden Apartment',
        'דירת גג': 'Penthouse',
        'בניין': 'Building',
        "קוטג'": 'Cottage',
        'בית פרטי': 'Detached House',
        'דופלקס': 'Duplex',
        'דירת נופש': 'Vacation Apartment',
        'פנטהאוז': 'Penthouse',
        "קוטג' טורי": 'Tower Cottage',
        'מיני פנטהאוז': 'Mini Penthouse',
        'מגרש': 'Plot',
        'דו משפחתי': 'Duplex',
        'אחר': 'Other',
        'טריפלקס': 'Triplex',
        'נחלה': 'Inheritance'
    }
    
    dict_rate = {
        'Apartment': 5,
        'Garden Apartment': 6,
        'Penthouse': 2,
        'Building': 14,
        'Cottage': 1,
        'Detached House': 3,
        'Duplex': 9,
        'Vacation Apartment': 7,
        'Tower Cottage': 12,
        'Mini Penthouse': 2,
        'Plot': 13,
        'Other': 10,
        'Triplex': 11,
        'Inheritance': 8
    }

    df['type'] = df['type'].replace(translation_dict)
    df['type'] = df['type'].replace(dict_rate)

    unique_cities = df['City'].unique()
    # When using API- 
    #distances = {city: Distance_km(city) for city in unique_cities}
    distances={'יהוד מונוסון': 18.377, 'נתניה': 32.82, 'תל אביב': 0.0, 'באר שבע': 108.848, 'בית שאן': 119.939, 'ראשון לציון': 18.034, 'חולון': 10.334, 'הוד השרון': 24.565, 'נוף הגליל': 122.561, 'פתח תקווה': 21.467, 'ירושלים': 65.234, 'חיפה': 94.076, 'נס ציונה': 22.788, 'רעננה': 22.564, 'הרצליה': 15.843, 'גבעת שמואל': 17.582, 'קרית ביאליק': 104.55, 'אריאל': 49.506, 'שוהם': 26.374, 'כפר סבא': 25.452, 'מודיעין מכבים רעות': 38.016, 'נהריה': 123.938, 'זכרון יעקב': 71.618, 'אילת': 343.227, 'רחובות': 31.19, 'בת ים': 12.805, 'רמת גן': 6.973, 'דימונה': 147.203, 'צפת': 168.281}
    df['Distance_from_Tel_Aviv'] = df['City'].apply(lambda city: distances[city])
    df['Distance_from_Tel_Aviv'] = np.where(df['City'] == 'ירושלים', 10, df['Distance_from_Tel_Aviv'])

    city_costs={'אילתאורים': 16666.666666666668, 'אילתאמדר': 13190.47619047619, 'אילתגנים א': 13750.0, 'אילתמצפה ים': 15970.873786407767, 'אילתשחמון': 18203.125, 'אריאלשכונה ב': 19879.518072289156, 'אריאלשכונה ג': 18229.166666666668, 'אריאלשכונה ד': 13152.173913043478, 'אריאלשכונה ה': 13667.18027734977, 'באר שבעב': 12545.454545454546, 'באר שבעג': 13800.0, 'באר שבעד': 12000.0, 'באר שבעה': 10131.578947368422, 'באר שבעו': 12125.0, 'באר שבעט': 12261.904761904761, 'באר שבעיא': 12432.432432432432, 'באר שבענווה זאב': 18437.5, 'באר שבערמות ב': 12277.486910994765, "באר שבערמות ב'": 12555.555555555555, 'באר שבעשכונה א': 4166.666666666667, 'באר שבעשכונה ב': 14416.666666666666, 'באר שבעשכונה ג': 10750.0, 'באר שבעשכונה ד': 13904.761904761905, 'באר שבעשכונה ה': 12352.941176470587, 'באר שבעשכונה ו': 14406.77966101695, 'באר שבעשכונה ט': 14342.105263157895, 'באר שבעשכונה יא': 18129.032258064515, 'בית שאןהאקליפטוס': 18750.0, 'בית שאןמרכז העיר': 11811.023622047243, 'בית שאןנוף גנים': 8365.921787709498, 'בית שאןנוף הגלבוע': 10632.911392405063, 'בית שאןנוף הירדן': 9642.857142857143, 'בית שאןקריית רבין': 12415.094339622641, 'בת יםבית וגן': 23793.103448275862, 'בת יםדרום מערב': 24072.727272727272, 'בת יםמתחם גן העיר': 28461.53846153846, 'בת יםעמידר ניצנה': 24747.47474747475, 'בת יםרובע העסקים': 37142.857142857145, 'בת יםרמת הנשיא': 26400.0, 'גבעת שמואלגיורא': 31313.131313131315, 'גבעת שמואלהשכונה הותיקה': 24484.536082474227, 'גבעת שמואלרמת אילן': 26909.090909090908, 'גבעת שמואלרמת הדר': 22636.165577342046, 'גבעת שמואלרמת הדר החדשה': 26347.517730496453, 'דימונה': 11513.93263451282, 'דימונההנצחון': 9117.64705882353, 'דימונההשחר': 11550.387596899225, 'דימונהחכמי ישראל (תשלוז)': 8187.250996015936, 'דימונהיוספטל': 10086.95652173913, 'דימונהמלכי ישראל': 43333.333333333336, 'דימונהממשית': 10474.330357142857, 'דימונהנאות הללי': 7764.705882352941, 'דימונהנווה דוד': 8472.66881028939, 'דימונהפרחי ארצנו': 8510.103127358094, 'דימונהשכונה לדוגמא': 7613.636363636364, 'הוד השרון': 33140.53101506331, 'הוד השרוןגיל עמל': 18535.816618911176, 'הוד השרוןגרינפארק': 31294.434125408312, 'הוד השרוןהדר': 27716.248765164884, 'הוד השרוןהפרחים': 34083.333333333336, 'הוד השרוןמרכז העיר': 31666.666666666668, 'הוד השרוןרמת הדר': 31266.666666666668, 'הוד השרוןרמתיים': 26794.258373205743, 'הרצליה': 30886.509635974304, 'הרצליההירוקה המרכזית': 35026.92998204668, 'הרצליההמרינה': 59615.38461538462, 'הרצליההרצליה הצעירה': 27500.0, 'הרצליהיד התשעה': 41428.57142857143, 'הרצליהמרכז': 29469.38775510204, 'הרצליהנוה ישראל': 34285.71428571428, 'הרצליהנוה עמל': 22916.666666666668, 'זכרון יעקבגבעת עדן': 22037.037037037036, 'זכרון יעקבהמושבה': 16137.184115523465, 'זכרון יעקבחלומות זכרון': 21111.11111111111, 'זכרון יעקבמול היקב': 22400.0, 'זכרון יעקבנווה הברון': 32352.941176470587, 'זכרון יעקבנווה שלו': 24277.456647398845, 'זכרון יעקבנווה שרת': 15440.0, 'זכרון יעקברמת צבי': 22551.020408163266, 'חולוןנאות שושנים': 23636.363636363636, 'חולוןקריית שרת': 25033.185840707964, 'חולוןקרית אילון': 28237.70491803279, 'חולוןקרית בן גוריון': 24952.380952380954, 'חולוןשדרת המגדלים': 28968.668407310706, 'חולוןשיכון ותיקים': 40750.0, 'חולוןתל גיבורים': 25609.756097560974, 'חיפה': 18513.820942282204, 'חיפהאחוזה': 16953.846153846152, 'חיפהבת גלים': 35200.0, 'חיפהגאולה': 14444.444444444445, 'חיפהגבעת דאונס': 11538.461538461539, 'חיפההדר הכרמל': 18230.337078651686, 'חיפהנוה פז': 14864.864864864865, 'חיפהקרית חיים מזרחית': 14500.0, 'חיפהרמות רמז': 15000.0, 'יהוד מונוסון': 26166.82738669238, 'יהוד מונוסוןמרכז העיר': 25092.460881934567, 'יהוד מונוסוןנווה אפרים': 26307.053941908714, 'יהוד מונוסוןקרית סביונים': 28984.771573604063, 'ירושלים': 36204.35057746283, 'ירושליםארמון הנציב': 31329.787234042553, 'ירושליםארנונה (תלפיות)': 36702.12765957447, 'ירושליםבקעה': 44117.64705882353, 'ירושליםגבעת מרדכי': 25363.636363636364, 'ירושליםגילה': 27171.628721541158, 'ירושליםהגבעה הצרפתית': 116959.06315789474, 'ירושליםהר חומה': 26051.28205128205, 'ירושליםטלביה': 36769.230769230766, 'ירושליםנוף ציון': 22033.898305084746, 'ירושליםנחלאות': 59090.90909090909, 'ירושליםעין כרם': 29924.242424242424, 'ירושליםפסגת זאב': 22219.21124928082, 'ירושליםקטמון או': 46076.92307692308, 'ירושליםקטמון הישנה': 40000.0, 'ירושליםקריית משה': 59523.80952380953, 'ירושליםקרית היובל': 37728.0, 'ירושליםקרית משה': 38087.24832214765, 'ירושליםרחביה': 61714.28571428572, 'ירושליםרמת שרת': 43718.75, 'ירושליםתלפיות': 30116.279069767443, 'כפר סבא': 28982.226147382426, 'כפר סבאאלי כהן': 27264.150943396227, 'כפר סבאהדרים': 28020.833333333332, 'כפר סבאהזמר העברי': 29950.49504950495, 'כפר סבאהשכונה הירוקה': 36103.896103896106, 'כפר סבאכפר סבא הצעירה': 30700.0, 'כפר סבאמוצקין דובדבן הכפר כיסופים': 29642.85714285714, 'כפר סבאמרכז העיר דרום': 25083.54678202438, 'כפר סבאסביוני הכפר': 32347.82608695652, 'כפר סבאקריית ספיר': 24369.747899159665, 'מודיעין מכבים רעות': 28812.86549707602, 'נהריהאוסישקין': 12534.246575342466, 'נהריהאכזיב': 27321.428571428572, 'נהריהגבעת כצנלסון': 13333.333333333334, 'נהריהמרכז העיר': 17368.42105263158, 'נהריהנוה אלון (עמידר)': 13945.578231292517, 'נהריהנוה מנחם בגין': 17665.615141955837, 'נהריהעין שרה': 14711.864406779661, 'נוף הגלילאשכול': 12169.811320754718, "נוף הגלילהר יונה ג'": 15887.573964497042, 'נוף הגלילזאב': 9811.32075471698, 'נוף הגלילנוף יזרעאל': 15625.0, 'נוף הגלילצפונית': 13009.25925925926, 'נוף הגלילשלום': 13750.0, 'נס ציונהארגמן': 45769.230769230766, 'נס ציונההדרי סמל': 28571.428571428572, 'נס ציונהוואלי (valley)': 31666.666666666668, 'נס ציונהמרכז העיר מערב': 28271.604938271605, 'נתניהאגמים': 25416.666666666668, 'נתניהבן ציון': 21929.824561403508, 'נתניהמרכז העיר דרום': 20600.0, 'נתניהמרכז העיר צפון': 23052.63157894737, 'נתניהמשכנות זבולון': 23545.454545454544, 'נתניהנאות הרצל': 18862.275449101795, 'נתניהנאות שקד': 28727.272727272728, 'נתניהנוף הטיילת': 40138.88888888889, 'נתניהעיר ימים': 33729.1280148423, 'נתניהקרית השרון': 25726.775956284153, 'נתניהקרית נורדאו': 21891.891891891893, 'נתניהקרית רבין': 30714.285714285714, 'נתניהרמת חן': 20642.85714285714, 'נתניהרמת ידין': 24506.172839506173, 'נתניהרצועת המלונות': 24770.642201834864, 'פתח תקווה': 25977.044817553866, 'פתח תקווהאחדות': 23684.21052631579, 'פתח תקווהאם המושבות הותיקה': 31343.283582089553, 'פתח תקווהאם המושבות החדשה': 27964.23658872077, 'פתח תקווהגני הדר': 27446.808510638297, 'פתח תקווההאחים ישראלית': 20757.575757575756, 'פתח תקווההדר גנים': 27063.38028169014, 'פתח תקווההמרכז השקט': 24002.16045769471, 'פתח תקווהכפר גנים א': 21688.555347091933, 'פתח תקווהכפר גנים ב': 24073.58738501971, 'פתח תקווהכפר גנים ג': 28223.504721930745, 'פתח תקווהמחנה יהודה': 26300.81300813008, 'פתח תקווהמרכז העיר': 21250.0, 'פתח תקווהנווה גן': 26886.201343297576, 'פתח תקווהעין גנים': 35263.15789473684, 'פתח תקווהעמישב': 32454.545454545456, 'פתח תקווהצמרת גנים': 24000.0, 'פתח תקווהקרול': 26938.775510204083, 'פתח תקווהקריית חזני': 34420.289855072464, 'פתח תקווהקרית אליעזר פרי': 21111.11111111111, 'פתח תקווהקרית הרב סלומון': 22083.333333333332, 'פתח תקווהקרית מטלון': 21633.333333333332, 'פתח תקווהרמת ורבר': 23900.0, 'פתח תקווהשיכון מפ"ם': 33437.5, 'פתח תקווהשיפר': 28201.0582010582, 'פתח תקווהשעריה': 26458.333333333332, 'צפת': 16576.923076923078, 'צפתבן גוריון כנען': 7000.0, 'צפתמאור חיים': 9687.5, 'קרית ביאליקגבעת הרקפות': 20932.20338983051, 'קרית ביאליקדרום': 16923.076923076922, 'קרית ביאליקמרכז העיר': 16065.573770491803, 'קרית ביאליקפרפר': 15600.0, 'קרית ביאליקצור שלום': 14239.130434782608, 'ראשון לציוןאברמוביץ': 22608.695652173912, 'ראשון לציוןהרקפות': 39843.75, 'ראשון לציוןהשומר': 25028.571428571428, 'ראשון לציוןכלניות': 20416.666666666668, 'ראשון לציוןכצנלסון': 25571.428571428572, 'ראשון לציוןנוה הדרים': 28241.75824175824, 'ראשון לציוןנווה חוף': 28494.62365591398, 'ראשון לציוןנווה ים': 25454.545454545456, 'ראשון לציוןקדמת ראשון': 21473.684210526317, 'ראשון לציוןקרית ראשון': 17109.409190371993, 'ראשון לציוןרביבים': 26282.722513089004, 'ראשון לציוןרמב"ם': 22972.461273666093, 'ראשון לציוןרמז': 29133.858267716536, 'ראשון לציוןשיכוני המזרח': 11408.730158730159, 'רחובותהיובל': 22815.533980582524, 'רחובותמרכז העיר': 20468.75, 'רחובותקרית דוד': 21196.581196581195, 'רחובותרחובות ההולנדית': 29224.137931034482, 'רחובותרחובות המדע': 26692.91338582677, 'רחובותרחובות הצעירה': 19647.35516372796, 'רחובותשעריים': 22169.811320754718, 'רמת גןהבורסה': 37037.03703703704, 'רמת גןיד לבנים': 29602.8880866426, "רמת גןמרכז העיר א'": 32307.69230769231, 'רמת גןקרית קריניצי': 29000.0, 'רמת גןרמת גן': 31366.666666666668, 'רמת גןרמת חן': 38778.40909090909, 'רמת גןרמת שקמה': 31818.18181818182, 'רמת גןשיכון ותיקים': 56900.0, 'רמת גןשכונת הראשונים': 35087.71929824561, 'רעננה': 29068.312527966864, 'רעננה2003': 37832.69961977186, 'רעננה2005': 23428.571428571428, 'רעננהדרום מזרח': 21200.0, 'רעננהלב הפארק': 30073.08160779537, 'רעננהלסטר': 29550.43859649123, 'רעננהמרכז דרום': 26023.34914264867, 'רעננהנווה זמר': 38619.044642857145, 'רעננהקרית בן צבי (רסקו)': 55000.0, 'רעננהקרית גנים': 22606.382978723403, 'רעננהקרית דוד רמז': 34339.181286549705, 'רעננהקרית שרת': 41818.181818181816, 'רעננהרעננה צפון': 47457.12031715433, 'שוהםברושים': 31489.36170212766, 'שוהםגבעולים': 18908.918406072105, 'שוהםורדים': 41666.666666666664, 'שוהםחמניות': 31404.95867768595, 'שוהםיובלים': 32129.96389891697, 'שוהםכרמים': 20000.0, 'שוהםרקפות': 47126.4367816092, 'תל אביבביצרון': 44927.536231884056, 'תל אביבהדר יוסף': 66896.55172413793, 'תל אביבהמשתלה': 39837.39837398374, 'תל אביבהצפון החדש החלק הצפוני': 62750.92936802974, 'תל אביבהצפון החדש סביבת כיכר המדינה': 59408.396946564884, 'תל אביבהצפון הישן החלק הדרום מזרחי': 75000.0, 'תל אביבהצפון הישן החלק המרכזי': 64117.64705882353, 'תל אביבהצפון הישן החלק הצפוני': 60900.0, 'תל אביביד אליהו': 50769.230769230766, 'תל אביביפו ג': 31609.19540229885, 'תל אביביפו ד': 32989.69072164949, 'תל אביבכרם התימנים': 54041.09589041096, 'תל אביבלב תל אביב': 59677.41935483871, 'תל אביבלב תל אביב החלק המערבי': 75000.0, 'תל אביבמרכז יפו': 39827.58620689655, 'תל אביבנאות אפקה א': 34000.0, 'תל אביבנאות אפקה ב': 50349.54685214114, 'תל אביבנוה אביבים': 47687.8612716763, 'תל אביבנוה חן': 25909.090909090908, 'תל אביבנוה שאנן': 43333.333333333336, 'תל אביבנוה שרת': 37600.0, 'תל אביבנווה עופר': 30773.809523809523, "תל אביבעג'מי": 33490.56603773585, 'תל אביבפלורנטין': 42391.30434782609, 'תל אביבצהלה': 91666.66666666667, 'תל אביבצהלון ושיכוני חסכון': 38095.23809523809, 'תל אביבקרית שלום': 30833.333333333332, 'תל אביברמות צהלה': 44591.836734693876, 'תל אביברמת אביב': 58450.704225352114, 'תל אביברמת אביב ג': 72115.38461538461, 'תל אביבשוק הפשפשים וצפון יפו': 41363.63636363636, 'תל אביבשיכון בבלי': 68556.70103092784, 'תל אביבתוכנית ל': 51775.700934579436, 'אילת': 16673.58803986711, 'אריאל': 14515.810276679842, 'באר שבע': 12436.472346786248, 'בית שאן': 11288.416075650119, 'בת ים': 27654.320987654322, 'גבעת שמואל': 25085.444902769592, 'זכרון יעקב': 21559.164733178655, 'חולון': 27390.10989010989, 'נהריה': 17418.07116104869, 'נוף הגליל': 13167.670682730924, 'נס ציונה': 34055.2016985138, 'נתניה': 26950.24077046549, 'קרית ביאליק': 16465.346534653465, 'ראשון לציון': 21993.438320209974, 'רחובות': 22894.131185270428, 'רמת גן': 33859.81308411215, 'שוהם': 27353.263850795393, 'תל אביב': 52120.53696942438, 'ממוצע כללי': 26789.312268889145}
    df['city_cityarea'] = df['City'] + df['city_area']
    df['city_cityarea'] = df['city_cityarea'].astype(str)
    df['cost_per_meter'] = df['city_cityarea'].map(city_costs)
    df['cost_per_meter'] = df['cost_per_meter'].fillna(df['City'].map(city_costs).fillna(city_costs['ממוצע כללי']))
    
    return df



def preparation (df):
    selected_columns = ['City','type' ,'room_number', 'Area', 'entranceDate', 'furniture', 'condition','Distance_from_Tel_Aviv','cost_per_meter']
    df = df[selected_columns]
    return df




app = Flask(__name__)
model = pickle.load(open('trained_model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    features = request.form.getlist('feature')
    print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # City	type	room_number	Area	entranceDate	furniture	condition	Distance_from_Tel_Aviv	cost_per_meter
    # Convert the features list to a pandas DataFrame
    features_df = pd.DataFrame([features], columns=['City', 'city_area', 'type', 'room_number', 'Area', 'entranceDate', 'furniture', 'condition'])
    try: 
        features_df = clean(features_df)
        features_df = preparation(features_df)
        # Make the prediction using the model
        prediction = model.predict(features_df)[0]
        output_text = format(int(prediction),",")+" NIS"
    except:
        output_text = "is not avalible - please fix your values"
        

    return render_template('index.html', prediction_text='{}'.format(output_text))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port,debug=True)
