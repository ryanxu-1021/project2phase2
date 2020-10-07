import tweepy
import re
import numpy as np
import pandas as pd
import twitter_credentials as tc
from google.cloud import language_v1
from google.cloud.language_v1 import enums
import matplotlib
import matplotlib.pyplot as plt

ACCESS_TOKEN = "1309945781290299392-40z873fpuIyALoBBa1COfcL3XOo4v1"
ACCESS_TOKON_SECRET ="4Enwb3l1szHJOV2tOncoR6cVKJITkNQjecL2dku004uRj"
CONSUMER_KEY = "sP0Ap4orRXQZvyijETm2D0g0m"
CONSUMER_SECRET ="AkdIB1rnik9dkRpUchhGeHRDOrhFLLTTPYZb0mcFa2P0Bt1h62"
# Anuthenticaiton
auth = tweepy.OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKON_SECRET)

api = tweepy.API(auth)


# read keywords from shell input
# screen_name = input("Whose twitter do you want to analysis? (type the user name e.g. JoeBiden, realDonaldTrump) ")




#################################
#user input test

## username test
while True:
  screen_name = input("Whose twitter do you want to analysis? (type the user name e.g. JoeBiden, realDonaldTrump) ")
  if re.search(r'[\s]', screen_name):
    print ("    No spaces please.")
  else:
    break


## count test
while True:
  count = input("How many tweets do you need? (range 10-1000) ")
  if (int(count) in range(10,1001)):
    count = int(count)
    break
  else:
    print ("    Please pick a integer between 10-1000")
True

## retweets test
rts_list_1 = ['1', 'True', 'true', 'TRUE','yes', 'YES']
rts_list_0 = ['0', 'False', 'false','FALSE', 'no', 'NO']
while True:
  rts = input("Do you need retweets? (type <true> if you do) ")
  if (rts in rts_list_1):
    rts = 'True'
    break
  elif (rts in rts_list_0):
    rts = 'False'
    break
  else:
    print ("    Please type <true>, or <false>")



## reply test

rpls_list_1 = ['1', 'True', 'true', 'TRUE','yes', 'YES']
rpls_list_0 = ['0', 'False', 'false','FALSE','no', 'NO']
while True:
  rpls = input("Do you need replies? (type <ture> if you do) ")
  if (rpls in rpls_list_1):
    rpls = 'False'
    break
  elif (rpls in rpls_list_0):
    rpls = 'True'
    break
  else:
    print ("    Please type <true>, or <false>")



#Retreive tweets from twitter
posts = api.user_timeline(screen_name = screen_name, 
                                    count = count, 
                                    lang = "en", 
                                    tweet_mode = "extended",
                                    include_rpls = rpls,
                                    exclude_replies = rpls )



#create a dataframe with a column called Tweets
print ()
print ('Retrieving data from Twitter API......')
df = pd.DataFrame([tweet.full_text for tweet in posts], columns = ['Tweets'])
print ('  Data received!  ')
print()



#Format/clean the text of the tweets
def cleanText(text):

  text = re.sub(r'@[A-Za-z0-9:]+', '', text) #remove @mentions
  text = re.sub(r'#', '', text) #remove #
  text = re.sub(r'RT[\s]+', '', text) # remove RT
  text = re.sub(r'https?:\/\/\S+','', text)# remove the link
  return text


# Create a function to get the subjectivity
def analyzeSentiment(text):
    client = language_v1.LanguageServiceClient()
    type_ = enums.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text, "type": type_, "language": language}

    encoding_tpye = enums.EncodingType.UTF8

    response = client.analyze_sentiment(document, encoding_type=encoding_tpye)
    return response






#clean text of tweets 
print ('Cleaning text content......')

df['Tweets'] = df['Tweets'].apply(cleanText)
print ('  Cleaning process finished!')
print ()


#Google NLP API & data formating
print('Conneting to Google NLP API ......')
for i in range(0,df.shape[0]):
    #retrive analysis resopnse
    response = analyzeSentiment(df.at[i,'Tweets'])
    print ('  Received data from Google NLP API, processing......')
    #format output
    df.at[i,'D_score'] = response.document_sentiment.score
    df.at[i,'D_magnitude'] = response.document_sentiment.magnitude
    df.at[i,'Response'] = response
print ("  Sentiment analysis finished!")    
print()


def getAnalysis(score):
  if score < -0.1:
    return 'Negative'
  elif ((score >= -0.1) & (score <= 0.1) ):
    return 'Neutral'
  else: 
    return 'Positive'


print ('Data formating......')
df['Analysis'] = df['D_score'].apply(getAnalysis)
print ('  Data format finished!')
print ()

#show the distribution of all tweets been analyzed
print ('Printing out Plots of the analysis result')
print()
plt.figure(figsize=(6,6))
for i in range(0,df.shape[0]):
    plt.scatter(df.at[i, 'D_score'], df.at[i, 'D_magnitude'])
plt.title('Sentiment Analysis')
plt.xlabel('Score')
plt.ylabel('Magnitude')
plt.show()
plt.close()

# show a bar chart of Neg/Neu/Pos
print()
print(df['Analysis'].value_counts())
print()
plt.figure(figsize=(6,6))

plt.title('Sentiment Analysis')
plt.xlabel('Sentiment')
plt.ylabel('Counts')
df['Analysis'].value_counts().plot(kind = 'bar')
plt.show()
plt.close()