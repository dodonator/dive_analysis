import datetime
import csv
from pathlib import Path

class Dive():
    
    def __init__(self, path: Path):
        if isinstance(path, str):
            path = Path(path)
        assert path.exists()
        self.path = path

        with path.open() as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            # get meta data from first two rows
            meta_data = dict(zip(next(reader), next(reader)))
            next(reader)  # ignore blank line
            more_meta = dict(zip(next(reader), next(reader)))
            meta_data.update(more_meta)
        
        self.date, self.time = self._convert_date(meta_data["\ufeffDate"])
        self.duration = self._convert_duration(meta_data["Duration"])
        self.max_depth = float(meta_data["Max depth [m]"])
        self.min_temperature = float(meta_data["Min temp [°C]"])
        self.dive_mode = meta_data["Dive mode"]
        self.deco_dive = meta_data["Deco dive [Y|N]"] == "Y"
        self.deco_stop_violation = meta_data["Deco stop violation [Y|N]"] == "Y"
        self.deco_stop_missed = meta_data["Deco stop missed [Y|N]"] == "Y"


    def load_dive_data(self):
        data = []
        with self.path.open() as file:
            # ignore meta data
            meta = [file.readline() for i in range(6)]
            del meta
            reader = csv.DictReader(file)
            for row in reader:
                row["Dive time [min:s]"] = self._convert_dive_time(row["Dive time [min:s]"])
                row["Depth [m]"] = float(row["Depth [m]"])
                row["Temperature [°C]"] = float(row["Temperature [°C]"])
                data.append(row)
        self.data = data


    def average_depth(self):
        if not hasattr(self, "data"):
            self.load_dive_data()
        
        depth_data = [float(d["Depth [m]"]) for d in self.data]
        average_depth = round(sum(depth_data) / len(depth_data), 2)
        return average_depth


    def __repr__(self):
        return f"""Dive:
    Date: {self.date}
    Time: {self.time}
    Duration: {self.duration}
    Depth: {self.max_depth}
    Temperature: {self.min_temperature}°C
    """


    def __iter__(self):
        for d in self.data:
            yield d


    def __hash__(self):
        return hash(hash(self.date) + hash(self.time))


    def __eq__(self, other):
        assert isinstance(other, Dive)
        return hash(self) == hash(other)


    def _convert_date(self, date_string):
        # date string format: "DD.MM.YYYY hh:mm:ss"
        d, t = date_string.split(" ")
        day, month, year = tuple(map(int, d.split(".")))
        hour, minute, second = tuple(map(int, t.split(":")))
        date = datetime.date(year, month, day)
        time = datetime.time(hour, minute, second)
        return (date, time)

            
    def _convert_duration(self, duration_string):
        # duration string format: hh:mm:ss
        h, m, s = tuple(map(int, duration_string.split(":")))
        duration = datetime.timedelta(hours=h, minutes=m, seconds=s)
        return duration

        
    def _convert_dive_time(self, dive_time_str):
        m, s = tuple(map(int, dive_time_str.split(":")))
        dive_time = datetime.timedelta(minutes=m, seconds=s)
        return dive_time