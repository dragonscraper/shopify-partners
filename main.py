from bs4 import BeautifulSoup
from pathlib import Path
import requests
import pandas as pd
import os

BASE_DIR  =  Path(__file__).resolve().parent

URLS_FILE = BASE_DIR / "urls.txt"
OUPTUT_FILE = BASE_DIR / "data.csv"

class Scraper:
    
    def __init__(self) -> None:
        self.session =  requests.Session()
        self.base_url = "https://www.shopify.com"
        self.page_url = "https://www.shopify.com/partners/directory/services/marketing-and-sales/conversion-rate-optimization"
        self.headers  = {
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                         "Accept-Language":"en-US,en;q=0.5",
                         "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
                         }
    
    def store_urls(self , url : str):
        with open(URLS_FILE,"a") as f:
            f.write(url + "\n") 
    
    def load_urls(self):
        with open(URLS_FILE , "r") as f:
            return [line.strip() for line in f.readlines()]       
    
    def to_csv(self,data : dict):
        df =pd.json_normalize(data)
        df.to_csv(OUPTUT_FILE,mode="a",header=not os.path.exists(OUPTUT_FILE),index=False)
    
    def fetch_page(self, page  : int):
        resposne =  self.session.get(self.page_url,params={'page':page})
        return BeautifulSoup(resposne.content , "html.parser") if resposne.status_code == 200  else print(resposne.status_code , " " , page)
    
    def fetch_url(self, url : str,**kwargs):
        response  =  self.session.get(url , **kwargs)
        return BeautifulSoup(response.content,"html.parser") if response.status_code  == 200  else print(response.status_code , " " , url) 
        
    
    def page_partners(self, soup : BeautifulSoup) -> list:
        objs =  soup.select("div.mb-4.bg-white.transition-colors.overflow-hidden.rounded-b-lg.rounded-t-lg.border.border-zinc-200")
        for obj in objs:
            url =  obj.select_one("a.w-full.pt-4.pr-6.pb-4.pl-4.bg-transparent.grid")['href']
            self.store_urls(self.base_url + url)  
    
    def contacts(self,soup : BeautifulSoup):
        contacts_info = soup.select("div.flex.flex-col.gap-y-3 div.flex.flex-wrap.gap-x-2.items-center")
        contacts_data = {}

        for contact in contacts_info:
            url =  contact.select_one("a").get('href',"")
            if "http" in url:
                contacts_data['website'] =  url
            elif "tel:" in url:
                contacts_data['tel'] =  url.replace('tel:',"")
            elif "mailto:" in url:
                contacts_data['email'] =  url.replace('mailto:',"")
            else:
                continue
        
        return contacts_data
    
    def extra(self, soup : BeautifulSoup):
        data_extra  =  soup.select("div.flex.flex-col.gap-y-5.relative div.flex.flex-col.gap-y-1")
        output  = {}
        
        for data in data_extra:
            p =  data.select_one("p.richtext.text-t7").get_text(strip=True)
            if p == "Social links":
                output['linkedin'] = data.select_one("a").get("href")
            
            elif p == "Primary location":
                output['location'] = data.select_one("p.richtext:not(.text-t7)").get_text(strip=True)
                
            elif p == "Languages":
                output['Languages'] = data.select_one("p.richtext:not(.text-t7)").get_text(strip=True)
            else:
                continue
        
        return output
                

    def page_detials(self, soup : BeautifulSoup ) -> dict :
        name  = soup.select_one("div.grid.gap-y-3 h1.richtext.text-t4")
        desc = soup.select_one("pre.text-body-base.font-sans.whitespace-pre-wrap.opacity-70.pb-4")
        contact_data  =  self.contacts(soup)
        extra =  self.extra(soup)
        return {'name' :  name.get_text(strip=True) if name else "NO DATA",
               'description' :  desc.get_text(strip=True)  if desc else "NO DATA",
               'tel' :   contact_data.get("tel","NO DATA"),
               'website' : contact_data.get("website","NO DATA"),
               'email' :  contact_data.get("email","NO DATA") ,
               "linkedin":extra.get("linkedin","NO DATA"),
               "location":extra.get("location","NO DATA"),
               "Languages":extra.get("Languages","NO DATA"),
        }
            
        
    def url_extractor(self):
        for i in range(1,76):
            print(f'checking page {i}')
            soup  =  self.fetch_page(i)
            self.page_partners(soup)
        
    
    def url_handler(self,):
        urls  =  self.load_urls()
        for url  in urls:
            print(f"checking {url}")
            soup =  self.fetch_url(url)
            data  = self.page_detials(soup)
            data['url'] =  url
            self.to_csv(data)
            
    def main(self,):
        print("Starting extracting urls.")
        urls =  self.url_extractor()
        print("Done extracted urls.")
        
        print("start url handling ")
        self.url_handler()
        
        
        
if __name__ == "__main__":
    Scraper().main()
            
            
        