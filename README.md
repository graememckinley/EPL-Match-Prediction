# EPL-Match-Prediction

This project uses `requests`, `BeautifulSoup`, and `pandas` to web scrape English Premier League games from [FBREF](https://fbref.com/en/comps/9/Premier-League-Stats)
This data is then used to train a machine learning model from `scikit-learn` to predict future outcomes of matches.

## Overview

### `MatchScraping.py`

This script pulls all the game data found on FBREF from the start of the 2017-2018 season to games from the 2022-2023 season prior to 26-01-2023.
All this data is written to the included `matches.csv` file.
To pull match data before the 2017-2018 season, or to pull less data, adjust the `years` list to the desired time frame and rerun `MatchScraping.py`.
Please note that rerunning will also add any matches played after 26-01-2023

### `MatchPrediction.py`

This script uses a `RandomForestClassifier` to make match outcome predictions.
The model is trained using games prior to 01-01-2023 and is then tested on games between this date (inclusive) and 26-01-2023.
Parameters for the model can be changed easily and more predictors can be added.
What games are used for training/testing can be changed as well by modifying the dates in the `make_predictions()` function.
The model makes a binary prediction where a win is 1 and a draw or a loss is 0.
Since football has so many draws, grouping losses and draws is perhaps not the best way to make predictions, but this can be improved upon in the future.

## Python

This project used Python 3.11 as well as:

* requests
* pandas
* BeautifulSoup
* scikit-learn
* time

The following were also imported due to errors when web scraping:

* html5lib
* lxml
