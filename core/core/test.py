import Main_functions
import AI
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("what should i do to be liked by girls")

print(response.text)




# x = Main_functions.Interpolate()

# data = [[-11.607440, 34.295660,7328],[-13.036810, 33.481230,4356],[-13.354770, 33.918180,7362], [-15.175940, 35.297280,4726], [-9.703080, 33.274658,2642]]

# x.interpolate(data=data,shapefile_path=r'C:\Users\blown\OneDrive\Desktop\Malawi Data\mw_districts_pop_2008_new.shp')