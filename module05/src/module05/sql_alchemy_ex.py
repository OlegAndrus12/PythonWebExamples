from sqlalchemy import create_engine, Column, Integer, String, Numeric, CheckConstraint, DateTime, ForeignKey, or_, and_, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from faker import Faker
from datetime import datetime


fake = Faker()
# orm -> object relational mapping

engine = create_engine("sqlite:///users.db")
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    password = Column(String(120), nullable=False)
    age = Column(Numeric, nullable=False)

    __table_args__ = (
        CheckConstraint("age > 10 AND age < 90", name="check_age_range"),
    )

    videos = relationship("YouTubeVideo", backref="author")

    def __repr__(self):
        return f"#{self.id}: {self.name}"


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    uploaded_on = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return f"<Video #{self.id}: {self.title}>"

Base.metadata.create_all(engine)

# users = [User(name=fake.name(), email=fake.email(), password=fake.password(), age=fake.random_int(min=11, max=89)) for _ in range(100)]
# session.add_all(users)
# session.commit()

# NUM_USERS = 10
# users = []

# for _ in range(NUM_USERS):
#     name = fake.name()
#     email = fake.email()
#     password = fake.password(length=10)
#     age = random.randint(15, 70)
#     user = User(name=name, email=email, password=password, age=age)
#     users.append(user)

# session.add_all(users)
# session.commit()

# # ------------------ Populate Videos ------------------

# NUM_VIDEOS = 30
# videos = []

# for _ in range(NUM_VIDEOS):
#     title = fake.sentence(nb_words=5)
#     views = random.randint(0, 10000)
#     likes = random.randint(0, views)  # likes <= views
#     uploaded_on = datetime.now() - timedelta(days=random.randint(0, 365))
#     user = random.choice(users)
#     video = YouTubeVideo(title=title, views=views, likes=likes, uploaded_on=uploaded_on, author=user)
#     videos.append(video)

# session.add_all(videos)
# session.commit()


# All users
all_users = session.query(User).all()
print(all_users)

# Single user by PK
user1 = session.get(User, 1)

# All videos
all_videos = session.query(YouTubeVideo).all()

# Full object
user = session.query(User).filter(User.name == "Alice").first()
print(user)        # <User object>
print(user.email)  # "alice@example.com"

# Only id
user_id = session.query(User.id).filter(User.name == "Alice").scalar()
print(user_id)     # 5

# Users between 20 and 30
young_users = session.query(User).filter(User.age.between(20, 30)).all()

# Users named either Alice or Bob
users_alice_bob = session.query(User).filter(User.name.in_(["Alice", "Bob"])).all()

# Videos not uploaded by users 1, 2, or 3
videos_exclude_users = session.query(YouTubeVideo).filter(~YouTubeVideo.user_id.in_([1, 2, 3])).all()

# Users with gmail
gmail_users = session.query(User).filter(User.email.like('%@gmail.com')).all()

# Videos with more than 1000 views
popular_videos = session.query(YouTubeVideo).filter(YouTubeVideo.views > 1000).all()

# Videos uploaded after Jan 1, 2025
recent_videos = session.query(YouTubeVideo).filter(YouTubeVideo.uploaded_on >= datetime(2025,1,1)).all()

# Videos with their author
videos_with_authors = session.query(YouTubeVideo, User).join(User).all()
print(videos_with_authors)
# Users with at least one video
users_with_videos = session.query(User).join(YouTubeVideo).all()

# Users with any videos having more than 1000 likes
highly_liked_users = session.query(User).filter(User.videos.any(YouTubeVideo.likes > 1000)).all()

# Videos by users whose name starts with "A"
videos_a_users = session.query(YouTubeVideo).join(User).filter(User.name.like("A%")).all()
# Videos with > 1000 views OR > 500 likes
videos_popular = session.query(YouTubeVideo).filter(
    or_(YouTubeVideo.views > 1000, YouTubeVideo.likes > 500)
).all()

# Videos with > 1000 views AND uploaded in 2025
videos_popular_2025 = session.query(YouTubeVideo).filter(
    and_(
        YouTubeVideo.views > 1000,
        YouTubeVideo.uploaded_on >= datetime(2025, 1, 1)
    )
).all()

# Total views across all videos
total_views = session.query(func.sum(YouTubeVideo.views)).scalar()

# Average likes per video
avg_likes = session.query(func.avg(YouTubeVideo.likes)).scalar()


# Count videos per user
videos_per_user = session.query(
    User.name,
    func.count(YouTubeVideo.id).label("video_count")
).join(YouTubeVideo).group_by(User.id).all()

# Users whose name is longer than 10 characters
long_name_users = session.query(User).filter(func.length(User.name) > 10).all()

# Users with name in lowercase "alice"
alice_user = session.query(User).filter(func.lower(User.name) == "alice").all()

# Videos uploaded today
today_videos = session.query(YouTubeVideo).filter(
    func.date(YouTubeVideo.uploaded_on) == datetime.today().date()
).all()



# Top 5 most-viewed videos
top_videos = session.query(YouTubeVideo).order_by(YouTubeVideo.views.desc()).limit(5).all()

# Users ordered by age
users_by_age = session.query(User).order_by(User.age).all()


total_views = session.query(
    User.name,
    func.sum(YouTubeVideo.views).label("total_views")
).join(YouTubeVideo).group_by(User.id).all()

from sqlalchemy import func

videos_per_user = session.query(
    User.name,
    func.count(YouTubeVideo.id).label("video_count")
).join(YouTubeVideo).group_by(User.id).all()

for name, count in videos_per_user:
    print(name, count)
