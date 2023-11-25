

#### SCRAPPING OF YOUTUBE INFLUENCER DATA ####
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import re
import os
import pandas as pd
import openpyxl

api_key = 'AIzaSyBJiQuqpt04yVsbs6rfJhPE1L6ui5s8oco'  
def impressions(view_count, subscriber_count):
    # Check if subscriber_count is zero to avoid division by zero
    if int(subscriber_count) == 0:
        return 0  # or any other value that makes sense in your context

    return int(view_count) / int(subscriber_count)

def reach(total_view, total_subscriber):
    # Check if total_subscriber is zero to avoid division by zero
    if int(total_subscriber) == 0:
        return 0  # or any other value that makes sense in your context

    return int(total_view) / int(total_subscriber)

def avg_comments(number_comments, number_subscriber):
    # Check if number_subscriber is zero to avoid division by zero
    if int(number_subscriber) == 0:
        return 0  # or any other value that makes sense in your context

    return int(number_comments) / int(number_subscriber)

def extract_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails
def build_youtube_service():
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)
    return youtube
def get_latest_channel_posts(channel_id, max_results=3):
   data_list = []

   youtube = build('youtube', 'v3', developerKey=api_key)
   
   # Set the channel ID or username of the desired YouTube channel
   channel_id = channel_id  # Replace with the desired channel ID or username
   
   # Retrieve the channel's uploads playlist ID
   channels_response = youtube.channels().list(
       part='contentDetails',
       id=channel_id
   ).execute()
   
   uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
   
   # Retrieve the latest three videos from the uploads playlist
   playlist_items_response = youtube.playlistItems().list(
       part='snippet',
       playlistId=uploads_playlist_id,
       maxResults=3  # Adjust the number of videos as needed
   ).execute()
   
   # Process the playlist items
   for playlist_item in playlist_items_response['items']:
       video_title = playlist_item['snippet']['title']
       video_id = playlist_item['snippet']['resourceId']['videoId']
       video_url = f'https://www.youtube.com/watch?v={video_id}'
       data =[{'video_title': video_title,
                      'video_id': video_id,
                      'video_url': video_url}] 
   data_list.append(data)
   return data_list
influencer_data = []
processed_channels = set()
def extract_video_data_with_hashtag(keyword, max_results):
    try:
        youtube = build_youtube_service()
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            maxResults=max_results
        )

        response = request.execute()

        for item in response['items']:
            channel_id = item['snippet']['channelId']
            video_id = item['id']['videoId']
        
            # Skip the current item if the channel ID is already processed
            if any(influencer['channel_id'] == channel_id for influencer in influencer_data):
                continue
            channel_title = item['snippet']['channelTitle']
    
            # Skip the current item if the channel title is already processed
            if channel_title in processed_channels:
                continue

            processed_channels.add(channel_title)
            if any(influencer['channel_title'] == item['snippet']['channelTitle'] for influencer in influencer_data):
                continue
                     # Check if the influencer with the same channel ID already exists
            influencer = next((infl for infl in influencer_data if infl['channel_id'] == channel_id), None)
        
            if influencer:
                # Update the latest posts for the influencer
                influencer['latest_posts'].append({'video_id': video_id, 'title': item['snippet']['title']})
                continue
        
            hashtag = keyword
            title = item['snippet']['title']
        
            # Fetch additional video information
            video_request = youtube.videos().list(
                part='statistics',
                id=video_id
            )
            video_response = video_request.execute()
        
            # Extract the desired statistics for the video
            statistics = video_response['items'][0]['statistics']
            views = statistics.get('viewCount', 0)
            likes = statistics.get('likeCount', 0)
            dislikes = statistics.get('dislikeCount', 0)
            shares = statistics.get('shareCount', 0)
            comments = statistics.get('commentCount', 0)
        
            # Fetch channel information
            channel_request = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            channel_response = channel_request.execute()
        
            # Extract the desired channel information
            channel_snippet = channel_response['items'][0]['snippet']
            #channel_title = channel_snippet['title']
            #if any(influencer['channel_title'] == item['snippet']['channelTitle'] for influencer in influencer_data):
            #    continue
            channel_username = channel_snippet['customUrl']
            full_name = channel_snippet.get('fullName', '')
            subscribers = channel_response['items'][0]['statistics'].get('subscriberCount', 0)
            country = channel_snippet.get('country', '') 
            #email = channel_snippet.get('email', '')  # Add email field
            biography = channel_snippet.get('description', '') 
            created_at = channel_snippet.get('publishedAt', '')
            updated_at = channel_snippet.get('updatedAt', '')
              # Get the video comments count
           # comment_request = youtube.commentThreads().list(
           # part='snippet',
           # videoId=video_id,
           # maxResults=1  # Fetch only one comment thread
           #  )
           # comment_response = comment_request.execute()
           # comments = comment_response['pageInfo']['totalResults']
              # Fetch channel information to get total view and subscriber count
            channel_request = youtube.channels().list(
            part='statistics',
            id=channel_id
             )
            channel_response = channel_request.execute()

           # Extract the total view and subscriber count
            total_view = channel_response['items'][0]['statistics'].get('viewCount', 0)
            total_subscriber = channel_response['items'][0]['statistics'].get('subscriberCount', 0)
            impression = impressions(view_count=views, subscriber_count=subscribers)
            reachs = reach(total_view, total_subscriber)
            avg_comment = avg_comments(comments, subscribers)
             # Calculate the engagement rate
            engagements = int(likes) + int(dislikes) + int(shares)
            engagement_rate = engagements / int(views) if int(views) > 0 else 0
            latest_post = get_latest_channel_posts(channel_id)
            #latest_post = [{'video_id': video_id, 'title': item['snippet']['title']}]
            email = extract_emails(biography)
            email = str(email).replace('[','').replace(']', '')
        
            # Create a dictionary for the influencer data
            influencer = {
                'channel_id': channel_id,
                'video_id': video_id,
                'hashtag': hashtag,
                'title': title,
                'views': views,
                'likes': likes,
                'dislikes': dislikes,
                'shares': shares,
                'channel_title': channel_title,
                'subscribers': subscribers,
                'channel_link': f"https://www.youtube.com/channel/{channel_id}",
                'channel_username': channel_username,
                'full_name': full_name,
                'video_thumbnail': item['snippet']['thumbnails']['default']['url'],
                'engagements': engagements,  # Example field, customize as needed
                'engagement_rate': engagement_rate,  # Example field, customize as needed
                'created_at': created_at,  # Add created_at field
                'updated_at': updated_at,  # Add updated_at field
                'comments': comments,  # Add comments field
                'country': country,  # Add country field
                'total_results': response['pageInfo']['totalResults'],
                'email': email,  # Add email field
                'impression':impression,
                'reachs':reachs,
                'avg_comments':avg_comment,
                'biography': biography,
                'latest_post':latest_post
            }
        
            # Append the influencer data to the list
            influencer_data.append(influencer)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        
        
# Define the CSV fieldnames
fieldnames = [
    'channel_id', 'video_id', 'hashtag', 'title', 'views', 'likes', 'dislikes', 'shares', 'channel_title',
    'subscribers', 'channel_link', 'channel_username', 'full_name', 'video_thumbnail', 'engagements',
    'engagement_rate', 'created_at', 'updated_at', 'comments', 'country','total_results','email','impression','reachs','avg_comments', 'biography', 'latest_post'
]

def delete_row(file_path,row_index=2):
    # Load the workbook
    sheet_name = "Sheet1"
    workbook = openpyxl.load_workbook(file_path)

    # Select the sheet
    sheet = workbook[sheet_name]

    # Delete the entire row
    sheet.delete_rows(row_index)

    # Save the changes
    workbook.save(file_path) 


if __name__ == '__main__':
    #hash_keyword = []
    counter = 1
    max_results = 500  # Specify the desired number of results
    
    checked_data =[]
    csv_file_path = 'data.csv'
    data_frame = pd.read_excel('Keywords (2).xlsx')
    column1 = data_frame['Keywords'].values.tolist()
    for column in column1:
       # print('#'+column)
       hash_tag = '#'+column
       extract_video_data_with_hashtag(hash_tag, max_results)
       file_exists = os.path.isfile(csv_file_path)
       if file_exists:
         # Check if the file is empty
         is_empty = os.stat(csv_file_path).st_size == 0
       #with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
       #   csv_writer = csv.writer(file)
       #   if not file_exists or is_empty:
       #      csv_writer.writerow(fieldnames)
          #encoded_row = []
       with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
          writer = csv.DictWriter(file, fieldnames=fieldnames)
          if not file_exists or is_empty:
             writer.writeheader()
          writer.writerows(influencer_data)
          checked_data.append(influencer_data)
        
          #for index,row in enumerate(influencer_data):
          #    csv_writer.writerow(row)
          #    checked_data.append(row)
          if checked_data:
             delete_row('Keywords (2).xlsx')
             print(f'{counter} .Successfully scrapping and store this information from {hash_tag}')
             print()
          else:
             print('The extraction aborted...')
          counter +=1




