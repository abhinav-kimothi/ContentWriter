import streamlit as st
import openai
from jinja2 import Template
import json
import random
import backoff

def moderation(text):
    response = openai.Moderation.create(input=text)
    if response["results"][0]["flagged"]:
        return 'Moderated : The generated text is of violent, sexual or hateful in nature. Try generating another piece of text or change your story topic. Contact us for more information'
    else:
        return text

@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, openai.error.ServiceUnavailableError,
                                     openai.error.APIConnectionError), max_tries=10)
def open_ai_call(models="", prompt="", temperature=0.7, max_tokens=256,top_p=0.5,frequency_penalty=1,presence_penalty=1,user_id="test-user"):
    response=openai.Completion.create(model=models, prompt=prompt,temperature=temperature,max_tokens=max_tokens,top_p=top_p,frequency_penalty=frequency_penalty,presence_penalty=presence_penalty,user=user_id)
    text=moderation(response['choices'][0]['text'])
    tokens=response['usage']['total_tokens']
    words=len(text.split())
    reason=response['choices'][0]['finish_reason']
    return text, tokens, words, reason

def brief_generator(content_brief=None, content_type=None, topic=None):
    if content_brief:
        prompt="Improve the content brief below for a "+content_type+" on the topic "+topic+". Ignore the text between '**'\n"+content_brief+"."
        text, tokens, words, reason=open_ai_call(models="text-davinci-003", prompt=prompt, temperature=0.7, max_tokens=256,top_p=0.5,frequency_penalty=1,presence_penalty=1,user_id="test-user")
    return text    

def prompt_generator(content_type=None,topic=None, length=None, keywords=None,brief=None,reference=None,tonal=None,style=None):

    with open('tonality.json', 'r') as f:
        emotion= json.load(f)
    
    randomize_tonality=random.choice(["1","2","3","4"])
    tonality=emotion[tonal][randomize_tonality]

    with open('prompts.json', 'r') as f:
        prompt_file= json.load(f)

    prompt_template=Template(prompt_file['Format'][content_type])
    
    init_prompt="You are "+prompt_template.render(topic=topic)

    prompt_tonality=Template(prompt_file['Tonality'][content_type])
    tonality_prompt=prompt_tonality.render(tonality=tonality)

    if style:
        prompt_style=Template(prompt_file[style][content_type])
        style_prompt=prompt_style.render()
    else:
        prompt_style=Template(prompt_file["Text Only"][content_type])
        style_prompt=prompt_style.render()

    if keywords:
        keywords_prompt=" Include the following keywords: "+keywords+"."
    else:
        keywords_prompt=""

    if length:
        length_prompt=" Remember to keep the length "+length+"."
    else:
        length_prompt=""

    if brief:
    #    brief_prompt=" Below is the content brief you have been provided.\n"+brief_generator(content_brief=brief, content_type=content_type, topic=topic)+".\n\n"
        brief_prompt=" Below is the content brief you have been provided.\n"+brief+".\n\n"
    else:
        brief_prompt=""

    if reference:
        reference_prompt=" You have also been provided with a reference content below only to take inspiration and not copy verbatim.\n\n"+reference+"\n\n"
    else:
        reference_prompt=""

    if topic!="":
        prompt=init_prompt+"\n\n"+tonality_prompt+"\n\n"+keywords_prompt+"\n\n"+brief_prompt+"\n\n"+reference_prompt+"\n\n"+style_prompt+"\n\n"+length_prompt
    else:
        prompt="Topic not provided"
 

    return prompt


def gpt_mdict(prompt):
    mdict=[{"role":"user","content":prompt}]
    return mdict


def chat_gpt_call(message_dict=[{"role":"user","content":"Hello!"}], model="gpt-3.5-turbo", max_tokens=2500,temperature=0.9):
    response=openai.ChatCompletion.create(model=model, messages=message_dict,max_tokens=max_tokens,temperature=temperature)
    response_dict=response.choices[0].message
    response_text=response_dict.content
    words=len(response_text.split())
    total_tokens=response.usage.total_tokens
    response_tokens=response.usage.completion_tokens
    return response_text, response_dict, words, total_tokens, response_tokens

def chat_gpt_call_stream(message_dict=[{"role":"user","content":"Hello!"}], model="gpt-3.5-turbo", max_tokens=2500,temperature=0.9):
    response=openai.ChatCompletion.create(model=model, messages=message_dict,max_tokens=max_tokens,temperature=temperature,stream=True)
    return response


