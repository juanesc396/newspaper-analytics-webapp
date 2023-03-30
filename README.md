# newspaper-analytics-webapp

In this repo, I will save the web app in where I show the data recolected and analized by the scraper and NLP model.

## Technical Details
The application is created in **Dash**, which is a Python library that allows, together with **Plotly**, to create graphs and place them within Html code.
I also use **Pandas** to clean and prepare the data. This caused the app to load very slowly when the dataset was larger. <br>
In the future I will try to implement Polars, a library write in Rust, that allows data process faster.

## Design
In my opinion, newspapers should represent sincerity and transparency, for that reason I chose a **glassed style** and colors that represent those emotions. <br>
I used css to styling the web. <br>
When I chose the fonts, I quickly leaned towards Serif fonts, but they didn't meet my expectations. That's why I chose a Sans Serif font that fits with the web style.
  
## For the Future
I want to:
- Improve the loading times.
- Improve the design.
- Add graphs like Scatter Plot, to show how the positivity varies over time.
- Use a better NLP model to get more accurated predictions.
