 #!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep

class MRJobTwitterFollows(MRJob):
    
    def mapper(self, _, line):
        """
        Processes each line of the input file, which consists of 
        one user and the users they follow.
        
        Parameter:
        - line: A string in the format "user: followed_user1 followed_user2 ..."
        
        Return Value:
        A tuple consisting of the original user and the number of users they follow. (user, count)
        """
        
        user, followed_users_str = line.split(':')
        user = user.strip()
        followed_users = followed_users_str.split()
            
        yield (user, len(followed_users))



    def reducer(self, user, values):
        """
        Summarises the counts of followers and follows for each user before collecting the 
        data on one node to compute statistics.
        
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of counts representing the number of users that the user follows, calculated by the mapper within a node.
        
        Return Value:
        A tuple consisting of a user, and their total follows count.
        (user, follows_count)
        """
        follows_count = 0
        for count in values:
            follows_count += count
                    
        yield (None, (user, follows_count))
        
    def statistics_reducer(self, _, counts):
        """
        Uses the output of the first reducer to compute the user with the most follows, how many they follow,
        the average number of followers, and the count of users that follow no-one.  
               
        Parameter:
        - user: A string representing a user ID.
        - values: An iterable of tuples, where each tuple consists of a user and their total follows count, calculated by the first reducer.
        
        Return Value:
        A tuple consisting of a key and a value for each of the following statistics:
        - ('id with most follows', user_id)
        - ('most follows of any id', follows_count)
        - ('average follows of all ids', average_follows)
        - ('count of ids that follows no-one', count_follows_no_one)
        """
        
        most_follows_user = None
        most_follows = 0
        total_follows = 0
        total_users = 0
        follows_no_one_count = 0
        
        for user, follows_count in counts:
            
            if follows_count > most_follows:
                most_follows_user = user
                most_follows = follows_count
            
            total_follows += follows_count
            total_users += 1
            
            if follows_count == 0:
                follows_no_one_count += 1
        
        average_follows = total_follows / total_users
        
        yield ('id with most follows', most_follows_user)
        yield ('most follows of any id', most_follows)
        yield ('average follows of all ids', average_follows)
        yield ('count of ids that follows no-one', follows_no_one_count)       
        
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer),
            MRStep(reducer=self.statistics_reducer)
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