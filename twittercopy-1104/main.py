#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
from datetime import datetime
from google.appengine.ext import ndb
from operator import attrgetter, itemgetter
config = {'default-group':'base-data'}

class User(ndb.Model):
    idnumber = ndb.IntegerProperty(required=True, indexed=True)
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

class PostMessage(ndb.Model):
    idnumber = ndb.IntegerProperty(required=True, indexed=True)
    timestamp = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    contents = ndb.StringProperty(required=True)
    latitude = ndb.StringProperty(required=False)
    longitude = ndb.StringProperty(required=False)

class MainHandler(webapp2.RequestHandler):
       
    def post(self):
        #need this to allow the app to play nicely with other domains
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        #reject if connection doesn't support JSON data for some reason
        if 'application/json' not in self.request.accept:
            self.response.status = 406
            self.response.status_message = "Not acceptable, API only supports JSON."
            return

        #get the action, this should be "trylogin", "adduser", "addposting", "editposting", or "deleteposting"
        action = self.request.get('action')

        if action is None or not action:
            self.response.set_status(200)
            self.response.write("ERROR: Action required! (adduser, addposting, trylogin, editposting, or deleteposting)")

        if action == "trylogin":
            #user is attempting to log in, ensure all needed values are present
            NewUserName = self.request.get('username', default_value=None)
            NewPassword = self.request.get('password', default_value=None)

            if NewUserName is None or not NewUserName:
                self.response.set_status(200)
                self.response.write("ERROR:username required!")
                BadFlag = True
                
            if NewPassword is None or not NewPassword:
                self.response.set_status(200)
                self.response.write("ERROR:password required!")
                BadFlag = True

            qry = User.query(NewUserName == User.username, ancestor=ndb.Key(User, 'base-data'))
            validate = qry.get()
            if validate is None or not validate:
                #ensure user exists, return error message if no user found
                self.response.set_status(200)
                self.response.write("Username %s not found." % NewUserName)
            else:
                #if user is found
                qry = User.query(NewUserName == User.username, NewPassword == User.password, ancestor=ndb.Key(User, 'base-data'))
                validate = None
                validate = qry.get()
                if validate is None or not validate:
                    #ensure password matches
                    self.response.set_status(200)
                    self.response.write("ERROR: Username/Password mismatch!")
                else:
                    #return user's data if login successful
                    display = validate.to_dict()
                    self.response.write(json.dumps(display))


        if action == "adduser":
            #add a new user to the datastore
            #iterate over list of users to determine user's ID number
            UserList = [{'idnumber':x.idnumber, 'username':x.username, 'password':x.password} for x in User.query(ancestor=ndb.Key(User, config.get('default-group'))).fetch()]
            NewUserID = 0
            if UserList:
                NewUserID += len(UserList)

            NewUserName = self.request.get('username', default_value=None)
            NewPassword = self.request.get('password', default_value=None)
            k = ndb.Key(User, 'base-data')
            NewUserObject = User(parent=k)
            NewUserObject.idnumber = NewUserID
            BadFlag = False

            if NewUserName is None or not NewUserName:
                self.response.set_status(200)
                self.response.write("ERROR:username required!")
                BadFlag = True
            else:
                NewUserObject.username = NewUserName
                

            if NewPassword is None or not NewPassword:
                self.response.set_status(200)
                self.response.write("ERROR:password required!")
                BadFlag = True
            else:
                NewUserObject.password = NewPassword

            dupeTest = User.query(NewUserName == User.username, ancestor=ndb.Key(User, 'base-data'))
            validate = dupeTest.get()
            if validate:
                #if validate exists then there's a duplicate user, return error
                self.response.set_status(200)
                self.response.write("ERROR:username already exists!")
                BadFlag = True
                

            if BadFlag != True:
                NewUserObject.put()
                out = NewUserObject.to_dict()
                self.response.write(json.dumps(out))

        if action == "addposting":
            #add a new post to the datastore

            BadFlag = False
            NewUserName = self.request.get('username', default_value=None)
            NewPassword = self.request.get('password', default_value=None)
            NewPosting = self.request.get('posting', default_value=None)
            NewLatitude = self.request.get('latitude', default_value=None)
            NewLongitude = self.request.get('longitude', default_value=None)
            
            if NewPosting is None or not NewPosting:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, post contents is required")

            if NewUserName is None or not NewUserName:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, username is required")

            if NewPassword is None or not NewPassword:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, password is required")

            qry = User.query(User.username == NewUserName, User.password == NewPassword)
            validate = qry.get()
            if validate is None:
                #if validate doesn't have any data, then no user with this password exists in the datastore
                #so the post can't be added
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: User ID/Password mismatch")

            if BadFlag != True:

                MessageList = [{'idnumber':x.idnumber, 'username':x.username, 'contents':x.contents, 'timestamp':x.timestamp} for x in PostMessage.query(ancestor=ndb.Key(PostMessage, config.get('default-group'))).fetch()]
                NewPostID = 0
                if MessageList:
                    for i in range(len(MessageList)):
                        if MessageList[i]['idnumber'] > NewPostID:
                            NewPostID = MessageList[i]['idnumber']
                    NewPostID = NewPostID + 1

                k = ndb.Key(PostMessage, 'base-data')
                NewPostingObject = PostMessage(parent=k)
                NewPostingObject.username = NewUserName
                NewPostingObject.idnumber = NewPostID
                NewPostingObject.contents = NewPosting
                NewPostingObject.timestamp = str(datetime.now())
                NewPostingObject.latitude = NewLatitude
                NewPostingObject.longitude = NewLongitude
                NewPostingObject.put()
                out = NewPostingObject.to_dict()
                self.response.write(json.dumps(out))

        if action == "deleteposting":
            #delete a posting
            BadFlag = False
            NewUserName = self.request.get('username', default_value=None)
            NewPassword = self.request.get('password', default_value=None)
            NewUserID = self.request.get('userid', default_value=None)
            PostID = self.request.get('postid', default_value=None)

            if NewUserName is None or not NewUserName:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, username is required")

            if NewPassword is None or not NewPassword:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, password is required")

            if PostID is None or not PostID:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, posting ID is required")
            else:
                try:
                    PostID = int(PostID)
                except ValueError:
                    self.response.status = 400
                    self.response.write("ERROR: Post ID must be an integer!")
                    return

            qry = User.query(User.username == NewUserName, User.password == NewPassword, ancestor=ndb.Key(User, 'base-data'))
            validate = qry.get()
            if validate is None:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: User ID/Password mismatch")

            qry = PostMessage.query(PostMessage.idnumber == PostID, PostMessage.username == NewUserName, ancestor=ndb.Key(PostMessage, 'base-data'))
            validate = qry.get()
            if validate is None:
                #if validate doesn't exist, then there's no post ID created by this user
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Posting ID/Username mismatch")

            if BadFlag != True:
                qry = PostMessage.query(PostMessage.idnumber == PostID, ancestor=ndb.Key(PostMessage, 'base-data'))
                NewPostingObject = qry.get()
                if NewPostingObject is None:
                    #if no data in this variable, then the post ID doesn't match what's in the datastore
                    self.response.status = 404
                    self.response.write("ERROR: No posting found with that ID")
                    return
                NewPostingObject.key.delete()
                out = "Posting ID# %i deleted" % PostID
                self.response.write(out)

        if action == "editposting":
            #edit an existing posting
            BadFlag = False
            NewUserName = self.request.get('username', default_value=None)
            NewPassword = self.request.get('password', default_value=None)
            NewPosting = self.request.get('posting', default_value=None)
            PostID = self.request.get('postid', default_value=None)
            
            
            if NewPosting is None or not NewPosting:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, post contents is required")

            if NewUserName is None or not NewUserName:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, username is required")

            if NewPassword is None or not NewPassword:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, password is required")

            if PostID is None or not PostID:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Bad Request, posting ID is required")
            else:
                try:
                    PostID = int(PostID)
                except ValueError:
                    self.response.status = 400
                    self.response.write("ERROR: Post ID must be an integer!")
                    return


            qry = User.query(User.username == NewUserName, User.password == NewPassword, ancestor=ndb.Key(User, 'base-data'))
            validate = qry.get()
            if validate is None:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: User ID/Password mismatch")

            qry = PostMessage.query(PostMessage.idnumber == PostID, PostMessage.username == NewUserName, ancestor=ndb.Key(PostMessage, 'base-data'))
            validate = qry.get()
            if validate is None:
                BadFlag = True
                self.response.status = 400
                self.response.write("ERROR: Posting ID/Username mismatch")

            if BadFlag != True:
                qry = PostMessage.query(PostMessage.idnumber == PostID, ancestor=ndb.Key(PostMessage, 'base-data'))
                NewPostingObject = qry.get()
                if NewPostingObject is None:
                    self.response.status = 404
                    self.response.write("ERROR: No posting found with that ID")
                    return
                NewPostingObject.contents = NewPosting
                NewPostingObject.timestamp = str(datetime.now())
                NewPostingObject.put()
                out = NewPostingObject.to_dict()
                self.response.write(json.dumps(out))

    def get(self, **param):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        display = self.request.get('display')
        if display == "allusers":
            #return a JSON object of all users in the datastore
            UserList = [{'idnumber':x.idnumber, 'username':x.username, 'password':x.password} for x in User.query(ancestor=ndb.Key(User, 'base-data')).fetch()]
            newList = sorted(UserList, key=itemgetter('idnumber'), reverse=True)
            self.response.write(json.dumps(newList))

        if display == "allposts":
            #return a JSON object of all posts in the datastore
            PostList = [{'idnumber':x.idnumber, 'username':x.username, 'timestamp':x.timestamp, 'contents':x.contents} for x in PostMessage.query(ancestor=ndb.Key(PostMessage, 'base-data')).fetch()]
            newList = sorted(PostList, key=itemgetter('idnumber'), reverse=True)
            self.response.write(json.dumps(newList))

        if display == "user":
            #return a JSON object of specified user's data
            username = self.request.get('username')
            if username is None or not username:
                self.response.status = 400
                self.response.write("ERROR: Username is required when requesting user!")
            else:
                qry = User.query(User.username == username, ancestor=ndb.Key(User, 'base-data'))
                validate = qry.get()
                if validate is None:
                    self.response.status = 404
                    message = "Error: Username %s not found" % username
                    self.response.write(message)
                else:
                    display = validate.to_dict()
                    self.response.write(json.dumps(display))

        if display == "posting":
            #return a JSON object of specified post ID's data
            postid = (self.request.get('postid'))
            if postid is None or not postid:
                self.response.status = 400
                self.response.write("ERROR: Post ID is required when requesting posting!")
            else:
                try:
                    postid = int(postid)
                except ValueError:
                    self.response.status = 400
                    self.response.write("ERROR: postid must be an integer!")
                    return

                qry = PostMessage.query(PostMessage.idnumber == postid, ancestor=ndb.Key(PostMessage, 'base-data'))
                validate = qry.get()
                if validate is None:
                    self.response.status = 404
                    message = "Error: Post ID %i not found" % postid
                    self.response.write(message)
                else:
                    display = validate.to_dict()
                    self.response.write(json.dumps(display))

        if display == "userposts":
            #display all posts created by specified user
            username = self.request.get('username')
            if username is None or not username:
                self.response.status = 400
                self.response.write("ERROR: Username is required when requesting posts by user!")
            else:
                qry = User.query(User.username == username, ancestor=ndb.Key(User, 'base-data'))
                validate = qry.get()
                if validate is None:
                    self.response.status = 404
                    message = "Error: Username %s not found" % username
                    self.response.write(message)
                else:
                    PostList = [{'idnumber':x.idnumber, 'username':x.username, 'timestamp':x.timestamp, 'contents':x.contents, 'latitude':x.latitude, 'longitude':x.longitude} for x in PostMessage.query(PostMessage.username == username, ancestor=ndb.Key(PostMessage, 'base-data')).fetch()]
                    newList = sorted(PostList, key=itemgetter('idnumber'), reverse=True)
                    self.response.write(json.dumps(newList))

        if display is None or not display:
            MessageList = [{'idnumber':x.idnumber, 'username':x.username, 'contents':x.contents, 'timestamp':x.timestamp} for x in PostMessage.query(ancestor=ndb.Key(PostMessage, config.get('default-group'))).fetch()]
            topPost = 0
            if MessageList:
                topPost += len(MessageList)
                topPost = topPost - 1
            qry = PostMessage.query(PostMessage.idnumber == topPost, ancestor=ndb.Key(PostMessage, 'base-data'))
            validate = qry.get()
            if validate is None or not validate:
                self.response.write("No postings to display")
                return
            display = validate.to_dict()
            self.response.write(json.dumps(display))
        
    def put(self, **param):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        if 'application/json' not in self.request.accept:
            self.response.status = 406
            self.response.status_message = "Not acceptable, API only supports JSON."
            return

        action = self.request.get('action')

        BadFlag = False
        NewUserName = self.request.get('username', default_value=None)
        NewPassword = self.request.get('password', default_value=None)
        NewPosting = self.request.get('posting', default_value=None)
        #NewUserID = self.request.get('userid', default_value=None)
        PostID = self.request.get('postid', default_value=None)
        
        
        if NewPosting is None or not NewPosting:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, post contents is required")

        if NewUserName is None or not NewUserName:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, username is required")

        if NewPassword is None or not NewPassword:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, password is required")

        # if NewUserID is None or not NewUserID:
        #     BadFlag = True
        #     self.response.status = 400
        #     self.response.write("ERROR: Bad Request, user ID is required")
        # else:
        #     try:
        #         NewUserID = int(NewUserID)
        #     except ValueError:
        #         self.response.status = 400
        #         self.response.write("ERROR: userid must be an integer!")
        #         BadFlag = True
        #         return

        if PostID is None or not PostID:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, posting ID is required")
        else:
            try:
                PostID = int(PostID)
            except ValueError:
                self.response.status = 400
                self.response.write("ERROR: Post ID must be an integer!")
                return


        qry = User.query(User.username == NewUserName, User.password == NewPassword, ancestor=ndb.Key(User, 'base-data'))
        validate = qry.get()
        if validate is None:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: User ID/Password mismatch")

        qry = PostMessage.query(PostMessage.idnumber == PostID, PostMessage.username == NewUserName, ancestor=ndb.Key(PostMessage, 'base-data'))
        validate = qry.get()
        if validate is None:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Posting ID/Username mismatch")

        if BadFlag != True:
            qry = PostMessage.query(PostMessage.idnumber == PostID, ancestor=ndb.Key(PostMessage, 'base-data'))
            NewPostingObject = qry.get()
            if NewPostingObject is None:
                self.response.status = 404
                self.response.write("ERROR: No posting found with that ID")
                return
            NewPostingObject.contents = NewPosting
            NewPostingObject.put()
            out = NewPostingObject.to_dict()
            self.response.write(json.dumps(out))

    def delete(self, **param):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.out.write(self.dump_csv())
        if 'application/json' not in self.request.accept:
            self.response.status = 406
            self.response.status_message = "Not acceptable, API only supports JSON."
            return

        action = self.request.get('action')

        BadFlag = False
        NewUserName = self.request.get('username', default_value=None)
        NewPassword = self.request.get('password', default_value=None)
        NewUserID = self.request.get('userid', default_value=None)
        PostID = self.request.get('postid', default_value=None)
        

        

        if NewUserName is None or not NewUserName:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, username is required")

        if NewPassword is None or not NewPassword:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, password is required")

        # if NewUserID is None or not NewUserID:
        #     BadFlag = True
        #     self.response.status = 400
        #     self.response.write("ERROR: Bad Request, user ID is required")
        # else:
        #     try:
        #         NewUserID = int(NewUserID)
        #     except ValueError:
        #         self.response.status = 400
        #         self.response.write("ERROR: userid must be an integer!")
        #         BadFlag = True
        #         return

        if PostID is None or not PostID:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Bad Request, posting ID is required")
        else:
            try:
                PostID = int(PostID)
            except ValueError:
                self.response.status = 400
                self.response.write("ERROR: Post ID must be an integer!")
                return

        qry = User.query(User.username == NewUserName, User.password == NewPassword, ancestor=ndb.Key(User, 'base-data'))
        validate = qry.get()
        if validate is None:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: User ID/Password mismatch")

        qry = PostMessage.query(PostMessage.idnumber == PostID, PostMessage.username == NewUserName, ancestor=ndb.Key(PostMessage, 'base-data'))
        validate = qry.get()
        if validate is None:
            BadFlag = True
            self.response.status = 400
            self.response.write("ERROR: Posting ID/Username mismatch")

        if BadFlag != True:
            qry = PostMessage.query(PostMessage.idnumber == PostID, ancestor=ndb.Key(PostMessage, 'base-data'))
            NewPostingObject = qry.get()
            if NewPostingObject is None:
                self.response.status = 404
                self.response.write("ERROR: No posting found with that ID")
                return
            NewPostingObject.key.delete()
            out = "Posting ID# %i deleted" % PostID
            self.response.write(out)
    

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

app.router.add(webapp2.Route(r'/posting/<id:[0-9]+><:/?>', MainHandler))
