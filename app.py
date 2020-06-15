import json
from io import BytesIO

import pycurl
import streamlit as st
import zipcodes

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


def main():
    st.title("Churn Prediction")

    url = st.text_input("Input endpoint url.")
    token = st.text_input("Input token.")
    state = st.selectbox('State', states, index=states.index('ME'))
    area_codes = set()
    for r in zipcodes.filter_by(state=state):
        area_codes.update(r['area_codes'])
    area_codes = list(area_codes)
    if '408' in area_codes:
        area_code = st.selectbox('Area code',
                                 area_codes,
                                 index=area_codes.index('408'))
    else:
        area_code = st.selectbox('Area code',
                                 area_codes,
                                 index=0)
    area_code = int(area_code)
    intl_plan = st.checkbox('Intl Plan', value=True)
    intl_plan = 1 if intl_plan else 0

    vmail_plan = st.checkbox('VMail Plan', value=True)
    vmail_plan = 1 if vmail_plan else 0

    vmail_message = st.number_input('VMail Message',
                                    min_value=0,
                                    max_value=None,
                                    value=21,
                                    step=1)
    custserv_calls = st.number_input('CustServ Calls',
                                     min_value=0,
                                     max_value=None,
                                     value=4,
                                     step=1)
    day_mins = st.number_input('Day Mins',
                               min_value=0.0,
                               max_value=None,
                               value=156.5,
                               step=0.1)
    day_calls = st.number_input('Day Calls',
                                min_value=0,
                                max_value=None,
                                value=122,
                                step=1)
    eve_mins = st.number_input('Eve Mins',
                               min_value=0.0,
                               max_value=None,
                               value=209.2,
                               step=0.1)
    eve_calls = st.number_input('Eve Calls',
                                min_value=0,
                                max_value=None,
                                value=125,
                                step=1)
    night_mins = st.number_input('Night Mins',
                                 min_value=0.0,
                                 max_value=None,
                                 value=158.7,
                                 step=0.1)
    night_calls = st.number_input('Night Calls',
                                  min_value=0,
                                  max_value=None,
                                  value=81,
                                  step=1)
    intl_mins = st.number_input('Intl Mins',
                                min_value=0.0,
                                max_value=None,
                                value=11.1,
                                step=0.1)
    intl_calls = st.number_input('Intl Calls',
                                 min_value=0,
                                 max_value=None,
                                 value=81,
                                 step=3)

    if url and token:
        if url[:4] == 'http' and url[4] != 's':
            url = 'https' + url[4:]

        data = {
            "State": state,
            "Area_Code": area_code,
            "Intl_Plan": intl_plan,
            "VMail_Plan": vmail_plan,
            "VMail_Message": vmail_message,
            "CustServ_Calls": custserv_calls,
            "Day_Mins": day_mins,
            "Day_Calls": day_calls,
            "Eve_Mins": eve_mins,
            "Eve_Calls": eve_calls,
            "Night_Mins": night_mins,
            "Night_Calls": night_calls,
            "Intl_Mins": intl_mins,
            "Intl_Calls": intl_calls
        }
        data = json.dumps(data).encode('utf-8')

        headers = ['Content-Type: application/json']
        headers.append('X-Bedrock-Api-Token: ' + token)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, headers)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.TIMEOUT_MS, 30000)
        c.setopt(pycurl.POSTFIELDSIZE, len(data))
        c.setopt(pycurl.READDATA, BytesIO(data))
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.perform()
        c.close()

        prob = json.loads(buffer.getvalue().decode('utf-8'))["churn_prob"]

        st.subheader(f"Probability of churn = {prob:.6f}")


if __name__ == "__main__":
    main()
