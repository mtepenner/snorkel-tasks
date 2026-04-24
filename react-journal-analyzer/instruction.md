hey can u throw together a quick react app for me. put the whole thing in /app/index.html and just use the babel and react cdns so we dont have to configure a build step.

it just needs to fetch a giant markdown file from /data/paper.md on load. once u have the text just run some regex or whatever to count how many citations there are (stuff like [1] or [42]). also need counts for the words quantum and entanglement ignoring case. last thing is grab all the main headers which are just lines that start with exactly # .

make whatever simple ui to show it but my automated tests will break if u dont dump the raw json into a <pre id="stats-output"></pre> tag. stringify it exactly like this {"citations": int, "keywords": {"quantum": int, "entanglement": int}, "headers": ["string"]}. thanks
