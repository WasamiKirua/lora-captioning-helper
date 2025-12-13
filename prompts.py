caption_length = ['short', 'medium-length', 'long', 'very long']

descriptive = f"""
Write a LENGTH detailed description for this image. If there is a person/character in the image you must refer to them as DIRECTORY. 
Do NOT mention the image's resolution. Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Do not mention the mood/feeling/etc of the image. Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle. Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc. Specify the depth of field and whether the background is in focus or blurred. 
If applicable, mention the likely use of artificial or natural lighting sources."""

descriptive_style = f"""Write a LENGTH detailed description for this image. 
Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style). 
Include information about camera angle. Do NOT mention the image's resolution. You MUST include information about the subjective aesthetic quality of the image from low to very high. 
Do NOT mention any text that is in the image. ONLY describe the most important elements of the image. 
If it is a work of art, do not include the artist's name or the title of the work. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc."""

descriptive_casual = f"""
Write a LENGTH descriptive caption for this image in a casual tone. If there is a person/character in the image you must refer to them as DIRECTORY. 
Do NOT mention the image's resolution. Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Do not mention the mood/feeling/etc of the image. Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle. Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc. Specify the depth of field and whether the background is in focus or blurred. 
If applicable, mention the likely use of artificial or natural lighting sources.
"""

descriptive_casual_style = f"""
Write a LENGTH descriptive caption for this image in a casual tone. 
Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style). 
Include information about camera angle. Do NOT mention the image's resolution. You MUST include information about the subjective aesthetic quality of the image from low to very high. 
Do NOT mention any text that is in the image. ONLY describe the most important elements of the image. 
If it is a work of art, do not include the artist's name or the title of the work. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc.
"""

sd_prompt = f"""
Output a LENGTH stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.
If there is a person/character in the image you must refer to them as DIRECTORY. Do NOT mention the image's resolution. 
Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Do not mention the mood/feeling/etc of the image. Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle. Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc. 
Specify the depth of field and whether the background is in focus or blurred. If applicable, mention the likely use of artificial or natural lighting sources.
"""

sd_prompt_style = f"""
Output a LENGTH stable diffusion prompt that is indistinguishable from a real stable diffusion prompt. 
Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style). 
Include information about camera angle. Do NOT mention the image's resolution. 
You MUST include information about the subjective aesthetic quality of the image from low to very high. Do NOT mention any text that is in the image. 
ONLY describe the most important elements of the image. If it is a work of art, do not include the artist's name or the title of the work. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc.
"""





