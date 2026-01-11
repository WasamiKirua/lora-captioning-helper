CAPTION_CHARACTER = """
Task: Write a short, blunt caption describing the image.

Rules:
- If there is a person/character in the image you must refer to them as TRIGGER.
- Use simple noun phrases or short sentences.
- Mention only the most important visible elements (clothing, pose, setting).
- Describe concrete details only (color, clothing, objects, location).
- Use casual, direct language.

Do NOT:
- Do NOT mention resolution, quality, mood, emotions, or style.
- Do NOT use meta phrases like “this image shows” or “you are looking at”.
- Do NOT mention missing elements.
- Do NOT mention any text in the image.
- Do NOT name artists or artwork titles.

Output:
- 1–3 short sentences
- No adjectives beyond what is visually obvious
- No commas unless necessary

Examples:
- woman in front of a red car wearing a white graphic tee
- woman leaning against a wall in a bar wearing a green floral dress
- close up of a woman
- woman on a talk show wearing  a sweater smiling
"""

CAPTION_STYLE = """
Write a short caption.
Describe only the main subject and key visible details.
Use simple language.
Do not mention text, mood, style, or image quality.
No meta phrases.
1–2 short sentences.
"""