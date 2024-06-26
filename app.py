import streamlit as st
import pandas as pd
from connector import send_post, check_flairs, send_comment
from logger import setup_custom_logger
from time import sleep

# Setup logger
logger = setup_custom_logger(__name__)
logger.propagate = False

# Streamlit UI setup
st.title("Reddit Bulk Poster")
st.write("""
This app allows you to posts on multiple subreddits at once. 
You can select the flair for each subreddit.
**IMPORTANT**: Your text file must be formatted like this example or it won't work:
""")

st.expander("Example", expanded=False).code("r/learnpython\nr/programming\nr/python")

uploaded_file = st.file_uploader("Choose your subreddit text file", type="txt", accept_multiple_files=False)
if uploaded_file:
    content = uploaded_file.getvalue().decode("utf-8")
    lines = content.split("\n")
    subreddits = [line.strip().removeprefix('r/') for line in lines if line.strip() and line.startswith('r/')]

    if subreddits:
        data = []
        for subreddit in subreddits:
            flairs = check_flairs(subreddit)
            if flairs and flairs['flairs']:
                flair_options = {flair['flair_text']: flair['flair_id'] for flair in flairs['flairs']}
                selected_flair_text = st.selectbox(f"Select flair for {subreddit}:", list(flair_options.keys()))
                selected_flair_id = flair_options[selected_flair_text]
                data.append([subreddit, selected_flair_text, selected_flair_id])
            else:
                # Append None or a similar indicator that no flair is available/required
                data.append([subreddit, "No Flair", None])

        df = pd.DataFrame(data, columns=['Subreddit', 'Flair Name', 'Flair ID'])
        st.table(df)

        title = st.text_input("Title")

        # Radio button to choose between text post or link post
        post_type = st.radio("Post Type", ["Text", "Link"])

        # Conditional input fields based on post type selection
        if post_type == "Text":
            body = st.text_area("Body")
            url = None  # No URL for text posts
        else:
            url = st.text_input("URL")
            body = None  # No body for link posts

        comment = st.text_area("Comment")

        if st.button("Submit Post"):
            success_count = 0  # Initialize success counter
            for index, row in df.iterrows():
                # Adjusting send_post parameters based on post type
                if post_type == "Text":
                    response = send_post(title, body, row['Flair ID'], row['Subreddit'], "selftext", None)

                else:
                    response = send_post(title, None, row['Flair ID'], row['Subreddit'], "link", url)

                if response:
                    st.success(f"Posted successfully on {row['Subreddit']}")
                    success_count += 1

                    # Check if comment is provided and post_id is available
                    sleep(2)
                    if comment and response.get('post_id'):
                        # Send comment
                        comment_response = send_comment(response['post_id'], comment)
                        if comment_response:
                            st.success(f"Comment posted on {row['Subreddit']}")
                        else:
                            st.error(f"Failed to post comment on {row['Subreddit']}")

                else:
                    st.error(f"Failed to post on {row['Subreddit']}")

            st.info(f"Finished. Posted to {success_count} subreddits.")
            st.balloons()
    else:
        st.error("No subreddits found in the file. Please make sure the file is formatted correctly.")
else:
    st.info("Please upload a text file to start scheduling posts.")