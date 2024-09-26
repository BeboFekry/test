import streamlit as st
from AiMemoryDB import Memory
# from GetDataFromJson import GetDataFromJSON
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
import time
import json
import os

st.columns([2,1,2])[1].image("electro-pi.png")
st.title("Advix Bot")
st.info("AI Memory Module")

template = """you are a helpfull assistant the help for question answering about financial data from json file in summary
            %Note%: your main task is only retrieve the needed data even if you asked for a mathematic operations only response with answer and the needed data for the operation
            the response should be clear and precise, providing exactly the information requested without many explaination

            %Note%: the json file is consists of some data about financial information, each key consists of all the year months, **you need to get into each needed month in the data and traverse all the data sequentialy**

            Given **Question Examples** it consists of "Question example", "Function you will need" these is what you need to do, and "Expected Output" these is how you should response
            %Note%: you should follow the **Function you will need** and perform it, and make your response as the shape of **Expected Output**

            %Note%: in case you asked about the average of quarter a year, divide a year into 4 quarters the first quarter from January to March, second quarter is from April to June, third quarter is from July to September, and the fourth quarter is from October to December, put the final answer in a big bracets before dividing by 4
            %Note%: Takes the zero values in considration

            **Question Examples**:
            Question Example: "What are the Total COGs of January?", "What are the Total COGs of July?", "What are the September Total COGs for previous years?"
            Function you will need: "The Total COGs for June is number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0, July 0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0, and Previous year is number + number + number + number + 0 + 0 + 0 + 0 + 0 + 0" 
            Expected output: "The Total COGs for June is number, July number, and Previous year is number + number + number + number"

            Question Example: "How many Total Active Users Month 6 / June?"
            Function you will need: number
            Expected Output: number

            Question Example: "هاتلي مصاريف ايجار المكتب من شهر 6 لحد شهر 11"
            Function you will need: number + 0 + number + 0 + 0 + 0
            Expected Output: number + number

            Question Example: "How many Total Completed Orders in these year and in the past years?"
            Function you will need: Completed orders for these year is  number + number + number + number + number + number + number + number + number + number + number + number, and for the past years is number
            Expected Output: Completed orders for these year is  number + number + number + number + number + number + number + number + number + number + number + number, and for the past years is number

            Question Example: "هاتلي متوسط الارباح في الشهر"
            Function you will need: ((number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0)) / 12
            Expected Output: (number + number + number + number + number + number + number + number + number + 0 + number + number) / 12

            Question Example: "هاتلي ارباح شهر 7"
            Function you will need: (0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0)
            Expected Output: number

            Question Example: "هاتلي ارباح اول شهرين"
            Function you will need: ((number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0))
            Expected Output: (number + number)

            Question Example: "هاتلي ارباح اول 3 شهور/اشهر"
            Function you will need: (number + 0 + number2 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0)
            Expected Output: ((number number2) + number + number)

            Question Example: "ايه هو اعلي شهر كان فيه مصاريف استشارات"
            Function you will need: in January 0, in February 0, in March 0, in April number, in May 0, in June 0, in July 0, in August 0, in September 0, in October number, in November 0, in December 0
            Expected Output: ابريل بناتج number

            Question Example: "ايه هي الايرادات الربع سنوية لاخر 3 شهور"
            Function you will need: ((0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0 + 0) + (0 + 0 + 0 + number + 0 + 0 + 0 + 0 + 0 + 0))
            Expected Output: 0 + number + number

            %Note%: in case you asked about specific object as "what is the maximum factor in ...", "what is the largest source of monthly income?" mention it and its value

            %Note%: set your response as the shape of **Expected Output**
            %Note%: don't get the previous year except you asked about it
            %Note%: put any denomenator in bracets

            %VERY IMPORTANT%: the examples above are only examples of questions and output format not a real values you need to get the real value

            %Money Currency%: Egyptian Pound

            %Data you need%: {json_data}
        """

files = ["extracted_jsons/" + f for f in os.listdir(path="extracted_jsons")]
json_data = []
for f in files:
    with open(f, 'r') as d:
        json_data.append(json.load(d))

prompt_template = PromptTemplate(input_variables=['json_data'], template=template).format(json_data=json_data)

session_id = 1
if 'conversation' not in st.session_state:
    st.session_state.conversation = -1
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'memory' not in st.session_state:
    st.session_state.memory = Memory(prompt_template, session_id)
    st.session_state.memory.prepare()
if 'new_conversation' not in st.session_state:
    st.session_state.new_conversation = False
if 'delete' not in st.session_state:
    st.session_state.delete = False

convs = st.session_state.memory.get_conversations()

st.sidebar.info("Conversations History")
if convs is not []:
    if st.sidebar.button(":material/delete:"):
        st.session_state.delete = not st.session_state.delete
    if st.session_state.delete==False:
        for c in convs:
            if st.sidebar.button(c[1], use_container_width=1):  #conv name
                st.session_state.conversation = c[0]  #conv id
                st.session_state.memory.set_conversation(st.session_state.conversation)
    else:
        for c in convs:
            if st.sidebar.button(f"{c[1]} :material/delete:", use_container_width=1):  #conv name
                # st.session_state.conversation = c[0]  #conv id
                st.session_state.memory.delete_conversation(c[0])
                st.session_state.delete = False
                st.sidebar.success("success")
                time.sleep(1)
                st.rerun()


if st.sidebar.button("\+ New conversation", use_container_width=1):
    st.session_state.conversation = st.session_state.memory.create_conversation()
    st.rerun()

if st.session_state.new_conversation == True or st.session_state.conversation != -1:
    st.session_state.messages = st.session_state.memory.get_messages()

# Download Button
if st.session_state.messages != []:
    data = {"Sender":[], "Content":[]}
    for m in st.session_state.messages:
        if m.type=='human':
            data['Sender'].append("Human")
            data["Content"].append(m.content)
        elif m.type=='ai':
            data['Sender'].append("Assistant")
            data["Content"].append(m.content)            
    df = pd.DataFrame(data)
    df.to_csv('ChatHistory.csv', index=False, encoding='utf-8-sig')
    with open('ChatHistory.csv', 'rb') as f:
        if st.download_button('Download CSV', f, file_name='ChatHistory.csv'):
            st.success("Your conversation history have been downloaded successfully!")

# ______________________________________________________________________________
# ______________________________________________________________________________


google_api_key = "AIzaSyBIvw7QEbrnN7HJTBqxu6CI_r7egCWf5tU"
chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, temprature=0)

for message in st.session_state.messages:
    if message.type=="human":
        with st.chat_message("user"):
            st.markdown(message.content)
    elif message.type=="ai":
        with st.chat_message("assistant"):
            st.markdown(message.content)
st.write("---")

if prompt := st.chat_input("من فضلك اكتب سؤالك هنا"):

    if st.session_state.new_conversation == False and st.session_state.conversation == -1:
        st.session_state.conversation = st.session_state.memory.create_conversation()
        st.session_state.messages = st.session_state.memory.get_messages()
        st.session_state.new_conversation = True

    st.chat_message("user").markdown(prompt)
    st.session_state.memory.add_human(prompt)

    # st.write(st.session_state.messages)
    response = chat(st.session_state.messages).content

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.memory.add_ai(response)

