create table PLAYER (
    idP int primary key auto_increment,
    pseudo varchar(50),
    passwd varchar(50),
    elo int default 1000
);

create table GAME (
    idG int primary key auto_increment,
    dateG date,
    duration float,
    stateG ENUM('in progress', 'finished')
);

create table PLAY (
    idP int,
    idG int,
    won int,
    color ENUM('WHITE','BLACK'),
    primary key(idP, idG),
    foreign key(idP) references PLAYER(idP),
    foreign key(idG) references GAME(idG)
);