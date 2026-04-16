#!/usr/bin/env python3

import sys
import duckdb

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(f'Usage: {sys.argv[0]} <input_csv>\n')
        sys.exit(1)
    
    input_csv = sys.argv[1]

    with duckdb.connect(database=":memory:") as con:
        con.execute('CREATE VIEW hour AS SELECT * FROM ' + 
                    f'read_csv_auto(\'{input_csv}\', header=True);')
        
        # Fetch number of rows in the dataset
        print(f'Number of rows in the dataset: {con.execute("SELECT COUNT(*) FROM hour;").fetchone()[0]}')
        
        # Fetch average hourly bike count
        print(f'Average hourly bike count: {con.execute("SELECT AVG(cnt) FROM hour;").fetchone()[0]}')
        
        # Fetch top 5 busiest hours from average bike rentals
        print('Top 5 busiest hours based on average bike rentals:')
        for row in con.execute('SELECT hr, AVG(cnt) AS avg_cnt FROM hour GROUP BY hr ORDER BY avg_cnt DESC LIMIT 5;').fetchall():
            print(f'Hour: {row[0]}, Average Count: {row[1]}')
            
        # Fetch average daily count of bike rentals in january 2012
        print(f'Average daily bike rentals in January 2012: {con.execute("SELECT AVG(cnt) FROM hour WHERE yr = 0 AND mnth = 1;").fetchone()[0]}')