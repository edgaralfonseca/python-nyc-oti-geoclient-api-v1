```python
# Author: Edgar Alfonseca
# LinkedIn: https://www.linkedin.com/in/edgar-alfonseca/
# GitHub: https://github.com/edgaralfonseca
#
# This Python script batch geocodes addresses using the NYC OTI Geoclient API v1.0
#
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
```


```python
# Import necessary python modules and prepare data

import pandas as pd
import requests
import numpy as np
import time
```


```python
# Import sample NYC address data (close to 6k records)

url = "https://raw.githubusercontent.com/edgaralfonseca/python-oti-geoclient-api-v1/main/nyc_sample_almost_6k_addresses.csv"

nyc_address_df = pd.read_csv(url)

# minor data cleaning on the postcode (zip code)

nyc_address_df['postcode'] = nyc_address_df['postcode'].astype(str).str[:5]
```


```python
nyc_address_df.head(10)
```





  <div id="df-f7a56bd9-d883-4620-b161-8f8db7878e78" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>row_id</th>
      <th>house_number</th>
      <th>street_name</th>
      <th>borough</th>
      <th>postcode</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>114</td>
      <td>SEIGEL STREET</td>
      <td>Brooklyn</td>
      <td>11206</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>1920</td>
      <td>UNION STREET</td>
      <td>Brooklyn</td>
      <td>11233</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2555</td>
      <td>WILLIAMSBRIDGE ROAD</td>
      <td>Bronx</td>
      <td>10469</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>763</td>
      <td>JENNINGS STREET</td>
      <td>Bronx</td>
      <td>10459</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>275</td>
      <td>PRESIDENT STREET</td>
      <td>Brooklyn</td>
      <td>11231</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>1402</td>
      <td>NEW YORK AVENUE</td>
      <td>Brooklyn</td>
      <td>11210</td>
    </tr>
    <tr>
      <th>6</th>
      <td>7</td>
      <td>658</td>
      <td>DRIGGS AVENUE</td>
      <td>Brooklyn</td>
      <td>11211</td>
    </tr>
    <tr>
      <th>7</th>
      <td>8</td>
      <td>740</td>
      <td>EAST 222 STREET</td>
      <td>Bronx</td>
      <td>10467</td>
    </tr>
    <tr>
      <th>8</th>
      <td>9</td>
      <td>390</td>
      <td>1 AVENUE</td>
      <td>Manhattan</td>
      <td>10010</td>
    </tr>
    <tr>
      <th>9</th>
      <td>10</td>
      <td>91</td>
      <td>VISITATION PLACE</td>
      <td>Brooklyn</td>
      <td>11231</td>
    </tr>
  </tbody>
</table>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-f7a56bd9-d883-4620-b161-8f8db7878e78')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-f7a56bd9-d883-4620-b161-8f8db7878e78 button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-f7a56bd9-d883-4620-b161-8f8db7878e78');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>


<div id="df-34b7141c-6c6a-4aba-88d5-c46eb569407e">
  <button class="colab-df-quickchart" onclick="quickchart('df-34b7141c-6c6a-4aba-88d5-c46eb569407e')"
            title="Suggest charts"
            style="display:none;">

<svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
     width="24px">
    <g>
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
    </g>
</svg>
  </button>

<style>
  .colab-df-quickchart {
      --bg-color: #E8F0FE;
      --fill-color: #1967D2;
      --hover-bg-color: #E2EBFA;
      --hover-fill-color: #174EA6;
      --disabled-fill-color: #AAA;
      --disabled-bg-color: #DDD;
  }

  [theme=dark] .colab-df-quickchart {
      --bg-color: #3B4455;
      --fill-color: #D2E3FC;
      --hover-bg-color: #434B5C;
      --hover-fill-color: #FFFFFF;
      --disabled-bg-color: #3B4455;
      --disabled-fill-color: #666;
  }

  .colab-df-quickchart {
    background-color: var(--bg-color);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    fill: var(--fill-color);
    height: 32px;
    padding: 0;
    width: 32px;
  }

  .colab-df-quickchart:hover {
    background-color: var(--hover-bg-color);
    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    fill: var(--button-hover-fill-color);
  }

  .colab-df-quickchart-complete:disabled,
  .colab-df-quickchart-complete:disabled:hover {
    background-color: var(--disabled-bg-color);
    fill: var(--disabled-fill-color);
    box-shadow: none;
  }

  .colab-df-spinner {
    border: 2px solid var(--fill-color);
    border-color: transparent;
    border-bottom-color: var(--fill-color);
    animation:
      spin 1s steps(1) infinite;
  }

  @keyframes spin {
    0% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
      border-left-color: var(--fill-color);
    }
    20% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    30% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
      border-right-color: var(--fill-color);
    }
    40% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    60% {
      border-color: transparent;
      border-right-color: var(--fill-color);
    }
    80% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-bottom-color: var(--fill-color);
    }
    90% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
    }
  }
</style>

  <script>
    async function quickchart(key) {
      const quickchartButtonEl =
        document.querySelector('#' + key + ' button');
      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.
      quickchartButtonEl.classList.add('colab-df-spinner');
      try {
        const charts = await google.colab.kernel.invokeFunction(
            'suggestCharts', [key], {});
      } catch (error) {
        console.error('Error during call to suggestCharts:', error);
      }
      quickchartButtonEl.classList.remove('colab-df-spinner');
      quickchartButtonEl.classList.add('colab-df-quickchart-complete');
    }
    (() => {
      let quickchartButtonEl =
        document.querySelector('#df-34b7141c-6c6a-4aba-88d5-c46eb569407e button');
      quickchartButtonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';
    })();
  </script>
</div>

    </div>
  </div>




**Example 1: Calling the OTI Geoclient "Address" API endpoint**

Create a custom function that takes a pandas dataframe (what you want to geocode) as an input and creates an output that is a copy of your original dataframe left joined to the API results.


```python
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
```


```python
# Create a copy of the nyc address pandas dataframe and sample 1000 records

address_input_df = nyc_address_df.sample(n=1000, random_state=1).copy()
```


```python
# Prepare parameters for API

# Read the subscription key from a text file

with open('/content/OTI geoclient API primary key.txt', 'r') as file:
    subscription_key = file.read().strip()

# Set the headers with the subscription key
headers_param = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': subscription_key
}

address_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/address.json"

search_return_columns_to_keep = ['bbl', 'bblBoroughCode', 'bblTaxBlock',
    'bblTaxLot', 'buildingIdentificationNumber', 'latitude', 'longitude',
    'xCoordinate', 'yCoordinate', 'communityDistrict', 'communityDistrictNumber',
    'geosupportFunctionCode',
    'geosupportReturnCode', 'geosupportReturnCode2', 'returnCode1a', 'returnCode1e'
]
```


```python
# Call the API using the custom function

oti_api_address_output_df = oti_geoclient_api_address_endpoint(
    api_endpoint= address_api_url_param,
    headers= headers_param,
    df_name= address_input_df,
    df_key_field='row_id',
    housenum_input_col = 'house_number', street_input_col = 'street_name' , boro_input_col= 'borough' , zip_input_col= 'postcode',
    response_columns= search_return_columns_to_keep)
```


```python
# Review api output dataframe

oti_api_address_output_df.head(10)
```





  <div id="df-4ee253fd-c90f-4ca5-ae85-7364a95b9fd1" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>row_id</th>
      <th>house_number</th>
      <th>street_name</th>
      <th>borough</th>
      <th>postcode</th>
      <th>bbl</th>
      <th>bblBoroughCode</th>
      <th>bblTaxBlock</th>
      <th>bblTaxLot</th>
      <th>buildingIdentificationNumber</th>
      <th>...</th>
      <th>longitude</th>
      <th>xCoordinate</th>
      <th>yCoordinate</th>
      <th>communityDistrict</th>
      <th>communityDistrictNumber</th>
      <th>geosupportFunctionCode</th>
      <th>geosupportReturnCode</th>
      <th>geosupportReturnCode2</th>
      <th>returnCode1a</th>
      <th>returnCode1e</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2597</td>
      <td>141</td>
      <td>5 AVENUE</td>
      <td>Brooklyn</td>
      <td>11217</td>
      <td>3009470011</td>
      <td>3</td>
      <td>00947</td>
      <td>0011</td>
      <td>3019401</td>
      <td>...</td>
      <td>-73.979230</td>
      <td>0990011</td>
      <td>0186368</td>
      <td>306</td>
      <td>06</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4698</td>
      <td>305</td>
      <td>EAST HOUSTON STREET</td>
      <td>Manhattan</td>
      <td>10002</td>
      <td>1003500056</td>
      <td>1</td>
      <td>00350</td>
      <td>0056</td>
      <td>1004268</td>
      <td>...</td>
      <td>-73.983445</td>
      <td>0988839</td>
      <td>0202084</td>
      <td>103</td>
      <td>03</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3978</td>
      <td>411</td>
      <td>EAST 10 STREET</td>
      <td>Manhattan</td>
      <td>10009</td>
      <td>1003820100</td>
      <td>1</td>
      <td>00382</td>
      <td>0100</td>
      <td>1078024</td>
      <td>...</td>
      <td>-73.976910</td>
      <td>0990650</td>
      <td>0203643</td>
      <td>103</td>
      <td>03</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2237</td>
      <td>1597</td>
      <td>NEW YORK AVENUE</td>
      <td>Brooklyn</td>
      <td>11210</td>
      <td>3075610037</td>
      <td>3</td>
      <td>07561</td>
      <td>0037</td>
      <td>3428759</td>
      <td>...</td>
      <td>-73.944801</td>
      <td>0999571</td>
      <td>0170098</td>
      <td>317</td>
      <td>17</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2295</td>
      <td>511</td>
      <td>EAST 20 STREET</td>
      <td>Manhattan</td>
      <td>10010</td>
      <td>1009780001</td>
      <td>1</td>
      <td>00978</td>
      <td>0001</td>
      <td>1083689</td>
      <td>...</td>
      <td>-73.977340</td>
      <td>0990530</td>
      <td>0206629</td>
      <td>106</td>
      <td>06</td>
      <td>1B</td>
      <td>00</td>
      <td>01</td>
      <td>01</td>
      <td>00</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2739</td>
      <td>253</td>
      <td>NOSTRAND AVENUE</td>
      <td>Brooklyn</td>
      <td>11205</td>
      <td>3017847502</td>
      <td>3</td>
      <td>01784</td>
      <td>7502</td>
      <td>3426325</td>
      <td>...</td>
      <td>-73.951515</td>
      <td>0997696</td>
      <td>0190727</td>
      <td>303</td>
      <td>03</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2409</td>
      <td>1224</td>
      <td>JEROME STREET</td>
      <td>Brooklyn</td>
      <td>11239</td>
      <td>3044520213</td>
      <td>3</td>
      <td>04452</td>
      <td>0213</td>
      <td>3421577</td>
      <td>...</td>
      <td>-73.876619</td>
      <td>1018485</td>
      <td>0177486</td>
      <td>305</td>
      <td>05</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>7</th>
      <td>3946</td>
      <td>45-57</td>
      <td>DAVIS STREET</td>
      <td>Queens</td>
      <td>11101</td>
      <td>4000850030</td>
      <td>4</td>
      <td>00085</td>
      <td>0030</td>
      <td>4000715</td>
      <td>...</td>
      <td>-73.944615</td>
      <td>0999597</td>
      <td>0210435</td>
      <td>402</td>
      <td>02</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1265</td>
      <td>210</td>
      <td>WEST 150 STREET</td>
      <td>Manhattan</td>
      <td>10039</td>
      <td>1020350001</td>
      <td>1</td>
      <td>02035</td>
      <td>0001</td>
      <td>1084147</td>
      <td>...</td>
      <td>-73.937404</td>
      <td>1001574</td>
      <td>0239877</td>
      <td>110</td>
      <td>10</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>9</th>
      <td>3170</td>
      <td>864</td>
      <td>49 STREET</td>
      <td>Brooklyn</td>
      <td>11220</td>
      <td>3056370032</td>
      <td>3</td>
      <td>05637</td>
      <td>0032</td>
      <td>3137539</td>
      <td>...</td>
      <td>-74.001794</td>
      <td>0983752</td>
      <td>0172760</td>
      <td>312</td>
      <td>12</td>
      <td>1B</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
      <td>00</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 21 columns</p>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-4ee253fd-c90f-4ca5-ae85-7364a95b9fd1')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-4ee253fd-c90f-4ca5-ae85-7364a95b9fd1 button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-4ee253fd-c90f-4ca5-ae85-7364a95b9fd1');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>


<div id="df-d4f3e1f3-221e-4a61-9b2a-98ae80496ccd">
  <button class="colab-df-quickchart" onclick="quickchart('df-d4f3e1f3-221e-4a61-9b2a-98ae80496ccd')"
            title="Suggest charts"
            style="display:none;">

<svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
     width="24px">
    <g>
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
    </g>
</svg>
  </button>

<style>
  .colab-df-quickchart {
      --bg-color: #E8F0FE;
      --fill-color: #1967D2;
      --hover-bg-color: #E2EBFA;
      --hover-fill-color: #174EA6;
      --disabled-fill-color: #AAA;
      --disabled-bg-color: #DDD;
  }

  [theme=dark] .colab-df-quickchart {
      --bg-color: #3B4455;
      --fill-color: #D2E3FC;
      --hover-bg-color: #434B5C;
      --hover-fill-color: #FFFFFF;
      --disabled-bg-color: #3B4455;
      --disabled-fill-color: #666;
  }

  .colab-df-quickchart {
    background-color: var(--bg-color);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    fill: var(--fill-color);
    height: 32px;
    padding: 0;
    width: 32px;
  }

  .colab-df-quickchart:hover {
    background-color: var(--hover-bg-color);
    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    fill: var(--button-hover-fill-color);
  }

  .colab-df-quickchart-complete:disabled,
  .colab-df-quickchart-complete:disabled:hover {
    background-color: var(--disabled-bg-color);
    fill: var(--disabled-fill-color);
    box-shadow: none;
  }

  .colab-df-spinner {
    border: 2px solid var(--fill-color);
    border-color: transparent;
    border-bottom-color: var(--fill-color);
    animation:
      spin 1s steps(1) infinite;
  }

  @keyframes spin {
    0% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
      border-left-color: var(--fill-color);
    }
    20% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    30% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
      border-right-color: var(--fill-color);
    }
    40% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    60% {
      border-color: transparent;
      border-right-color: var(--fill-color);
    }
    80% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-bottom-color: var(--fill-color);
    }
    90% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
    }
  }
</style>

  <script>
    async function quickchart(key) {
      const quickchartButtonEl =
        document.querySelector('#' + key + ' button');
      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.
      quickchartButtonEl.classList.add('colab-df-spinner');
      try {
        const charts = await google.colab.kernel.invokeFunction(
            'suggestCharts', [key], {});
      } catch (error) {
        console.error('Error during call to suggestCharts:', error);
      }
      quickchartButtonEl.classList.remove('colab-df-spinner');
      quickchartButtonEl.classList.add('colab-df-quickchart-complete');
    }
    (() => {
      let quickchartButtonEl =
        document.querySelector('#df-d4f3e1f3-221e-4a61-9b2a-98ae80496ccd button');
      quickchartButtonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';
    })();
  </script>
</div>

    </div>
  </div>





```python
# Export geocoded output to csv

oti_api_address_output_df.to_csv('oti_api_address_output_df.csv', index=False)
```

**Example 2: Using the OTI Geoclient BIN API endpoint**

A BIN (Building Identification Nummber) is a unique, immutable, citywide standard for building identification developed by NYC Department of City Planning. Is is a 7-byte numeric item. You can read more about them here: https://nycplanning.github.io/Geosupport-UPG/chapters/chapterVI/section03/


```python
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
```


```python
# Prepare a pandas dataframe to pass to OTI api

# Specify the columns you want to keep from the original dataframe

input_columns_to_keep = ['row_id', 'buildingIdentificationNumber']  # Replace with the columns you want to keep

# Create a copy of the OTI address output pandas dataframe and sample 500 records

bin_input_df = oti_api_address_output_df[oti_api_address_output_df['buildingIdentificationNumber'].notna()][input_columns_to_keep].sample(n=500, random_state=1).copy()
```


```python
# Prepare parameters for API

# Read the subscription key from a text file

with open('/content/OTI geoclient API primary key.txt', 'r') as file:
    subscription_key = file.read().strip()

# Set the headers with the subscription key
headers_param = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': subscription_key
}

bin_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/bin.json"

bin_return_columns_to_keep = ['bbl', 'bblBoroughCode', 'bblTaxBlock',
    'bblTaxLot',
    'internalLabelXCoordinate', 'internalLabelYCoordinate',
    'geosupportFunctionCode',
    'geosupportReturnCode'
]
```


```python
# Call the API using the custom function

oti_api_bin_output_df = oti_geoclient_api_bin_endpoint(
    api_endpoint= bin_api_url_param,
    headers= headers_param,
    df_name= bin_input_df,
    df_key_field='row_id',
    api_input_column='buildingIdentificationNumber',
    response_columns= bin_return_columns_to_keep)
```


```python
# Review api output dataframe

oti_api_bin_output_df.head(10)
```





  <div id="df-f53c4641-513d-490d-b66c-4aa26d11a83f" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>row_id</th>
      <th>buildingIdentificationNumber</th>
      <th>bbl</th>
      <th>bblBoroughCode</th>
      <th>bblTaxBlock</th>
      <th>bblTaxLot</th>
      <th>internalLabelXCoordinate</th>
      <th>internalLabelYCoordinate</th>
      <th>geosupportFunctionCode</th>
      <th>geosupportReturnCode</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1029</td>
      <td>3119614</td>
      <td>3051870032</td>
      <td>3</td>
      <td>05187</td>
      <td>0032</td>
      <td>0996555</td>
      <td>0173377</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2305</td>
      <td>3325569</td>
      <td>3032530028</td>
      <td>3</td>
      <td>03253</td>
      <td>0028</td>
      <td>1004718</td>
      <td>0192588</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>725</td>
      <td>3399068</td>
      <td>3017680046</td>
      <td>3</td>
      <td>01768</td>
      <td>0046</td>
      <td>0999932</td>
      <td>0192170</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>5015</td>
      <td>3399250</td>
      <td>3025560058</td>
      <td>3</td>
      <td>02556</td>
      <td>0058</td>
      <td>0995465</td>
      <td>0205275</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4569</td>
      <td>4618244</td>
      <td>4125290239</td>
      <td>4</td>
      <td>12529</td>
      <td>0239</td>
      <td>1047327</td>
      <td>0187467</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>5</th>
      <td>4403</td>
      <td>1079982</td>
      <td>1022000009</td>
      <td>1</td>
      <td>02200</td>
      <td>0009</td>
      <td>1006443</td>
      <td>0253362</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>6</th>
      <td>4897</td>
      <td>1089873</td>
      <td>1015380021</td>
      <td>1</td>
      <td>01538</td>
      <td>0021</td>
      <td>0998244</td>
      <td>0224298</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1580</td>
      <td>1052316</td>
      <td>1016440065</td>
      <td>1</td>
      <td>01644</td>
      <td>0065</td>
      <td>1000269</td>
      <td>0230555</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2163</td>
      <td>3057984</td>
      <td>3020310001</td>
      <td>3</td>
      <td>02031</td>
      <td>0001</td>
      <td>0991669</td>
      <td>0192969</td>
      <td>BN</td>
      <td>00</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2822</td>
      <td>2001152</td>
      <td>2023590210</td>
      <td>2</td>
      <td>02359</td>
      <td>0210</td>
      <td>1008757</td>
      <td>0237672</td>
      <td>BN</td>
      <td>00</td>
    </tr>
  </tbody>
</table>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-f53c4641-513d-490d-b66c-4aa26d11a83f')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-f53c4641-513d-490d-b66c-4aa26d11a83f button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-f53c4641-513d-490d-b66c-4aa26d11a83f');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>


<div id="df-87507e75-839c-4b41-a6ae-ae80d586ee35">
  <button class="colab-df-quickchart" onclick="quickchart('df-87507e75-839c-4b41-a6ae-ae80d586ee35')"
            title="Suggest charts"
            style="display:none;">

<svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
     width="24px">
    <g>
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
    </g>
</svg>
  </button>

<style>
  .colab-df-quickchart {
      --bg-color: #E8F0FE;
      --fill-color: #1967D2;
      --hover-bg-color: #E2EBFA;
      --hover-fill-color: #174EA6;
      --disabled-fill-color: #AAA;
      --disabled-bg-color: #DDD;
  }

  [theme=dark] .colab-df-quickchart {
      --bg-color: #3B4455;
      --fill-color: #D2E3FC;
      --hover-bg-color: #434B5C;
      --hover-fill-color: #FFFFFF;
      --disabled-bg-color: #3B4455;
      --disabled-fill-color: #666;
  }

  .colab-df-quickchart {
    background-color: var(--bg-color);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    fill: var(--fill-color);
    height: 32px;
    padding: 0;
    width: 32px;
  }

  .colab-df-quickchart:hover {
    background-color: var(--hover-bg-color);
    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    fill: var(--button-hover-fill-color);
  }

  .colab-df-quickchart-complete:disabled,
  .colab-df-quickchart-complete:disabled:hover {
    background-color: var(--disabled-bg-color);
    fill: var(--disabled-fill-color);
    box-shadow: none;
  }

  .colab-df-spinner {
    border: 2px solid var(--fill-color);
    border-color: transparent;
    border-bottom-color: var(--fill-color);
    animation:
      spin 1s steps(1) infinite;
  }

  @keyframes spin {
    0% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
      border-left-color: var(--fill-color);
    }
    20% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    30% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
      border-right-color: var(--fill-color);
    }
    40% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    60% {
      border-color: transparent;
      border-right-color: var(--fill-color);
    }
    80% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-bottom-color: var(--fill-color);
    }
    90% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
    }
  }
</style>

  <script>
    async function quickchart(key) {
      const quickchartButtonEl =
        document.querySelector('#' + key + ' button');
      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.
      quickchartButtonEl.classList.add('colab-df-spinner');
      try {
        const charts = await google.colab.kernel.invokeFunction(
            'suggestCharts', [key], {});
      } catch (error) {
        console.error('Error during call to suggestCharts:', error);
      }
      quickchartButtonEl.classList.remove('colab-df-spinner');
      quickchartButtonEl.classList.add('colab-df-quickchart-complete');
    }
    (() => {
      let quickchartButtonEl =
        document.querySelector('#df-87507e75-839c-4b41-a6ae-ae80d586ee35 button');
      quickchartButtonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';
    })();
  </script>
</div>

    </div>
  </div>





```python
# Export geocoded output to csv

oti_api_bin_output_df.to_csv('oti_api_bin_output_df.csv', index=False)
```

**Example 3: Calling the OTI Geoclient BBL API endpoint**

A Borough-Block-and-Lot (BBL) is a single data item used that can be used to uniquely identify a city tax lot. It is maintained by the NYC Department of Finance (DOF). A city tax lot is a a subdivision of the broader city tax geography, which DOF manages.

You can read more about them here: https://nycplanning.github.io/Geosupport-UPG/chapters/chapterVI/section02/


```python
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
```


```python
# Prepare a pandas dataframe to pass to OTI api

# Specify the columns you want to keep from the original dataframe

input_columns_to_keep = ['row_id', 'bblBoroughCode', 'bblTaxBlock', 'bblTaxLot']  # Replace with the columns you want to keep

# Create a copy of the OTI address output pandas dataframe and sample 500 records

bbl_input_df = oti_api_address_output_df[oti_api_address_output_df['bblBoroughCode'].notna()][input_columns_to_keep].sample(n=500, random_state=1).copy()
```


```python
# Prepare parameters for API

# Read the subscription key from a text file

with open('/content/OTI geoclient API primary key.txt', 'r') as file:
    subscription_key = file.read().strip()

# Set the headers with the subscription key
headers_param = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': subscription_key
}

bbl_api_url_param = "https://api.nyc.gov/geo/geoclient/v1/bbl.json"

bbl_return_columns_to_keep = ['bbl','buildingIdentificationNumber',
    'latitudeInternalLabel','longitudeInternalLabel',
    'internalLabelXCoordinate', 'internalLabelYCoordinate',
    'numberOfEntriesInListOfGeographicIdentifiers','numberOfExistingStructuresOnLot',
    'numberOfStreetFrontagesOfLot',
    'geosupportFunctionCode',
    'geosupportReturnCode', 'returnCode1a'
]
```


```python
# Example usage:

oti_api_bbl_output_df = oti_geoclient_api_bbl_endpoint(
    api_endpoint= bbl_api_url_param,
    headers= headers_param,
    df_name= bbl_input_df,
    df_key_field='row_id',
    boro_input_col='bblBoroughCode',
    block_input_col='bblTaxBlock',
    lot_input_col='bblTaxLot',
    response_columns= bbl_return_columns_to_keep)
```


```python
# Review api output dataframe

oti_api_bbl_output_df.head(10)
```





  <div id="df-6de7d0fa-8e6f-451d-8a04-199470ac6632" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>row_id</th>
      <th>bblBoroughCode</th>
      <th>bblTaxBlock</th>
      <th>bblTaxLot</th>
      <th>bbl</th>
      <th>buildingIdentificationNumber</th>
      <th>latitudeInternalLabel</th>
      <th>longitudeInternalLabel</th>
      <th>internalLabelXCoordinate</th>
      <th>internalLabelYCoordinate</th>
      <th>numberOfEntriesInListOfGeographicIdentifiers</th>
      <th>numberOfExistingStructuresOnLot</th>
      <th>numberOfStreetFrontagesOfLot</th>
      <th>geosupportFunctionCode</th>
      <th>geosupportReturnCode</th>
      <th>returnCode1a</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1029</td>
      <td>3</td>
      <td>05187</td>
      <td>0032</td>
      <td>3051870032</td>
      <td>3119614</td>
      <td>40.642548</td>
      <td>-73.955661</td>
      <td>0996555</td>
      <td>0173377</td>
      <td>0003</td>
      <td>0002</td>
      <td>02</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2305</td>
      <td>3</td>
      <td>03253</td>
      <td>0028</td>
      <td>3032530028</td>
      <td>3325569</td>
      <td>40.695263</td>
      <td>-73.926188</td>
      <td>1004718</td>
      <td>0192588</td>
      <td>0001</td>
      <td>0001</td>
      <td>01</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>725</td>
      <td>3</td>
      <td>01768</td>
      <td>0046</td>
      <td>3017680046</td>
      <td>3399068</td>
      <td>40.694125</td>
      <td>-73.943449</td>
      <td>0999932</td>
      <td>0192170</td>
      <td>0001</td>
      <td>0001</td>
      <td>01</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>5015</td>
      <td>3</td>
      <td>02556</td>
      <td>0058</td>
      <td>3025560058</td>
      <td>3399250</td>
      <td>40.730102</td>
      <td>-73.959535</td>
      <td>0995465</td>
      <td>0205275</td>
      <td>0006</td>
      <td>0001</td>
      <td>03</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4569</td>
      <td>4</td>
      <td>12529</td>
      <td>0239</td>
      <td>4125290239</td>
      <td>4618244</td>
      <td>40.681006</td>
      <td>-73.772580</td>
      <td>1047327</td>
      <td>0187467</td>
      <td>0001</td>
      <td>0001</td>
      <td>01</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>5</th>
      <td>4403</td>
      <td>1</td>
      <td>02200</td>
      <td>0009</td>
      <td>1022000009</td>
      <td>1079981</td>
      <td>40.862067</td>
      <td>-73.919767</td>
      <td>1006443</td>
      <td>0253362</td>
      <td>0003</td>
      <td>0003</td>
      <td>01</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>6</th>
      <td>4897</td>
      <td>1</td>
      <td>01538</td>
      <td>0021</td>
      <td>1015380021</td>
      <td>1078601</td>
      <td>40.782311</td>
      <td>-73.949469</td>
      <td>0998244</td>
      <td>0224298</td>
      <td>0003</td>
      <td>0003</td>
      <td>03</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1580</td>
      <td>1</td>
      <td>01644</td>
      <td>0065</td>
      <td>1016440065</td>
      <td>1052316</td>
      <td>40.799482</td>
      <td>-73.942142</td>
      <td>1000269</td>
      <td>0230555</td>
      <td>0001</td>
      <td>0001</td>
      <td>01</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2163</td>
      <td>3</td>
      <td>02031</td>
      <td>0001</td>
      <td>3020310001</td>
      <td>3057984</td>
      <td>40.696329</td>
      <td>-73.973245</td>
      <td>0991669</td>
      <td>0192969</td>
      <td>0002</td>
      <td>0001</td>
      <td>02</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2822</td>
      <td>2</td>
      <td>02359</td>
      <td>0210</td>
      <td>2023590210</td>
      <td>2001152</td>
      <td>40.818996</td>
      <td>-73.911459</td>
      <td>1008757</td>
      <td>0237672</td>
      <td>0004</td>
      <td>0001</td>
      <td>02</td>
      <td>BL</td>
      <td>00</td>
      <td>00</td>
    </tr>
  </tbody>
</table>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-6de7d0fa-8e6f-451d-8a04-199470ac6632')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-6de7d0fa-8e6f-451d-8a04-199470ac6632 button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-6de7d0fa-8e6f-451d-8a04-199470ac6632');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>


<div id="df-ee26c3f2-a661-4526-a751-dd966ec733df">
  <button class="colab-df-quickchart" onclick="quickchart('df-ee26c3f2-a661-4526-a751-dd966ec733df')"
            title="Suggest charts"
            style="display:none;">

<svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
     width="24px">
    <g>
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
    </g>
</svg>
  </button>

<style>
  .colab-df-quickchart {
      --bg-color: #E8F0FE;
      --fill-color: #1967D2;
      --hover-bg-color: #E2EBFA;
      --hover-fill-color: #174EA6;
      --disabled-fill-color: #AAA;
      --disabled-bg-color: #DDD;
  }

  [theme=dark] .colab-df-quickchart {
      --bg-color: #3B4455;
      --fill-color: #D2E3FC;
      --hover-bg-color: #434B5C;
      --hover-fill-color: #FFFFFF;
      --disabled-bg-color: #3B4455;
      --disabled-fill-color: #666;
  }

  .colab-df-quickchart {
    background-color: var(--bg-color);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    fill: var(--fill-color);
    height: 32px;
    padding: 0;
    width: 32px;
  }

  .colab-df-quickchart:hover {
    background-color: var(--hover-bg-color);
    box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
    fill: var(--button-hover-fill-color);
  }

  .colab-df-quickchart-complete:disabled,
  .colab-df-quickchart-complete:disabled:hover {
    background-color: var(--disabled-bg-color);
    fill: var(--disabled-fill-color);
    box-shadow: none;
  }

  .colab-df-spinner {
    border: 2px solid var(--fill-color);
    border-color: transparent;
    border-bottom-color: var(--fill-color);
    animation:
      spin 1s steps(1) infinite;
  }

  @keyframes spin {
    0% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
      border-left-color: var(--fill-color);
    }
    20% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    30% {
      border-color: transparent;
      border-left-color: var(--fill-color);
      border-top-color: var(--fill-color);
      border-right-color: var(--fill-color);
    }
    40% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-top-color: var(--fill-color);
    }
    60% {
      border-color: transparent;
      border-right-color: var(--fill-color);
    }
    80% {
      border-color: transparent;
      border-right-color: var(--fill-color);
      border-bottom-color: var(--fill-color);
    }
    90% {
      border-color: transparent;
      border-bottom-color: var(--fill-color);
    }
  }
</style>

  <script>
    async function quickchart(key) {
      const quickchartButtonEl =
        document.querySelector('#' + key + ' button');
      quickchartButtonEl.disabled = true;  // To prevent multiple clicks.
      quickchartButtonEl.classList.add('colab-df-spinner');
      try {
        const charts = await google.colab.kernel.invokeFunction(
            'suggestCharts', [key], {});
      } catch (error) {
        console.error('Error during call to suggestCharts:', error);
      }
      quickchartButtonEl.classList.remove('colab-df-spinner');
      quickchartButtonEl.classList.add('colab-df-quickchart-complete');
    }
    (() => {
      let quickchartButtonEl =
        document.querySelector('#df-ee26c3f2-a661-4526-a751-dd966ec733df button');
      quickchartButtonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';
    })();
  </script>
</div>

    </div>
  </div>





```python
# Export geocoded output to csv

oti_api_bbl_output_df.to_csv('oti_api_bbl_output_df.csv', index=False)
```
