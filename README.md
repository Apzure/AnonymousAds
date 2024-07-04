# Anonymous Ads

1. Generates User Data (collect and compile search engine results, tiktok)
2. Encryption 
3. Send to external Server [do we have to implement this?]
4. Apply transformations to process it into encrypted Tags, Categories, Keywords that help determine what ads to show a specific user
5. Send back to the user
6. Decryption
7. Add dummy tags and request the set of ads from TikTok
8. Display selected ads, with the real tags to the user


0. 
    - On start-up Concrete ML model is trained on clear data on server side
    - Client generates public keys and sends to server
1. Search-Engine FrontEnd
    - Your Search History, sends after every 10 Requests / Button
2. Encryption and send to server
    - 
3. Apply Transformations on the server-side
5. Send back transformed data along with set of all tags to user
6. Decryption
7. User randomly selects dummy tags from the set of all tags
8. User requests ads from the server that include these tags

    - Concrete ML model is trained and compiled on clear data on dev side using the FHEModelDev class


    - Client generates public keys and sends to server
    - Client inputs search queries and this is saved
    - Search History is converted to "input" is sent to server
    - Server takes input and uses model to predict tags (output is encrypted)
    - Server sends encrypted prediction to Client and set of all tags
    - Client decrypts prediction, and adds noise to the prediction
    - Server gets ads 



Dependencies:
- Flask
- ConcreteML