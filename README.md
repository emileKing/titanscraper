TITANScraper 
=========
v0.0.20


Description
----------
A web scraping library that makes scraping easy.
You can build complete web spiders and crawlers in a few lines of code


Installation
----------
```
pip install titanscraper
```

Example
------
Assuming you have installed the library using pip as above,
the next thing to do is to import the module and create an instance of the `TitanScraper` class
```python
from titanscraper import TitanScraper


scraper = TitanScraper()
```

Then you need to define `rules`. Rules are basically the instructions given to
the scraper to describe what to collect and name the data from a webpage. The most basic 
structure of a rule is as follows:
```python
{
    "name": "item_name",
    "selector": "some-css-selector",
}
```
The attribute `name` describes the name that will be given to specific data scraped from an 
element that matches the selector in `selector`. Where `selector` is a valid CSS selector that actually references an HTML DOM element.  

For example, assuming you want to collect the price of an item from an e-commerce website
where the price of the product is found within a `span` with class name `price` that is in an article object with class name `product`, you might want to do the following:  

```python
{
    "name": "price",
    "selector": "article.product > span.price",
}
```

Now you define your rules as a list as follows:
```python 
RULES = [
    {
        "name": "product-title",
        "selector": "article.product > span.name"
    },
    {
        "name": "product-price",
        "selector": "article.product > span.price"
    }
]
```
The next thing to do is to define your target webpages. This is just a list of URLS
```python
#  define a list of all the web pages you intend to scrap
target_pages = [
    "https://www.target_website.fr/target_one",
    "https://www.target_website.fr/target_two",
]
```

With that set, now you can scrap the data from all the pages in `target_pages` and parse data using the rules defined in `RULES` above as follows

```python
# start the scraping of the target webpages.
data = scraper.scrap(target_pages, RULES)
```

The data returned by `TitanScraper.scrap` is a list of dictionaries
where the keys are the values from `name` in `RULES` and the values are
the data collected from the corresponding `selector` in the same rule.
Print your data to see what you have recieved as result.
```python
print(data)
```
In normal circumstances (all pages scraped without error), the length of the list `data`
will be equal to the length of the list `target_pages` and the length of each item in 
`data` will be the same as the number of rules in `RULES`.

Check python scripts in `/examples` directory to try real examples