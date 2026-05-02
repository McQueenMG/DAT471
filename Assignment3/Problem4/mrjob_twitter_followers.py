 #!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep

class MRJobTwitterFollowers(MRJob):
    
    def mapper(self, _, line):
        """
        Processes each line of the input file, which consists of 
        one user and the users they follow.
        
        Parameter:
        - line: A string in the format "user: followed_user1 followed_user2 ..."
        
        Return Value:
        A tuple consisting of a followed user and a count of 1 to signinfy that they now have +1 follower. (followed_user, ('follower', 1))
        A tuple consisting of the original user and the number of users they follow. (user, ('follows', count))
        """
        
        user, followed_users_str = line.split(':')
        user = user.strip()
        followed_users = followed_users_str.split()
    
        for followed_user in followed_users:
            yield (followed_user, ('follower', 1))
            
        yield (user, ('follows', len(followed_users)))
            
            
    def combiner(self, user, values):
        """
        Summarises the counts of followers and follows for each user within one node before sending them to the reducer.
        
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of tuples, where each tuple is either:
            - ('follower', 1) indicating that this user has one more follower.
            - ('follows', count) indicating that this user follows 'count' users.
        
        Return Value:
        A tuple consisting of a followed user and a count of their total followers. (followed_user, ('follower', follower_count))
        A tuple consisting of the original user and the number of users they follow. (user, ('follows', follows_count))
        """
        
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
        """
        Summarises the counts of followers and follows for each user before collecting the 
        data on one node to compute statistics.
        
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of tuples, where each tuple is either:
            - ('follower', count) indicating that this user has 'count' more followers.
            - ('follows', count) indicating that this user follows 'count' users.
        
        Return Value:
        A tuple consisting of a user, their total follower count, and their total follows count. 
        (user, follower_count, follows_count)
        """
        follower_count = 0
        follows_count = 0
        for value_type, count in values:
            if value_type == 'follower':
                follower_count += count
            elif value_type == 'follows':
                follows_count += count
                    
        yield (None, (user, follower_count, follows_count))
        
    def statistics_reducer(self, _, counts):
        """
        Uses the output of the first reducer to compute the user with the most follows, how many they follow,
        the average number of followers, and the count of users that follow no-one.  
               
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of tuples, where each tuple is either:
            - ('follower', count) indicating that this user has 'count' more followers.
            - ('follows', count) indicating that this user follows 'count' users.
        
        Return Value:
        A tuple consisting of a key and a value for each of the following statistics:
        - ('id with most follows', user_id)
        - ('most follows of any id', follows_count)
        - ('average followers of all ids', average_followers)
        - ('count of ids that follows no-one', count_follows_no_one)
        """
        
        most_followers_user = None
        most_followers = 0
        total_followers = 0
        total_users = 0
        has_no_followers_count = 0
        
        for user, follower_count, follows_count in counts:
            
            if follower_count > most_followers:
                most_followers_user = user
                most_followers = follower_count
            
            total_followers += follower_count
            total_users += 1
            
            if follower_count == 0:
                has_no_followers_count += 1
        
        average_followed = total_followers / total_users
        
        yield ('id with most followers', most_followers_user)
        yield ('most followers of any id', most_followers)
        yield ('average followers of all ids', average_followed)
        yield ('count of ids that has no followers', has_no_followers_count)       
        
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(reducer=self.statistics_reducer)
        ]
        

if __name__ == '__main__':
    MRJobTwitterFollowers.run()

    # The final (key,value) pairs returned by the class should be
    # 
    # yield ('most followers id', ???)
    # yield ('most followers', ???)
    # yield ('average followers', ???)
    # yield ('count no followers', ???)
    #
    # You will, of course, need to replace ??? with a suitable expression