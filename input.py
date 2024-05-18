import streamlit as st
import praw
import pandas as pd

# Streamlit interface for entering Reddit API credentials
st.title('Reddit Subreddit Scraper')

client_id = st.text_input("Enter your Reddit client ID", type="default")
client_secret = st.text_input("Enter your Reddit client secret", type="password")
user_agent = st.text_input("Enter your Reddit user agent")

# Only proceed with Reddit interactions if credentials are provided
if client_id and client_secret and user_agent:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    def collect_comments_and_replies(submission):
        """Collect comments and directly associated replies."""
        data_list = []
        submission.comments.replace_more(limit=0)  # Load all comments and remove MoreComments

        for comment in submission.comments.list():
            comment_data = {
                "post_id": submission.id,
                "author": str(submission.author),
                "url": submission.url,
                "title": submission.title,
                "comment_id": comment.id,
                "comment_body": comment.body,
                "comment_author": str(comment.author),
                "reply_body": ""
            }

            comment.replies.replace_more(limit=0)
            for reply in comment.replies:
                reply_data = comment_data.copy()
                reply_data['reply_body'] = reply.body
                data_list.append(reply_data)

            if not comment.replies:
                data_list.append(comment_data)

        return data_list

    def extract_subreddit_posts(subreddit_name, limit=10):
        all_data = []
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.hot(limit=limit):
            all_data.extend(collect_comments_and_replies(submission))

        return pd.DataFrame(all_data)

    # User inputs for subreddit scraping
    subreddit_name = st.text_input("Enter Subreddit Name", "python")
    limit = st.number_input("Number of Posts to Scrape", min_value=1, max_value=100, value=10)

    if st.button("Scrape"):
        data_df = extract_subreddit_posts(subreddit_name, limit)
        st.write(data_df)
        csv = data_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "comments_and_replies.csv", "text/csv", key='download-csv')
else:
    st.warning("Please enter all required Reddit API credentials to enable scraping functionality.")
