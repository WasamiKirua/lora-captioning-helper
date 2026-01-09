caption_length = ['short', 'medium-length', 'long', 'very long']

descriptive = f"""
Write a LENGTH detailed description for this image. If there is a person/character in the image you must refer to them as DIRECTORY. 
Do NOT mention the image's resolution. Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle. Specify the depth of field and whether the background is in focus or blurred. 
If applicable, mention the likely use of artificial or natural lighting sources."""

descriptive_casual = f"""
Write a LENGTH descriptive caption for this image in a casual tone. If there is a person/character in the image you must refer to them as DIRECTORY. 
Do NOT mention the image's resolution. Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle. Specify the depth of field and whether the background is in focus or blurred. 
If applicable, mention the likely use of artificial or natural lighting sources.
"""

sd_prompt = f"""
Output a LENGTH stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.
If there is a person/character in the image you must refer to them as DIRECTORY. Do NOT mention the image's resolution. 
Do NOT mention any text that is in the image. 
Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc. 
ONLY describe the most important elements of the image. Include information about lighting. 
Include information about camera angle.
Specify the depth of field and whether the background is in focus or blurred. If applicable, mention the likely use of artificial or natural lighting sources.
"""

style_prompt = f"""Write a very short straightforward caption for this image. Begin with the main subject and medium. 
Mention pivotal elements—people, objects, scenery—using confident, definite language. 
Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. 
Omit mood and speculative wording. If text is present, quote it exactly. 
Note any watermarks, signatures, or compression artifacts. 
Never mention what's absent, resolution, or unobservable details. 
Vary your sentence structure and keep the description concise, without starting with “This image is…” or similar phrasing. 
Do NOT mention the image's resolution. Do NOT mention any text that is in the image. Do NOT use any ambiguous language. 
If it is a work of art, do not include the artist's name or the title of the work. 
Do NOT use polite euphemisms—lean into blunt, casual phrasing. Do not mention the mood/feeling/etc of the image. 
Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc."""

