import requests
import pandas as pd
from io import StringIO
# import json

# URL for the AJAX request
def rationCardTables(form_data):
    url = "https://aepos.ap.gov.in/ShopAbstractM.jsp"
    # Send POST request to fetch table data
    response = requests.post(url, data=form_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Wrap the HTML content in a StringIO object
        html_content = StringIO(response.text)
        
        # Parse the HTML content using pandas
        try:
            tables = pd.read_html(html_content,header=None)
            if tables:
                df = tables[0]  # Assuming the first table is the one you need
                DataDetail = df.keys()[0][0].replace("'"," ")
                # print(DataDetail)
                # print(repr(DataDetail))
                df.columns = df.columns.map(lambda x: x[-1])
                # lk=df
                try:
                    TotalRice = df['Fortified Rice (Kgs)'].iloc[-1]
                    df = df[:-1]
                    df = df[['Sl No','Date','Fortified Rice (Kgs)']]
                except KeyError as e:
                    TotalRice = df['Sortex Rice (Kgs)'].iloc[-1]
                    df = df[:-1]
                    df = df[['Sl No','Date','Sortex Rice (Kgs)']]
                df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
                # print(df)
            else:
                print("No tables found in the page source.")
        except ValueError as e:
            # print(f"Error parsing HTML: {e}")
            shop_no = form_data["shop_no"]
            month_names = ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
            month = month_names[int(form_data["month"])-1]
            year = form_data["year"]
            type_names = ["All pds","Cash pds","Cashless pds"]
            type = type_names[int(form_data["type"])-1]
            raise Exception(f"No Transaction Details Found for FPS {shop_no} for {month} in {year} for {type}")
    else:
        # print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
        raise Exception(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
    
    # Group by 'date' and aggregate
    try:
        aggregated_df = df.groupby('Date').agg(
            count=('Fortified Rice (Kgs)', 'size'),
            total_weight=('Fortified Rice (Kgs)', 'sum')
        ).reset_index()
    except KeyError as e:
        aggregated_df = df.groupby('Date').agg(
            count=('Sortex Rice (Kgs)', 'size'),
            total_weight=('Sortex Rice (Kgs)', 'sum')
        ).reset_index()
    # Format the 'date' column as 'day: month: year'
    aggregated_df['Date'] = aggregated_df['Date'].dt.strftime('%d-%b-%Y')
    
    # Add a serial number column
    aggregated_df['serial_number'] = range(1, len(aggregated_df) + 1)
    
    # Reorder columns to have 'serial_number' as the first column
    aggregated_df = aggregated_df[['serial_number', 'Date', 'count', 'total_weight']]
    TotalCards = aggregated_df['count'].sum()
    table = aggregated_df.to_dict(orient='records')
    dictionary = {
        'DataDetail': DataDetail,
        'TotalRice': TotalRice.item(),
        'TotalCards': TotalCards.item(),
        'table': table
    }
    # json_data = json.dumps(dictionary)
    # return json_data
    return dictionary