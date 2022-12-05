import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import pycountry_convert as pc

# define path
PATH = './Data/customer_information.csv'

# reading the CSV file
df = pd.read_csv(PATH)
 
# explore
df.head()
df.shape

# set seed
random.seed(0)

# generate sample id
sample_ID = np.random.randint(10000, 99999, size=1000)
sample_ID = sample_ID.tolist()
for i in range(1000):
    sample_ID[i] = '000' + str(sample_ID[i])

df["sid"] = sample_ID

# dataset with sid and sensitive PII
df_s = df[['sid', 'given_name', 'surname', 'phone_number', 'national_insurance_number', 'bank_account_number']]

# dataset without sensitive PII
df_ns = df.drop(columns=['given_name', 'surname', 'phone_number', 'national_insurance_number', 'bank_account_number'])

############### current country: all in UK --> remove ###############
df_ns = df_ns.drop(columns = 'current_country')

############# birthdate --> age --> banding ###########
# convert to age
birthyear = pd.to_datetime(df['birthdate']).dt.year
df_ns['age'] = 2022 - birthyear
df_ns = df_ns.drop(columns = ['birthdate'])

########### country of birth --> continent ##############
df_ns['country_of_birth'].describe()
cb_count = df_ns.groupby(['country_of_birth']).size().reset_index(name='count')
cb_count
# define functional for converting country to continent
def country_to_continent(country_name):
    if country_name in ['Korea', 'Palestinian Territory', 'Timor-Leste']:
        return 'Asia'
    elif country_name in ['Saint Barthelemy','United States Minor Outlying Islands']:
        return 'North America'
    elif country_name in ['Saint Helena', 'Reunion', 'Western Sahara', 'Libyan Arab Jamahiriya', "Cote d'Ivoire"]:
        return 'Africa'
    elif country_name in ['Antarctica (the territory South of 60 deg S)','Bouvet Island (Bouvetoya)']:
        return 'Antarctica'
    elif country_name == 'Svalbard & Jan Mayen Islands':
        return 'the Arctic Ocean'
    elif country_name == 'Pitcairn Islands':
        return 'Oceania'
    elif country_name in ['Slovakia (Slovak Republic)', 'Holy See (Vatican City State)']:
        return 'Europe'
    elif country_name == 'British Indian Ocean Territory (Chagos Archipelago)':
        return 'Indian Ocean'
    elif country_name == 'Netherlands Antilles':
        return 'South America'
    else:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
# convert
df_ns['place_of_birth'] = df_ns['country_of_birth'].apply(country_to_continent)
# drop country of birth column
df_ns = df_ns.drop(columns = 'country_of_birth')

################ postcode --> banding ################
####### keep outbound characters only
# define function for finding the index of the first digit in a string
def find_first_digit(s):
    for i, c in enumerate(s):
        if c.isdigit():
            return i
            break
# keep characters before the first digit
df_ns['postcode'] = df['postcode'].apply(lambda x: x[:find_first_digit(x)])
# check number in each category
post_count = df_ns.groupby(['postcode']).size().reset_index(name='count')
post_count
# get the postcode with only 1 person
post_agr = post_count['postcode'].loc[post_count['count'] == 1]
# group these postcodes together
df_ns['postcode'] = np.where(df_ns['postcode'].isin(post_agr), '000', df_ns['postcode'])

########## mixup entries for variables ###########
# split data set into with/without gene
df_cc0 = df_ns[df_ns['cc_status'] == 0]
df_cc1 = df_ns[df_ns['cc_status'] == 1]

# random sample all variables
def samp_cols(x):
    n = x.shape[0]
    df_n = x.copy()
    for i in x.columns:
        samp = random.sample(list(x[i]), n)
        df_n[i] = samp
    return df_n
# random sampled group data
df_cc0_n = samp_cols(df_cc0)
df_cc1_n = samp_cols(df_cc1)
# combine
df_n = pd.concat([df_cc0_n, df_cc1_n], axis = 0)

# save CSVs
# sensitive file
#df_s.to_csv('Data/')
# file for government collaborators
#df_n.to_csv('Data/')