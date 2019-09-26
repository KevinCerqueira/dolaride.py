import requests
from bs4 import BeautifulSoup

class ScrapDoll:
    
    def reqUrl(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        return soup

    def getValDol(self):
        return self.reqValorDolar()

    def reqValorDolar(self):
        url = 'https://br.advfn.com/cambio'
        soup = self.reqUrl(url)
        page = soup.find_all('input', ({'id' : 'to_val'}))
        rawhtml = str(page)
        return self.htmlToFloat(rawhtml)
        
    def htmlToFloat(self, rawHtml):
        strVal = ''
        for per in range(len(rawHtml)):
            if(rawHtml[per] == '.'):
                strVal = rawHtml[per-1] + '.' + rawHtml[per+1] + rawHtml[per+2]# + rawHtml[per+3] + rawHtml[per+4]
                break
        return float(strVal)