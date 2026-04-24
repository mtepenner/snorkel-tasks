we are having issues processing 50k+ token pdfs so i need a python api built at /app/workspace/src/api.py. bind the server to 0.0.0.0:8000. since the docs are so big you have to implement text chunking (cap it at 1000 words per chunk max) so it doesnt run out of memory.

the endpoint needs to be POST /extract and accept a multipart/form-data upload using file as the field name. pull the author and title straight out of the pdf metadata properties. if its missing those fields just fallback to "Unknown Author" and "Untitled". after that, parse the text chunks themselves to figure out the topics.

for the output it has to be a flat json object. do not change these keys or types: author as string, title as string, topics as an array of strings, total_chunks as int, filename as string, and total_words as int.

finally just make a really basic test ui at /app/workspace/src/static/index.html. all it needs is a file picker that hits the api and dumps the raw json response on the screen so i can verify the math.
