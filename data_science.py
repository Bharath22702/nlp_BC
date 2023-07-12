!pip3 install textstat

import nltk
nltk.download('vader_lexicon')

import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from textstat import flesch_reading_ease
from nltk.sentiment import SentimentIntensityAnalyzer

# Load the input data from Excel file
input_file = "/content/Input.xlsx"
df = pd.read_excel(input_file)

# Extract the URLs
urls = df["URL"].tolist()

file_list = []
for url in urls:
    try:
        # Retrieve the web page content
        response = requests.get(url)
        html_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract the article title
        title = soup.title.text.strip()

        # Extract the article text
        article_text = ""
        article_body = soup.find("article")  # Assuming the article is enclosed in an <article> tag
        if article_body:
            paragraphs = article_body.find_all("p")
            article_text = "\n".join([p.text.strip() for p in paragraphs])

        # Save the article text in a text file
        url_id = urlsplit(url).path.strip("/")  # Extract the URL ID

        file_name = f"{url_id}.txt"
        file_list.append(file_name)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n\n")
            f.write(article_text)

        print(f"Article saved: {file_name}")

    except Exception as e:
        print(f"Error processing URL: {url}")
        print(f"Error details: {str(e)}")

import pandas as pd
import os
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from textstat import flesch_reading_ease, textstat


nltk.download('punkt')
nltk.download('stopwords')

# Create a list of positive and negative words
positive_words = ['good', 'great', 'excellent']  # Add your positive words here
negative_words = ['bad', 'terrible', 'awful']  # Add your negative words here

# Write the positive words to positive-words.txt file
with open("positive-words.txt", "w") as f:
    for word in positive_words:
        f.write(word + "\n")

# Write the negative words to negative-words.txt file
with open("negative-words.txt", "w") as f:
    for word in negative_words:
        f.write(word + "\n")

# Set folder path containing the .txt files
folder_path = '/content'  # Replace with the actual folder path

# Create an empty DataFrame for the output
output_columns = [
    "URL",
    "POSITIVE SCORE",
    "NEGATIVE SCORE",
    "POLARITY SCORE",
    "SUBJECTIVITY SCORE",
    "AVG SENTENCE LENGTH",
    "PERCENTAGE OF COMPLEX WORDS",
    "FOG INDEX",
    "AVG NUMBER OF WORDS PER SENTENCE",
    "COMPLEX WORD COUNT",
    "WORD COUNT",
    "SYLLABLE PER WORD",
    "PERSONAL PRONOUNS",
    "AVG WORD LENGTH"
]
df_output = pd.DataFrame(columns=output_columns)

# Initialize the sentiment analyzer
sid = SentimentIntensityAnalyzer()

# Function to calculate the percentage of complex words
def calculate_percentage_complex_words(tokens):
    stop_words = set(stopwords.words("english"))
    total_words = len(tokens)
    complex_words = sum(1 for token in tokens if token.lower() not in positive_words and token.lower() not in negative_words and token.lower() not in stop_words)
    return (complex_words / total_words) * 100

# Function to calculate the FOG index
def calculate_fog_index(avg_sentence_length, percentage_complex_words):
    return 0.4 * (avg_sentence_length + percentage_complex_words)

# Function to calculate the average number of words per sentence
def calculate_avg_words_per_sentence(tokens, sentences):
    total_words = len(tokens)
    total_sentences = len(sentences)
    return total_words / total_sentences

# Function to count personal pronouns
def count_personal_pronouns(tokens):
    personal_pronouns = ["I", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"]
    return sum(1 for token in tokens if token.lower() in personal_pronouns)

# Function to calculate the average word length
def calculate_avg_word_length(tokens):
    total_chars = sum(len(token) for token in tokens)
    total_words = len(tokens)
    return total_chars / total_words

# Iterate over the files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        try:
            # Read the text file
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Perform text preprocessing
            tokens = nltk.word_tokenize(text.lower())
            sentences = nltk.sent_tokenize(text)

            # Compute the positive and negative scores
            sentiment_scores = sid.polarity_scores(text)
            positive_score = sentiment_scores["pos"]
            negative_score = sentiment_scores["neg"]

            # Compute the polarity and subjectivity scores
            polarity_score = sentiment_scores["compound"]
            subjectivity_score = sentiment_scores["compound"] + 1 - sentiment_scores["neu"]

            # Compute the average sentence length
            avg_sentence_length = sum(len(nltk.word_tokenize(sentence)) for sentence in sentences) / len(sentences)

            # Compute the percentage of complex words
            percentage_complex_words = calculate_percentage_complex_words(tokens)

            # Compute the FOG index
            fog_index = calculate_fog_index(avg_sentence_length, percentage_complex_words)

            # Compute the average number of words per sentence
            avg_words_per_sentence = calculate_avg_words_per_sentence(tokens, sentences)

            # Count the complex words
            complex_word_count = sum(
                1 for token in tokens if token.lower() not in positive_words and token.lower() not in negative_words)

            # Count the total number of words
            word_count = len(tokens)

            # Compute the average number of syllables per word
            syllables_per_word = textstat.syllable_count(text) / word_count

            # Count personal pronouns
            personal_pronouns_count = count_personal_pronouns(tokens)

            # Compute the average word length
            avg_word_length = calculate_avg_word_length(tokens)

            # Create a row for the output DataFrame

            url = "https://insights.blackcoffer.com/"+file_name[:-4]+"/"
            row = [
                url,
                positive_score,
                negative_score,
                polarity_score,
                subjectivity_score,
                avg_sentence_length,
                percentage_complex_words,
                fog_index,
                avg_words_per_sentence,
                complex_word_count,
                word_count,
                syllables_per_word,
                personal_pronouns_count,
                avg_word_length
            ]

            # Append the row to the output DataFrame
            df_output.loc[len(df_output)] = row

        except Exception as e:
            print(f"Error processing file: {file_name}")
            print(f"Error details: {str(e)}")

# Save the output DataFrame to Excel
output_file = "output.xlsx"
df_output.to_excel(output_file, index=False)

print(f"Output saved to: {output_file}")
