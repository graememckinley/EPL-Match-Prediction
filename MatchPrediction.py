import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score

# Import the matches database
matches = pd.read_csv("matches.csv", index_col=0)

# Fix date and time
matches["date"] = pd.to_datetime(matches["date"])

# Create predictors
matches["venue_code"] = matches["venue"].astype("category").cat.codes  # Venue
matches["opp_code"] = matches["opponent"].astype("category").cat.codes  # Opponent
matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")  # Time
matches["day_code"] = matches["date"].dt.dayofweek  # Day of week

# Create target
matches["target"] = (matches["result"] == "W").astype("int")  # Combines losses and draws

# Initialize random forest classifier
# Higher n_estimators: longer run but potentially more accurate
# Higher min_samples_split: less likely to overfit but lower accuracy on training data
# random_state deal with random parameters, setting at 1 means multiple runs product same output
rf = RandomForestClassifier(n_estimators=100, min_samples_split=8, random_state=1)

# Setup predictors
predictors = ["venue_code", "opp_code", "hour", "day_code"]

# Create a dataframe for every team
grouped_matches = matches.groupby("team")


# Define rolling averages function
def rolling_averages(g, c, n_c):  # g=group, c=cols, n_c=new_cols
    g = g.sort_values("date")
    rolling_stats = g[c].rolling(3, closed='left').mean()  # Ignore the current week
    g[n_c] = rolling_stats
    g = g.dropna(subset=n_c)

    return g


# Compute rolling averages
cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{col}_rolling" for col in cols]

# Apply rolling averages to all teams
matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
matches_rolling = matches_rolling.droplevel('team')

# Reassign values
matches_rolling.index = range(matches_rolling.shape[0])


# Define a function for making predictions
def make_predictions(data, predic):
    # Split up training and test data
    train = data[data["date"] < '2023-01-01']
    test = data[data["date"] >= '2023-01-01']

    # Fit model
    rf.fit(train[predic], train["target"])

    # Make predictions
    preds = rf.predict(test[predic])

    # Find where our accuracy is high/low
    comb = pd.DataFrame(dict(actual=test["target"], predicted=preds), index=test.index)

    # Calculate precision
    prec = precision_score(test["target"], preds)

    # Calculate accuracy
    acc = accuracy_score(test["target"], preds)

    return comb, prec, acc


combined, precision, accuracy = make_predictions(matches_rolling, predictors + new_cols)

combined = combined.merge(matches_rolling[["date", "team", "opponent", "result"]], left_index=True, right_index=True)

print("Accuracy:", accuracy)
print("Precision:", precision)
print(combined.to_string())
