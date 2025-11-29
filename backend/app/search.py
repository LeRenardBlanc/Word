import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

INDEX_DIR = "indexdir"

def init_index():
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
        schema = Schema(id=ID(stored=True), title=TEXT(stored=True), content=TEXT)
        create_in(INDEX_DIR, schema)

def add_to_index(note_id, title, content):
    ix = open_dir(INDEX_DIR)
    writer = ix.writer()
    writer.add_document(id=str(note_id), title=title, content=content)
    writer.commit()

def search_index(query_str):
    ix = open_dir(INDEX_DIR)
    results_list = []
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query)
        for r in results:
            results_list.append({"id": r['id'], "title": r['title']})
    return results_list

def update_index(note_id, title, content):
    # For simplicity, Whoosh update can be delete + add or update_document
    ix = open_dir(INDEX_DIR)
    writer = ix.writer()
    writer.update_document(id=str(note_id), title=title, content=content)
    writer.commit()
