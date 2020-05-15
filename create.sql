---------------------------------- TABLE DELETIONS BELOW ----------------------------------------------------
-- uncomment below if need to drop tables in one go 
drop table pokemon, evolution, ptype, has_type, description, has_move, all_moves, egg_group, part_of_egg_group, ailments, causes_ailment, habitats, lives_in cascade;


---------------------------------- TABLE CREATIONS BELOW ----------------------------------------------------

-- create poke_info table 

create table pokemon (
	poke_id INT NOT NULL, 
	poke_name VARCHAR(30) unique NOT NULL, 
	poke_height NUMERIC(5,1) NOT NULL,
	poke_weight NUMERIC(5,1) NOT NULL,
	poke_catch_rate NUMERIC(4,1) NOT NULL,
	poke_level_rate VARCHAR(30) NOT NULL,
	base_health INT NOT NULL,
	base_attack INT NOT NULL,
	base_defense INT NOT NULL,
	base_special_attack INT NOT NULL,
	base_special_defense INT NOT NULL,
	base_speed INT NOT NULL,
	constraint poke_pk 
	primary key (poke_id)
); 

-- create pokemon evolution recursive relationship entity 

create table evolution(
	poke_id INT references pokemon (poke_id) ON UPDATE CASCADE,
	evolution_id INT references pokemon (poke_id) ON UPDATE CASCADE,
	constraint evolution_pk 
	primary key (poke_id, evolution_id)
);

-- Pokemon Types and Weaknesses 
create table ptype (
	ptype_id INT NOT NULL,
	ptype_name VARCHAR(30) NOT NULL,
	weak_against_normal BOOLEAN NOT NULL, 
	weak_against_fire BOOLEAN NOT NULL, 
	weak_against_water BOOLEAN NOT NULL, 
	weak_against_electric BOOLEAN NOT NULL, 
	weak_against_grass BOOLEAN NOT NULL, 
	weak_against_ice BOOLEAN NOT NULL, 
	weak_against_fighting BOOLEAN NOT NULL, 
	weak_against_poison BOOLEAN NOT NULL, 
	weak_against_ground BOOLEAN NOT NULL, 
	weak_against_flying BOOLEAN NOT NULL, 
	weak_against_psychic BOOLEAN NOT NULL, 
	weak_against_bug BOOLEAN NOT NULL, 
	weak_against_rock BOOLEAN NOT NULL, 
	weak_against_ghost BOOLEAN NOT NULL, 
	weak_against_dragon BOOLEAN NOT NULL, 
	weak_against_dark BOOLEAN NOT NULL, 
	weak_against_steel BOOLEAN NOT NULL, 
	weak_against_fairy BOOLEAN NOT NULL, 
	constraint ptype_pk 
	primary key (ptype_id) 
);

create table has_type (
	poke_id INT references pokemon (poke_id) ON UPDATE CASCADE,
	ptype_id INT references ptype (ptype_id) ON UPDATE CASCADE,
	constraint has_type_pk
	primary key (poke_id, ptype_id)
); 


-- Pokemon Description 

create table description (
	descr_id SERIAL, 
	poke_id INT NOT NULL, 
	pokedex_entry VARCHAR(1000) NOT NULL,
	constraint descr_pk 
	primary key (descr_id, poke_id),
	constraint descr_poke_fk 
	foreign key (poke_id) references pokemon (poke_id) ON UPDATE CASCADE 
); 



-- Pokemon Moves and M:N Pokemon_Move mapping 

create table all_moves (
	move_id INT NOT NULL, 
	move_name VARCHAR(100) NOT NULL,
	move_description VARCHAR(1000) NOT NULL,
	move_type VARCHAR(50) NOT NULL,
	move_category VARCHAR(50) NOT NULL,
	move_pp INT NOT NULL,
	move_power VARCHAR(10) NOT NULL,
	constraint moves_pk 
	primary key (move_id)
);

create table has_move (
	poke_id INT NOT NULL references pokemon (poke_id) ON UPDATE CASCADE, 
	move_id INT NOT NULL references all_moves (move_id) ON UPDATE CASCADE,
	constraint has_move_pk 
	primary key (poke_id, move_id)
);

-- Egg Group 

create table egg_group (
	egg_group_id INT NOT NULL,
	egg_group_name VARCHAR (100) NOT NULL,
	constraint egg_group_pk 
	primary key (egg_group_id)
);

create table part_of_egg_group(
	poke_id INT NOT NULL references pokemon (poke_id) ON UPDATE CASCADE,
	egg_group_id INT NOT NULL references egg_group (egg_group_id) ON UPDATE CASCADE,
	constraint part_of_egg_group_pk 
	primary key (poke_id, egg_group_id)
);

-- Ailment Group 

create table ailments(
	ailment_id INT NOT NULL,
	ailment_name VARCHAR (100) NOT NULL,
	constraint ailments_pk
	primary key (ailment_id)
);

create table causes_ailment(
	move_id INT NOT NULL references all_moves (move_id) ON UPDATE CASCADE,
	ailment_id INT NOT NULL references ailments (ailment_id) ON UPDATE CASCADE,
	constraint causes_ailment_pk 
	primary key (move_id, ailment_id)
); 

-- Habitat Group and Lives in 

create table habitats (
	habitat_id INT NOT NULL,
	habitat_name VARCHAR (100) NOT NULL,
	constraint habitat_pk 
	primary key (habitat_id)
);

create table lives_in (
	poke_id INT NOT NULL references pokemon (poke_id) ON UPDATE CASCADE, 
	habitat_id INT NOT NULL references habitats (habitat_id) ON UPDATE CASCADE, 
	constraint lives_in_pk 
	primary key (poke_id, habitat_id)
);









