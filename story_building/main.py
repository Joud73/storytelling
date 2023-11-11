import streamlit as st
import openai
import os
from dotenv import load_dotenv 
from PIL import Image
import time
import webcolors
import random
import webcolors
import json

load_dotenv()
openai.api_key=os.getenv('OPENAI_API_KEY')



def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def hex_to_color_name(hex_color):
    try:
        color_name = webcolors.hex_to_name(hex_color)
    except ValueError:
        closest_hex_color = closest_color(webcolors.hex_to_rgb(hex_color))
        color_name = closest_hex_color
    return color_name

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2, 
        max_tokens=150
    )
    return response.choices[0].message["content"]



TAMPLATE1="""
[
  {"id": 1, "option": "A mysterious character appears in the story."},
  {"id": 2, "option": "The setting of the story suddenly changes."},
  {"id": 3, "option": "An unexpected magical event occurs."}
]
"""
TAMPLATE2 = """ { "questions":
[
  {
    "id": 1,
    "question": "What was the color of the main character's shirt?",
    "options": [
      "A. Blue.",
      "B. Red.",
      "C. Black"
    ],
    "Correct_answer": "C. Black"
  } 
]}
"""




st.set_page_config(page_title='Storytelling app')
st.title("**Let's build our story togather 🎈**")
st.divider()
st.markdown("\n")
st.markdown("\n")


desired_size = (250, 200)  
image_files = ['zoo.jpg', 'cars.jpg', 'fam.jpg', 'fr.jpg']


images = {
    'Zoo 🐘': Image.open(image_files[0]),
    'Cars 🚗': Image.open(image_files[1]),
    'Family 👨‍👩‍👦': Image.open(image_files[2]),
    'Friendship 👭': Image.open(image_files[3])
}


resized_images = {
    key: img.resize(desired_size, Image.Resampling.LANCZOS) for key, img in images.items()
}


options = list(images.keys())
option_index = st.radio("**Choose the theme for your story:**", range(len(options)), format_func=lambda x: options[x])


st.image(resized_images[options[option_index]], caption=options[option_index])
selected_theme = options[option_index]
st.divider()


main_character=None
if selected_theme == 'Zoo 🐘':
    main_character = st.radio("**Choose the main character of your story:**", ['Lion', 'Elephant', 'Monkey', 'Giraffe'])
elif selected_theme == 'Family 👨‍👩‍👦':
    main_character = st.radio("**Choose the main character of your story:**", ['Mother', 'Father', 'Brother', 'Sister'])
elif selected_theme == 'Cars 🚗':
    main_character = st.radio("**Choose the main character of your story:**", ['Sports Car', 'Police Car', 'Motorcycle', 'Bicycle'])
    car_color = st.color_picker("Choose the color of the car:", '#000000')  
    color_name = hex_to_color_name(car_color)
    st.write(f"You have chosen {color_name} as the color for your car.")
elif selected_theme =='Friendship 👭':
    main_character = st.radio("**Choose the main character of your story:**", ['Best Friend', 'Classmate', 'Neighbor', 'Pet'])


st.write(f"You have chosen {main_character} as the main character for your {selected_theme} story.")
st.divider()
st.markdown("\n")

user_input = st.text_input('Enter a scenario to start the story, or leave blank for a random start:')

story_state = st.session_state.get('story_state', '')





if st.button('Generate Story'):
    prompt = f"A story about {selected_theme.lower()} and {main_character.lower()}. {user_input}" if user_input else f"A story about {selected_theme.lower()} and {main_character.lower()}." 
    if selected_theme=='Cars 🚗' :
        prompt = f"A story about {selected_theme.lower()} and {main_character.lower()} and the color of the car is {color_name}. {user_input}" if user_input else f"A story about {selected_theme.lower()} and {main_character.lower()}." 


    with st.spinner(f'Generating your {selected_theme} story...'):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""You are a story generator specialized in crafting children's stories. 
    Your language should be simple, engaging, and child-friendly. 
    The stories you create should feature '{main_character}' as the main character and revolve around the theme of '{selected_theme}'. 
    Please ensure that the narrative is suitable for a children's story night.
    each sentence has to be complete.
    generate two paragraphs only."""},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150
        )
    

    story = response['choices'][0]['message']['content']
    story_state = story 
    st.session_state['story_state'] = story_state
    
    
    st.write('Generated Story:')
    st.write(story)





if story_state:
    if 'choices_responses' not in st.session_state or st.button('Continue Story'):
     with st.spinner('Generating your next events...'):
   

        propmt1 = (""" 
            Your task is to suggest three distinct and abstract next events for the story delimited by triple backticks.
             '''{}'''
            Provide them in JSON format with the following key: id, option.
            Each event should be a single, short sentence, completely independent from the others, and not directly continuing the story. 
            The events should be imaginative and suitable for a child's story, without providing a sequence or additional context.
            I want the output the same as template delimited by FOUR STARS backticks: ****{}****""").format(story, TAMPLATE1)
        choices_json = json.loads(get_completion(propmt1))
        choices_text = [choice["option"] for choice in choices_json]

        
    
        st.session_state['choices_responses'] = choices_text
       

   
    choice = st.radio("Choose the next event for your story:", st.session_state.get('choices_responses', []))



    if st.button('Continue with Selected Event'):
        if choice:
            new_prompt = story_state + ' ' + choice
            
            with st.spinner('Continuing your story...'):
               propmt3=f"""Continue the story using the selected next event delimited by triple backticks.
                maintaining the style and context of the story delimited by triple stars. 
                End the story with happy ending.
                selected_next_event=''''{choice}''''
                the story= ****{story_state}****"""

               continuation=get_completion(propmt3)
                  
               
               story_state += ' ' + continuation
               st.session_state['story_state'] = story_state
                
            st.write('Story Continuation:')
            st.write(continuation)







if story_state and st.button('Generate Quiz'):
      with st.spinner("Generating Your Quiz..."):
        message =( """Creat one question based on the story delimted by four backquot.
             the response must be formatted in JSON format with the following key:  id, question, options as a list,correct answer.
             this is an example of the respose: ''''{}''''
             that is the story: ''''{}''''
             """).format(TAMPLATE2,story_state)
        questions = json.loads(get_completion(message))
        q_id=str(questions["questions"][0]["id"])
        st.write(f" Q{q_id} \ {questions['questions'][0]['question']}",)
        option_text=""
        quiz_options=questions['questions'][0]['options']
        for q in quiz_options:
            option_text+=f"{q}\n"
        st.write(option_text)    
        with st.expander("Show Answer",expanded=False):
            st.write(questions['questions'][0]['Correct_answer'])




      



