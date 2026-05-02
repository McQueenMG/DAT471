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
        A tuple consisting of the followed user and a count of 1. (followed_user, 1)
        Additionally, it yields a tuple to count the total number of users. ('total_users', 1)
        """
        
        user, followed_users_str = line.split(':')
        user = user.strip()
        followed_users = followed_users_str.split()
        
        for followed_user in followed_users:
            followed_user = followed_user.strip()
            yield (followed_user, 1)
        yield ('total_users', 1)
            
            
    def combiner(self, user, counts):
        """
        Combines the counts of followers for each user within one node

        Parameters:
        - user: A string representing a user ID.
        - counts: An iterable of counts representing the number of followers for the user, calculated by the mapper within a node.
        
        Return Value:
        A tuple consisting of a user and their total followers count within a node. (user, followers_count)
        """
        yield (user, sum(counts))


    def reducer(self, user, values):
        """
        Summarises the counts of followers and follows for each user before collecting the 
        data on one node to compute statistics.
        
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of counts representing the number of followers for the user, calculated by the mapper within a node.
        
        Return Value:
        A tuple consisting of a user, and their total followers count.
        (user, followers_count)
        """
    
            
        followers_count = 0
        for count in values:
            followers_count += count
                    
        yield (None, (user, followers_count))
        
    def statistics_reducer(self, _, counts):
        """
        Uses the output of the first reducer to compute the user with the most followers, how many they follow,
        the average number of followers, and the count of users that follow no-one.  
               
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of tuples, where each tuple consists of a user and their total followers count, calculated by the first reducer.
        
        Return Value:
        A tuple consisting of a key and a value for each of the following statistics:
        - ('id with most followers', user_id)
        - ('most followers of any id', followers_count)
        - ('average followers of all ids', average_followers)
        - ('count of ids that follows no-one', count_follows_no_one)
        """
        
        most_followers_user = None
        most_followers = 0
        total_followers = 0
        follows_someone = 0
        total_users_count = 0
        
        for user, followers_count in counts:
            if user == 'total_users':
                total_users_count += followers_count
                continue
            
            if followers_count > most_followers:
                most_followers_user = user
                most_followers = followers_count
                
            if followers_count > 0:
                follows_someone += 1
            
            total_followers += followers_count
            
        followers_no_one_count = total_users_count - follows_someone
        
        average_followers = total_followers / total_users_count
        
        yield ('id with most followers', most_followers_user)
        yield ('most followers of any id', most_followers)
        yield ('average followers of all ids', average_followers)
        yield ('count of ids that has no followers', followers_no_one_count)       
        
        
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