import pandas as pd


url = 'https://api.coinranking.com/v1/public/coin/1/history/30d'


json_df = pd.read_json(url)

df = pd.DataFrame(json_df['data']['history'])
df2 = df
df['date'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
df['datehour'] = df['date'].dt.hour
df.sort_values(by=['date'], inplace=True, ascending=True)
df = df[(df['datehour'] > 0) & (df['datehour'] <= 1)]

# "%Y-%m-%dT%H:%M:%S"
df['price'] = df['price'].astype(float)
df['price'] = df['price'].apply(lambda x: float("{:.2f}".format(x)))

df['price_previous'] = df['price'].shift(1)


def check_previous(x):
    if x['price'] > x['price_previous']:
        return 'up'
    elif x['price'] < x['price_previous']:
        return 'down'
    elif x['price'] == x['price_previous']:
        return 'same'
    else:
        return 'na'


df['direction'] = df.apply(check_previous, axis=1)


def change_value(x):
    if x['price'] and x['price_previous']:
        return x['price'] - x['price_previous']
    else:
        return 'na'


df['change'] = df.apply(change_value, axis=1)

df['dayOfWeek'] = df['date'].dt.day_name()


def find_highSinceStart(x, y, z):
    if z == x['date']:
        return 'na'

    if x['price'] > y:
        return True
    else:
        return False


def find_lowSinceStart(x, y, z):
    if z == x['date']:
        return 'na'

    if x['price'] < y:
        return True
    else:
        return False


df['highSinceStart'] = df.apply(find_highSinceStart, args=(df['price'].iloc[0], df['date'].iloc[0]), axis=1)

df['lowSinceStart'] = df.apply(find_lowSinceStart, args=(df['price'].iloc[0], df['date'].iloc[0]), axis=1)

df['date'] = df['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')

df[['date', 'price', 'direction', 'change', 'dayOfWeek', 'highSinceStart', 'lowSinceStart']]