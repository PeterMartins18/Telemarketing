# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Set seaborn theme for better plot visuals
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Function to read data
@st.cache(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

# Function to filter based on multi-selection of categories
@st.cache
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Function to convert df to csv
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to convert df to excel
@st.cache
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# Main function of the application
def main():
    # Initial page configuration
    st.set_page_config(page_title='Telemarketing Analysis',
                       page_icon='telmarketing_icon.png',
                       layout="wide",
                       initial_sidebar_state='expanded')

    # Main title of the application
    st.write('# Telemarketing Analysis')
    st.markdown("---")
    
    # Display image in the sidebar
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    # Button to upload file in the application
    st.sidebar.write("## Upload the file")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Check if there is any uploaded content
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Before filtering')
        st.write(bank_raw.head())

        # Check if 'y' column exists and print columns
        st.write('### Columns in the dataset:')
        st.write(bank.columns.tolist())

        with st.sidebar.form(key='my_form'):
            # Select graph type
            graph_type = st.radio('Graph type:', ('Bar', 'Pie'))
        
            # Age filter
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Age', 
                               min_value=min_age,
                               max_value=max_age, 
                               value=(min_age, max_age),
                               step=1)

            # Profession filter
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected = st.multiselect("Profession", jobs_list, ['all'])

            # Marital status filter
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect("Marital status", marital_list, ['all'])

            # Default filter
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect("Default", default_list, ['all'])

            # Housing loan filter
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect("Has housing loan?", housing_list, ['all'])

            # Personal loan filter
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect("Has personal loan?", loan_list, ['all'])

            # Contact filter
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect("Contact", contact_list, ['all'])

            # Month filter
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect("Contact month", month_list, ['all'])

            # Day of the week filter
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected = st.multiselect("Day of the week", day_of_week_list, ['all'])

            # Method chaining to filter the selection
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                    )

            submit_button = st.form_submit_button(label='Apply')
        
        # Download buttons for filtered data
        st.write('## After filtering')
        st.write(bank.head())
        
        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download filtered table in EXCEL',
                           data=df_xlsx,
                           file_name='bank_filtered.xlsx')
        st.markdown("---")

        # Check if 'y' column exists and print columns
        st.write('### Columns after filtering:')
        st.write(bank.columns.tolist())

        # Plots    
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))

        if 'y' in bank_raw.columns:
            bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
            bank_raw_target_perc.columns = ['percentage']
            bank_raw_target_perc = bank_raw_target_perc.sort_index()
            st.write('### Bank Raw Target Perc:')
            st.write(bank_raw_target_perc)
        else:
            st.error("'y' column is missing in the raw data!")

        if 'y' in bank.columns:
            try:
                bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
                bank_target_perc.columns = ['percentage']
                bank_target_perc = bank_target_perc.sort_index()
                st.write('### Bank Target Perc:')
                st.write(bank_target_perc)
            except KeyError as e:
                st.error(f'Error in filter: {e}')
        else:
            st.error("'y' column is missing in the filtered data!")

        # Download buttons for plot data
        col1, col2 = st.columns(2)

        if 'y' in bank_raw.columns:
            df_xlsx = to_excel(bank_raw_target_perc)
            col1.write('### Original proportion')
            col1.write(bank_raw_target_perc)
            col1.download_button(label='📥 Download',
                                 data=df_xlsx,
                                 file_name='bank_raw_y.xlsx')
        
        if 'y' in bank.columns:
            df_xlsx = to_excel(bank_target_perc)
            col2.write('### Proportion of filtered table')
            col2.write(bank_target_perc)
            col2.download_button(label='📥 Download',
                                 data=df_xlsx,
                                 file_name='bank_y.xlsx')
        st.markdown("---")
    
        if 'y' in bank_raw.columns and 'y' in bank.columns:
            st.write('## Acceptance proportion')
            if graph_type == 'Bar':
                sns.barplot(x=bank_raw_target_perc.index, 
                            y=bank_raw_target_perc['percentage'],
                            data=bank_raw_target_perc, 
                            ax=ax[0])
                ax[0].bar_label(ax[0].containers[0])
                ax[0].set_title('Raw data',
                                fontweight="bold")
                
                sns.barplot(x=bank_target_perc.index, 
                            y=bank_target_perc['percentage'], 
                            data=bank_target_perc, 
                            ax=ax[1])
                ax[1].bar_label(ax[1].containers[0])
                ax[1].set_title('Filtered data',
                                fontweight="bold")
            else:
                bank_raw_target_perc.plot(kind='pie', y='percentage', autopct='%.2f', ax=ax[0])
                ax[0].set_title('Raw data',
                                fontweight="bold")
                
                bank_target_perc.plot(kind='pie', y='percentage', autopct='%.2f', ax=ax[1])
                ax[1].set_title('Filtered data',
                                fontweight="bold")

            st.pyplot(plt)

if __name__ == '__main__':
    main()
