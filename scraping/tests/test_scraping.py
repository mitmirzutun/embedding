from scraping.scraper import get_last_url_part, wiki_to_txt

def test_get_last_url_part():
   urls = [
   	'http://www.test.com/TEST1',
    	'http://www.test.com/page/TEST2',
    	'http://www.test.com/page/page/12345',
    	'http://www.test.com/page/page/12345?abc=123'
   ]
   assert get_last_url_part(urls[0]) == "TEST1"
   assert get_last_url_part(urls[1]) == "TEST2"
   assert get_last_url_part(urls[2]) == "12345"
   assert get_last_url_part(urls[3]) == "12345"

def test_wiki_to_txt():
   wiki_to_txt(urllistfile = "scraping/tests/testurl.csv", datadir = "tests")   
   with open("scraping/tests/Nettersheim.txt") as outputfile:
      scraped = outputfile.read()
   assert "50.4919444444446.6277777777778470" in scraped
   	
