from flask import Blueprint, jsonify
from data import db_session
from data.subcategories import SubCat

blueprint = Blueprint('subcats', __name__, template_folder='templates')

@blueprint.route('/api/subcats/<cat>')
def getSubCats(cat):
    db_sess = db_session.create_session()
    res = db_sess.query(SubCat).filter(SubCat.category == cat).all()
    db_sess.close()
    return jsonify({'success': True, 'data': [(str(i.id), i.name) for i in res]})