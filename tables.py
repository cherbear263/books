  CREATE TABLE reviews (
      id SERIAL PRIMARY KEY,
      rating NUMERIC(1,0) NOT NULL,
review TEXT NOT NULL,
      user_id INTEGER REFERENCES users,
book_id INTEGER REFERENCES books
  );

  CREATE TABLE reviews (
      id SERIAL PRIMARY KEY,
      username VARCHAR NOT NULL,
      password VARCHAR NOT NULL

  );