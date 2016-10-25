import pandas as pd
import os
import json
import requests
import time
import argparse
parser = argparse.ArgumentParser(description='Chunks a NBA game into smaller bits.')
parser.add_argument('--path', type=str,
                    help='a path to json file to read the events from',
                    required = True)

args = parser.parse_args()

game_df = pd.read_json(args.path)
events = game_df.events
num_events = len(game_df)
data_path = args.path.split('/')[0]
game_name = args.path.split('/')[1][:-5]

game_df = pd.read_json(data_path + '/' + game_name + '.json', dtype={'gameid': str})
gameid = game_df['gameid'][0]
print gameid
url="http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&EndRange=55800&GameID="+gameid+"&RangeType=2&StartPeriod=1&StartRange=0"
print url
content = requests.get(url).content
while len(content) == 0:
    time.sleep(5)
    content = requests.get(url).content
    print len(content)
s=json.loads(content)
scores = pd.DataFrame(s['resultSets'][0]['rowSet'], columns=s['resultSets'][0]['headers'])
scores = scores.drop(['EVENTNUM','EVENTMSGTYPE','EVENTMSGACTIONTYPE','NEUTRALDESCRIPTION', u'PERSON3TYPE',
       u'PLAYER3_ID', u'PLAYER3_NAME', u'PLAYER3_TEAM_ID',
       u'PLAYER3_TEAM_CITY', u'PLAYER3_TEAM_NICKNAME',
       u'PLAYER3_TEAM_ABBREVIATION'], axis=1)
scores['MINUTES']= scores['PCTIMESTRING'].apply(lambda d: d.split(':')[0]).astype('int')
scores['SECONDS']= scores['PCTIMESTRING'].apply(lambda d: d.split(':')[1]).astype('int')
scores['GAMECLOCK'] = scores['MINUTES']*60 + scores['SECONDS']
scores = scores[~ (scores['HOMEDESCRIPTION'].isnull() & scores['VISITORDESCRIPTION'].isnull())]
scores.to_json(data_path+'/play_by_play/play.by.play-'+game_name+'.json')