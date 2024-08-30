# Author: Edgar Alfonseca
# LinkedIn: https://www.linkedin.com/in/edgar-alfonseca/
# GitHub: https://github.com/edgaralfonseca
#
# This Python script creates three functions that enable you to geocode location information using the NYC OTI Geoclient API v1.0
# 1) oti_geoclient_api_address_endpoint: Sends a pandas dataframe (with address data points) to the API and returns a copy of the pandas dataframe with API results
# 2) oti_geoclient_api_bin_endpoint: Sends a pandas dataframe (with BIN data points) to the API and returns a copy of the pandas dataframe with API results
# 3) oti_geoclient_api_bbl_endpoint: Sends a pandas dataframe (with BBL data points) to the API and returns a copy of the pandas dataframe with API results
#
# API description: https://api-portal.nyc.gov/api-details#api=geoclient&operation=geoclient
# v1.0 documentation: https://api.nyc.gov/geoclient/v1/doc/
# GitHub repo: https://github.com/CityOfNewYork/geoclient

# Pre-requisites
#
# 1) Create a new account on the NYC API Developers Portal: https://api-portal.nyc.gov/
# 2) Request an API key by subscribing to the Geoclient API in the portal

# Notes
# The OTI geoclient api handles 2,500 requests per minute / 500,000 requests per day
# NYC Department of City Planning's Geosupport (https://www.nyc.gov/site/planning/data-maps/open-data/dwn-gde-home.page) is used to power Geoclient
# Sometimes there might be a several week delay in Geoclient reflecting what is in GeoSupport
# Geoclient serves up a subset of attributes whereas Geosupport has all attributes

# Import necessary python modules and prepare data

import pandas as pd
import requests
import numpy as np
import time

# Create a custom function to make API calls to the 'Address' endpoint

def oti_geoclient_api_address_endpoint(api_endpoint, headers, df_name, df_key_field, housenum_input_col, street_input_col, boro_input_col=None, zip_input_col=None, response_columns=None):
    """
    Fetch data from the OTI geoclient API, merge the response with the original dataframe, and return the merged dataframe.

    Parameters:
    - api_endpoint (str): The API endpoint URL.
    - headers (dict): The headers to send with the API request.
    - df_name (pd.DataFrame): The input pandas DataFrame.
    - df_key_field (str): The name of the primary key column in the DataFrame.
    - housenum_input_col (str): The name of the column in the DataFrame that provides the house number for the API.
    - street_input_col (str): The name of the column in the DataFrame that provides the street name for the API.
    - boro_input_col (str): The name of the column in the DataFrame that provides the borough for the API (required if zip is not given).
    - zip_input_col (str): The name of the column in the DataFrame that provides the zip code for the API (required if borough is not given).
    - response_columns (dict): Optional. A dictionary specifying which API response columns you want to keep.

    Returns:
    - pd.DataFrame: The merged DataFrame containing the original data and the filtered API response data.
    """

    # Create a session object
    session = requests.Session()
    session.headers.update(headers)

    # Define the function to send a request
    def send_request(house_number, street, borough=None, zip_code=None):
        params = {
            'houseNumber': house_number,
            'street': street,
        }
        if borough:
            params['borough'] = borough
        if zip_code:
            params['zip'] = zip_code

        try:
            response = session.get(api_endpoint, params=params, headers=headers)
            if response.status_code == 200:
                json_response = response.json()  # Parse the JSON response
                if 'address' in json_response:
                    return json_response['address']  # Return the 'address' object
                else:
                    return {}
            else:
                return {}
        except Exception as e:
            return {}

    # Prepare data for processing
    house_numbers = df_name[housenum_input_col].tolist()
    streets = df_name[street_input_col].tolist()
    boroughs = df_name[boro_input_col].tolist() if boro_input_col else [None] * len(df_name)
    zip_codes = df_name[zip_input_col].tolist() if zip_input_col else [None] * len(df_name)
    key_field_values = df_name[df_key_field].tolist()

    # List to store results
    results = []

    # Calculate the delay needed to stay within the rate limit
    delay_per_request = 60 / 2500  # 60 seconds divided by 2500 requests

    # Send requests sequentially with delay
    for house_number, street, borough, zip_code in zip(house_numbers, streets, boroughs, zip_codes):
        result = send_request(house_number, street, borough, zip_code)
        results.append(result)
        time.sleep(delay_per_request)  # Delay between requests to respect the rate limit

    # Convert the list of responses to a DataFrame
    if results and any(results):  # Check if results list is not empty and contains non-empty dictionaries
        response_df = pd.DataFrame(results)

        # If response_columns dictionary is provided, filter to keep only those columns
        if response_columns:
            response_df = response_df[response_columns]

        # Add the df_key_field from the original dataframe to the response_df for merging
        response_df[df_key_field] = key_field_values

        # Perform a left join of the original DataFrame with the response DataFrame on df_key_field
        merged_df = pd.merge(df_name, response_df, on=df_key_field, how='left')
    else:
        # If all results are empty, return the original DataFrame
        merged_df = df_name.copy()

    # Close the session when done
    session.close()

    return merged_df

# Create a custom function to make API calls to the 'BIN' endpoint

def oti_geoclient_api_bin_endpoint(api_endpoint, headers, df_name, df_key_field, api_input_column, response_columns=None):
    """
    Fetch data from the OTI geoclient API, merge the response with the original dataframe, and return the merged dataframe.

    Parameters:
    - api_endpoint (str): The API endpoint URL.
    - headers (dict): The headers to send with the API request.
    - df_name (pd.DataFrame): The input pandas DataFrame.
    - df_key_field (str): The name of the primary key column in the DataFrame.
    - api_input_column (str): The name of the column in the DataFrame that provides input for the API.
    - response_columns (dict): Optional. A dictionary specifying which API response columns you want to keep.

    Returns:
    - pd.DataFrame: The merged DataFrame containing the original data and the filtered API response data.
    """

    # Create a session object
    session = requests.Session()
    session.headers.update(headers)

    # Define the function to send a request
    def send_request(bin_input):
        params = {'bin': bin_input}
        #print(f"Sending request to API with URL: {api_endpoint} and headers: {headers}")  # Print the full URL and headers
        try:
            response = session.get(api_endpoint, params=params, headers=headers)
            if response.status_code == 200:
                json_response = response.json()  # Parse the JSON response
                if 'bin' in json_response:
                    return json_response['bin']  # Return the 'bin' object
                else:
                    return {}
            else:
                return {}
        except Exception as e:
            #print(f"Request failed for {bin_input}: {e}")
            return {}

    # Prepare data for processing
    bins = df_name[api_input_column].tolist()
    key_field_values = df_name[df_key_field].tolist()

    # List to store results
    results = []

    # Calculate the delay needed to stay within the rate limit
    delay_per_request = 60 / 2500  # 60 seconds divided by 2500 requests

    # Send requests sequentially with delay
    for bin_input in bins:
        result = send_request(bin_input)
        results.append(result)
        time.sleep(delay_per_request)  # Delay between requests to respect the rate limit

    # Convert the list of responses to a DataFrame
    if results and any(results):  # Check if results list is not empty and contains non-empty dictionaries
        response_df = pd.DataFrame(results)

        # If response_columns dictionary is provided, filter to keep only those columns
        if response_columns:
            response_df = response_df[response_columns]

        # Add the df_key_field from the original dataframe to the response_df for merging
        response_df[df_key_field] = key_field_values

        # Perform a left join of the original DataFrame with the response DataFrame on df_key_field
        merged_df = pd.merge(df_name, response_df, on=df_key_field, how='left')
    else:
        # If all results are empty, return the original DataFrame
        #print("API returned empty results for all rows.")
        merged_df = df_name.copy()

    # Close the session when done
    session.close()

    return merged_df

# Create a custom function to make API calls to the 'BBL' endpoint

def oti_geoclient_api_bbl_endpoint(api_endpoint, headers, df_name, df_key_field, boro_input_col, block_input_col, lot_input_col, response_columns=None):
    """
    Fetch data from the OTI geoclient API, merge the response with the original dataframe, and return the merged dataframe.

    Parameters:
    - api_endpoint (str): The API endpoint URL.
    - headers (dict): The headers to send with the API request.
    - df_name (pd.DataFrame): The input pandas DataFrame.
    - df_key_field (str): The name of the primary key column in the DataFrame.
    - boro_input_col (str): The name of the column in the DataFrame that provides the borough input for the API.
    - block_input_col (str): The name of the column in the DataFrame that provides the block input for the API.
    - lot_input_col (str): The name of the column in the DataFrame that provides the lot input for the API.
    - response_columns (dict): Optional. A dictionary specifying which API response columns you want to keep.

    Returns:
    - pd.DataFrame: The merged DataFrame containing the original data and the filtered API response data.
    """

    # Create a session object
    session = requests.Session()
    session.headers.update(headers)

    # Define the function to send a request
    def send_request(borough, block, lot):
        params = {
            'borough': borough,
            'block': block,
            'lot': lot
        }
        #print(f"Sending request to API with URL: {api_endpoint}, params: {params}, and headers: {headers}")  # Print the full URL, params, and headers
        try:
            response = session.get(api_endpoint, params=params)
            if response.status_code == 200:
                json_response = response.json()  # Parse the JSON response
                if 'bbl' in json_response:
                    return json_response['bbl']  # Return the 'bbl' object
                else:
                    return {}
            else:
                return {}
        except Exception as e:
            #print(f"Request failed for bbl {borough}{block}{lot}: {e}")
            return {}

    # Prepare data for processing
    boroughs = df_name[boro_input_col].tolist()
    blocks = df_name[block_input_col].tolist()
    lots = df_name[lot_input_col].tolist()
    key_field_values = df_name[df_key_field].tolist()

    # List to store results
    results = []

    # Calculate the delay needed to stay within the rate limit
    delay_per_request = 60 / 2500  # 60 seconds divided by 2500 requests

    # Send requests sequentially with delay
    for borough, block, lot in zip(boroughs, blocks, lots):
        result = send_request(borough, block, lot)
        results.append(result)
        time.sleep(delay_per_request)  # Delay between requests to respect the rate limit

    # Convert the list of responses to a DataFrame
    if results and any(results):  # Check if results list is not empty and contains non-empty dictionaries
        response_df = pd.DataFrame(results)

        # If response_columns dictionary is provided, filter to keep only those columns
        if response_columns:
            response_df = response_df[response_columns]

        # Add the df_key_field from the original dataframe to the response_df for merging
        response_df[df_key_field] = key_field_values

        # Perform a left join of the original DataFrame with the response DataFrame on df_key_field
        merged_df = pd.merge(df_name, response_df, on=df_key_field, how='left')
    else:
        # If all results are empty, return the original DataFrame
        #print("API returned empty results for all rows.")
        merged_df = df_name.copy()

    # Close the session when done
    session.close()

    return merged_df
