# Classes

Python classes should be defined as **Pydantic** models to be supported. 

## Classes with only primitive types

Lets start with a simple example

```python title="main.py" linenums="1"
--8<-- "tutorial/simple-classes/models.py"
```
and ...

```sh
$ uvicorn main:app --reload
```


Vuolà!

![Image](../assets/tutorial/simple-classes/get_person.png)

!!! Note "Star Wars :rocket:"
    Please don't take the Star Wars reference so seriusly, Height and age of 
    Luke Skywalker may vary depending on many different factors :smile:.

## Dissecting the Code