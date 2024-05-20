# import streamlit as st
# # import wget
# import subprocess
# import datetime

# def runcmd(cmd, verbose=False):
#     process = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         shell=True
#     )
#     std_out, std_err = process.communicate()
#     if verbose:
#         st.write(std_out.strip(), std_err)
#     return std_out.strip()


# def main():
#     st.title("Nepal Stock Market Data")

#     # # Get today's date in YEAR-MONTH-DAY format
#     today = datetime.date.today() - datetime.timedelta(days=3)

#     # # Download the CSV file
#     df_out = runcmd(f'cat {today} || wget --no-check-certificate https://www.nepalstock.com.np/api/nots/market/export/todays-price/{today}', verbose=False)
#     # print(df_out)

#     st.write(df_out)


# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
import datetime


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return response.text
    except requests.RequestException as e:
        st.error(f"Failed to fetch data: {e}")


def main():
    st.title("Nepal Stock Market Data")

    # Get today's date in YEAR-MONTH-DAY format
    today = datetime.date.today() - datetime.timedelta(days=3)

    # Construct the URL for the API endpoint
    url = f"https://www.nepalstock.com.np/api/nots/market/export/todays-price/{today}"

    # Fetch the data
    data = fetch_data(url)
    print(data)
    # Display the data
    if data:
        st.write(data)


if __name__ == "__main__":
    main()
