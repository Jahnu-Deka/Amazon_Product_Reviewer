import streamlit as st
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import time

# Function to scrape Amazon reviews using Selenium and Microsoft Edge
def get_amazon_reviews_selenium(url):
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    # Open the product page
    driver.get(url)

    # Scroll to load reviews
    reviews = []
    while True:
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        for review in soup.find_all("span", {"data-hook": "review-body"}):
            reviews.append(review.text.strip())

        # Find the 'Next' button and click it to load more reviews
        next_button = soup.find('li', {'class': 'a-last'})
        if next_button and 'a-disabled' not in next_button.get('class', []):
            driver.find_element(By.CSS_SELECTOR, 'li.a-last a').click()
        else:
            break  # No more pages

    driver.quit()
    return reviews

# Function for sentiment analysis
def analyze_sentiment(reviews):
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for review in reviews:
        analysis = TextBlob(review).sentiment.polarity
        if analysis > 0:
            sentiments["positive"] += 1
        elif analysis < 0:
            sentiments["negative"] += 1
        else:
            sentiments["neutral"] += 1
    return sentiments

# Function to generate word cloud
def generate_wordcloud(reviews):
    all_reviews = " ".join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reviews)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Set the layout of the Streamlit app
st.set_page_config(page_title="Amazon Review Analysis", page_icon="🛒", layout="wide")

# Add a sidebar with a logo and description
st.sidebar.markdown("""
    <h2 style='text-align: center; color: #ffba08;'>Amazon Review Analysis</h2>
    <div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-top: 20px;'>
        <h4 style='color: #1a73e8; text-align: center;'>Analyze Amazon Product Reviews</h4>
        <p style='text-align: center; color: #333;'>Enter an Amazon product link and get sentiment analysis along with a word cloud!</p>
    </div>
""", unsafe_allow_html=True)


# Add a main title and subtitle
st.markdown("<h1 style='text-align: center; color: #ffba08;'>Amazon Product Review Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #6c757d;'>Gain insights from customer reviews with sentiment analysis and word cloud visualization.</h4>", unsafe_allow_html=True)

# Input for Amazon product URL
product_url = st.sidebar.text_input("Enter Amazon Product URL:")

# Display a button that links to Amazon
st.sidebar.markdown("<a href='https://www.amazon.in/' target='_blank' style='text-decoration: none;'><button style='background-color: #ffba08; color: white; padding: 10px; border-radius: 5px;'>Go to Amazon</button></a>", unsafe_allow_html=True)

# Main content area for displaying results
if product_url:
    try:
        st.markdown("<h3 style='color: #ffba08;'>Fetching reviews, please wait...</h3>", unsafe_allow_html=True)
        reviews = get_amazon_reviews_selenium(product_url)
        
        if reviews:
            st.success(f"Total reviews found: {len(reviews)}")
            
            # Display reviews with a golden highlight
            with st.expander("Show Reviews"):
                st.write(pd.DataFrame(reviews, columns=["Review"]))

            # Sentiment Analysis with metrics styled in gold
            st.subheader("📊 Sentiment Analysis")
            sentiments = analyze_sentiment(reviews)
            col1, col2, col3 = st.columns(3)
            col1.metric("Positive", sentiments['positive'], delta_color="inverse")
            col2.metric("Negative", sentiments['negative'], delta_color="inverse")
            col3.metric("Neutral", sentiments['neutral'], delta_color="inverse")

            # Generate and display word cloud with a custom heading
            st.subheader("🌤 Word Cloud of Reviews")
            st.markdown("<h4 style='color: #ffba08;'>The most frequent words in the reviews are displayed below.</h4>", unsafe_allow_html=True)
            generate_wordcloud(reviews)
        else:
            st.warning("No reviews found for this product.")
    
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Add a golden footer with your LinkedIn profile link
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; color: #ffba08;'>Developed by <a href='https://www.linkedin.com/in/jahnu-deka-126979113/' target='_blank' style='color: gold;'>Jahnu Deka</a></p>", unsafe_allow_html=True)
