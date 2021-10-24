class Statistics:
    def __init__(self) -> None:
        self.data: dict[str, list[float]] = {}


    def log(self, key: str, value: float):
        if not key in self.data:
            self.data[key] = []
        
        self.data[key].append(value)

    
    def log_dict(self, dictionary: dict[str, float]):
        for k, v in dictionary.items():
            self.log(k, v)


    def sample_last(self, key: str, lookback: int = 10):
        lookback = min(lookback, len(self.data[key]))
        return self.data[key][-lookback:]


    def rolling_avg(self, key: str, lookback: int = 10):
        sample = self.sample_last(key, lookback)
        return sum(sample) / len(sample)


    def trend(self, key: str, lookback: int = 10) -> float:
        sample = self.sample_last(key, lookback)
        sample_count = len(sample)

        if sample_count == 1: return 0

        trend = [(sample[i + 1] - sample[i]) / sample[i] for i in range(sample_count - 1)]

        return sum(trend) / len(trend)


    def plot(self, keys: list[str] = None, title: str = "stats"):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if keys == None:
            keys = list(self.data.keys())
        

        fig = make_subplots()
        fig.update_layout(title_text = title, template = "plotly_dark")

        for key in keys:
            fig.add_trace(go.Scatter(y = self.data[key], name = key))

        fig.update_xaxes(title_text="iteration")
        #fig.update_yaxes(title_text="average score")

        fig.show()
    
