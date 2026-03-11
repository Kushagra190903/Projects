from openaq import OpenAQ
import pandas as pd

api_key = "98d5e8bf9c21d15170c206962c48de1e71940e796176f442ba5ddee69b8750bc"
client = OpenAQ(api_key=api_key)

print("🔍 Searching for stations...")

# We pull locations by country code 'IN'
# The library will now accept 'iso' correctly
res = client.locations.list(iso="IN", limit=1000)

station_list = []
for loc in res.results:
    # We only keep the ones where 'Delhi' is in the name or metadata
    if "Delhi" in str(loc.name):
        station_list.append({
            "ID": loc.id,
            "Name": loc.name,
            "Sensors": [s.parameter.name for s in loc.sensors]
        })

df = pd.DataFrame(station_list)
df.to_csv("delhi_stations_catalog.csv", index=False)

print(f"\n✅ Success! Found {len(df)} stations in Delhi.")
print(df.head())