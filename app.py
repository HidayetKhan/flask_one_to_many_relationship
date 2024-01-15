from flask import Flask ,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api,Resource


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api=Api(app)
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(200))
    password=db.Column(db.String(200))
    
    addresses=db.relationship('Address',back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Address(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    street=db.Column(db.String(150))
    city=db.Column(db.String(150))
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))

    user=db.relationship('User',back_populates='addresses')

db.configure_mappers()
class UserResorse(Resource):
    def get(self,user_id=None):
        if user_id:
            user=User.query.get(user_id)
            if user:
                addresses=[{'id':address.id,'street':address.street,'city':address.city}for address in user.addresses]
                return {'id':user.id,'username':user.username,'password':user.password,'addresses':addresses},200
            else:
                return {'message':'user not found'}
        else:
            users=User.query.all()
            user_list=[{
                'id':user.id,
                'username':user.username,
                'password':user.password,
                'addresses':[{
                    'id':address.id,
                    'street':address.street,
                    'city':address.city
                }for address in user.addresses]
            }for user in users]
            return {'users':user_list}
        

    def post(self):
        data = request.get_json()
        user_data = {
            'username': data['username'],
            'password': data['password']
        }
        # Extract address data
        address_data = data.get('addresses', [])
        new_user = User(**user_data)
        db.session.add(new_user)
        for address_item in address_data:
            new_address = Address(
                street=address_item.get('street', ''),
                city=address_item.get('city', ''),
                user=new_user
            )
            db.session.add(new_address)
        db.session.commit()
        return {'message': 'New user and addresses created successfully', 'user_id': new_user.id}
    
    def put(self,user_id):
        user=User.query.get(user_id)
        if user:
            data=request.get_json()
            username=data['username']
            password=data['password']
            if 'addresses' in data:
                for existing_address in user.addresses:
                    db.session.delete(existing_address)
                for address_data in data['addresses']:
                    new_address=Address(street=data['street'],city=data['city'])
                    db.session.add(new_address)

            db.session.commit()
            return {'message':'user data is updated'},200
        else:
            return {'message':'user not found'},404
        
    def delete(self,user_id):
        user=User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message':'user deleted'}
        else:
            {'message':'user not found'},404

api.add_resource(UserResorse,'/user','/user/<int:user_id>')
        
    

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)