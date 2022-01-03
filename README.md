# gatech_fintechlab


# How to Run

- Clone repo
- [Install](https://docs.conda.io/en/latest/miniconda.html) Conda
- Run miniconda script
```
bash Miniconda3-latest-MacOSX-x86_64.sh
```
- Refresh the terminal and use ```conda``` to test installation.

# Setting up Environment

- Create a conda environment with:
```
conda create -n gatech_fintechlab python=3.9
```
- Activate conda and install all dependencies including poetry:
```
   conda activate fb-env
   pip install poetry
   poetry install
```

# Running the Code

- While in the environment run the script with:
```
python download.py
```

# What to Expect

The script will begin and output statetments corresponding to which set of files is being downloaded.  
The script automatically starts at the year 1995 Quarter 1 and ends at year 2021 Quarter 4.  
The 8-K files will be stored in a csv file called filings in a folder called "files" in the current directory.  
