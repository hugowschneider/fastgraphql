# Classes with complex attributes

**FastGraphQL** also supports classes with attributes
having as type any other supported type.

Let us have a look at the following code

```python title="main.py" linenums="1"
--8<-- "tutorial/complex-classes/main.py"
```

and, as always, run

```sh
$ uvicorn main:app --reload
```

and under <a href="http://127.0.0.1:8000/graphql" target="_blank">http://127.0.0.1:8000/graphql</a>
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

#### Forward References

Let us take a closer look at line `24``, here we are using a
<a href="https://peps.python.org/pep-0484/#forward-references" target="_black">*Forward Reference*</a>.
The special thing about _Forward References_ is that it allows annotating something
yet not fully defined or yet not defined at all. In our case, we are referencing
the type `Person` inside the definition scope of `Person` itself, `which means at that moment`
 `Person` is not yet fully defined.

**FastGraphQL** only supports _Forward References_ in the form `List["Person"]` and not
`"List[Person]"` even though both are correct. This holds to all generic
annotations, e.g. `Optional["Person"]` vs `"Optional[Person]"`.


