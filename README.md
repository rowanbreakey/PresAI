#Pres.AI
Improve your presentation through AI feedback


## Features:
- User account creation and sign in
- Slidedeck viewer with pdf upload and slide controls
- microphone and camera support
- live quick feedback during presentation
- overall final analysis and presentation feedback


## Tech Stack:
Frontend: React.js, Bootstrap
Backend: Fastapi
Data Processing: FasterWhisper, MediaPipe, GeminiAPI
Database and Authentication: Supabase


## Challenges and Solutions:
This project taught me a lot and came with its fair share of challenges and decisions.
Some of my biggest challenges in the development of Pres.AI include:
1. Inefficient data processing:
Problem: In the original prototype for Pres.AI which was built in a hackathon all the microphone and camera data was passed directly to GeminiAPI for processing. This worked however it led to high processing times and token usage.
Solution: In order to mitigate this issue I implemented FasterWhisper to handle transcribing the audio and Mediapipe to track key points on the users body/face. This allowed me to do the majority of the analysis before sending it to the AI increasing analysis from about 8 seconds to <4 seconds and increasing token efficiency
2. Backend framework Decision:
Problem: I wasn't too sure how to create a backend or have it communicate with my frontend and so I needed to decide what framework I was going to use.
Solution: After some research about the options available I decided on FastAPI. This framework used python which is a language I am very comfortable with and provided very high speed communication with the frontend (as the name suggests). I also found out that FastAPI is used in industry and so this helped me in my decision as I figured if I worked with it now I may be able to work with it at a job in the future.
3. Final Feedback Data:
Problem: I knew I wanted to have some kind of final analysis of the users entire presentation. The problem was I didn't know how to store the data from the quick feedback in order to efficiently analyze it at the end of the users session.
Solution: I decided to use Supabase to store this data in a table with the timestamp, uid and data itself. This way at the end of the session I can query the database for all lines with that user's uid, do the analysis then delete all those lines to be ready for the next session. I also included the timestamp and made a scheduled job that runs every day to delete any outlying user data that has been in the table longer than 24 hours. This way if a user leaves the app mid session and their data is not deleted, it does not persist and clog my database forever.


## Conclusion:
Overall this project has been a very valuable experience for me and has taught me so much about full stack development and software in general. I am excited to continue with even cooler fullstack projects in the future


