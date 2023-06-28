# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 15:25:51 2023

@author: Hen Abitbul
"""

import re
import numpy as np
import pandas as pd
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
import pickle
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold


url =  "output_all_students_Train_v10.csv"
df = pd.read_csv(url)

def room_num_big(value):
    if isinstance(value,float):
        if value>10 and value%5==0:
            return value/10
    return value

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
    
    df['price'].fillna('', inplace=True)
    df['price'] = df['price'].str.split('TOP').str[0]
    df['price'] = df['price'].str.replace(r'\D', '', regex=True)
    df = df[df['price']!='']
    df['price'] = df['price'].apply(lambda x: int(x) if x else x)
    
    df['Area'].fillna('', inplace=True)
    df.loc[df['Area'].str.contains('1000'), 'Area'] = ''
    df['Area'] = df['Area'].str.replace(r'\D', '', regex=True)
    df['Area'] = df['Area'].apply(lambda x: int(x) if x else x)
    
    df['Street'].fillna('', inplace=True)
    df["Street"] = df["Street"].str.replace(r'[^א-ת\s]', '')
    df["Street"] = df["Street"].str.strip()

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

    df['number_in_street'] = df['number_in_street'].replace([np.nan, "None", "-", 'FALSE'], "")
    df['number_in_street'] = df['number_in_street'].apply(lambda x: int(x) if x else x)

    #num of images - we have non and None and empty
    df['num_of_images'].fillna('', inplace=True)
    df['num_of_images']=df['num_of_images'].astype(str)
    df.loc[df['num_of_images'].str.contains('קומה'), 'num_of_images'] = ''
    df.loc[df['num_of_images'].str.contains('לכל'), 'num_of_images'] = ''
    df.loc[df['num_of_images'].str.contains('קרקע'), 'num_of_images'] = ''
    df['num_of_images'] = df['num_of_images'].apply(lambda x: float(x) if x else x)

    df['floor_out_of'] = df['floor_out_of'].apply(lambda x: '0' if 'קומת קרקע' in str(x) else x)
    df['floor_out_of'] = df['floor_out_of'].apply(lambda x: '100000' if 'קומת מרתף' in str(x) else x)
    df['floor_out_of'] = df['floor_out_of'].str.replace('קומה', '')
    df['floor_out_of'] = df['floor_out_of'].str.replace('מתוך', '')
    df['floor_out_of'] = df['floor_out_of'].str.replace('תוך', '')
    
    df['first'] = df['floor_out_of'].str.extract(r'(\d+)').astype(float)
    df['second'] = df['floor_out_of'].str.extract(r'(\d+)\s+(\d+)').iloc[:, 1].astype(float)
    df['floor'] = df[['first', 'second']].min(axis=1)
    df['floor'].fillna('', inplace=True)
    df['total_floor'] = df[['first', 'second']].max(axis=1)
    df['total_floor'] = df['total_floor'].where(df['second'].notnull(), '')
    # Replace NaN values in 'total_floor' with None
    df['total_floor'] = df['total_floor'].where(df['total_floor'].notnull(), None)
    df.loc[df['first'] == 100000, 'floor'] = -1
    df.loc[df['first'] == 100000, 'total_floor'] = ''
    df = df.drop(['first', 'second','floor_out_of'], axis=1)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין מעלית', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש מעלית', 'יש']
    # Replace the desired values with 0
    df['hasElevator'] = np.where(np.isin(df['hasElevator'], replace_values_0), 0, df['hasElevator'])
    df['hasElevator'] = np.where(np.isin(df['hasElevator'], replace_values_1), 1, df['hasElevator'])
    df['hasElevator'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין חניה', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש חניה', 'יש',"יש חנייה"]
    # Replace the desired values with 0
    df['hasParking'] = np.where(np.isin(df['hasParking'], replace_values_0), 0, df['hasParking'])
    df['hasParking'] = np.where(np.isin(df['hasParking'], replace_values_1), 1, df['hasParking'])
    df['hasParking'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין סורגים', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש','יש סורגים']
    # Replace the desired values with 0
    df['hasBars'] = np.where(np.isin(df['hasBars'], replace_values_0), 0, df['hasBars'])
    df['hasBars'] = np.where(np.isin(df['hasBars'], replace_values_1), 1, df['hasBars'])
    df['hasBars'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין מחסן', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש','יש מחסן']
    # Replace the desired values with 0
    df['hasStorage'] = np.where(np.isin(df['hasStorage'], replace_values_0), 0, df['hasStorage'])
    df['hasStorage'] = np.where(np.isin(df['hasStorage'], replace_values_1), 1, df['hasStorage'])
    df['hasStorage'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין מיזוג אויר', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש','יש מיזוג אויר',"יש מיזוג אוויר"]
    # Replace the desired values with 0
    df['hasAirCondition'] = np.where(np.isin(df['hasAirCondition'], replace_values_0), 0, df['hasAirCondition'])
    df['hasAirCondition'] = np.where(np.isin(df['hasAirCondition'], replace_values_1), 1, df['hasAirCondition'])
    df['hasAirCondition'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין מרפסת', 'אין', 'no','0']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש',"יש מרפסת"]

    # Replace the desired values with 0
    df['hasBalcony'] = np.where(np.isin(df['hasBalcony'], replace_values_0), 0, df['hasBalcony'])
    df['hasBalcony'] = np.where(np.isin(df['hasBalcony'], replace_values_1), 1, df['hasBalcony'])
    df['hasBalcony'].fillna('', inplace=True)

    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'אין ממ"ד', 'אין', 'no','0',"אין ממ״ד"]
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש','יש ממ"ד','יש ממ״ד']
    # Replace the desired values with 0
    df['hasMamad'] = np.where(np.isin(df['hasMamad'], replace_values_0), 0, df['hasMamad'])
    df['hasMamad'] = np.where(np.isin(df['hasMamad'], replace_values_1), 1, df['hasMamad'])
    df['hasMamad'].fillna('', inplace=True)
    
    # Define the values you want to replace with 0
    replace_values_0 = ['FALSE', 'לא', 'לא נגיש לנכים', 'אין', 'no','0','לא נגיש']
    replace_values_1 = ['TRUE', 'כן', 'yes', '1','יש',"נגיש לנכים",'נגיש']
    # Replace the desired values with 0
    df['handicapFriendly'] = np.where(np.isin(df['handicapFriendly'], replace_values_0), 0, df['handicapFriendly'])
    df['handicapFriendly'] = np.where(np.isin(df['handicapFriendly'], replace_values_1), 1, df['handicapFriendly'])
    df['handicapFriendly'].fillna('', inplace=True)

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
    
    values_to_replace = ['None ', np.nan, 'None', '-', 'Nan']
    df['publishedDays'] = df['publishedDays'].replace(values_to_replace, '')
    values_to_replace1= ['חדש', 'חדש!']
    df['publishedDays'] = df['publishedDays'].replace(values_to_replace1, '0')
    df['publishedDays'] = df['publishedDays'].str.replace(r'\D', '', regex=True)
    df['publishedDays'] = df['publishedDays'].apply(classify_days)

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
    df['description'].fillna('', inplace=True)
    df["description"] = df["description"].str.replace(r'[^א-ת.\d\s]', ' ')
    df["description"] = df["description"].str.strip()
    
    df.drop_duplicates(inplace=True)
    df = df.replace('', np.nan)
    return df


def transformer(df):
    # Fill NaN values in 'Area' with the calculated values
    df['Area'] = df.apply(fill_area1, axis=1)

    # Calculate the average 'Area' and 'room_number' by 'city'
    average_area_by_city = df.groupby('City')['Area'].mean()
    average_room_number_by_city = df.groupby('City')['room_number'].mean()

    # Fill NaN values in 'Area' with the calculated values
    df['Area'] = df.apply(
        lambda row: row['room_number'] * (average_area_by_city[row['City']] / average_room_number_by_city[row['City']])
                    if pd.isna(row['Area']) else row['Area'],
        axis=1
    )

    # Fill NaN values in 'Area' with the calculated values
    df['Area'] = df.apply(fill_area2, axis=1)

    # Fill NaN values in 'room_number' with the calculated values
    df['room_number'] = df.apply(fill_room_number1, axis=1)

    # Fill NaN values in 'room_number' with the calculated values
    df['room_number'] = df.apply(fill_room_number2, axis=1)

    # Fill NaN values in 'room_number' with the calculated values
    df['room_number'] = df.apply(fill_room_number3, axis=1)
    

    unique_cities = df['City'].unique()
    # When using API- 
    #distances = {city: Distance_km(city) for city in unique_cities}
    distances={'יהוד מונוסון': 18.377, 'נתניה': 32.82, 'תל אביב': 0.0, 'באר שבע': 108.848, 'בית שאן': 119.939, 'ראשון לציון': 18.034, 'חולון': 10.334, 'הוד השרון': 24.565, 'נוף הגליל': 122.561, 'פתח תקווה': 21.467, 'ירושלים': 65.234, 'חיפה': 94.076, 'נס ציונה': 22.788, 'רעננה': 22.564, 'הרצליה': 15.843, 'גבעת שמואל': 17.582, 'קרית ביאליק': 104.55, 'אריאל': 49.506, 'שוהם': 26.374, 'כפר סבא': 25.452, 'מודיעין מכבים רעות': 38.016, 'נהריה': 123.938, 'זכרון יעקב': 71.618, 'אילת': 343.227, 'רחובות': 31.19, 'בת ים': 12.805, 'רמת גן': 6.973, 'דימונה': 147.203, 'צפת': 168.281}
    df['Distance_from_Tel_Aviv'] = df['City'].apply(lambda city: distances[city])
    df['Distance_from_Tel_Aviv'] = np.where(df['City'] == 'ירושלים', 10, df['Distance_from_Tel_Aviv'])
    
    df['city_area'].fillna("",inplace=True)
    return df

def cost_per_meter(df):
    city_costs = {}
    # Group the data by city and calculate the sum of price and area
    df['city_cityarea']= df['City']+df['city_area']
    grouped_data = df.groupby('city_cityarea').agg({'price': 'sum', 'Area': 'sum'})
    grouped_data2 = df.groupby('City').agg({'price': 'sum', 'Area': 'sum'})
    # Calculate the cost per meter for each city and store it in the dictionary
    for city, data in grouped_data.iterrows():
        city_costs[city] = data['price'] / data['Area']
    for city, data in grouped_data2.iterrows():
        city_costs[city] = data['price'] / data['Area']

    df['cost_per_meter'] = df['city_cityarea'].apply(lambda city: city_costs[city])
    city_costs['ממוצע כללי']= df['price'].sum() / df['Area'].sum()
    return df

def preparation (df):
    selected_columns = ['City','type' ,'room_number', 'Area', 'price', 'entranceDate', 'furniture', 'condition','Distance_from_Tel_Aviv','cost_per_meter']
    df = df[selected_columns]
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    return df

def prepare_data(df2):
    df2=clean(df2)
    df2=transformer(df2)
    df2=cost_per_meter(df2)
    df2=preparation(df2)
    return df2
df=prepare_data(df)


data = df.copy()
X_train= data.drop("price", axis=1)
y_train= data["price"]
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# data2 = df2.copy()
# X_test = data2.drop("price", axis=1)
# y_test = data2["price"]

# Define the column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), ["room_number","Area",'Distance_from_Tel_Aviv','cost_per_meter','type', "condition", "furniture"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["City", "entranceDate"])
    ])


# Create the pipeline
pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('E', ElasticNet())
])

# Define the parameter grid for hyperparameter search
param_grid = {
    'E__alpha': [0.01, 0.05, 0.06,0.07,0.08, 0.09, 0.1, 0.5, 1.0, 5.0, 10, 30, 50, 90],
    'E__l1_ratio': [0.01, 0.95, 0.1, 0.3, 0.5,0.6, 0.7,0.8, 0.9]
}

# Create the GridSearchCV object with 10-fold cross-validation
grid_search = GridSearchCV(estimator=pipe, param_grid=param_grid, scoring='neg_mean_squared_error', cv=10)

# Fit the GridSearchCV on the training data
grid_search.fit(X_train, y_train)

# Get the best hyperparameters and model
best_params = grid_search.best_params_
best_model = grid_search.best_estimator_
pickle.dump(best_model, open("trained_model.pkl","wb"))


# # Perform cross-validation and calculate the mean squared error
# cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
# rmse_scores = np.sqrt(-cv_scores)

# # Print the root mean squared error for each fold
# print("Root Mean Squared Error for each fold:", rmse_scores)

# # Calculate the average root mean squared error
# avg_rmse = np.mean(rmse_scores)
# print("Average Root Mean Squared Error:", avg_rmse)

