# Text file data split creator
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](#python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tool that creates random data splits from text files, where data is organized on a line-by-line basis. Splits are to be defined in percentages of lines. Input data can either be a local text file or a URL to a text file. If an URL is provided the data will be downloaded (if the file is not found in the cache directory). Optionally, the user can specify to ignore cached files. For reproducibility reasons a random seed is set prior to drawing the random numbers to select the lines from the file.



## Download and Installation

1. Install the requiremennts:

```
conda install --yes --file requirements.txt
```

or

```
pip install -r requirements.txt
```

2. Basic usage:

a) Creation of a 1% data split of the Wiki1m dataset
```
python create_split.py --input_file https://huggingface.co/datasets/princeton-nlp/datasets-for-simcse/resolve/main/wiki1m_for_simcse.txt --split_percentage 1
```

Output will be the file called: 

```
wiki1m_for_simcse_001.00percent.txt
```

b) Creation of a 1000 samples data split from Wikipedia (English):

```
python create_split.py --input_file_or_path wikipedia-en --split_samples 1000
```

Output will be the file called: 

```
wikipedia-en_1K_samples.txt
```

3. If you want to ignore cache, simply specify using the FLAG --ignore_cache:

```
python create_split.py --input_file https://huggingface.co/datasets/princeton-nlp/datasets-for-simcse/resolve/main/wiki1m_for_simcse.txt \ 
--split_percentage 1 \
--ignore_cache
```
