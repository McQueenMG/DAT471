import os
import argparse
import sys
import time
import multiprocessing as mp

global_counts = {}

def get_filenames(path):
    """
    A generator function: Iterates through all .txt files in the path and
    returns the full names of the files

    Parameters:
    - path : string, path to walk through

    Yields:
    The full filenames of all files ending in .txt
    """
    for (root, dirs, files) in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                yield f'{root}/{file}'

def get_file(path):
    """
    Reads the content of the file and returns it as a string.

    Parameters:
    - path : string, path to a file

    Return value:
    The content of the file in a string.
    """
    with open(path,'r') as f:
        return f.read()

def count_words_in_file(filename_queue,wordcount_queue,batch_size):
    """
    Counts the number of occurrences of words in the file
    Performs counting until a None is encountered in the queue
    Counts are stored in wordcount_queue
    Whitespace is ignored

    Parameters:
    - filename_queue, multiprocessing queue :  will contain filenames and None as a sentinel to indicate end of input
    - wordcount_queue, multiprocessing queue : (word,count) dictionaries are put in the queue, and end of input is indicated with a None
    - batch_size, int : size of batches to process

    Returns: None
    """
    
    batch = []
    while (filename := filename_queue.get()) is not None:
        counts = dict()
        for word in get_file(filename).split():
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        batch.append(counts)
        if len(batch) >= batch_size:
            for counts in batch:
                wordcount_queue.put(counts)
            batch = []
    
    for counts in batch:
        wordcount_queue.put(counts)
    wordcount_queue.put(None)
    return None



def get_top10(counts):
    """
    Determines the 10 words with the most occurrences.
    Ties can be solved arbitrarily.

    Parameters:
    - counts, dictionary : a mapping from words (str) to counts (int)
    
    Return value:
    A list of (count,word) pairs (int,str)
    """
    top10 = sorted(
        [(v,k) for (k,v) in counts.items()],
        reverse=True)[:10] 
    return top10



def merge_counts(output_queue,wordcount_queue,num_workers):
    """
    Merges the counts from the queue into the shared dict global_counts. 
    Quits when num_workers Nones have been encountered.

    Parameters:
    - output_queue, multiprocessing queue : the checksum and top 10 will be put in this queue when the merging is done
    - wordcount_queue, manager queue : queue that contains (word,count) pairs and Nones to signal end of input from a worker
    - num_workers, int : number of workers (i.e., how many Nones to expect)

    Return value: None
    """
    none_count = 0
    while none_count < num_workers:
        if (counts := wordcount_queue.get()) is None:
            none_count += 1
        else:
            for (k,v) in counts.items():
                if k not in global_counts:
                    global_counts[k] = v
                else:
                    global_counts[k] += v
                    
    output_queue.put(compute_checksum(global_counts))
    output_queue.put(get_top10(global_counts))
    return None



def compute_checksum(counts):
    """
    Computes the checksum for the counts as follows:
    The checksum is the sum of products of the length of the word and its count

    Parameters:
    - counts, dictionary : word to count dictionary

    Return value:
    The checksum (int)
    """
    checksum = 0
    for (k,v) in counts.items():
        checksum += len(k) * v
    
    return checksum


if __name__ == '__main__':
    total_start_time = time.time()
    parser = argparse.ArgumentParser(description='Counts words of all the text files in the given directory')
    parser.add_argument('-w', '--num-workers', help = 'Number of workers', default=1, type=int)
    parser.add_argument('-b', '--batch-size', help = 'Batch size', default=1, type=int)
    parser.add_argument('path', help = 'Path that contains text files')
    args = parser.parse_args()

    path = args.path

    if not os.path.isdir(path):
        sys.stderr.write(f'{sys.argv[0]}: ERROR: `{path}\' is not a valid directory!\n')
        quit(1)

    num_workers = args.num_workers
    if num_workers < 1:
        sys.stderr.write(f'{sys.argv[0]}: ERROR: Number of workers must be positive (got {num_workers})!\n')
        quit(1)

    batch_size = args.batch_size
    if batch_size < 1:
        sys.stderr.write(f'{sys.argv[0]}: ERROR: Batch size must be positive (got {batch_size})!\n')
        quit(1)
    print(f'Parser arguments: num_workers={num_workers}, batch_size={batch_size}, path={path}')

    # construct workers and queues
    filename_queue = mp.Queue()
    wordcount_queue = mp.Queue()
    output_queue = mp.Queue()
    
    workers = [mp.Process(target=count_words_in_file, args=(filename_queue,wordcount_queue,batch_size)) for _ in range(num_workers)]
    print(f'Constructed {len(workers)} workers.')
    for w in workers:
        w.start()
    
    # construct a special merger process
    merger_process = mp.Process(target=merge_counts, args=(output_queue,wordcount_queue,num_workers))
    print(f'Constructed {merger_process is not None} merger process.')
    merger_process.start()

        
    # put filenames into the input queue
    worker_time = time.time() - total_start_time
    for filename in get_filenames(path):
        filename_queue.put(filename)
    print(f'Finished putting filenames in the queue in {time.time() - worker_time:.2f} seconds.')
    
    for _ in range(num_workers):
        filename_queue.put(None) 
    print(f'Finished putting sentinels in the queue in {time.time() - worker_time:.2f} seconds.')
    print(f'Worker execution time: {time.time() - worker_time}')
    
    for w in workers:
        w.join()
    # workers then put dictionaries for the merger
    # the merger shall return the checksum and top 10 through the out queue
    
    checksum = output_queue.get()
    print(f'Checksum: {checksum}')
    top10 = output_queue.get()
    print('Top 10 words:')
    for (count, word) in top10:
        print(f'{word}: {count}')
    
    merger_process.join()
    print(f'Total execution time: {time.time() - total_start_time}')