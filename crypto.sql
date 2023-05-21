CREATE DATABASE crypto;

CREATE Table blockchain (
    number varchar(10),
    hash VARCHAR(64),
    previous VARCHAR(64),
    data VARCHAR(100),
    nounce VARCHAR(15)
);


create table user (
    name varchar(30),
    username VARCHAR(30), 
    email varchar(50), 
    password varchar(100)
    );