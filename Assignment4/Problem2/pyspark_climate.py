import time
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import IntegerType
import pandas as pd
import sys

nineteeenth_lower_lim = jdn(dt.strptime('1910-01-01', '%Y-%m-%d'))
nineteenth_upper_lim = jdn(dt.strptime('1919-12-31', '%Y-%m-%d'))
twentieth_lower_lim = jdn(dt.strptime('2010-01-01', '%Y-%m-%d'))
twentieth_upper_lim = jdn(dt.strptime('2019-12-31', '%Y-%m-%d'))

@udf(returnType=IntegerType())
def jdn(dt):
    """
    Computes the Julian date number for a given date.
    Parameters:
    - dt, datetime : the Gregorian date for which to compute the number

    Return value: an integer denoting the number of days since January 1, 
    4714 BC in the proleptic Julian calendar.
    """
    y = dt.year
    m = dt.month
    d = dt.day
    if m < 3:
        y -= 1
        m += 12
    a = y//100
    b = a//4
    c = 2-a+b
    e = int(365.25*(y+4716))
    f = int(30.6001*(m+1))
    jd = c+d+e+f-1524
    return jd

    
# you probably want to use a function with this signature for computing the
# simple linear regression with least squares using applyInPandas()
# key is the group key, df is a Pandas dataframe
# should return a Pandas dataframe
def lsq(key,df):
    beta = 0.0
    
    y_avg = df['TAVG'].mean()
    x_avg = df['JDN'].mean()
    
    nominator = ((df['JDN'] - x_avg) * (df['TAVG'] - y_avg)).sum()
    denominator = ((df['JDN'] - x_avg)**2).sum()
    if denominator != 0:
        beta = nominator / denominator

    return pd.DataFrame({'STATION': [key[0]], 'NAME': [key[1]], 'BETA': [beta]})

def century_diff(key, df):
    nineteenth_avg = df.filter((col('JDN') >= nineteeenth_lower_lim) & (col('JDN') <= nineteenth_upper_lim)) \
        .select('TAVG').agg({'TAVG': 'mean'}).collect()[0][0]
    twentieth_avg = df.filter((col('JDN') >= twentieth_lower_lim) & (col('JDN') <= twentieth_upper_lim)) \
        .select('TAVG').agg({'TAVG': 'mean'}).collect()[0][0]
    tavg_diff = twentieth_avg - nineteenth_avg
    return pd.DataFrame({'STATION': [key[0]], 'NAME': [key[1]], 'TAVGDIFF': [tavg_diff]})

@udf(returnType=FloatType())
def temp_avg(tmin, tmax):
    return (tmin + tmax) / 2

if __name__ == '__main__':
    # do not change the interface
    parser = argparse.ArgumentParser(description = \
                                    'Compute climate data.')
    parser.add_argument('-w','--num-workers',default=1,type=int,
                            help = 'Number of workers')
    parser.add_argument('filename',type=str,help='Input filename')
    args = parser.parse_args()

    # this bit is important: by default, Spark only allocates 1 GiB of memory 
    # which will likely cause an out of memory exception with the full data
    spark = SparkSession.builder \
            .master(f'local[{args.num_workers}]') \
            .config("spark.driver.memory", "16g") \
            .getOrCreate()
    
    # example data row, the actual data will have many more rows and may have different values
    #STATION,DATE,LATITUDE,LONGITUDE,ELEVATION,NAME,PRCP,TMAX,TMIN
    #ASN00009514,1965-01-01,-33.3,115.6,4.0,"BUNBURY POST OFFICE, AS",0.0,95.4,67.3
    
    # read the CSV file into a pyspark.sql dataframe and compute the things you need
    df = spark.read.csv(args.filename, header=True, inferSchema=True)
    
    timedf = df.withColumn('JDN', jdn(col('DATE')))
    

    temp_avg = timedf.withColumn('TAVG', temp_avg(col('TMIN'), col('TMAX'))) \
        .cache() 
    
    
    lin = temp_avg.select('STATION', 'NAME', 'JDN', 'TAVG').groupBy('STATION', 'NAME') \
        .applyInPandas(lsq, schema='STATION string, NAME string, BETA float') \
        .cache()
        
    lin.orderBy('BETA', ascending=False).limit(5).show()
    
    five_num_summary = lin.approxQuantile('BETA', [0.0, 0.25, 0.5, 0.75, 1.0], 0.01)
    for i, q in enumerate(['beta_min', 'beta_q1', 'beta_median', 'beta_q3', 'beta_max']):
        print(f'{q} {five_num_summary[i]} °F/d')
        
    pos_fraction = lin.filter(col('BETA') > 0).count() / lin.count()
    print(f'Fraction of positive coefficients: {pos_fraction}')
    

    # only select stations that have entries in both decades, otherwise the difference will be meaningless
    century_diff_df = temp_avg.select('STATION', 'NAME', 'JDN', 'TAVG').groupBy('STATION', 'NAME') \
        .applyInPandas(century_diff, schema='STATION string, NAME string, TAVGDIFF float') \
        .cache()      
    
    
    
    
    raise NotImplementedError

    # top 5 slopes are printed here
    # replace None with your dataframe, list, or an appropriate expression
    # replace STATIONCODE, STATIONNAME, and BETA with appropriate expressions
    print('Top 5 coefficients:')
    for row in None:
        print(f'{STATIONCODE} at {STATIONNAME} BETA={BETA:0.3e} °F/d')

    # replace None with an appropriate expression
    print('Fraction of positive coefficients:')
    print(None)

    # Five-number summary of slopes, replace with appropriate expressions
    print('Five-number summary of BETA values:')
    beta_min, beta_q1, beta_median, beta_q3, beta_max = 5*[0.0]
    print(f'beta_min {beta_min:0.3e}')
    print(f'beta_q1 {beta_q1:0.3e}')
    print(f'beta_median {beta_median:0.3e}')
    print(f'beta_q3 {beta_q3:0.3e}')
    print(f'beta_max {beta_max:0.3e}')

    # Here you will need to implement computing the decadewise differences 
    # between the average temperatures of 1910s and 2010s

    # There should probably be an if statement to check if any such values were 
    # computed (no suitable stations in the tiny dataset!)

    # Note that values should be printed in celsius

    # Replace None with an appropriate expression
    # Replace STATION, STATIONNAME, and TAVGDIFF with appropriate expressions

    print('Top 5 differences:')
    for row in None:
        print(f'{STATION} at {STATIONNAME} difference {TAVGDIFF:0.1f} °C)')

    # replace None with an appropriate expression
    print('Fraction of positive differences:')
    print(None)

    # Five-number summary of temperature differences, replace with appropriate expressions
    print('Five-number summary of decade average difference values:')
    tdiff_min, tdiff_q1, tdiff_median, tdiff_q3, tdiff_max = 5*[0.0]
    print(f'tdiff_min {tdiff_min:0.1f} °C')
    print(f'tdiff_q1 {tdiff_q1:0.1f} °C')
    print(f'tdiff_median {tdiff_median:0.1f} °C')
    print(f'tdiff_q3 {tdiff_q3:0.1f} °C')
    print(f'tdiff_max {tdiff_max:0.1f} °C')

    # Add your time measurements here
    # It may be interesting to also record more fine-grained times (e.g., how 
    # much time was spent computing vs. reading data)
    print(f'num workers: {args.num_workers}')
    print(f'total time: {None:0.1f} s')
