from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


app = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='API Rest.')
spec.register(app)
database = TinyDB(storage=MemoryStorage)
c = count()


class QueryItem(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]


class Item(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    quantidade: int


class Itens(BaseModel):
    itens: list[Item]
    count: int


@app.get('/itens')  # Rota, endpoint...
@spec.validate(query=QueryItem, resp=Response(HTTP_200=Itens))
def buscar_itens():
    '''Retorna todos os itens da base de dados.'''
    query = request.context.query.dict(exclude_none=True)
    todos_os_itens = database.search(Query().fragment(query))
    return jsonify(Itens(itens=todos_os_itens, count=len(todos_os_itens)).dict())


@app.get('/itens/<int:id>')
@spec.validate(resp=Response(HTTP_200=Item))
def buscar_item(id):
    '''Retorna apena o item solicitado da base de dados.'''
    try:
        item = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Item not found!'}, 404
    return jsonify(item)


@app.post('/itens')
@spec.validate(body=Request(Item), resp=Response(HTTP_201=Item))
def inserir_item():
    '''Insere um item no banco de dados.'''
    body = request.context.body.dict()
    database.insert(body)
    return body


@app.put('/itens/<int:id>')
@spec.validate(body=Request(Item), resp=Response(HTTP_200=Item))
def altera_item(id):
    '''Altera um Item no banco de dados.'''
    body = request.context.body.dict()
    database.update(body, Query().id == id)
    return jsonify(body)


@app.delete('/itens/<int:id>')
@spec.validate(resp=Response(HTTP_204=Item))
def deleta_item(id):
    '''Remove um Item no banco de dados.'''
    database.remove(Query().id == id)
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
