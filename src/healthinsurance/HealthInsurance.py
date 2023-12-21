import pickle
import pandas as pd
import numpy as np
import inflection

class HealthInsurance(object):
    def __init__(self):
        self.home_path = ''
        self.annual_premium_scaler = pickle.load(open(self.home_path + 'features/annual_premium_scaler.pkl', 'rb'))
        self.age_scaler = pickle.load(open(self.home_path + 'features/age_scaler.pkl', 'rb'))
        self.vintage_scaler = pickle.load(open(self.home_path + 'features/vintage_scaler.pkl', 'rb'))
        self.gender_encoder = pickle.load(open(self.home_path + 'features/gender_encoder.pkl', 'rb'))
        self.region_code_encoder = pickle.load(open(self.home_path + 'features/region_code_encoder.pkl', 'rb'))
        self.policy_sales_encoder = pickle.load(open(self.home_path + 'features/policy_sales_encoder.pkl', 'rb'))

    def rename_columns(self, dataframe):
        df = dataframe.copy()
        title = lambda x: inflection.titleize(x)
        snakecase = lambda x: inflection.underscore(x)
        spaces = lambda x: x.replace(" ", "")
        cols_old = list(df.columns)
        cols_old = list(map(title, cols_old))
        cols_old = list(map(spaces, cols_old))
        cols_new = list(map(snakecase, cols_old))
        df.columns = cols_new

        return df
        
    def data_cleaning(self, df1):
        # Using the function we created in section 0.1
        df1 = self.rename_columns(df1)

        return df1

    def feature_engineering(self, df2):
        # Vehicle damage
        damage = {'Yes': 1, 'No':0}
        df2['vehicle_damage'] = df2['vehicle_damage'].map(damage)

        # Vehicle age
        age_dict = {'< 1 Year':'below_1_year', '1-2 Year':'between_1_2_year', '> 2 Years':'above_2_year'}
        df2['vehicle_age'] = df2['vehicle_age'].map(age_dict)

        return df2
    
    def data_preparation(self, df3):
        # Transformation
        # StandardScaler
        df3['annual_premium'] = self.annual_premium_scaler.transform(df3[['annual_premium']].values)
        
        # MinMaxScaler
        df3['age'] = self.age_scaler.transform(df3[['age']].values)
        df3['vintage'] = self.vintage_scaler.transform(df3[['vintage']].values)
        
        # Target Encoder
        df3.loc[:, 'gender'] = df3['gender'].map(self.gender_encoder)
        df3.loc[:, 'region_code'] = df3['region_code'].map(self.region_code_encoder)
        df3.loc[:, 'policy_sales_channel'] = df3['policy_sales_channel'].map(self.policy_sales_encoder)
        df3 = pd.get_dummies(df3, prefix='vehicle_age', columns=['vehicle_age'])

        # Feature selection
        cols_selected = ['vintage', 'annual_premium', 'age', 'region_code', 
                 'vehicle_damage', 'policy_sales_channel', 'previously_insured']

        return df3[cols_selected]
    
    def get_prediction(self, model, original_data, test_data):
        # Model prediction
        pred = model.predict_proba(test_data)

        # Join prediction into original data
        original_data['score'] = pred[:, 1].tolist()

        return original_data.to_json(orient='records', date_format='iso')
    
