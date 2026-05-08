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
    
    return (user, len(followed_users))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = \
                                    'Compute Twitter follows.')
    parser.add_argument('-w','--num-workers',default=1,type=int,
                            help = 'Number of workers')
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    start = time.time()
    sc = SparkContext(master = f'local[{args.num_workers}]')

    lines = sc.textFile(args.filename)
    
    data = lines.map(parse_line) \
                .reduceByKey(lambda x, y: x + y) \
                .cache()
    
    max_follows = data.map(lambda x: x[1]).max()
    max_user = data.filter(lambda x: x[1] == max_follows).map(lambda x: x[0]).collect()[0]
    average_follows = data.map(lambda x: x[1]).mean()
    no_follows = data.filter(lambda x: x[1] == 0).count()
    
    end = time.time()
    
    total_time = end - start

    # the first ??? should be the twitter id
    print(f'max follows: {max_user} follows {max_follows}')
    print(f'users follow on average: {average_follows}')
    print(f'number of user who follow no-one: {no_follows}')
    print(f'num workers: {args.num_workers}')
    print(f'total time: {total_time}')

