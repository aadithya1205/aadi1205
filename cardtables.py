#!/usr/bin/env python
# coding: utf-8

# In[3]:


# importing library
import mysql.connector as mysql


# In[4]:


#coonecting sql
mydb=mysql.connect(
      host="localhost",
      user="root",
      password="Positive011205?",
      )
mycursor=mydb.cursor(buffered=True)


# In[5]:


#creating a database
mycursor.execute("CREATE DATABASE card")


# In[6]:


#connecting asql with new database
mydb=mysql.connect(
      host="localhost",
      user="root",
      password="Positive011205?",
      database="card"
      )
mycursor=mydb.cursor(buffered=True)


# In[7]:


#creating a table
mycursor.execute(
            "CREATE TABLE IF NOT EXISTS BUSINESSCARD(NAME VARCHAR(50), DESIGNATION VARCHAR(100), "
            "COMPANY_NAME VARCHAR(100), CONTACT VARCHAR(35), EMAIL VARCHAR(100), WEBSITE VARCHAR("
            "100), ADDRESS TEXT, PINCODE VARCHAR(100))")
mydb.commit()


# In[ ]:




