 #!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep

class MRJobTwitterFollows(MRJob):
    
    def mapper(self, _, line):
        
        # Example line from twitter_x.txt: id_0: id_1, id_2, ... where id_0 follows id_1, id_2, ...
        # here is an example line from twitter-2010_x.txt: 12926542: 30329952 46174421 17126283 21356017 18898143 18277078 16442847 19896448 24316789 32645182 15364232 51474362 22427119 20746022 49490040 36206550 28903864 19003801 47151158
        user, followed_users_str = line.split(':')
        user = user.strip()
        followed_users = followed_users_str.split()
    
        # Emit each followed user with the follower as the key
        for followed_user in followed_users:
            yield (followed_user, ('follower', 1))
            
        yield (user, ('follows', len(followed_users)))
            
            
    def combiner(self, user, values):
        follower_count = 0
        follows_count = 0
        for value_type, count in values:
            if value_type == 'follower':
                follower_count += count
            elif value_type == 'follows':
                follows_count += count
        yield (user, ('follower', follower_count))
        yield (user, ('follows', follows_count))



    def reducer(self, user, values):
        follower_count = 0
        follows_count = 0
        for value_type, count in values:
            if value_type == 'follower':
                follower_count += count
            elif value_type == 'follows':
                follows_count += count
            
        yield (None, (user, follower_count, follows_count))
        
    def reducer_final(self, _, counts):
        most_follows_user = None
        most_follows = 0
        total_followers = 0
        total_users = 0
        follows_no_one_count = 0
        
        for user, follower_count, follows_count in counts:
            
            if follows_count > most_follows:
                most_follows_user = user
                most_follows = follows_count
            
            total_followers += follower_count
            total_users += 1
            
            if follows_count == 0:
                follows_no_one_count += 1
        
        average_followed = total_followers / total_users
        
        yield ('id with most follows', most_follows_user)
        yield ('most follows of any id', most_follows)
        yield ('average followers of all ids', average_followed)
        yield ('count of ids that follows no-one', follows_no_one_count)       
        
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(reducer=self.reducer_final)
        ]
        

if __name__ == '__main__':
    MRJobTwitterFollows.run()

    # The final (key,value) pairs returned by the class should be
    # 
    # yield ('most followed id', ???)
    # yield ('most followed', ???)
    # yield ('average followed', ???)
    # yield ('count follows no-one', ???)
    #
    # You will, of course, need to replace ??? with a suitable expression