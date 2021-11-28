from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from starlette.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

# uvicorn main:app --reload
# instans of the fast api
app: FastAPI = FastAPI()


# post model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# make connection to the database
# try  to connect to thr database untill its got connected
# to the databse
while True:
    try:
        connection = psycopg2.connect(
            host='localhost',
            database='MuktadirDB',
            user='postgres',
            password='123456',
            cursor_factory=RealDictCursor
        )
        cursor = connection.cursor()
        print('-> Database connected successfully! <-')
        break
    except Exception as error:
        time.sleep(2)
        print('-> Failed to connect to the database <-')
        print('-> Error: ', error)


# return all posts from POSTS table
@app.get('/get-all-posts')
def get_all_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts_list = cursor.fetchall()
    return posts_list

# create and return a row from table
@app.post('/create-post', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
    """INSERT INTO posts (title, content, published) 
    VALUES (%s, %s, %s) RETURNING *""",
    (post.title, post.content, post.published))

    created_post = cursor.fetchone()
    connection.commit()

    return created_post

# return a post by id
@app.get('/get-post-by-id/{post_id}')
def get_post_by_id(post_id: int):
    cursor.execute(
        """SELECT * FROM posts WHERE id = %s""",
        ([str(post_id)])
    )
    fetched_post = cursor.fetchone()

    if not fetched_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'the post with id = {post_id} is not found'
        )
    
    return fetched_post    

# delete a post by id
@app.delete('/delete-post/{post_id}')
def delete_post(post_id: int):
    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""",
        (str(post_id)),
    )

    deleted_post = cursor.fetchone()

    connection.commit()

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id={post_id} not found',
        )
    
    return {'message': 'Post deleted successfully'}

#Update a post by id
@app.put('/update-post/{post_id}')
def update_post(post_id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(post_id)),
    )

    updated_post = cursor.fetchone()

    connection.commit()

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id={post_id} not found',
        )
    
    return updated_post    
