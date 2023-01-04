# pip install Flask Flask-SQLAlchemy flask-wtf WTForms-SQLAlchemy flask-login
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from models import Analytics, Bookmarks, Categories, Comments, Followers, History, Notifications, Posts, Reports, Types, \
    db, News, Users
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, login_required, logout_user, LoginManager, current_user

from webforms import ByCategoryForm, CatgoryForm, DraftForm, EditForm, LoginForm, NoteForm, OnlineStatusForm, ReplyForm, \
    ReportForm, Search, SignUpForm, WriteNewsForm, WritePost

from flask_statistics import Statistics
import pandas as pd
import requests
from itables import show

newvar = 2
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'any secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'my_db.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_DOMAIN'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
# to speech conversion
from gtts import gTTS


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))


with app.app_context():
    db.create_all()
    # types = [Types(name = "news"), Types(name = "comment"), Types(name = "reply")]
    # for type in types:
    #     db.session.add(type)
    # db.session.commit()

csrf = CSRFProtect()
csrf.init_app(app)

statistic = Statistics(app, db, Analytics)


@app.route("/")
def hello_world():
    signup = SignUpForm()
    signin = LoginForm()
    search_form = Search()
    news = News.query.order_by().all()

    response_data = {}
    articles = {}  # all normal news from scraper
    path = os.path.basename("static") + "/scraper/92_News.csv"
    articles = pd.read_csv(path, encoding="utf-8", nrows=newvar)
    print(type(articles))
    # this code is used to get top news from the scrapper
    articles1 = {}  # trendingnews
    # thus is pandas dataframe and nrows gets top six
    articles1 = pd.read_csv(path, encoding="utf-8", nrows=6)
    # articles is dictionry and article is value .. loop itterrows
    summary = []
    data_conv = []  # list/array for save all the translaion of summaries
    for key, article in articles.iterrows():  # articles are dictionary ,2 things key(index,string) and value
        payload = {"inputs": article['News_Content']}
        API_URL = "https://api-inference.huggingface.co/models/google/pegasus-large"
        headers = {"Authorization": f"Bearer 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"}
        response = requests.post(API_URL, headers=headers, json=payload)
        data = response.json()
        summary.append(data[0]['summary_text'])  #
        tspeech(data[0]['summary_text'], key)  # data kia hai or 2nd key is index

        API_URL1 = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ur"
        payload1 = {"inputs": data[0]['summary_text']}
        response1 = requests.post(API_URL1, headers=headers, json=payload1)
        data1 = response1.json()
        data_conv.append(data1[0]['translation_text'])

    print(summary)
    print("aisha")
    # show(summary)

    if not current_user.is_anonymous:
        if current_user.username == 'admin':
            return redirect('/Admindashboard')
    popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()
    return render_template("index.html", signup=signup, signin=signin, news=news, articles=articles,
                           articles1=articles1, popular_news=popular_news,
                           summary=summary, data_conv=data_conv, search_form=search_form)


def tspeechadmin(mytext, key):
    # The text that you want to convert to audio

    # Language in which you want to convert
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    url = "static/admin/" + str(key) + ".mp3"
    myobj.save(url)

    # Playing the converted file
    # os.system("mpg321 welcome.mp3")
    return


def tspeech(mytext, key):
    # The text that you want to convert to audio

    # Language in which you want to convert
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    url = "static/" + str(key) + ".mp3"
    myobj.save(url)

    # Playing the converted file
    # os.system("mpg321 welcome.mp3")
    return


# @app.route("/")
# def hello_world1():
#     signup = SignUpForm()
#     signin = LoginForm()
#     news = News.query.order_by().all()

#     response_data = {}
#     articles1 = {}
#     path = os.path.basename("static") + "/scraper/Trending.csv"
#     articles1 = pd.read_csv(path, nrows=6)
#     print(type(articles1))

#     if not current_user.is_anonymous:
#         if current_user.username == 'admin':
#             return redirect('/Admindashboard')
#     popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()

#     return render_template("index.html", signup=signup, signin=signin, news=news, articles1=articles1, popular_news = popular_news)


@app.route('/statistics')
def statistics():
    return redirect('/statistics/')


@app.route("/logout/<userid>")
@login_required
def logout(userid):
    user = load_user(userid)
    user.status = False
    db.session.commit()
    message = f"{current_user.username}, You are Logged out!"
    notification = Notifications(notifier_id=current_user.id, activity=message)
    logout_user()
    db.session.add(notification)
    db.session.commit()
    users = Users.query.order_by().all()
    for user in users:
        print(user.is_active)
        print(current_user.is_active)
    signin = LoginForm()
    signup = SignUpForm()
    return redirect('/')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    signup = SignUpForm()
    signin = LoginForm()
    if signup.validate_on_submit():
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        profile = request.files['profile']
        image_data = profile.read()
        mimetype = profile.mimetype
        status = False
        # role = 'admin'
        user = Users(username=username, email=email, role=role, password=password, profile_pic=image_data,
                     mimetype=mimetype, status=status)
        db.session.add(user)
        db.session.commit()

        message = f"{username}, You are Welcome to Telenews!"
        user = Users.query.filter_by(username=username, password=password).first()
        if user:
            notification = Notifications(notifier_id=user.id, activity=message)
            db.session.add(notification)
            db.session.commit()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    signin = LoginForm()
    signup = SignUpForm()
    print(request.form['submit'])
    if signin.validate_on_submit():
        user = Users.query.filter_by(username=request.form['username']).first()
        print(user)
        if user:
            password = request.form['password']
            if user.verify_password(password):
                login_user(user)
                user.status = True
                db.session.commit()
                session['username'] = user.username
                if current_user.role == 'admin':
                    notification = Notifications(notifier_id=current_user.id,
                                                 activity=f"{current_user.username} logged in!")
                    db.session.add(notification)
                    db.session.commit()
                    return render_template('AdminDashboard.html')
                elif current_user.role == 'journalist':
                    notification = Notifications(notifier_id=current_user.id,
                                                 activity=f"{current_user.username} logged in!")
                    db.session.add(notification)
                    db.session.commit()
                    return redirect('/generalistNews')
                else:
                    notification = Notifications(notifier_id=current_user.id,
                                                 activity=f"{current_user.username} logged in!")
                    db.session.add(notification)
                    db.session.commit()
                    return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')


@app.route('/<int:id>')
def get_profile(id):
    user = Users.query.filter_by(id=id).first()
    if not user:
        return 'Img Not Found!', 404

    return Response(user.profile_pic, mimetype=user.mimetype)


@app.route('/delete_acctount/<user_id>')
@login_required
def delete_account(user_id):
    user = Users.query.get(user_id)
    message = f"You have deleted user: {user.username}"
    notification = Notifications(notifier_id=current_user.id, activity=message)
    db.session.add(notification)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    if current_user.role == 'admin':
        return redirect('/Accountdetails')
    else:
        return redirect('/')


@app.route('/updateprofile/<user_id>', methods=['GET', 'POST'])
def update_profile(user_id):
    form = EditForm()
    if request.method == 'GET':
        print("UPDATE")
        user = Users.query.get(user_id)
        old_password = request.form['old_password']
        if user.password == old_password:
            username = request.form['username']
            email = request.form['email']

            email_exists = Users.query.filter(Users.email == email, Users.id != user.id).first()
            if email_exists:
                flash('email already registered')
                return redirect(f'/editprofile/{user_id}')
            else:
                password = request.form['confirm_passowrd']
                profile = request.files['profile']
                print('profile')
                if profile:
                    image_data = profile.read()
                    mimetype = profile.mimetype
                    user.profile_pic = image_data
                    user.mimetype = mimetype
                status = False
                user.username = username
                user.email = email
                user.password = password
                user.status = status
                db.session.update(user)
                db.session.commit()
                return redirect('/')
        else:
            flash('Old password is not correct')
            return redirect(f'/editprofile/{user_id}')
    else:
        return redirect(f'/editprofile/{user_id}')
        # message = f"{username}, You are Welcome to Telenews!"
        # user = Users.query.filter_by(username = username, password = password).first()


@app.route('/onlinestatus', methods=['GET', 'POST'])
@login_required
def get_online_users():
    status_form = OnlineStatusForm()
    users = Users.query.order_by().all()
    if status_form.validate_on_submit():
        role = request.form['role']
        if role == 'any':
            users = Users.query.order_by().all()
        else:
            users = Users.query.filter_by(role=role).all()

        if status_form.search.data:
            searched = request.form['search']
            if role == 'any':
                users = Users.query.filter(Users.username.like('%' + searched + '%')).all()
            else:
                users = Users.query.filter(Users.username.like('%' + searched + '%'), Users.role == role).all()

    return render_template("OnlineStatus.html", users=users, status_form=status_form)


@app.route('/bookmark/<news_id>')
@login_required
def bookmark(news_id):
    news = News.query.get(int(news_id))
    if news:
        if not Bookmarks.query.filter_by(news_id=news_id, bookmarker_id=current_user.id).first():
            bookmark = Bookmarks(bookmarker_id=current_user.id, news_id=news_id)
            news = News.query.get(news_id)
            message = f"You bookmarked news: {news.title}"
            link = "go to bookmarks!"
            notification = Notifications(notifier_id=current_user.id, activity=message, link=link)
            db.session.add(bookmark)
            db.session.add(notification)

            db.session.commit()
            # flash('news bookmarked!')
        else:
            # flash('already bookmarked!')
            pass
    else:
        pass
        # flash('news not found!')
    return redirect('/generalistNews')


@app.route('/unbookmark/<bookmark_id>')
@login_required
def unbookmark(bookmark_id):
    bookmark = Bookmarks.query.get(bookmark_id)
    message = f"You Unbookmarked news: {bookmark.news.title}"
    notification = Notifications(notifier_id=current_user.id, activity=message)
    db.session.delete(bookmark)
    db.session.add(notification)
    db.session.commit()
    return redirect('/list')


@app.route('/update_history/<news_id>/<url>')
def method_name(news_id, url):
    history = History.query.filter_by(news_id=news_id).first()
    if history:
        db.session.delete(history)
        db.session.add(history)
    else:
        db.session.add(history)
    db.session.commit()
    return redirect(f'/{url}')


@app.route("/list")
@login_required
def list_news():
    users = Users.query.filter(Users.role == 'journalist', Users.id != current_user.id).all()
    followers = Followers.query.filter_by(follow_by=current_user.id).all()
    follow_users = []
    following_users = []
    if followers:
        for follow in followers:
            following_users.append(Users.query.filter_by(id=follow.follow_to).first())
        for user in users:
            if user not in following_users:
                follow_users.append(user)
        print(following_users)
    else:
        follow_users = users
    bookmarks = Bookmarks.query.order_by().all()
    history = History.query.order_by(History.id.desc()).all()
    history_list = []
    for data in history:
        history_list.append([News.query.filter_by(id=data.news_id).first(), data])
    return render_template("List.html", bookmarks=bookmarks, history_list=history_list, follow=follow_users,
                           following=following_users)


@app.route('/addcategory', methods=['GET', 'POST'])
def add_category():
    category_form = CatgoryForm()
    if category_form.validate_on_submit():
        name = request.form['category']
        if not Categories.query.filter_by(name=name).first():
            category = Categories(name=name)
            db.session.add(category)
            message = f'{current_user.username}! You added new {name} Category'
            notification = Notifications(notifier_id=current_user.id, activity=message)
            db.session.add(notification)
            db.session.commit()
    category_form.category.data = None
    categories = Categories.query.order_by().all()
    return render_template('AdminAddCategories.html', categories=categories, category_form=category_form)


@app.route('/deleteCategory/<id>')
def delete_category(id):
    category = Categories.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return redirect('/addcategory')


@app.route("/Accountdetails")
@login_required
def Account_details():
    signup = SignUpForm()
    signin = LoginForm()
    users = Users.query.order_by(Users.id.desc()).all()
    return render_template("AccountDetails.html", users=users, signup=signup, signin=signin)


@app.route("/Admindashboard")
@login_required
def Admin_dashboard():
    return render_template("AdminDashboard.html")


@app.route("/Adminnotification")
@login_required
def Admin_notification():
    notifications = Notifications.query.filter_by(notifier_id=current_user.id).all()
    notifications.reverse()
    return render_template("AdminNotification.html", notifications=notifications)


@app.route("/AdminarticleDetails")
@login_required
def Admin_article_details():
    note_form = NoteForm()
    news = News.query.filter_by(published=True).order_by(News.id.desc()).all()
    return render_template("AdminArticleDetails.html", news=news, note_form=note_form)


@app.route('/writenote/<id>/<current_url>', methods=['GET', 'POST'])
def writenote(id, current_url):
    note_form = NoteForm()
    if note_form.validate_on_submit():
        note = request.form['note']
        message = f'note: {note}'
        send_note_notifi = Notifications(notifier_id=id, activity=message)
        user = Users.query.filter_by(id=id).first()
        message = f'You sent a note to {user.username}'
        notification = Notifications(notifier_id=current_user.id, activity=message)
        db.session.add(send_note_notifi)
        db.session.add(notification)
        db.session.commit()
        print(current_url)
    return redirect(f'/{current_url}')


@app.route("/articleView")
@login_required
def article_view():
    return render_template("ArticleView.html")


@app.route("/editprofile/<user_id>", methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    edit_form = EditForm()
    user = Users.query.get(user_id)
    if edit_form.validate_on_submit():
        if edit_form.delete.data:
            message = f"You have deleted user: {user.username}"
            notification = Notifications(notifier_id=current_user.id, activity=message)
            db.session.add(notification)
            db.session.commit()
            db.session.delete(user)
            db.session.commit()
            if current_user.role == 'admin':
                return redirect('/Accountdetails')
            else:
                return redirect('/')
        elif edit_form.update.data:
            old_password = request.form['old_password']
            old_password = user.verify_password(old_password)

            if old_password or current_user.role == 'admin':
                username = request.form['username']
                email = request.form['email']

                email_exists = Users.query.filter(Users.email == email, Users.id != user.id).first()
                if email_exists:
                    flash('email already registered')
                    return redirect(f'/editprofile/{user_id}')
                else:
                    profile = request.files['profile']
                    if profile:
                        image_data = profile.read()
                        mimetype = profile.mimetype
                        user.profile_pic = image_data
                        user.mimetype = mimetype
                    user.username = username
                    user.email = email
                    if edit_form.confirm_password.data:
                        password = request.form['confirm_password']
                        user.password = password
                        status = False
                        user.status = status
                        db.session.commit()
                        if not current_user.role == 'admin':
                            logout_user()

                    db.session.commit()
                    if current_user.role == 'admin':
                        return redirect('/Accountdetails')
                    else:
                        return redirect('/')
            else:
                flash('Old password is not correct')
                return redirect(f'/editprofile/{user_id}')
    return render_template("EditProfile.html", edit_form=edit_form, user=user)


@app.route('/follow/<user_id>')
@login_required
def follow(user_id):
    user = Users.query.filter_by(id=user_id).first()
    follow_to = user.id
    follow_by = current_user.id
    follow = Followers(follow_by=follow_by, follow_to=follow_to)
    message = f'You start following {user.username}'
    notification = Notifications(notifier_id=current_user.id, activity=message)
    db.session.add(follow)
    db.session.add(notification)
    db.session.commit()
    return redirect("/followerlist")


@app.route('/unfollow/<user_id>')
@login_required
def unfollow(user_id):
    follow = Followers.query.filter_by(follow_by=current_user.id, follow_to=user_id).first()
    db.session.delete(follow)
    db.session.commit()
    return redirect('/followerlist')


@app.route("/followerlist")
@login_required
def follower_list():
    users = Users.query.filter(Users.role == 'journalist', Users.id != current_user.id).all()
    followers = Followers.query.filter_by(follow_by=current_user.id).all()
    follow_users = []
    following_users = []
    if followers:
        for follow in followers:
            following_users.append(Users.query.filter_by(id=follow.follow_to).first())
        for user in users:
            if user not in following_users:
                follow_users.append(user)
        print(following_users)
    else:
        follow_users = users
    print(follow_users, following_users)
    return render_template("FollowerList.html", follow=follow_users, following=following_users)


@app.route("/newsSummary")
@login_required
def news_summary():
    signup = SignUpForm()
    signin = LoginForm()
    category_form = ByCategoryForm()
    news = News.query.order_by().all()

    response_data = {}
    articles = {}  # all normal news from scraper
    path = os.path.basename("static") + "/scraper/92_News.csv"
    articles = pd.read_csv(path, encoding="utf-8", nrows=newvar)
    print(type(articles))
    # this code is used to get top news from the scrapper
    articles1 = {}  # trendingnews
    # thus is pandas dataframe and nrows gets top six
    articles1 = pd.read_csv(path, encoding="utf-8", nrows=6)
    # articles is dictionry and article is value .. loop itterrows
    summary = []
    data_conv = []  # list/array for save all the translaion of summaries
    for key, article in articles.iterrows():  # articles are dictionary ,2 things key(index,string) and value
        payload = {"inputs": article['News_Content']}
        API_URL = "https://api-inference.huggingface.co/models/google/pegasus-large"
        headers = {"Authorization": f"Bearer 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"}
        response = requests.post(API_URL, headers=headers, json=payload)
        data = response.json()
        summary.append(data[0]['summary_text'])  #
        tspeech(data[0]['summary_text'], key)  # data kia hai or 2nd key is index

        API_URL1 = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ur"
        payload1 = {"inputs": data[0]['summary_text']}
        response1 = requests.post(API_URL1, headers=headers, json=payload1)
        data1 = response1.json()
        data_conv.append(data1[0]['translation_text'])

    print(summary)
    print("aisha")
    # show(summary)
    popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()
    if not current_user.is_anonymous:
        if current_user.username == 'admin':
            return redirect('/Admindashboard')

    # popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()
    categories = Categories.query.order_by()
    return render_template("NewsSummary.html", signup=signup, signin=signin, news=news, articles=articles,
                           articles1=articles1, popular_news=popular_news, categories=categories,
                           summary=summary, data_conv=data_conv, category_form=category_form)


@app.route("/generalistNews", methods=['GET', 'POST'])
@login_required
def generalist_news():
    report_form = ReportForm()
    reply_form = ReplyForm()
    category_form = ByCategoryForm()
    search_form = Search()
    new_news = []
    users = []
    if search_form.validate_on_submit():
        searched = request.form['search']

        # add ur code here.
        #  

        news = News.query.filter((News.title.like('%' + searched + '%')), News.published == True)

    else:
        follows = Followers.query.filter_by(follow_by=current_user.id).all()

        # users = []
        for follow in follows:
            users.append(Users.query.filter_by(id=follow.follow_to).first())

        # new_news = []
        for user in users:
            print("user", user)
            sql = """select n.id, n.title, n.post_id, p.description, p.poster_id, n.views, p.created_at from news n inner join posts p on n.post_id = p.id """
            n_news_list = db.engine.execute(sql)

            # news_list = News.query.filter_by(published=True).order_by(News.id.desc()).all()
            if n_news_list:
                for new in n_news_list:
                    if new.poster_id == user.id:
                        new_news.append(
                            {
                                'id': new.id,
                                'poster_id': new.poster_id,
                                'title': new.title,
                                'post_id': new.post_id,
                                'description': new.description,
                                'views': new.views,
                                'created_at': new.created_at,
                            }

                        )

        # print("new_news list", new_news)

        news = []
        for user in users:
            news_list = News.query.filter_by(published=True).order_by(News.id.desc()).all()
            if news_list:
                for new in news_list:
                    if new.article.poster.id == user.id:
                        news.append(new)

        # print("news list", news)

    comments = Comments.query.filter_by(is_reply=False).order_by(Comments.id.desc()).all()
    # replys = []
    # for comment in comments:
    #     reply = Comments.query.filter_by(news_id = comment.id, is_reply = True).all()
    #     for data in reply:
    #         replys.append(data)
    summary = []
    data_conv = []
    print(type(news))

    summary_list = []
    translate = []
    for idx, word in enumerate(new_news):  # loop nd list
        payload = {"inputs": word['description']}
        API_URL = "https://api-inference.huggingface.co/models/google/pegasus-large"
        headers = {"Authorization": f"Bearer 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"}  # for authorization key
        response = requests.post(API_URL, headers=headers, json=payload)
        data = response.json()
        summary_list.append(data[0]['summary_text'])

        API_URL1 = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ur"
        payload1 = {"inputs": data[0]['summary_text']}
        response1 = requests.post(API_URL1, headers=headers, json=payload1)
        data_conv = response1.json()
        translate.append(data_conv[0]['translation_text'])

        # print(data[0]['summary_text'])
        tspeechadmin(data[0]['summary_text'], idx)

    # for idx, word in enumerate(news):
    #     payload = {"inputs": word.title}
    #     API_URL = "https://api-inference.huggingface.co/models/google/pegasus-large"
    #     headers = {"Authorization": f"Bearer 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"}
    #     response = requests.post(API_URL, headers=headers, json=payload)
    #     data = response.json()
    #     summary.append(data[0]['summary_text'])
    #     print(summary)
    #     print(word.title)

    # show(summary)
    # print(translate)
    replys = Comments.query.filter_by(is_reply=True).all()
    print(replys)
    popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()
    categories = Categories.query.order_by()
    return render_template("GeneralistNews.html", news_list=new_news, comments=comments, report_form=report_form,
                           search_form=search_form, popular_news=popular_news, reply_form=reply_form, replys=replys,
                           categories=categories, category_form=category_form, summary=summary_list,
                           translate=translate)


@app.route('/newsbycategory', methods=['GET', 'POST'])
@login_required
def news_by_category():
    report_form = ReportForm()
    reply_form = ReplyForm()
    search_form = Search()
    category_form = ByCategoryForm()
    if search_form.validate_on_submit():
        search_string = request.form['search']
        print("search_string: ", search_string)


    if category_form.validate_on_submit():
        name = request.form['submit']
        if name != 'search':
            category = Categories.query.filter_by(name=name).first()
            news = News.query.filter_by(published=True, category_id=category.id).order_by(News.id.desc()).all()
        else:
            news = News.query.filter(News.title.like("%"+search_string+"%")).all()
    comments = Comments.query.order_by(Comments.id.desc()).all()
    replys = []
    for comment in comments:
        reply = Comments.query.filter_by(news_id=comment.id).all()
        for data in reply:
            replys.append(data)
    print(replys)
    popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()
    categories = Categories.query.order_by()
    return render_template("GeneralistNewsUpdated.html", news_list=news, comments=comments, report_form=report_form,
                           search_form=search_form, popular_news=popular_news, reply_form=reply_form, replys=replys,
                           categories=categories, category_form=category_form, summary='', translate='')


@app.route("/add_comment/<news_id>", methods=['GET', 'POST'])
@login_required
def add_comment(news_id):
    type = Types.query.filter_by(name="comment").first()
    description = request.form['comment_area']
    post = Posts(poster_id=current_user.id, type_id=type.id, description=description)
    db.session.add(post)
    db.session.commit()

    post = Posts.query.filter_by(poster_id=current_user.id, type_id=type.id).all()
    post = post[len(post) - 1]
    news = News.query.filter_by(id=news_id).first()
    comment = Comments(post_id=post.id, news_id=news.id, is_reply=False)

    message = f"{current_user.username}, you just commented on {news.article.poster.username}'s news"
    notification = Notifications(notifier_id=current_user.id, activity=message)

    db.session.add(comment)
    db.session.add(notification)

    db.session.commit()
    return redirect('/generalistNews')


@app.route('/delete_comment/<post_id>')
@login_required
def delete_comment(post_id):
    post = Posts.query.filter_by(id=post_id).first()
    comment = Comments.query.filter_by(comment_post=post).first()
    message = f'Your comment on post {comment.commented_news.title} deleted!'
    notification = Notifications(notifier_id=post.poster.id, activity=message)

    db.session.delete(post)
    db.session.add(notification)
    db.session.commit()
    if current_user.role == 'admin':
        return redirect('/reportedComments')
    return redirect('/generalistNews')


@app.route('/delete_news/<post_id>')
@login_required
def delete_news(post_id):
    print(post_id)
    post = Posts.query.filter_by(id=post_id).first()
    news = News.query.filter_by(article=post).first()
    message = f'Your news {news.title} deleted!'
    print(news.title)
    notifications = Notifications(notifier_id=post.poster.id, activity=message)

    db.session.delete(post)
    db.session.add(notifications)
    db.session.commit()
    if current_user.role == 'admin':
        return redirect('/Adminnotification')
    else:
        return redirect('/generalistNews')


@app.route('/report_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def report_comment(comment_id):
    report_form = ReportForm()
    print(comment_id)
    if report_form.validate_on_submit():
        reason = request.form['reason']
        comment = Comments.query.filter_by(id=comment_id).first()
        report = Reports(reporter_id=current_user.id, post_id=comment.comment_post.id, reason=reason)
        message = f'Your comment on post {comment.commented_news.title} is reported!'
        notification = Notifications(notifier_id=comment.comment_post.poster.id, activity=message)

        db.session.add(report)
        db.session.add(notification)
        db.session.commit()
    return redirect(url_for('generalist_news'))


@app.route('/reportnews/<news_id>', methods=['GET', 'POST'])
@login_required
def report_news(news_id):
    report_form = ReportForm()
    if report_form.validate_on_submit():
        news = News.query.filter_by(id=news_id).first()
        report = Reports.query.filter_by(reporter_id=current_user.id, post_id=news.article.id).first()
        if not report:
            report = Reports(reporter_id=current_user.id, post_id=news.article.id, reason=request.form['reason'])
            message = f'Your news {news.title} is reported!'
            notification = Notifications(notifier_id=news.article.poster.id, activity=message)
            db.session.add(report)
        else:
            message = f'You have already reported {news.title} news!'
            notification = Notifications(notifier_id=current_user.id, activity=message)

        db.session.add(notification)
        db.session.commit()
    return redirect(f'/summaryview/{news.id}')


@app.route("/news/delete/<int:news_id>/", methods=["GET"])
@login_required
def delete_post(news_id):
    news = News.query.get(news_id)
    post = news.article
    message = f'Your news article is deleted'
    notification = Notifications(notifier_id=current_user.id, activity=message)
    db.session.delete(post)
    db.session.add(notification)
    db.session.commit()
    # flash("Your comment has been added. Welcome!")
    return redirect(url_for('news_summary'))


@app.route("/notifications")
@login_required
def full_notifications():
    users = Users.query.filter(Users.role == 'journalist', Users.id != current_user.id).all()
    followers = Followers.query.filter_by(follow_by=current_user.id).all()
    follow_users = []
    following_users = []
    if followers:
        for follow in followers:
            following_users.append(Users.query.filter_by(id=follow.follow_to).first())
        for user in users:
            if user not in following_users:
                follow_users.append(user)
    else:
        follow_users = users
    notifications = Notifications.query.filter_by(notifier_id=current_user.id).all()
    notifications.reverse()
    return render_template("Notifications.html", notifications=notifications, follow=follow_users)


@app.route("/reportedComments")
@login_required
def reported_comments():
    note_form = NoteForm()
    reports = Reports.query.order_by(Reports.id.desc()).all()
    reported_comments = []
    for report in reports:
        if report.post.type.name == 'comment':
            comment = Comments.query.filter_by(post_id=report.post_id).first()
            news = News.query.filter_by(id=comment.news_id).first()
            reported_comments.append([report, news])
    return render_template("ReportedComments.html", note_form=note_form, comments=reported_comments, edit=False)


@app.route("/reportednews")
@login_required
def reported_news():
    note_form = NoteForm()
    reports = Reports.query.order_by(Reports.id.desc()).all()
    reported_news = []
    if reports:
        for report in reports:
            if report.post.type.name == 'news':
                news = News.query.filter_by(post_id=report.post.id).first()
                reported_news.append([news, report.reason])
    print(reported_news)
    return render_template("ReportedNews.html", news=reported_news, note_form=note_form)


@app.route("/reportedcommmetsAdmin")
@login_required
def reported_commnets_admin():
    comments = Comments.query.filter_by(report=1)
    return render_template("ReportedCommentsAdmin.html", comments=comments)


@app.route("/comment/report/<int:comment_id>")
@login_required
def add_report_comment(comment_id):
    comment = Comments.query.get(comment_id)
    comment.report = 1
    db.session.commit()
    return redirect(request.referrer)


@app.route('/news/<int:id>')
@login_required
def get_news_img(id):
    news = News.query.filter_by(id=id).first()
    if not news:
        return 'Img Not Found!', 404
    return Response(news.image, mimetype=news.mimetype)


@app.route("/summaryview/<int:news_id>")
@login_required
def summary_view(news_id):
    report_form = ReportForm()
    reply_form = ReplyForm()
    news = News.query.get(news_id)
    news.views += 1
    db.session.add(news)
    db.session.commit()
    comments = Comments.query.filter_by(news_id=news.id, is_reply=False).all()
    # reply_list = Comments.query.filter_by(is_reply = True).all()
    replys = []
    for comment in comments:
        reply = Comments.query.filter_by(news_id=comment.id, is_reply=True).all()
        for data in reply:
            replys.append(data)
    popular_news = News.query.filter(News.published == True).order_by(News.views.desc()).all()

    history = History.query.filter_by(news_id=news_id).first()
    print(history)
    if history:
        db.session.delete(history)
        history = History(news_id=news_id)
        db.session.add(history)
    else:
        history = History(news_id=news_id)
        db.session.add(history)
    db.session.commit()

    return render_template("SummaryView.html", news=news, comments=comments, popular_news=popular_news,
                           report_form=report_form, reply_form=reply_form, replys=replys)


@app.route('/reply/<comment_id>/<news_id>', methods=['GET', 'POST'])
def reply(comment_id, news_id):
    form = ReplyForm()
    if form.validate_on_submit():
        type = Types.query.filter_by(name="reply").first()
        description = request.form['description']
        post = Posts(poster_id=current_user.id, type_id=type.id, description=description)
        db.session.add(post)
        db.session.commit()

        post = Posts.query.filter_by(poster_id=current_user.id, type_id=type.id).all()
        post = post[len(post) - 1]
        comment = Comments.query.filter_by(id=comment_id).first()
        # news_id is basically post id. 
        reply = Comments(post_id=post.id, news_id=comment.id, is_reply=True)
        news = News.query.filter_by(id=news_id).first()
        message = f"{current_user.username}, you just replyed on {news.article.poster.username}'s news comment"
        notification = Notifications(notifier_id=current_user.id, activity=message)

        db.session.add(reply)
        db.session.add(notification)

        db.session.commit()

    return redirect(f'/summaryview/{news_id}')


@app.route("/writenews", methods=['GET', 'POST'])
@login_required
def write_news():
    form = WriteNewsForm()
    categories = Categories.query.order_by().all()
    form.category.choices = [category.name for category in categories]
    if form.validate_on_submit():
        description = request.form['description']
        type = Types.query.filter_by(name="news").first()
        type_id = type.id

        image = request.files['image']
        image_data = image.read()
        mimetype = image.mimetype
        title = request.form['title']

        post = Posts(poster_id=current_user.id, type_id=type_id, description=description)
        db.session.add(post)
        db.session.commit()

        post = Posts.query.order_by().all()
        last_post = post[len(post) - 1]
        category = request.form['category']
        category = Categories.query.filter_by(name=category).first()
        if 'publish' in request.form.keys():
            followers = Followers.query.filter_by(follow_to=current_user.id).all()
            message = f'{current_user.username} is published {title} news!'
            for follow in followers:
                notification = Notifications(notifier_id=follow.follow_by, activity=message)
                db.session.add(notification)
            news = News(post_id=last_post.id, title=title, category_id=category.id, image=image_data, mimetype=mimetype,
                        views=0, published=True)
            message = f"Your News {title} is Successfully Published"

        elif 'draft' in request.form.keys():
            news = News(post_id=last_post.id, title=title, category_id=category.id, image=image_data, mimetype=mimetype,
                        views=0, published=False)
            message = f"Your News {title} is Draft"

        notification = Notifications(notifier_id=current_user.id, activity=message)
        flash(message)
        db.session.add(news)
        db.session.add(notification)
        db.session.commit()

        return redirect("/writenews")
    return render_template("WriteNews.html", news_form=form)


@app.route('/writenews/<news_id>', methods=['GET', 'POST'])
def view_draft(news_id):
    print(news_id)
    if request.method == 'GET':
        news = News.query.filter_by(id=news_id).first()
        print(news.id)
        form = WriteNewsForm()
        form.title.data = news.title
        # form.image.mimetype = news.mimetype
        form.description.data = news.article.description
    return render_template('WriteNews.html', news_form=form)


@app.route("/yournewsarticles", methods=['GET', 'POST'])
@login_required
def yournews_articles():
    form = Search()
    draft_form = DraftForm()
    responded_news = []

    following = [following.follow_to for following in Followers.query.filter_by(follow_by=current_user.id).all()]
    follower = [follower.follow_by for follower in Followers.query.filter_by(follow_to=current_user.id).all()]
    followings = []
    followers = []
    searched_following = []
    searched_followers = []
    if form.validate_on_submit():
        searched = request.form['search']
        if following:
            for user in following:
                followings.append(Users.query.filter_by(id=user).first())
            for user in followings:
                if searched in user.username:
                    searched_following.append(user)
            followings = searched_following
        if follower:
            for user in follower:
                followers.append(Users.query.filter_by(id=user).first())
            for user in followers:
                if searched in user.username:
                    searched_followers.append(user)
            followers = searched_followers
    else:
        if following:
            for user in following:
                followings.append(Users.query.filter_by(id=user).first())
        if follower:
            for user in follower:
                followers.append(Users.query.filter_by(id=user).first())
    published_news = News.query.filter_by(published=True).order_by(News.id.desc()).all()
    draft_news = News.query.filter_by(published=False).order_by(News.id.desc()).all()
    comments = Comments.query.filter_by(is_reply=False).order_by().all()
    for comment in comments:
        if comment.commented_news:
            if comment.commented_news not in responded_news:
                responded_news.append(comment.commented_news)
    print(responded_news)
    return render_template("YourNewsArticles.html", published_news=published_news, draft_news=draft_news,
                           responded_news=responded_news, draft_form=draft_form, follower=followers,
                           following=followings, form=form)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
