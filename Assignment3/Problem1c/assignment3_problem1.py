#!/usr/bin/env python3

from mrjob.job import MRJob

class MRMineral(MRJob):
    def configure_args(self):
        super(MRMineral, self).configure_args()
    
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
        
        yield (starsystem, sum(RU_values))

if __name__ == '__main__':    
    MRMineral.run()