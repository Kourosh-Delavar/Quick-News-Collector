import pwinput

def add_api(url: str, token: str, source_path: str) -> None:
    with open(source_path, 'a+') as file:
        file.write(url + " " + token + "\n")

def main() -> None:
    url: str = input("Please insert your API URL : ")
    token: str = pwinput.pwinput(prompt="Please insert your API token : ")
    path: str = "/home/kou/projects/QNC/test.txt"
    add_api(url=url, token=token, source_path=path)
        
if __name__ == '__main__':
    main()