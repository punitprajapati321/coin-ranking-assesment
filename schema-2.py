import requests
import pandas as pd
from datetime import datetime

response = requests.get("https://api.coinranking.com/v1/public/coin/1/history/30d")

df = pd.DataFrame(response.json()["data"]["history"])

df_2 = df.copy()

df_2["price"] = round(pd.to_numeric(df_2["price"]), 2)

df_2["date"] = [datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d") for ts in df_2["timestamp"]]

df_2["datetime"] = [datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%dT%H:%M:%S") for ts in df_2["timestamp"]]

df_2 = df_2.drop(columns=["timestamp"])

df_2_copy = df_2

df_2_mean = df_2.groupby(["date"]).mean()

df_2_var = df_2.groupby(["date"]).var()

df_2_std = df_2.groupby(["date"]).std()

df_2 = pd.DataFrame({"date": df_2_mean.index, "dailyAverage": df_2_mean["price"], "dailyVariance": df_2_var["price"]})

df_2 = df_2.reset_index(drop=True)

volatilityAlert = []

for i in range(len(df_2.index)):
    temp_df = df_2_copy[df_2_copy["date"] == df_2["date"][i]]

    upper_alert = (temp_df["price"].max() > df_2["dailyAverage"][i] + 2 * df_2_std["price"][i])

    lower_alert = (temp_df["price"].min() < df_2["dailyAverage"][i] - 2 * df_2_std["price"][i])

    volatilityAlert.append(upper_alert or lower_alert)

df_2["volatilityAlert"] = volatilityAlert

df_2["date"] = [date + "T00:00:00" for date in df_2["date"]]

df_2 = df_2.merge(df_2_copy, how="left", left_on="date", right_on="datetime")

df_2 = df_2.drop(columns=["date_y", "datetime"])

df_2 = df_2.rename(columns={"date_x": "date"})

df_2[["price", "dailyAverage", "dailyVariance"]] = round(df_2[["price", "dailyAverage", "dailyVariance"]], 2)

df_2 = df_2[["date", "price", "dailyAverage", "dailyVariance", "volatilityAlert"]]

df_2.to_csv("df_2.csv", sep=",", na_rep="NA", header=True, index=False)

dict_2 = df_2.to_dict("records")

print("Schema 2:")

print(dict_2)