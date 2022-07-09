import urllib.request
import json
import xmltodict
import csv
import time

verbose = True

def build_search_url(query_term, apikey, mindate, maxdate):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='
    if mindate == None and maxdate == None:
        end_url = '&retmode=json&RetMax=100&api_key=' + apikey
    else:
        end_url = '&retmode=json&RetMax=100&mindate=' + str(mindate) + '&maxdate=' + str(maxdate) + '&api_key=' + apikey
    query_term = query_term.replace(' ', '%')
    url = base_url + query_term + end_url
    return url

def get_search_author(authorname, university, apikey, mindate, maxdate, mode = "last; first"):
    if mode == "first last":
        lf_list = authorname.split(' ')
        if len(lf_list) == 3: # handling for initials
            last_first = lf_list[2] + ', ' + lf_list[0] + ' ' + lf_list [1]
            last = lf_list[2]
        else:
            last_first = lf_list[1] + ', ' + lf_list[0]
            last = lf_list[1]
    if mode == "last; first":
        last_first = authorname.replace('; ',',')

    author_query = last_first + '[author] ' + university + '[AD]'

    url = build_search_url(author_query, apikey, mindate, maxdate)
    if verbose == True:
        print(author_query)
        print(url)
    response = urllib.request.urlopen(url, timeout = 30)
    response_body = response.read()
    response_json = json.loads(response_body)

    count = response_json['esearchresult']['count']
    id_list = response_json['esearchresult']['idlist']
    ret_data = [count, id_list]
    if verbose == True:
        print(ret_data)
    return ret_data

def build_efetch_url(pmid, apikey):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='
    end_url = '&retmode=xml&api_key=' + apikey
    url = base_url + pmid + end_url
    return url

def get_author_papers(pmid_list, apikey):
    pmid = ",".join(pmid_list)
    pmid_list_len = len(pmid_list) # should be 5, but just in case...
    #print(pmid)
    url = build_efetch_url(pmid, apikey)
    response = urllib.request.urlopen(url, timeout = 30)
    response_body = response.read().decode('utf-8')
    #print(response_body)
    response_dict = xmltodict.parse(response_body)
    article_dict = response_dict['PubmedArticleSet']['PubmedArticle']
    articles = []
    if len(pmid_list) > 1:
        for article in article_dict:
            output_article_dict = {}
            try:
                pmid = article['MedlineCitation']['PMID']['#text']
            except:
                pmid = None
            try:
                journal_name = article['MedlineCitation']['Article']['Journal']['Title']
            except:
                journal_name = None
            try:
                publication_year = article['MedlineCitation']['Article']['Journal']\
                                  ['JournalIssue']['PubDate']['Year']
            except:
                publication_year = None
            try:
                article_title = article['MedlineCitation']['Article']['ArticleTitle']['#text']
            except:
                try:
                    article_title = article['MedlineCitation']['Article']['ArticleTitle']
                except:
                    article_title = None
            output_article_dict['pmid'] = pmid
            output_article_dict['journal_name'] = journal_name
            output_article_dict['publication_year'] = publication_year
            output_article_dict['article_title'] = article_title
            articles.append(output_article_dict)
    else: # handles the case where len(pmid_list = 1)
        article = article_dict # in this case
        output_article_dict = {}
        try:
            pmid = article['MedlineCitation']['PMID']['#text']
        except:
            pmid = None
        try:
            journal_name = article['MedlineCitation']['Article']['Journal']['Title']
        except:
            journal_name = None
        try:
            publication_year = article['MedlineCitation']['Article']['Journal']\
                              ['JournalIssue']['PubDate']['Year']
        except:
            publication_year = None
        try:
            article_title = article['MedlineCitation']['Article']['ArticleTitle']['#text']
        except:
            try:
                article_title = article['MedlineCitation']['Article']['ArticleTitle']
            except:
                article_title = None
        output_article_dict['pmid'] = pmid
        output_article_dict['journal_name'] = journal_name
        output_article_dict['publication_year'] = publication_year
        output_article_dict['article_title'] = article_title
        articles.append(output_article_dict)
    return articles

def piquery(pi_name, university, apikey, mindate, maxdate):
    count, id_list = get_search_author(pi_name, university, apikey, mindate, maxdate)
    if count == '0':
        ret = ['0', None]
    else:
        articles = get_author_papers(id_list, apikey)
        ret = [count, articles]
    return ret

def main(input_file, apikey_file, output_file, mindate = None, maxdate = None):
    """
    input_file    the file name of the input_file (see example.csv)
    apikey_file   the file name of the apikey file where the NCBI apikey is stored
    output_file   the file name that you want this program to output data into (see example_output.csv)
    mindate       you can limit the search from mindate - maxdate. Defaults both to None, which means that all articles are included
    maxdate       same as above
    """
    output_data = [['Name','Department','University','count_articles',
                   'publication_year','journal','article_title','pmid']]

    with open(apikey_file, 'r') as f:
        data = f.readlines()
        apikey = data[0].rstrip()

    with open(input_file, 'r', encoding = 'latin-1') as f:
        result = f.readlines()
        for line in result[1:]:
            if line.rstrip() == '':
                continue
            pi_entry = line.rstrip().split(',')
            pi_name = pi_entry[0]
            dept = pi_entry[1]
            university = pi_entry[2]
            if pi_name.rstrip() == '':
                continue

            time.sleep(1)
            count, articles = piquery(pi_name, university, apikey, mindate, maxdate)
            print(pi_name)
            print(count)
            if articles == None:
                data_row = [pi_name, dept ,university, count, None, None, None, None]
                output_data.append(data_row)
                time.sleep(1)
            elif count == "1":
                article = articles[0]
                data_row = [pi_name, dept ,university, count] + [article['publication_year']] \
                + [article['journal_name']] + [article['article_title']] + [article['pmid']]
                output_data.append(data_row)
                time.sleep(1)
            else:
                i = 0
                for article in articles:
                    if i == 0:
                        data_row = [pi_name, dept ,university, count] + [article['publication_year']] \
                        + [article['journal_name']] + [article['article_title']] + [article['pmid']]
                    else: # format so that sucessive entries dont have repeated names
                        data_row = [None, None, None, None] + [article['publication_year']] \
                        + [article['journal_name']] + [article['article_title']] + [article['pmid']]
                    output_data.append(data_row)
                    i += 1
                    time.sleep(1)

    with open(output_file,'w') as f:
        wr = csv.writer(f)
        wr.writerows(output_data)

    return None

# see comments on the main function to see how to use it
main(input_file = 'example.csv', apikey_file = 'apikey.txt', output_file = 'example_output.csv', mindate = '2019', maxdate = '2022')
