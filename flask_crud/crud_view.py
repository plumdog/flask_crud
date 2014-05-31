from flask.ext.classy import FlaskView, route
from flask import render_template, request, redirect, url_for, abort
from os.path import join as path_join


class CrudView(FlaskView):
    """Gives a quick template

    form, a form class

    model, assumed to be a model that implements both save_form(form)
    and delete() methods

    presenter, a callable that when called with a list of models gives
    something that should be sent out to the template

    template_directory, name of the directory that all of the
    templates are in

    index_template, name of the template to use for the index page,
    defaults to index.html

    show_template, name of the template to use for the show page,
    defaults to show.html

    add_template, name of the template to use for the add page,
    defaults to add.html

    edit_template, name of the template to use for the edit page,
    defaults to edit.html

    """

    index_template = 'index.html'
    show_template = 'show.html'
    add_template = 'add.html'
    edit_template = 'edit.html'

    template_directory = ''
    presenter = list

    db_session = None
    addto_index_field = None

    methods = ['index', 'add', 'edit', 'show', 'delete']

    @classmethod
    def register(cls, app, db_session, *args, **kwargs):
        cls.db_session = db_session
        super(CrudView, cls).register(app, *args, **kwargs)

    def _url_for_index(self):
        return url_for(self.__class__.__name__ + ':index')

    def _success_redirect_url(self, item, prev=None):
        return self._url_for_index()

    @classmethod
    def _template_path(cls, template_name):
        return path_join(cls.template_directory, template_name)

    def index(self):
        if 'index' not in self.methods:
            abort(404)
        items = self._index_items()
        if self.presenter:
            items = self.presenter(items)
        return render_template(self._template_path(self.index_template), items=items, **self._index_extras(items))

    def _index_items(self):
        return self.model.query.all()

    def _index_extras(self, items):
        return {}

    @route('/add/', methods=['POST', 'GET'])
    def add(self):
        if 'add' not in self.methods:
            abort(404)
        form = self.form(request.form)
        if form.validate_on_submit():
            item = self.model()
            item.save_form(form, session=self.db_session)
            return redirect(self._success_redirect_url(item, 'add'))
        return render_template(self._template_path(self.add_template), form=form)

    @route('/addto/<int:id_>', methods=['POST', 'GET'])
    def addto(self, id_):
        if 'addto' not in self.methods:
            abort(404)
        form = self.form(request.form)
        if form.validate_on_submit():
            item = self.model()
            if self.addto_index_field:
                extras = {self.addto_index_field: id_}
            else:
                extras = {}
            item.save_form(form, session=self.db_session, extras=extras)
            return redirect(self._success_redirect_url(item, 'addto'))
        return render_template(self._template_path(self.add_template), form=form, **self._addto_extras(id_))

    def _addto_extras(self, id_):
        return {}

    @route('/show/<int:id_>')
    def show(self, id_):
        if 'show' not in self.methods:
            abort(404)
        item = self.model.query.get_or_404(id_)
        return render_template(self._template_path(self.show_template), item=item, **self._show_extras(item))

    def _show_extras(self, item):
        return {}

    @route('/edit/<int:id_>', methods=['POST', 'GET'])
    def edit(self, id_):
        if 'edit' not in self.methods:
            abort(404)
        item = self.model.query.get_or_404(id_)
        form = self.form(request.form, obj=item)
        if form.validate_on_submit():
            item.save_form(form, session=self.db_session)
            return redirect(self._success_redirect_url(item, 'edit'))
        return render_template(self._template_path(self.edit_template), form=form, **self._edit_extras(item))

    def _edit_extras(self, item):
        return {}

    @route('/delete/<int:id_>', methods=['POST'])
    def delete(self, id_):
        if 'delete' not in self.methods:
            abort(404)
        item = self.model.query.get_or_404(id_)
        item.delete(session=self.db_session)
        return redirect(self._success_redirect_url(item, 'delete'))
