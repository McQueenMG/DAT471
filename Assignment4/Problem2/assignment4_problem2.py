import time
from datetime import datetime as dt
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, when, sum as _sum, avg
from pyspark.sql.types import FloatType
from pyspark.sql.types import IntegerType
import pandas as pd
import sys

def jdn_raw(dt):
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
    
    jdn = udf(jdn_raw, returnType=IntegerType())
    # example data row, the actual data will have many more rows and may have different values
    #STATION,DATE,LATITUDE,LONGITUDE,ELEVATION,NAME,PRCP,TMAX,TMIN
    #ASN00009514,1965-01-01,-33.3,115.6,4.0,"BUNBURY POST OFFICE, AS",0.0,95.4,67.3
    
    # read the CSV file into a pyspark.sql dataframe and compute the things you need
    start_time = time.time()
    df = spark.read.csv(args.filename, header=True, inferSchema=True)
    read_time = time.time() - start_time
    
    temp_avg_time_start = time.time()
    timedf = df.withColumn('JDN', jdn(col('DATE')))
    temp_avg = timedf.withColumn('TAVG', temp_avg(col('TMIN'), col('TMAX'))) \
        .withColumn('TAVG_C', (col('TAVG') - 32.0) * 5.0/9.0) \
        .cache() 
    temp_avg_time = time.time() - temp_avg_time_start
    
    reg_time_start = time.time()
    lin = temp_avg.select('STATION', 'NAME', 'JDN', 'TAVG').groupBy('STATION', 'NAME') \
        .applyInPandas(lsq, schema='STATION string, NAME string, BETA float') \
        .cache()
    five_num_summary = lin.approxQuantile('BETA', [0.0, 0.25, 0.5, 0.75, 1.0], 0.01)
    reg_time = time.time() - reg_time_start
        
    # top 5 slopes are printed here
    # replace None with your dataframe, list, or an appropriate expression
    # replace STATIONCODE, STATIONNAME, and BETA with appropriate expressions
    print('Top 5 coefficients:')
    for row in lin.orderBy('BETA', ascending=False).limit(5).collect():
        print(f'{row.STATION} at {row.NAME} BETA={row.BETA:0.3e} °F/d')
    
        
    pos_fraction = lin.filter(col('BETA') > 0).count() / lin.count()
    # replace None with an appropriate expression
    print('Fraction of positive coefficients:')
    print(pos_fraction)
         
    # Five-number summary of slopes, replace with appropriate expressions
    print('Five-number summary of BETA values:')
    beta_min, beta_q1, beta_median, beta_q3, beta_max = five_num_summary
    print(f'beta_min {beta_min:0.3e}')
    print(f'beta_q1 {beta_q1:0.3e}')
    print(f'beta_median {beta_median:0.3e}')
    print(f'beta_q3 {beta_q3:0.3e}')
    print(f'beta_max {beta_max:0.3e}')
    
    nineteenth_lower = jdn_raw(dt.strptime('1910-01-01', '%Y-%m-%d'))
    nineteenth_upper = jdn_raw(dt.strptime('1919-12-31', '%Y-%m-%d'))
    twentieth_lower = jdn_raw(dt.strptime('2010-01-01', '%Y-%m-%d'))
    twentieth_upper = jdn_raw(dt.strptime('2019-12-31', '%Y-%m-%d'))
    century_diff_time_start = time.time()
    decade_avgs = temp_avg.groupBy('STATION','NAME').agg(
        avg(when((col('JDN')>=nineteenth_lower)&(col('JDN')<=nineteenth_upper), col('TAVG_C'))).alias('avg_1910s'),
        avg(when((col('JDN')>=twentieth_lower)&(col('JDN')<=twentieth_upper), col('TAVG_C'))).alias('avg_2010s'),
    )
    
    only_relevant = decade_avgs.filter(col('avg_1910s').isNotNull() & col('avg_2010s').isNotNull())
    century_diff_df = only_relevant.withColumn('TAVGDIFF', col('avg_2010s') - col('avg_1910s')).cache()
    no_suitable_stations = century_diff_df.count() == 0
    cen_pos_fraction = century_diff_df.filter(col('TAVGDIFF') > 0).count() / century_diff_df.count() if not no_suitable_stations else 0
    cen_five_num_summary = century_diff_df.approxQuantile('TAVGDIFF', [0.0, 0.25, 0.5, 0.75, 1.0], 0.01) if not no_suitable_stations else [0.0]*5
    century_diff_time = time.time() - century_diff_time_start


    # Here you will need to implement computing the decadewise differences 
    # between the average temperatures of 1910s and 2010s

    # There should probably be an if statement to check if any such values were 
    # computed (no suitable stations in the tiny dataset!)

    # Note that values should be printed in celsius

    # Replace None with an appropriate expression
    # Replace STATION, STATIONNAME, and TAVGDIFF with appropriate expressions

    print('Top 5 differences:')
    if not no_suitable_stations:
        for row in century_diff_df.orderBy('TAVGDIFF', ascending=False).limit(5).collect():
            print(f'{row.STATION} at {row.NAME} difference {row.TAVGDIFF:0.1f} °C)')
    else:
        print('No suitable stations found in the dataset.')
        

    # replace None with an appropriate expression
    print('Fraction of positive differences:')
    print(cen_pos_fraction)
    

    if not no_suitable_stations:
        # Five-number summary of temperature differences, replace with appropriate expressions
        print('Five-number summary of decade average difference values:')
        tdiff_min, tdiff_q1, tdiff_median, tdiff_q3, tdiff_max = cen_five_num_summary
        print(f'tdiff_min {tdiff_min:0.1f} °C')
        print(f'tdiff_q1 {tdiff_q1:0.1f} °C')
        print(f'tdiff_median {tdiff_median:0.1f} °C')
        print(f'tdiff_q3 {tdiff_q3:0.1f} °C')
        print(f'tdiff_max {tdiff_max:0.1f} °C')
    else:
        print('No suitable stations found in the dataset, cannot compute five-number summary.')
        
    
    total_time = time.time() - start_time
    measured_time = read_time + temp_avg_time + reg_time + century_diff_time
    other = total_time - measured_time
    # Add your time measurements here
    # It may be interesting to also record more fine-grained times (e.g., how 
    # much time was spent computing vs. reading data)
    print(f'num workers: {args.num_workers}')
    print(f'read time: {read_time:0.1f} s')
    print(f'temp avg time: {temp_avg_time:0.1f} s')
    print(f'regression time: {reg_time:0.1f} s')
    print(f'century diff time: {century_diff_time:0.1f} s')
    print(f'other time: {other:0.1f} s')
    print(f'total time: {total_time:0.1f} s')
