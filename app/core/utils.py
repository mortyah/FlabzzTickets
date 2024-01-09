import json

def get_data(f: str):
    with open(f"./app/config/data/{f}.json") as file:
        return json.load(file)
    
def update_data(f: str, data: any):
    with open(f"./app/config/data/{f}.json", "w") as file:
        return json.dump(data, file, indent=4)