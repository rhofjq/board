create table users(user_email varchar(20),user_pw varchar(20),user_nick varchar(10),user_phone varchar(20));
create table board(idx integer primary key, title varchar(100), text varchar(400),writer varchar(20), dt date default current_timestamp,_file BLOB default NULL);
create table board_reply(idx integer primary key,idx2 integer NOT NULL ,text varchar(400),writer varchar(20),dt date default current_timestamp);
