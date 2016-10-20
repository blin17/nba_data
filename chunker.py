import pandas as pd
import argparse
import os
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

if not os.path.exists(game_name):
    os.makedirs(game_name)


for i in range(0,num_events,10):
	subset_df = game_df[i:i+10].copy()
	subset_df.to_json(game_name+'/event'+str(i)+'-'+str(i+10)+'.'+game_name+'.json')

