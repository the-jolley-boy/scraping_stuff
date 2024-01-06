import streamlit as st
from urllib.error import URLError
import pandas as pd
import altair as alt
from datetime import datetime
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

@st.cache_data
def get_UN_data():
    df = pd.read_csv("full_staff_dataset.csv")
    df = df.drop('nameid', axis=1)
    return df

def remove_partial_elements(main_list, filter_list):
    filtered_list = []
    
    for item in main_list:
        if any(part in item for part in filter_list):
            filtered_list.append(item)
    
    return filtered_list

try:
    # Title and removing excess space
    st.set_page_config(layout="wide")
    st.title("Staff Data")
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

    # Get DF
    df = get_UN_data()

    # Hardset Name column
    selected_col = "name"

    # Allow 2 dropdowns side by side
    dropdown_columns = st.columns(2)
    dropdown_columns2 = st.columns(2)

    # Select Rows
    with dropdown_columns[0]:
        staff = st.multiselect(
            "Choose Staff Member(s)", df['name']
        )
    #Filter Rows based on staff wanted
    filtered_df = df[df['name'].isin(staff)]

    # Select date(s) you want
    # Gets the current date
    date_options = []
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthyear = ""
    if current_month > 9:
        monthyear = str(current_month) + "/" + str(current_year).replace("20", "")
        current_year = int(str(current_year).replace("20", ""))
    else:
        monthyear = "0" + str(current_month) + "/" + str(current_year).replace("20", "")
        current_month = int("0" + str(current_month))
        current_year = int(str(current_year).replace("20", ""))
    # Gets a list of available dates
    start_month = 11
    start_year = 22
    while True:
        date_options.append(str(start_month) + "/" + str(start_year))
        if start_month >= current_month and start_year >= current_year:
            break
        if start_month == 12:
            start_year = start_year + 1
            start_month = 1
        else:
            start_month = start_month + 1

    with dropdown_columns[1]:
        dates = st.multiselect(
            'What date(s) to filter?',
            date_options
        )

    # Select if you want messages, characters or words
    types_mapping = {'messages':'msg', 'words':'word', 'characters':'char'}
    with dropdown_columns2[0]:
        types = st.multiselect(
            'What type(s) to filter?',
            types_mapping.keys()
        )

    types_values = [types_mapping[label] for label in types]

    # Select what Discord category to filter
    category_mapping = {'Canada':'ca', 'General':'gen', 'Advice & Support':'gen2', 'Important':'imp', 'Sneaker Info':'snki', 'Releases':'snkr', 'Staff':'sta', 'Support':'sup'}
    with dropdown_columns2[1]:
        category = st.multiselect(
            'What Discord category(ies) would you like to filter?',
            category_mapping.keys()
        )
    category_values = [category_mapping[label] for label in category]

    columns = []
    first_row = df.columns.tolist()
    first_row.pop(0)

    columns_dates = remove_partial_elements(first_row, dates)
    columns_types = remove_partial_elements(columns_dates, types_values)
    columns = remove_partial_elements(columns_types, category_values)

    # First checks for no staff selected, then continues
    if not columns:
        st.error("Please select at least one option from each drop down.")
    else:
        if columns:

            #Remove if not asked for 
            if "gen2" not in category_values and "gen" in category_values:
                columns = [ x for x in columns if "gen2" not in x ]

            # Adding default column to the selected ones.
            sel = [selected_col] + columns
            st.write("List of staff and their data.", filtered_df[sel])
        else:
            st.write(filtered_df)

        sel = [selected_col] + columns
        data = filtered_df[sel]
        #data.set_index('name', inplace=True)
        #data = data.T

        altair_df = data.melt(id_vars='name', var_name='Item', value_name='Value')

        # , height=90, width={"step": 100}
        chart = alt.Chart(altair_df).mark_bar(size=10).encode(
            x=alt.X('name:N', title='Name'),
            y=alt.Y('sum(Value):Q', title='Total Msg/Word/Char'),
            color='name:N',
            column='Item:N'
        ).properties(
            width=alt.Step(30)
        )

        cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1])
        with cols[0]:
            st.altair_chart(chart)

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )