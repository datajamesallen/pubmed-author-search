# pubmed-author-search
Use the NCBI/pubmed API to collect data on publications by author name

takes an input csv file with a list of names, deptartments, and universities and outputs the publications found on pubmed for each person
see example.csv for how this is structured, and example_output.csv to see how it looks after it's run.

apikey.txt
to run this properly, you need to register an apikey with NCBI, and then save the key as as plain text on the first line of a text apikey.txt
here's info on how to get an api key:
https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

You might be able to modify this code to get it work without the api key, but you will be severely limited on the number of requests you can make
I'm already throttling the script with time.sleep(1) to slow it down and limit the requests per second, and i've found this is fine for me.
