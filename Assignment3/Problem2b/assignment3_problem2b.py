#!/usr/bin/env python3

from mrjob.job import MRJob
from mrjob.step import MRStep

class MRMineral(MRJob):
    def configure_args(self):
        super(MRMineral, self).configure_args()
        self.add_passthru_arg('-k', '--topk', type=int, default=10, help='Number of top results to return')
    
    def mapper(self, _, planet):
        """
        Determens the name of the star system the planet belongs to as well as
        the RU mineral value for it

        Parameters:
        - planet, a row in the planets.csv dataset
        
        Return value:
        key value pair of (starsystem, RUvalue)
        """
        
        
        if planet.startswith("Constellation,"):
            return
        
        starsystem = ""
        planet_data = planet.split(',')
        RU_value = int(planet_data[5])
        if planet_data[1] != 'Prime':
            starsystem = planet_data[1] + " " + planet_data[0]
        else:
            starsystem = planet_data[0]

        yield (starsystem, RU_value)


    def combiner(self, starsystem, RU_values):
        """
        Combines the RU values of duplicate starsystems within one node

        Parameters:
        - starsystem, starsystem calculated by the mapper within a node
        - RU_values, the RU values for that starsystem calculated by the mapper within a node
        
        Return value:
        Dictionairy: (starsystem, R_value)
        """
        
        yield (starsystem, sum(RU_values))
        
    def reducer(self, starsystem, RU_values):
        """
        Combines the RU values of duplicate starsystems accross nodes

        Parameters:
        - starsystem, starsystem calculated by the combiner within a node
        - RU_values, the RU values for that starsystem calculated by the combiner within a node
        
        Return value:
        Dictionairy: (starsystem, RU_value)
        """
        yield (None, (starsystem, sum(RU_values)))
        
    def reducer_topk(self, _, starsystem_RU):
        """
        Reducer that takes the output of the first reducer and returns the top k starsystems with the highest RU values

        Parameters:
        - starsystem_RU, a list of (starsystem, RU_value) pairs calculated by the first reducer
        
        Return value:
        Dictionairy: (starsystem, RU_value) for the top k starsystems with the highest RU values
        """
        
        topk = self.options.topk
        sorted_starsystems = sorted(starsystem_RU, key=lambda x: x[1], reverse=True)
        for starsystem, RU_value in sorted_starsystems[:topk]:
            yield (starsystem, RU_value)
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper, combiner=self.combiner, reducer=self.reducer),
            MRStep(reducer=self.reducer_topk)
        ]

if __name__ == '__main__':    
    MRMineral.run()