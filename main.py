#!/usr/bin/env python
# coding: utf-8

# In[23]:


#IMPORTING REQUIRED lIBRARIES
import streamlit as st
import easyocr
from PIL import Image, ImageDraw
import pandas as pd
import numpy as np
import re
import mysql.connector as mysql
import io

st.set_page_config(page_title= "BIZCARDX",
                   layout= "wide",
                   initial_sidebar_state= "expanded")
#CONNECTING TO SQL
mydb=mysql.connect(
      host="localhost",
      user="root",
      password="Positive011205?",
      database="card"
      )
mycursor=mydb.cursor(buffered=True)
#CREATING A FUNCTION TO CONVERT DATAFRAME TO CSV FILE
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')
#CREATING A FUNCTION TO EXTRACT DATA FROM IMAGE
def extract_data(Data):
    Dict = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [],
               'Address': [], 'Pincode': []}

    Dict['Name'].append(bounds1[0])
    Dict['Designation'].append(bounds1[1])

    for m in range(2, len(bounds1)):
        if bounds1[m].startswith('+') or (bounds1[m].replace('-', '').isdigit() and '-' in bounds1[m]):
            Dict['Contact'].append(bounds1[m])

        elif '@' in bounds1[m] and '.com' in bounds1[m]:
            small = bounds1[m].lower()
            Dict['Email'].append(small)

        elif 'www' in bounds1[m] or 'WWW' in bounds1[m] or 'wwW' in bounds1[m]:
            small = bounds1[m].lower()
            Dict['Website'].append(small)

        elif 'TamilNadu' in bounds1[m] or 'Tamil Nadu' in bounds1[m] or bounds1[m].isdigit():
            Dict['Pincode'].append(bounds1[m])

        elif re.match(r'^[A-Za-z]', bounds1[m]):
            Dict['Company name'].append(bounds1[m])

        elif(re.findall(r'^123+\s[\w\.-]+',bounds1[m])):
            removed_colon = bounds[m[0:10]]
            Dict['Address'].append(removed_colon)

    for k, val in Dict.items():
        if len(val) > 0:
            concatenated_string = ' '.join(val)
            Dict[k] = [concatenated_string]
        else:
            val = 'NA'
            Dict[k] = [val]
    return Dict



tab1,tab2,tab3,tab4=st.tabs([":red[HOME]",":orange[UPLOAD IMAGE]",":orange[DATA]",":red[UPDATE AND DOWNLOAD]"])
with tab1:
    st.header("BizCardX: Extracting Business Card Data with OCR")
    st.subheader("Technologies Used")
    st.write("##   -->OCR")
    st.write("##   -->streamlit GUI ")
    st.write("##   -->SQL")
    st.info("go to next tab to upload image")
            
             
with tab2:
    #GETTTING IMAGE FROM USER
    image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")
    #SPECIFY A LANGUAGE
    reader = easyocr.Reader(['en'])
    if image is not None:
        with st.spinner('Wait for it...'):
            im= Image.open(image)
            #PERFORM CHARACTER RECOGNITION
            bounds1=reader.readtext(np.array(im),detail=0)   
            #EXTRACTING THE DATA
            data=extract_data(bounds1)
            #CREATING A DATAFRAME
            df=pd.DataFrame(data)
            #CONVERTING IMAGE TO BYTES
            image_bytes = io.BytesIO()
            im.save(image_bytes, format='PNG')
            image_data1 = image_bytes.getvalue()
            data1 = {"Image": [image_data1]}
            df1 = pd.DataFrame(data1)
            df2 = pd.concat([df1, df1], axis=1)
            #RESIZING THE IMAGE
            im1=im.resize((500,300))
            bounds=reader.readtext(np.array(im1),detail=1)  
            #DRAW RECTANGE ON DETECTED WORDS
            draw = ImageDraw.Draw(im1)
            for bound in bounds: # iterate though all the tuples of output
                p0, p1, p2, p3 = bound[0] # get coordinates 
                draw.line([*p0, *p1, *p2, *p3, *p0], fill="yellow", width=2)
        st.image(im1,caption="DETECTED WORDS")
        button=st.button("Migrate to sql")
        if button:
            #MIGRATING TO SQL
            for i,row in df.iterrows():
                sql = "INSERT INTO BUSINESSCARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, ADDRESS,PINCODE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                mycursor.execute(sql, tuple(row))
                mydb.commit()
                st.success("Migrated to Sql")
                st.info("Go to data Tab to Visualize the data")
    else:
        st.info("upload image and click \"Migrate to sql\"")
with tab3:
    #DISPLAYING THE DATA FROM BUSINESS CARD
    st.header("Table:ALL THE BUSINESS CARD DATA")
    mycursor.execute(f"SELECT * FROM BUSINESSCARD ")
    K= mycursor.fetchall()
    column_name = ["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS","PINCODE"]
    d_f2 = pd.DataFrame(K, columns=column_name, index=np.arange(1, len(K) + 1))
    st.dataframe(d_f2)
    st.info("Go to next tab to update and download data")
    
with tab4:
    #TO DELETE THE DATA
    st.header("Update details and download")
    col1, col2 = st.columns([4, 4])
    with col1:
                mycursor.execute("SELECT NAME FROM BUSINESSCARD")
                Y = mycursor.fetchall()
                name = ["Select"]
                for i in Y:
                    name.append(i[0])
                name_selected = st.selectbox("Select the name to delete", options=name,key="2")
               
    with col2:
                mycursor.execute(f"SELECT DESIGNATION FROM BUSINESSCARD WHERE NAME = '{name_selected}'")
                Z = mycursor.fetchall()
                designation = ["Select"]
                for j in Z:
                    designation.append(j[0])
                designation_selected = st.selectbox("Select the designation of the chosen name", options=designation,key="3")

                st.markdown(" ")

                col_a, col_b, col_c = st.columns([5, 3, 3])
                with col_b:
                    remove = st.button("Click here to delete")
                    if name_selected and designation_selected and remove:
                        mycursor.execute(
                        f"DELETE FROM BUSINESSCARD WHERE NAME = '{name_selected}' AND DESIGNATION = '{designation_selected}'")
                        mydb.commit()
                    if remove:
                        st.warning('DELETED', icon="⚠️")
    col3, col4 = st.columns([4, 4])
    with col3:
        #TO DOWNLOAD PARTICULAR BUSINESS CARD DATA
        st.header("To download specific card data")
        mycursor.execute("SELECT NAME FROM BUSINESSCARD")
        Y = mycursor.fetchall()
        name = ["Select"]
        for i in Y:
            name.append(i[0])
        name_selected = st.selectbox("Select the name to see the data", options=name,key="4")
        mycursor.execute(f"SELECT * FROM BUSINESSCARD WHERE NAME = '{name_selected}'")
        Z = mycursor.fetchall()
        column_name = ["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS","PINCODE"]

        d_f = pd.DataFrame(Z, columns=column_name, index=np.arange(1, len(Z) + 1))
        csv = convert_df(d_f)
        st.download_button(
             label="Download data as CSV",
            data=csv,
            file_name='Your-Data.csv',
            mime='text/csv',
            )
    with col4:
        #TO DOWNLOAD ALL DATA AS CSV FILE
        st.header("To Download all the business card data ")
        mycursor.execute(f"SELECT * FROM BUSINESSCARD ")
        T = mycursor.fetchall()
        column_name = ["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS","PINCODE"]
        d_f1 = pd.DataFrame(T, columns=column_name, index=np.arange(1, len(T) + 1))
        csv1 = convert_df(d_f1)
        st.download_button(
            label="Download all data as CSV",
            data=csv1,
            file_name='Your-Data.csv',
            mime='text/csv',
            )

    
    
            

         
        
    
    
    


# In[ ]:





# In[ ]:




