# UniTalk

Make it easy to connect with anyone, anytime, anywhere.
What are our features, what did we do, and how does it work? 
- Ability to translate between languages, provide live transcripts of what people are saying, generate ai output to suggest topics to talk about, and personal identification.
- Lens Spectacles comes with a built in library for text transcription. We improved it by editing and making our own code instead of using this library as it was slow and not generating transcripts correctly.
- We generate ai output by implementing ais, and feeding the transcripts we generate to the ai. WE also allow the user to give us a resume that is given as context to the ai to help generate
  even more accurate responses. 
- We personally identify the person you are talking to. We do this by parsing transcripts and checking for important info someone says about themselves such as name, company, and/or role
- that are often mentioned at networking events. 
    - we then call the linkd api which provides the ability to search for someone given inputs adn return it back to the screen, and also feed this into the ai to generate even more conversation topics!
Some smaller features
  - resume upload which is parsed by an api and then given feedback to improve it.
  - conversation follow ups which are automated: we take transcripts of the conversation, store it, then feed it to the ai to make followups for linkedin messages.
  - Created a website that integrates with the spectacles conversations https://unitalk.streamlit.app/ 
  
More info on our project can be found here: https://devpost.com/software/live-networking-helper#updates
