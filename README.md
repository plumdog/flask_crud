Flask CRUD
==========

Quick and Easy CRUD for Flask, built on top of Flask-Classy.
In a very vague sense, half way to Flask-Admin.

Quick Start
===========

If you need to store a bunch of stuff, and you have some
Flask-SQLAlchemy models and some WTForms Forms, then this will allow
you to lace together some sections for CRUD-ing your data. It also
works nicely with Flask-Table if you want to use it for displaying
tables.

```python
# import Flask-CRUD things
from flask_crud import CrudView

# import form and model
from forms import MyForm
from models import MyModel

class MyView(CrudView):
    form = MyForm
    model = MyModel
```

You will also need to add the CrudBase mixin from flask_crud.mixins to
your models.

If you register* this view onto your app, or onto a Blueprint, then
going to parent-app-or-blueprint-url/my/ will try to load the models
and show output them to a template called 'index.html', which you
should write yourself, which should display items, which are, by
default, output as a list as a variable name `items`.

(*See Registering below for why this is non-standard)

Similarly, /my/add/ will try to load the form and output it to
'add.html', as a variable named `form`.

Similarly, /my/edit/[id] will try to load the model with the given id,
populate the form and output it to 'edit.html', as a variable named
`form`.

Similarly, /my/show/[id] will try to load the model with the given id
and output it to 'show.html', as a variable named `item`.

Similarly, a POST to /my/delete/[id] will try to delete the model with
the given id, and the redirect to index.

Adjusting the Above Behaviour
-----------------------------

[By 'set foo', I mean put foo = thing in the class definition]

If your templates live in their own subdirectory, then set
template_directory.

If your templates do not have the same names as those given above,
then set (index|show|add|edit)_template.

If you want to use something to modify you items before you output
them to the index template, then set presenter. If you are using
Flask-Table, set this to be a Table class, and just {{ items }} in
your template. Alternatively, set presenter to None and the items will
not be altered at all.

If you do not want some methods to be allowed, then set methods. By
default, this is
```python
['index', 'add', 'edit', 'show', 'delete']
```

But you can override this to set a different collection of
methods. The only acknowleged methods are the defaults along with
'addto' (described below).

If you need to output extra information to a template, then use the
_(index|addto|show|edit)_extras methods. These each take a single
argument, the one that is output to the template for each associated
method, and should return a dict of extra values to be sent to the
template.

Other methods you may need to override and what they do:

| Method                                       | Use                                                                               |
|----------------------------------------------|-----------------------------------------------------------------------------------|
| _url_for_index(self)                         | The url for the index page. Defaults to url_for(clsname:index)                    |
| _success_redirect_url(self, item, prev=None) | The redirect url. Defaults to _url_for_index                                      |
| _index_items(self)                           | The items to be displayed by the index method. Defaults to self.model.query.all() |

Further, as CrudView is just a subclass of flask.ext.classy.FlaskView,
you can use everything that you would use with Classy view classes.

Add To
------

If you are adding something that belongs to a parent item, then
include 'addto' in your methods and set addto_index_field to be the
field name used for the parent index. For example, if I have Artists
and Albums where Artists have many Albums, and the Album has an
artist_id field, set addto_index_field = 'artist_id'. Then if you get
a form posted to /addto/13, it will populate artist_id = 13 when
creating a new item.

Registering
===========

Because we need to save things, and because of how Flask-SQLAlchemy
works, we need to add any new or changed items to the database
session, and commit that session. I couldn't find a nicer way of doing
this than including the database session when registering:

```python
from flask import Flask
from my_view import MyView
from models import db

app = Flask(__name__)
MyView.register(app, db.session)
```

This doesn't feel altogether beautiful, but it works. I'm absolutely
open to better ways doing this.
