"""Keeping track of numerical data over time"""

class Statistics:
    """Statistics class for keeping track of sequences of numerical data by keys."""
    def __init__(self) -> None:
        """Initializes the class."""        
        self.data: dict[str, list[float]] = {}


    def log(self, key: str, value: float) -> None:
        """Stores a numerical value in a series specified by a key.

        Args:
            key (str): Key specifying the type of data.
            value (float): Data to store.
        """
        if not key in self.data:
            self.data[key] = []
        
        self.data[key].append(value)

    
    def log_dict(self, dictionary: dict[str, float]) -> None:
        """Stores the numerical values of a dictionary in a series specified by the corresponding key. 

        Args:
            dictionary (dict[str, float]): Dictionary containing the data.
        """        
        for k, v in dictionary.items():
            self.log(k, v)


    def sample_last(self, key: str, lookback: int = 10) -> list[float]:
        """Returns the last few samples in a series.

        Args:
            key (str): Name of the series.
            lookback (int, optional): Maximum number of samples to include. Defaults to 10.

        Returns:
            list[float]: The retrieved subset.
        """        
        lookback = min(lookback, len(self.data[key]))
        return self.data[key][-lookback:]


    def rolling_avg(self, key: str, lookback: int = 10) -> float:
        """Calculates average of the last few samples in a series.

        Args:
            key (str): Name of the series.
            lookback (int, optional): Maximum number of samples to include. Defaults to 10.

        Returns:
            float: Calculated average.
        """        
        samples = self.sample_last(key, lookback)
        return sum(samples) / len(samples)


    def trend(self, key: str, lookback: int = 10) -> float:
        """Calculates average normalized difference between a sample and the next for the last few samples in a series.

        Args:
            key (str): Name of the series.
            lookback (int, optional): Maximum number of samples to include. Defaults to 10.

        Returns:
            float: Calculated trend.
        """        
        samples = self.sample_last(key, lookback)
        sample_count = len(samples)

        if sample_count == 1: return 0

        trend = [(samples[i + 1] - samples[i]) / samples[i] for i in range(sample_count - 1)]

        return sum(trend) / len(trend)


    def plot(self, keys: list[str] = None, title: str = "stats") -> None:
        """Plots the stored data using ploty. Browser tab containing graph will open.

        Args:
            keys (list[str], optional): List describing series to include. Defaults to None.
            title (str, optional): Title to show in the graph. Defaults to "stats".
        """
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if keys == None:
            keys = list(self.data.keys())
        

        fig = make_subplots()
        fig.update_layout(title_text = title, template = "plotly_dark")

        for key in keys:
            fig.add_trace(go.Scatter(y = self.data[key], name = key))

        fig.update_xaxes(title_text="iteration")

        fig.show()
    
