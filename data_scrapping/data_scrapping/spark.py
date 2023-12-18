# --------- Connexion et extraction de données de Mongodb --------- #
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SparkApplication") \
    .master("local") \
    .config("spark.mongodb.input.uri", "mongodb://localhost:27017/ScrappedData.articles") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/ScrappedData.articles") \
    .getOrCreate()

df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", "mongodb://localhost:27017/ScrappedData.articles").load()
df.printSchema()

# --------- Nombre d'articles / Date publication --------- #
import matplotlib.pyplot as plt
import numpy as np

df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
                    "mongodb://localhost:27017/ScrappedData.articles").load()

df = df[df['title'] != ""]
df = df[df['date_publication'] != 0]

gr = df.groupBy("date_publication").count().sort("count", ascending=True)
gr.show()
gr = gr.toPandas()

y = gr['count'].values.tolist()
x = gr['date_publication'].values.tolist()

plt.bar(x, y)
plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.title("Nombre d'articles par Année")
plt.xlabel("Année")
plt.ylabel("Nombre articles")
plt.show()

# ----------- Nombre d'articles d'un sujet / Date publication ----------- #
import matplotlib.pyplot as plt
import numpy as np

df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
                        "mongodb://localhost:27017/ScrappedData.articles").load()

df = df[df['title'] != ""]
df = df[df['topic'] == "Blockchain"]
df = df[df['date_publication'] != 0]

gr = df.groupBy("date_publication").count().sort("count", ascending=True)
gr.show()
gr = gr.toPandas()

y = gr['count'].values.tolist()
x = gr['date_publication'].values.tolist()

plt.bar(x, y)
plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.title("Nombre d'articles Blockchain par Année")
plt.xlabel("Année")
plt.ylabel("Nombre d'articles Blockchain")
plt.show()

# ------- Nombre de downloads de chaque sujet / Date publication ------- #
import matplotlib.pyplot as plt

df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
                        "mongodb://localhost:27017/ScrappedData.articles").load()
df = df[df['title'] != ""]
df = df[df['date_publication'] != 0]

g1 = df.groupBy("topic").sum()
g1.show()
g1 = g1.toPandas()
g1

y = g1['sum(downloads)'].values.tolist()
x = g1['topic'].values.tolist()

plt.bar(x, y)
plt.title("Nombre d'enregistrements par Sujet")
plt.xlabel("Sujet")
plt.ylabel("Nombre d'enregistrements par Sujet")
plt.show()

# --------- Map : Nombre d'articles par pays --------- #
import pandas as pd
import pycountry as pycountry
import plotly.express as px

df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
                "mongodb://localhost:27017/ScrappedData.articles").load()
df = df.toPandas()
df = df[df['title'] != ""]
df = df[df['authors_country'] != ""]

x = df[['authors_country']]
y = pd.DataFrame({'authors_country' : x['authors_country'] \
    .apply(lambda x : pd.Series(list(set(x.split(';'))))).stack().tolist()})
y['count'] = 0

countries_number = y.groupby("authors_country").count() \
    .sort_values(by=["count"], ascending = True).reset_index()

l = countries_number['authors_country'].values.tolist()

for i, c in enumerate(l):
    l[i] = c.strip()

for i, c in enumerate(l):
    countries_number['authors_country'][i] = l[i]

countries_number_dataframe = countries_number.values.tolist()
countries_number_df = pd.DataFrame(countries_number_dataframe)

countries_number_df.columns = ['Country', 'Nombre Articles']

countries_list = countries_number_df['Country'].unique().tolist()

countries_codes = {}
for country in countries_list:
    try :
        country_info = pycountry.countries.search_fuzzy(country)
        country_code = country_info[0].alpha_3
        countries_codes.update({country : country_code})
    except :
        print("Error: can't add this country's code => ", country)
        if country == "P.R.China" or country == "China Beijing" or country == "P.R. China" \
                or country == "Guangxi China" or country == "P R China" or country == "P.R China" \
                or country == "P. R. China (86)13521389761" or country == "Qingdao Shandong China" \
                or country == "P. R. China" or country == "Beijing China":
            countries_codes.update({country: 'CHN'})
        elif country == "U.S.A" or country == "Kent. Ohio." or country == "Irvine" or country == "Rochester" \
                or country == "San Diego" or country == "MD USA" or country == "MD 20742" or country == "Miami" \
                or country == "Palo Alto":
            countries_codes.update({country: 'USA'})
        elif country == "MORROCO" or country == "Morocco Laboratory of Applied mathematics and applications" \
                or country == "Morroco" or country == "Maroc":
            countries_codes.update({country: 'MAR'})
        elif country == "S. Korea" or country == "Rebublic of Korea" or country == "Rep. of Korea":
            countries_codes.update({country: 'KR'})
        elif country == "Montreal":
            countries_codes.update({country: 'FRA'})
        elif country == "Moscow Russia":
            countries_codes.update({country: 'RUS'})
        elif country == "SW7 2AZ United Kingdom" or country == "U.K." or country == "Scotland Uk" \
                or country == "U.K":
            countries_codes.update({country: 'GBR'})
        elif country == "Turkey" or country == "Istanbul Turkey":
            countries_codes.update({country: 'TUR'})
        elif country == "UAE" or country == "Abu Dhabi UAE":
            countries_codes.update({country: 'AE'})
        elif country == "Brasil":
            countries_codes.update({country: 'BR'})
        elif country == "European Union":
            countries_codes.update({country: 'EU'})
        else:
            countries_codes.update({country: ' '})

for k, v in countries_codes.items():
    countries_number_df.loc[(countries_number_df.Country == k), 'iso_alpha'] = v

fig = px.choropleth(data_frame = countries_number_df,
                    locations = 'iso_alpha',
                    color = "Nombre Articles",
                    hover_name = "Country",
                    color_continuous_scale = 'RdYlGn',
                    range_color=(0, 1000),
                    color_continuous_midpoint=500,
                    )
fig.show()
