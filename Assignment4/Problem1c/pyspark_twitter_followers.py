#!/usr/bin/env python3

import time
import argparse
import findspark
findspark.init()
from pyspark import SparkContext

def parse_line(line):
    """
    Parses a line of the input file, which consists of one user and the users they follow.
    
    Parameter:
    - line: A string in the format "user: followed_user1 followed_user2 ..."
    
    Return Value:
    A tuple consisting of the original user and a list of users that follow them. (user, follows_count)
    """
    user, followed_users_str = line.split(':')
    user = user.strip()
    followed_users = followed_users_str.split()
    for followed_user in followed_users:
        yield (followed_user, 1)
    yield ("user_count", 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = \
                                    'Compute Twitter followers.')
    parser.add_argument('-w','--num-workers',default=1,type=int,
                            help = 'Number of workers')
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    start = time.time()
    sc = SparkContext(master = f'local[{args.num_workers}]')

    lines = sc.textFile(args.filename)

    data = lines.flatMap(parse_line) \
        .reduceByKey(lambda x, y: x + y) \
        .cache()
        
    max_followers = data.filter(lambda x: x[0] != "user_count").map(lambda x: x[1]).max()
    total_users = data.filter(lambda x: x[0] == "user_count").map(lambda x: x[1]).collect()[0]
    total_followers = data.map(lambda x: x[1]).sum() - 1  # subtract 1 to exclude the user_count key
    average_followers = total_followers / total_users
    no_followers = total_users - data.filter(lambda x: x[0] != "user_count").count()
    max_user = data.filter(lambda x: x[1] == max_followers).map(lambda x: x[0]).collect()[0]
    
    end = time.time()
    
    total_time = end - start

    # the first ??? should be the twitter id
    print(f'max followers: {max_user} has {max_followers} followers')
    print(f'followers on average: {average_followers}')
    print(f'number of user with no followers: {no_followers}')
    print(f'num workers: {args.num_workers}')
    print(f'total time: {total_time}')

