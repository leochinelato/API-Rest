from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

app = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Estudando API Rest.')
spec.register(app)
database = TinyDB('database.json')
c = count()


class Item(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    quantidade: int


class Itens(BaseModel):
    itens: list[Item]
    count: int


@app.get('/itens')  # Rota, endpoint...
@spec.validate(resp=Response(HTTP_200=Itens))
def buscar_itens():
    '''Retorna todos os itens da base de dados.'''
    return jsonify(Itens(itens=database.all(), count=len(database.all())).dict())


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
    Item = Query()
    body = request.context.body.dict()
    database.update(body, Item.id == id)
    return jsonify(body)


@app.delete('/itens/<int:id>')
@spec.validate(resp=Response(HTTP_204=Item))
def deleta_item(id):
    '''Remove um Item no banco de dados.'''
    Item = Query()
    database.remove(Item.id == id)
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
