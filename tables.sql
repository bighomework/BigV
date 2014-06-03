create table Comment(

	c_id INTEGER PRIMARY KEY, 
	c_mid INTEGER, 
	c_uid INTEGER, 
	text TEXT,
	thumbs INTEGER, 
	comments INTEGER
	);

create table Weibo (

	m_id INTEGER PRIMARY KEY, 
	m_omid INTEGER, 
	m_uid INTEGER,
	thumbs INTEGER, 
	forwarding INTEGER, 
	comments INTEGER, 
	pubtime INTEGER, 
	text TEXT
	);
	
create table Figure (

	u_id INTEGER PRIMARY KEY, 
	domainid INTEGER, 
	name TEXT, 
	follow INTEGER, 
	fans INTEGER, 
	weibo INTEGER, 
	establishtime INTEGER
	);


create table Bigv (
	
	uid INTEGER PRIMARY KEY
	);