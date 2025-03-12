

## Repo Name: python-nyc-oti-geoclient-api-v1

## Owner

- [@edgaralfonseca](https://github.com/edgaralfonseca)
- [LinkedIn](https://www.linkedin.com/in/edgar-alfonseca/)

## Repo description

This repository contains files that enable you to use Python to call the Geoclient v1.0 API maintained by the NYC Office of Technology and Innovation (OTI) to batch geocode data. There are also copies of the files I used to conduct a presentation on this to NYC government colleagues at the October 2024 Analytics Exchange (AnEx) Learning Summit hosted by NYC OTI.

## Key Repo files

- [October 2024 AnEx Learning Summit Python Notebook](https://github.com/edgaralfonseca/python-nyc-oti-geoclient-api-v1/blob/main/Oct_2024_AnEx_Learning_Summit_Notebook.ipynb)
- [October 2024 AnEx Learning Summit Deck](https://github.com/edgaralfonseca/python-nyc-oti-geoclient-api-v1/blob/main/Edgar%20AnEx%20Oct%202024%20Learning%20Summit%20Deck.pdf)
- [nyc_oti_geoclient_api_1_0.py](https://raw.githubusercontent.com/edgaralfonseca/python-nyc-oti-geoclient-api-v1/main/nyc_oti_geoclient_api_1_0.py)

## Things to Know

**Geoclient API description:** [https://api-portal.nyc.gov/api-details#api=geoclient&operation=geoclient](https://api-portal.nyc.gov/api-details#api=geoclient&operation=geoclient)  
**NYC OTI Geoclient v2.0 documentation:** [https://mlipper.github.io/geoclient/docs/current/user-guide/](https://mlipper.github.io/geoclient/docs/current/user-guide/)    
**Note, the 1.0 documentation is no longer avaiable, but 2.0 is documentation is applicable to 1.0**    
**NYC OTI GitHub repo:** [https://github.com/CityOfNewYork/geoclient](https://github.com/CityOfNewYork/geoclient)

### Pre-requisites for you to use the API

1. Create a new account on the NYC API Developers Portal: [https://api-portal.nyc.gov/](https://api-portal.nyc.gov/)
2. Request an API key by subscribing to the Geoclient API in the portal.

### Notes about the API

- The OTI geoclient API handles 2,500 requests per minute / 500,000 requests per day.
- NYC Department of City Planning's Geosupport ([https://www.nyc.gov/site/planning/data-maps/open-data/dwn-gde-home.page](https://www.nyc.gov/site/planning/data-maps/open-data/dwn-gde-home.page)) is used to power Geoclient.
- Sometimes there might be a several week delay in Geoclient reflecting what is in Geosupport.
- Geoclient serves up a subset of attributes whereas Geosupport has all attributes.

### How to use the 'nyc_oti_geoclient_api_1_0.py' python code

```python

# Example 1: Complete example that samples a pandas dataframe with NYC addresses
# and sends it to the NYC Geoclient 'address' API endpoint

# Import sample NYC address data (close to 6k records)

url = "https://raw.githubusercontent.com/edgaralfonseca/python-oti-geoclient-api-v1/main/nyc_sample_almost_6k_addresses.csv"

nyc_address_df = pd.read_csv(url)

# Minor data cleaning on the postcode (zip code)

nyc_address_df['postcode'] = nyc_address_df['postcode'].astype(str).str[:5]

# Create a copy of the nyc address pandas dataframe and sample 1,000 records

address_input_df = nyc_address_df.sample(n=1000, random_state=1).copy()

# Prepare parameters for API

# Read your API subscription key from a text file

with open('/content/OTI geoclient API primary key.txt', 'r') as file:
    subscription_key = file.read().strip()

# Sdd your API subscription key to the headers parameter

headers_param = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': subscription_key
}

# Store the relevant url endpoint 

address_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/address.json"

# After reviewing the API documentation, specify the response columns you are interested in keeping

search_return_columns_to_keep = ['bbl', 'bblBoroughCode', 'bblTaxBlock',
    'bblTaxLot', 'buildingIdentificationNumber', 'latitude', 'longitude',
    'xCoordinate', 'yCoordinate', 'communityDistrict', 'communityDistrictNumber',
    'geosupportFunctionCode',
    'geosupportReturnCode', 'geosupportReturnCode2', 'returnCode1a', 'returnCode1e'
]

# Call the address endpoint API using the custom function
# Save the result in a new pandas dataframe 'oti_api_address_output_df'

oti_api_address_output_df = oti_geoclient_api_address_endpoint(
    api_endpoint= address_api_url_param,
    headers= headers_param,
    df_name= address_input_df,
    df_key_field='row_id',
    housenum_input_col = 'house_number', street_input_col = 'street_name' , boro_input_col= 'borough' , zip_input_col= 'postcode',
    response_columns= search_return_columns_to_keep)

# Export geocoded output to csv

oti_api_address_output_df.to_csv('oti_api_address_output_df.csv', index=False)

# Example 2: Takes the previous example's 'address' API endpoint output (oti_api_address_output_df)
# and sends it to the NYC Geoclient 'BIN' API endpoint

# Specify the columns you want to keep from oti_api_address_output_df

input_columns_to_keep = ['row_id', 'buildingIdentificationNumber']  # Replace with the columns you want to keep

# Create a copy of the OTI address output pandas dataframe and sample 500 records

bin_input_df = oti_api_address_output_df[oti_api_address_output_df['buildingIdentificationNumber'].notna()][input_columns_to_keep].sample(n=500, random_state=1).copy()

# Prepare parameters for API

# Note: You can re-use the headers_param you set in Example #1

# Store the relevant url endpoint 

bin_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/bin.json"

# After reviewing the API documentation, specify the response columns you are interested in keeping

bin_return_columns_to_keep = ['bbl', 'bblBoroughCode', 'bblTaxBlock',
    'bblTaxLot',
    'internalLabelXCoordinate', 'internalLabelYCoordinate',
    'geosupportFunctionCode',
    'geosupportReturnCode'
]

# Call the API using the custom function
# Save the result in a new pandas dataframe 'oti_api_bin_output_df'

oti_api_bin_output_df = oti_geoclient_api_bin_endpoint(
    api_endpoint= bin_api_url_param,
    headers= headers_param,
    df_name= bin_input_df,
    df_key_field='row_id',
    api_input_column='buildingIdentificationNumber',
    response_columns= bin_return_columns_to_keep)

# Export geocoded output to csv

oti_api_bin_output_df.to_csv('oti_api_bin_output_df.csv', index=False)

# Example 3: Takes Example #1's 'address' API endpoint output API (oti_api_address_output_df)
# and sends it to the NYC Geoclient 'BBL' API endpoint

# Specify the columns you want to keep from oti_api_address_output_df

input_columns_to_keep = ['row_id', 'bblBoroughCode', 'bblTaxBlock', 'bblTaxLot']  # Replace with the columns you want to keep

# Create a copy of the OTI address output pandas dataframe and sample 500 records

bbl_input_df = oti_api_address_output_df[oti_api_address_output_df['bblBoroughCode'].notna()][input_columns_to_keep].sample(n=500, random_state=1).copy()

# Prepare parameters for API

# Note: You can re-use the headers_param you set in Example #1

# Store the relevant url endpoint 

bbl_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/bbl.json"

# After reviewing the API documentation, specify the response columns you are interested in keeping

bbl_return_columns_to_keep = ['bbl','buildingIdentificationNumber',
    'latitudeInternalLabel','longitudeInternalLabel',
    'internalLabelXCoordinate', 'internalLabelYCoordinate',
    'numberOfEntriesInListOfGeographicIdentifiers','numberOfExistingStructuresOnLot',
    'numberOfStreetFrontagesOfLot',
    'geosupportFunctionCode',
    'geosupportReturnCode', 'returnCode1a'
]

# Call the API using the custom function
# Save the result in a new pandas dataframe 'oti_api_bbl_output_df'

oti_api_bbl_output_df = oti_geoclient_api_bbl_endpoint(
    api_endpoint= bbl_api_url_param,
    headers= headers_param,
    df_name= bbl_input_df,
    df_key_field='row_id',
    boro_input_col='bblBoroughCode',
    block_input_col='bblTaxBlock',
    lot_input_col='bblTaxLot',
    response_columns= bbl_return_columns_to_keep)

# Export geocoded output to csv

oti_api_bbl_output_df.to_csv('oti_api_bbl_output_df.csv', index=False)

```
