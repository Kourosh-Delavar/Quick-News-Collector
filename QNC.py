import requests
from transformers import pipeline 
from fpdf import FPDF


class Collector():
    
    def __init__(self, urls_source_path: str, collection_path: str) -> None:
        self.urls_source_path: str = urls_source_path
        self.collection_path: str = collection_path
            
    def _filewriter(self, response: dict) -> None:
        with open(self.collection_path, 'a+', encoding='utf-8') as file:
            file.write(response[...])
            
    def fetchdata(self) -> None:   
        with open(self.urls_source_path, 'r') as file:    
            for line in file:
                url: str = line.strip()
                response: dict = requests.get(url=url).json()
                self._filewriter(response=response)

class Summarizer(Collector):
    default_prompt: str = """
                    Please summarize the following text in the style of newspaper headlines.
                    preserve details and usefull insights for each point:
                """
            
    def __init__(self, collection_path: str, model: str) -> None: 
        super().__init__(collection_path)
        self.model = model
    
    def _makeprompt(self, ask: str = default_prompt) -> str:
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
        
        