import argparse
import random
import os
from numerize import numerize 
import numpy as np
import datasets as huggingface_datasets
from tqdm import tqdm
from urllib.parse import urlparse
import requests
import time
import nltk

nltk. download("punkt")
parser = argparse.ArgumentParser()


parser.add_argument('--input_file_or_path', required=True, type=str, help='Filename or http address of text file from which split is to be generated.')
parser.add_argument('--seed', type=int, default=48, help='Random seed to produce reproducible split.')
parser.add_argument('--split_percentage', type=float, help='Percentage of samples to be in target split.')
parser.add_argument('--split_samples', type=int, help='Number of samples in target split.')
parser.add_argument('--output_file', type=str, help='Name of split file  to be generated. If unspecified, postfix corresponding to split percentage will be attached to input filename.')
parser.add_argument('--cache_dir', type=str, default='./cache', help='Cache directory for files downloaded from internet')
parser.add_argument('--ignore_cache', help='Set if cached files should be ignored.',  action='store_true')
parser.add_argument('--data_split', choices=['train', 'validation', 'test'], default='train')


def main():

    
    _textfile = False
    _newline = False
    
    FLAGS = parser.parse_args()
    
    assert FLAGS.split_samples or FLAGS.split_percentage, "Percentage of samples of number of smaples has to be specified"
    
    # check if input is a text file
    if FLAGS.input_file_or_path.lower().find("http") == -1 and FLAGS.input_file_or_path.lower().find("txt") != -1:
        if not os.path.isfile(FLAGS.input_file_or_path):
            assert os.path.isfile(FLAGS.input_file_or_path), "Source file does not exists."
    else: # input is either URL or dataset
        # check if cache path exists, if not create it
        if not os.path.exists(FLAGS.cache_dir):
            os.mkdir(FLAGS.cache_dir)
        
        
        # check if we have a text file as input
        if FLAGS.input_file_or_path.lower().find("txt") != -1:
            _textfile = True
            # extract filename from URL
            URL_filename = os.path.basename(urlparse(FLAGS.input_file_or_path).path)

            if FLAGS.ignore_cache == True or (FLAGS.ignore_cache == False and not os.path.isfile(os.path.join(FLAGS.cache_dir,URL_filename))):



                # download file
                response = requests.get(FLAGS.input_file_or_path, stream=True)
                with tqdm.wrapattr(open(os.path.join(FLAGS.cache_dir,URL_filename), "wb"), "write",
                                   miniters=1, desc=FLAGS.input_file_or_path.split('/')[-1],
                                   total=int(response.headers.get('content-length', 0))) as fout:
                    for chunk in response.iter_content(chunk_size=4096):
                        fout.write(chunk)
            else:
                print("Use cached file: "+os.path.join(FLAGS.cache_dir,URL_filename))

            # change input filename to local file
            FLAGS.input_file_or_path = os.path.join(FLAGS.cache_dir,URL_filename)
            
        elif FLAGS.input_file_or_path.lower() == 'wikipedia-en': # alternatively, it must be a dataset
            _textfile = False
            _newline = True
            dataset = huggingface_datasets.load_dataset('wikipedia', '20200501.en', split=FLAGS.data_split, cache_dir=FLAGS.cache_dir)
            print("Processing input ....")
            n_documents = dataset.num_rows
            
            if FLAGS.split_percentage:
                n_sentences =  int(np.ceil(n_documents/100*FLAGS.split_percentage))
            else:
                n_sentences = FLAGS.split_samples
             # make split generation reproducible with fixed seed  
            random.seed(FLAGS.seed)
            idx = random.sample(range(n_documents), n_sentences)
            
            wiki_subset =  dataset.select(idx)
            
            input_lines = []
            for index, val in enumerate(tqdm(range(len(wiki_subset)))):
                document = wiki_subset[index]['text']
                a_list = nltk.tokenize.sent_tokenize(document)

                cleaned_sentences = []
                for x in a_list:
                    cleaned_sentences.append(x.replace("\n", ""))
                # choose one random sentence per document
                random_sentence_idx = random.sample(range(len(cleaned_sentences)), 1)[0]

                input_lines.append(cleaned_sentences[random_sentence_idx])
                
            idx = list(range(n_sentences))
            
            # for correct creation output name
            FLAGS.input_file_or_path =  FLAGS.input_file_or_path + '.txt'
    
    # check if output filename is specified. if not 
    if FLAGS.output_file == None:
        _, filename = os.path.split(FLAGS.input_file_or_path)
        extension = ".txt" #os.path.splitext(FLAGS.input_file_or_path)[1]
        # remove path from input filename (cached0
        if FLAGS.split_percentage:
            _,FLAGS.output_file = os.path.split(FLAGS.input_file_or_path.replace(extension, "_{:06.2F}".format(FLAGS.split_percentage)+"percent"+extension))
        else:
            _,FLAGS.output_file = os.path.split(FLAGS.input_file_or_path.replace(extension, "_"+str(numerize.numerize(FLAGS.split_samples))+"_samples"+extension))
    
    # check if target path exists, if not create it
    if not os.path.exists(os.path.dirname(os.path.abspath(FLAGS.output_file))):
        os.mkdir(os.path.dirname(os.path.abspath(FLAGS.output_file)))
    
    if _textfile:
        # read data from file
        input_lines = open(FLAGS.input_file_or_path, 'r').readlines()

        # make split generation reproducible with fixed seed
        random.seed(FLAGS.seed)
        if FLAGS.split_percentage:
            idx = random.sample(range(len(input_lines)), int(np.ceil(len(input_lines)/100*FLAGS.split_percentage)))
        else:
            idx = random.sample(range(len(input_lines)), FLAGS.split_samples)
    #else: # loading data from dataset
    
    
    avg = 0
    with open(FLAGS.output_file, 'w') as f:
        for i in idx:
            f.write(input_lines[i])
            if _newline:
                f.write('\n')
            avg += len(input_lines[i])
    avg /= len(idx)
    print("Number of sentences: "+str(len(idx))+" | Average length: "+str(avg)+" | Written to file: "+FLAGS.output_file)
    
    
    # sanity check
    output_lines = open(FLAGS.output_file, 'r').readlines()
    if (FLAGS.split_percentage and not(len(output_lines) == int(np.ceil(len(input_lines)/100*FLAGS.split_percentage)))) or (FLAGS.split_samples and not (len(output_lines) == FLAGS.split_samples)):
        print("Split creation failed - mismatch in line numbers")

if __name__ == "__main__":
    main()
