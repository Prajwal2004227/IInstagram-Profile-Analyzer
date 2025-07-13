from flask import Flask, render_template, request, jsonify
import instaloader
from textblob import TextBlob

app = Flask(__name__)
bot = instaloader.Instaloader()

# Function to get profile info
def get_profile_info(profileid):
    try:
        profile = instaloader.Profile.from_username(bot.context, profileid)
        profile_data = {
            "username": profile.username,
            "user_id": profile.userid,
            "posts_count": profile.mediacount,
            "followers_count": profile.followers,
            "following_count": profile.followees,
            "bio": profile.biography,
            "external_url": profile.external_url or "No URL provided",
            "profile_picture_url": profile.profile_pic_url  # Profile picture URL
        }
        print(f"Profile picture URL: {profile_data['profile_picture_url']}")  # Debug log
        return profile_data
    except instaloader.exceptions.ProfileNotExistsException:
        return {"error": f"Profile '{profileid}' does not exist."}
    except Exception as e:
        return {"error": str(e)}

# Function to analyze sentiment of text
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Function for user profile sentiment risk analysis
def profile_risk_analysis(profileid):
    try:
        profile = instaloader.Profile.from_username(bot.context, profileid)
        user_posts = [post.caption for post in profile.get_posts() if post.caption]

        if not user_posts:
            return "The user has no posts with captions to analyze."
        
        print(f"Analyzing {len(user_posts)} posts...")  # Debug log
        
        # Calculate average sentiment of the captions
        total_sentiment = sum(analyze_sentiment(post) for post in user_posts)
        avg_sentiment = total_sentiment / len(user_posts)

        print(f"Average Sentiment: {avg_sentiment}")  # Debug log
        
        # Risk analysis based on average sentiment
        if avg_sentiment >= 0.2:
            return "High Risk (Positive Sentiment)"
        elif -0.2 < avg_sentiment < 0.2:
            return "Medium Risk (Neutral Sentiment)"
        else:
            return "Low Risk (Negative Sentiment)"
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Error: The profile '{profileid}' does not exist."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.route('/')
def home():
    return render_template('main1.html')

@app.route('/get_profile_info', methods=['POST'])
def get_profile_info_api():
    profileid = request.form['username']
    profile_data = get_profile_info(profileid)
    return jsonify(profile_data)

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment_api():
    text = request.form['text']
    sentiment = analyze_sentiment(text)
    return jsonify({'sentiment': sentiment})

@app.route('/profile_risk_analysis', methods=['POST'])
def profile_risk_analysis_api():
    profileid = request.form['username']
    result = profile_risk_analysis(profileid)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
