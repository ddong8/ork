CREATE TABLE public.city
(
    uuid VARCHAR(63) PRIMARY KEY,
    id VARCHAR(63) NOT NULL,
    name varchar(255) NOT NULL
);
CREATE TABLE public.line
(
    uuid VARCHAR(63) PRIMARY KEY,
    id int NOT NULL,
    name varchar(255) NOT NULL,
    city_id varchar(63) NOT NULL
);