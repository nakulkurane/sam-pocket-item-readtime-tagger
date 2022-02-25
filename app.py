from pocket import Pocket
from datetime import datetime, timedelta
import os
import json

def stamp_to_epoch(timestamp):
    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hours = int(timestamp[11:13])
    mins = int(timestamp[14:16])
    epoch_seconds = int(datetime(year, month, day, hours, mins).strftime('%s'))
    return epoch_seconds

def authenticate():
    p = Pocket(
        consumer_key=os.environ['POCKET_KEY'],
        access_token=os.environ['POCKET_TOKEN']
    )
    return p

def tag_items(p):

    # From how many days ago do you want to retrieve Pocket list items?
    days_prior_today = 7

    days_from_today_stamp = datetime.now() - timedelta(days_prior_today)

    epoch_start_date_for_list = stamp_to_epoch(str(days_from_today_stamp))

    # retrieve all my unread saved articles from 7 days ago
    lis = p.get(since=epoch_start_date_for_list, state="unread")

    sub_list = lis[0]['list']

    '''
    Iterate through dictionary and remove items which were added before the specified date parameter.
    This is so we minimize the load on the Pocket tagging. Pocket's GET request will return
    all items last _updated_ after the time specified (which includes old items that may have been tagged the last time 
    the function was run)
    '''
    for k, v in list(sub_list.items()):
        if int(v['time_added']) <= epoch_start_date_for_list:
            # print (sub_dict[k]['item_id'])
            del sub_list[k]
    '''
    Iterate through the sub list and tag items accordingly
    '''
    for index, i in enumerate(sub_list):
        print(index+1, "out of", len(sub_list))
        if 'is_article' in sub_list[str(i)].keys() or 'has_video' in sub_list[str(i)].keys():
            # if item is an article outright OR item is def NOT a video (has_video value 0 means not a video, 1 means has
            # a video, 2 means is a video
            if (int(sub_list[str(i)]['is_article']) == 1 or int(sub_list[str(i)]['has_video']) == 0):

                if 'top_image_url' in sub_list[str(i)].keys() and "ytimg" not in sub_list[str(i)]['top_image_url']:

                    if 'time_to_read' in sub_list[str(i)].keys():

                        read_time = sub_list[str(i)]['time_to_read']
                        print("tagging item", i, index+1, "out of", len(sub_list))
                        if int(read_time) <= 2:
                            p.tags_add(item_id=i, tags="a quick read").commit()
                        elif read_time > 2 and read_time <= 5:
                            p.tags_add(item_id=i, tags="a medium read").commit()
                        else:
                            p.tags_add(item_id=i, tags="a long read").commit()

                    else:

                        word_count = sub_list[str(i)]['word_count']
                        read_time = int(word_count) / 250
                        print("tagging item", i, index+1, "out of", len(sub_list))

                        if read_time <= 2:
                            p.tags_add(item_id=i, tags="a quick read").commit()
                        elif read_time > 2 and read_time <= 5:
                            p.tags_add(item_id=i, tags="a medium read").commit()
                        else:
                            p.tags_add(item_id=i, tags="a long read").commit()

                elif 'top_image_url' in sub_list[str(i)].keys() and "ytimg" in sub_list[str(i)]['top_image_url']:
                    print("tagging item", i, index+1, "out of", len(sub_list))

                    p.tags_add(item_id=i, tags="article with video").commit()

    print('Tagged items successfully')

def main():
    p = authenticate()
    tag_items(p)


if __name__ == '__main__':
    main()


def lambda_handler(event, context):
    main()
