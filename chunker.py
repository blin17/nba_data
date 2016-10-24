import pandas as pd
import argparse
import os
from pandas.io.json import json_normalize
import json

parser = argparse.ArgumentParser(description='Chunks a NBA game into smaller bits.')
parser.add_argument('--path', type=str,
                    help='a path to json file to read the events from',
                    required = True)

args = parser.parse_args()

data_path = args.path.split('/')[0]
game_name = args.path.split('/')[1][:-5]
game_df = pd.read_json(args.path)

game_date = game_df['gamedate'][0]
game_id = game_df['gameid'][0]
print "Finished Loading DataFrame... Starting to Remove Duplicates"

frames_df = pd.DataFrame()
for i in range(len(game_df.events)):
    frame = json_normalize(game_df.events[i], 'moments', 
                   ['eventId', 'home', 'visitor'])
    frames_df = pd.concat([frames_df,frame])
frames_df.columns = ['quarter', 'time', 'game_clock', 'shot_clock', 'null', 'moments', 'eventId', 'home', 'visitor']

home = frames_df.iloc[0]['home']
visitor = frames_df.iloc[0]['visitor']
frames_df = frames_df.drop(['null', 'home', 'visitor', 'eventId'],axis=1)

frames_df_no_dupes = frames_df.drop_duplicates(subset=['time'],keep='first')
frames_df_no_dupes = frames_df_no_dupes.reset_index()
print "Finished Removing Duplicates... Starting to Write Files"
if not os.path.exists(game_name):
    os.makedirs(game_name)

for i in range(len(frames_df_no_dupes)/1000 + 1):
    num_moments = len(frames_df_no_dupes[i*1000:(i+1)*1000])
    l = pd.DataFrame([game_date, game_id, i, len(frames_df_no_dupes)/1000, num_moments, home, visitor, frames_df_no_dupes[i*1000:(i+1)*1000].to_dict('index')]).T
    l.columns=['gamedate','gameid','frameid', 'max_frame','num_moments', 'home','visitor','frames']
    l.to_json(game_name+'/frame'+str(i)+'-'+game_name+'.json')
print "Finished Writing Files"

