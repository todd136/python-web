use blog;

create table t_user(
    fid varchar(50) not null,
    email varchar(50) not null,
    name varchar(50) not null,
    passwd varchar(50) not null,
    admin bool not null,
    image varchar(500) not null,
    create_time real not null,
    unique key idx_email (email),
    key idx_create_time (create_time),
    primary key (fid)
    ) engine innodb default character set utf8;

create table t_blog(
    fid varchar(50) not null,
    userId varchar(50) not null,
    userName varchar(50) not null,
    userImage varchar(500) not null,
    name varchar(50) not null,
    sumary varchar(500) not null,
    content MEDIUMTEXT not null,
    create_time real not null,
    key idx_create_time (create_time),
    primary key (fid)
    ) engine innodb default character set utf8;

create table t_comment(
    fid varchar(50) not null,
    blogId varchar(50) not null,
    userId varchar(50) not null,
    userName varchar(50) not null,
    userImage varchar(500) not null,
    content MEDIUMTEXT not null,
    create_time real not null,
    key idx_create_time (create_time),
    primary key (fid)
) engine innodb default character set utf8;
