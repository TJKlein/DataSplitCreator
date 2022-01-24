import argparse
import random
import os
import numpy as np
from tqdm import tqdm
from urllib.parse import urlparse
import requests
import time

parser = argparse.ArgumentParser()


parser.add_argument('--input_file', required=True, type=str, help='Filename or http address of text file from which split is to be generated.')
parser.add_argument('--seed', type=int, default=48, help='Random seed to produce reproducible split.')
parser.add_argument('--split_percentage', required=True, type=int, help='Percentage of samples to be in target split.')
parser.add_argument('--output_file', type=str, help='Name of split file  to be generated. If unspecified, postfix corresponding to split percentage will be attached to input filename.')
parser.add_argument('--cache_dir', type=str, default='./cache', help='Cache directory for files downloaded from internet')
parser.add_argument('--ignore_cache', help='Set if cached files should be ignored.',  action='store_true')


def main():

    FLAGS = parser.parse_args()
    
    
    if FLAGS.input_file.lower().find("http") == -1:
        if not os.path.isfile(FLAGS.input_file):
            assert os.path.isfile(FLAGS.input_file), "Source file does not exists."
    else:
        # check if cache path exists, if not create it
        if not os.path.exists(FLAGS.cache_dir):
            os.mkdir(FLAGS.cache_dir)
        
        # extrace filename from URL
        URL_filename = os.path.basename(urlparse(FLAGS.input_file).path)
            
        if FLAGS.ignore_cache == True or (FLAGS.ignore_cache == False and not os.path.isfile(os.path.join(FLAGS.cache_dir,URL_filename))):
        
        

            # download file
            response = requests.get(FLAGS.input_file, stream=True)
            with tqdm.wrapattr(open(os.path.join(FLAGS.cache_dir,URL_filename), "wb"), "write",
                               miniters=1, desc=FLAGS.input_file.split('/')[-1],
                               total=int(response.headers.get('content-length', 0))) as fout:
                for chunk in response.iter_content(chunk_size=4096):
                    fout.write(chunk)
        else:
            print("Use cached file: "+os.path.join(FLAGS.cache_dir,URL_filename))
                
        # change input filename to local file
        FLAGS.input_file = os.path.join(FLAGS.cache_dir,URL_filename)
    
    # check if output filename is specified. if not 
    if FLAGS.output_file == None:
        _, filename = os.path.split(FLAGS.input_file)
        extension = os.path.splitext(FLAGS.input_file)[1]
        # remove path from input filename (cached0
        _,FLAGS.output_file = os.path.split(FLAGS.input_file.replace(extension, "_"+f'{int(FLAGS.split_percentage):03}'+"percent"+extension))
    
    # check if target path exists, if not create it
    if not os.path.exists(os.path.dirname(os.path.abspath(FLAGS.output_file))):
        os.mkdir(os.path.dirname(os.path.abspath(FLAGS.output_file)))
    
    # read data from file
    input_lines = open(FLAGS.input_file, 'r').readlines()
    
    # make split generation reproducible with fixed seed
    random.seed(FLAGS.seed)
    idx = random.sample(range(len(input_lines)), int(np.ceil(len(input_lines)/100*FLAGS.split_percentage)))
    
    
    avg = 0
    with open(FLAGS.output_file, 'w') as f:
        for i in idx:
            f.write(input_lines[i])
            avg += len(input_lines[i])
    avg /= len(idx)
    print("Number of sentences: "+str(len(idx))+" | Average length: "+str(avg)+" | Written to file: "+FLAGS.output_file)
    
    
    # sanity check
    output_lines = open(FLAGS.output_file, 'r').readlines()
    if not(len(output_lines) == int(np.ceil(len(input_lines)/100*FLAGS.split_percentage))):
        print("Split creation failed - mismatch in line numbers")

if __name__ == "__main__":
    main()