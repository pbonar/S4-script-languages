from wikipedia import page, PageError

name = input("Enter the name of a Wikipedia article: ")

data = None
try:
    data = page(name)
except PageError:
    print("Page not found!")

if data:
    print(">>>>>> Summary:")
    print(data.summary)
    print(">>>>>> URL:")
    print(data.url)
