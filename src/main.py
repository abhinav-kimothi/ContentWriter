import streamlit as st
import openai
from utils import *
import time
import json
from PIL import Image





submit=False
delay_time=.01
answer=''
start_time = time.time()
style=None
st.set_page_config(page_title="GPT-3.5 Content Writer", page_icon="🧠", layout="wide")

def load_css_file(css_file_path):
     with open(css_file_path) as f:
          return st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
     
load_css_file("./style/main.css")

st.markdown("<h2 style='text-align:center;'>🖋<span style='color:#ed9a7b'>GPT Content Writer</span>💬</h3>",unsafe_allow_html=True)
st.caption("<h6 style='text-align:center;'>A GPT-3.5 based content writer for all your content needs</h3>",unsafe_allow_html=True)

hline=Image.open('./assets/hline.png')
st.image(hline,use_column_width=True)
logo=Image.open('./assets/logo.png')
st.sidebar.image(logo,use_column_width=True)

#st.divider()
#st.sidebar.title("Choose content type")
content_type=""
#plan=st.sidebar.select_slider("Choose your plan",options=['Basic','Premium'])
content_type = st.sidebar.radio("Select from options below", ("Presentation", "Mobile Presentation", "Slide Show Video", "Case Study", "Company Update","Event Announcement","Share News","Greetings","Advertisement","Share Experience","Client Testimonials","How-To Articles","Listicle","Text Post","LinkedIn Article","LinkedIn Single Slide Post","LinkedIn Multi Slide Post","LinkedIn Carousel Post","LinkedIn Ad","LinkedIn Slide Show Video","Facebook Single Slide Post","Facebook Multi Slide Post","Facebook Ad","Facebook Story","Instagram Single Slide Post","Instagram Carousel Post","Instagram Ad","Instagram Story","Single Tweet","Twitter Thread","Tweet with Image","Blog Intro","Blog Outro","Blog","Blog Outline","Listicle Blog","Press Release","Testimonial","Highlight Product Benefits","Product Description","Product Features","AIDA","PAS","BAB","Welcome Email","New Product Launch Email","Product Update Email","Cold Outreach Email","Event Promotion Email","Greetings Email"))


col1,col2,col3=st.columns([5,1,5])
if content_type != "":
        with col1:
            with st.form(key='my_form',clear_on_submit=False):
                topic=st.text_input("Enter topic")
                tonality=st.selectbox('Choose the tonality of your desire',('Witty', 'Sarcastic', 'Funny','Enthusiatic','Formal','Conversational','Casual','Respectful','Sympathetic','Romantic'))
        
                length=None
                if content_type in ("Presentation","Mobile Presentation","Slide Show Video","Listicle","Greetings","Advertisement","LinkedIn Single Slide Post","LinkedIn Multi Slide Post","LinkedIn Carousel Post","LinkedIn Ad","LinkedIn Slide Show Video","Facebook Single Slide Post","Facebook Multi Slide Post","Facebook Ad","Facebook Story","Instagram Single Slide Post","Instagram Carousel Post","Instagram Ad","Instagram Story","Tweet with Image"):
                    style=st.selectbox("Choose slide design",("Heading only","Paragraph only","Heading and Paragraph","Heading and CTA","Paragraph and CTA","Heading, Paragraph and CTA","CTA Only"))
                else:
                      length=st.text_input("Enter length")
                
                with open('./brief.json', 'r') as f:
                    brief_file = json.load(f)

                brief_text=brief_file[content_type]                
                #if plan=='Basic':
                brief=st.text_area("Enter brief",value=brief_text,height=100)
                if brief==brief_text:
                    brief=None
                #else:
                #    premium_brief=brief_generator(content_type=content_type,topic=topic,content_brief=brief_text)
                #    brief=st.text_area("Enter brief",value=premium_brief,height=400)
                keywords=st.text_input("Enter keywords")
                reference=st.text_area("Enter reference",height=50)
                submit=st.form_submit_button(label='Submit Details',use_container_width=True)
                #st.write(submit)
            if submit:
                prompt=prompt_generator(content_type,topic,length,keywords,brief,reference,tonality,style)
                #st.write(prompt)
                if prompt:
                    with col3:
                         with st.expander("View Prompt",expanded=False):
                            st.code(prompt)

                    mdict=gpt_mdict(prompt)
                
                    response=chat_gpt_call_stream(mdict)
                    with col3:
                        t=st.empty()
                        for event in response: 
                    #        # STREAM THE ANSWER
                            t.markdown(answer,unsafe_allow_html=True) # Print the response    
                            # RETRIEVE THE TEXT FROM THE RESPONSE
                            event_time = time.time() - start_time  # CALCULATE TIME DELAY BY THE EVENT
                            event_text = event['choices'][0]['delta'] # EVENT DELTA RESPONSE
                            answer =answer + event_text.get('content', '') # RETRIEVE CONTENT
                            time.sleep(delay_time)
#
with col3:
    with st.expander("View Answer",expanded=False):
        st.code(answer,language='textile')


st.image(hline,use_column_width=True)



