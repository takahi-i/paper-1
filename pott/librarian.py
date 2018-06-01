# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery
from pott.index import Index
from pott.yaml import Yaml
from pott.utils.html_utils import extract_papers_from
from pott.utils.log import logger


class Librarian:

    __SCHOLAR_URL = "https://scholar.google.com/scholar"

    def __init__(self):
        self.yaml = Yaml()
        self.index = Index()

    def global_search(self, keywords, start, year_low, year_high):
        url = self._set_url(keywords, start, year_low, year_high)
        pq_html = PyQuery(url)
        papers = extract_papers_from(pq_html)
        return papers

    def _set_url(self, keywords, start, year_low, year_high):
        url = self.__SCHOLAR_URL + '?q=' + ' '.join(keywords)
        if start != 0:
            url += '&start=' + str(start)
        if year_low is not None:
            url += '&as_ylo=' + year_low
        if year_high is not None:
            url += '&as_yhi=' + year_high
        return url

    def save(self, papers):
        for paper in papers:
            response = self._download(paper)
            self._save(paper, response)

    def _download(self, paper):
        print('downloading "' + paper.title + '"')
        try:
            response = requests.get(paper.url, timeout=10)
            if response.status_code == 200:
                return response
        except requests.ConnectionError as e:
            logger.warn(str(e))

    def _save(self, paper, response):
        paper.pdf.save(response.content)
        paper.text.save(paper.pdf.extract_text())
        self.index.save(paper)
        self.yaml.update(paper)
        print('saved in the following location:\n' + paper.pdf.file_path)

    def local_search(self, keywords):
        papers = self.index.search(keywords)
        return papers

    def list(self):
        paper_by_id = self.yaml.load()
        return paper_by_id.values()

    def reindex(self):
        paper_by_id = self.yaml.load()
        self.index.reindex(paper_by_id)
