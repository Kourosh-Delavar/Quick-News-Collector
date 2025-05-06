import requests
from transformers import pipeline 
from fpdf import FPDF


class Collector():
    
    def __init__(self,
                 api_source_path: str,
                 collection_path: str,
                 category: list[str],
                 lang: str = 'en') -> None:
        
        self.api_source_path: str = api_source_path
        self.collection_path: str = collection_path
        self.category: list[str] = category
        self.lang: str = lang
             
    def _filewriter(self, response: str) -> None:
        with open(self.collection_path, 'a+', encoding='utf-8') as file:
            file.write(response)
            
    def _fetch(self, url: str, api_key: str) -> str:
        resp_dict: dict = {}
        text: str = ""
        for category in self.category:
            
            params: dict = {
                'apiKey': api_key,
                'category': self.category,
                'language': self.lang
            }
            
            response = requests.get(url=url, params=params).json()
            if response.status_code == 200:
                print("Response received successfully")
                for article in response['articles']:
                    # NOTE: This takes so much RAM 
                    text = text + article['description'] + "\n" 
            else:
                print(f"Failed to receive response from {url}. Status code : {response.status_code}")    
        
        return text    
            
    def _fetch_currentsapi(self, api_key: str) -> str:        
        url: str = "https://api.currentsapi.services/v1/latest-news"
        currentsapi_output: str = self._fetch(url=url, api_key=api_key)
        
        return currentsapi_output
        
    def _fetch_gnews(self, api_key: str) -> str:
        url: str = "https://gnews.io/api/v4/search"
        gnews_output: str = self._fetch(url=url, api_key=api_key)
        
        return gnews_output
        
    def _fetch_newsapi(self, api_key: str) -> str:
        url: str = "https://gnews.io/api/v4/search"
        newsapi_output: str = self._fetch(url=url, api_key=api_key)
        
        return newsapi_output
    
    # FIXME: This needs to be fixed with its api keys setting 
    def final_output(self) -> str: 
        currentsapi_output: str = self._fetch_currentsapi(api_key=...) 
        gnews_output: str = self._fetch_gnews(api_key=...) 
        newsapi_output: str = self._fetch_newsapi(api_key=...) 
        final_output: str = "\n".join([currentsapi_output,
                                       gnews_output,
                                       newsapi_output])
        
        return final_output
    
class Summarizer(Collector):
            
    def __init__(self, collection_path: str, model: str) -> None: 
        super().__init__(collection_path)
        self.model = model
    
    def _makeprompt(self) -> str:
        ask: str = (
                    "Please summarize the following text in the style of newspaper headlines,"
                    " preserving all the details and usefull insights for each point:"
                )
    
        with open(self.collection_path, 'r') as file:
            text: str = file.read()
            prompt: str = ask + '\n' + text
            return prompt
             
    def summarize(self) -> str:            
        
        messages: list = [
            {"role": "user", 
             "content": self._makeprompt()}
        ]
        
        pipe = pipeline("text-generation", model=self.model)
        output: list = pipe(messages)
        generated_text: str = output[0]['generated_text'] 
        
        return generated_text
    
class ExportResults():
    
    def __init__(self, generated_text) -> None:
        self.generated_text: str = generated_text
        
    def as_txt(self, path: str) -> None:
        with open(path, '+a', encoding='utf-8') as file:
            file.write(self.generated_text)
    
    def as_pdf(self, path: str, font_size: int = 12) -> None:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=font_size)
        pdf.multi_cell(0, 10, self.generated_text)
        pdf.output(dest=path)
    
    def to_telegram(self, token: str, chat_id: str) -> None:
        url: str = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload: dict = {
            'chat_id': chat_id,
            'text': self.generated_text,
            'parse_mode': 'MarkdownV2'
        }
        
        response = requests.post(url=url, json=payload)
        
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message. Status code : {response.status_code}")
        