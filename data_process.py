from utils import get_filename, load_json

class DataAnalysis:
    def __init__(self, date=None, file_path=None):
        if not file_path:
            file_path = get_filename('/home/NewTeamWeb/json_log', date)
        self.info = load_json(file_path) if file_path else None

    def __len__(self):
        return len(self.info)

    def __getitem__(self, idx):
        return self.info[idx]

    def __str__(self):
        for d in self.info:
            print(d)
        return '--------------------------'
    

if __name__ == '__main__':
    analyzer = DataAnalysis()
    print(analyzer.data)
    print(analyzer.datetime)
