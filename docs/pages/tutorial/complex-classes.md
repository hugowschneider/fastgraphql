# Classes with complex attributes

**FastGraphQL** also support classes with attributes
having as type any other supported type.

Lets have a look on in the following code

```python title="main.py" linenums="1"
--8<-- "tutorial/complex-classes/main.py"
```

and as always run

```sh
$ uvicorn main:app --reload
```

and under <a href="http://127.0.0.1:8000" target="_blank">http://127.0.0.1:8000</a>
you can see the result.

![Image](../assets/tutorial/complex-classes/get_person.png)

## Dissecting

### Step 1: Define models

```python title="main.py" linenums="1" hl_lines="12 13 17 18"
--8<-- "tutorial/complex-classes/main.py"
```

In the highlighted lines we are defining **Pydantinc** models as explained in the
previous chapter, [Classes](simple-classes.md)

### Step 2: Reference other models

```python title="main.py" linenums="1" hl_lines="23 24"
--8<-- "tutorial/complex-classes/main.py"
```

Now we declare class attributes whose types are other **Pydantinc** models.
Nothing else is needed.

#### Forward Referece

Lets take a closer look into line `24`, here we are using a
<a href="https://peps.python.org/pep-0484/#forward-references" target="_black">*Forward Referece*</a>.
The special thing about *Forward Refereces* is that it allows annotating something with a type
yet not fully defined or yet not defined at all. In our case, we are referencing
the type `Person` inside the definition scope of `Person` itself, that means in that
moment `Person` is not yet fully defined.

**FastGraphQL** only supports *Forward Referece* in the form `List["Person"]` and not
`"List[Person]"` eventhough both are correct. This holds true to all generic
annotations, e.g. `Optional["Person"]` vs `"Optional[Person]"`.


