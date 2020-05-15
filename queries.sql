
------------------------- GENERAL QUERIES ---------------------------------------------------------------------------
		
-- Query 1: Get all pokemon and all their related information in one large data dump 
select * from pokemon
inner join has_type using (poke_id) 
inner join ptype using (ptype_id)  		-- get the types and weaknesses 
inner join has_move using (poke_id)
inner join all_moves using (move_id)  	-- get the moves 
inner join description using (poke_id)  -- get the pokemon's pokedex entries 
inner join lives_in using (poke_id)		-- get the pokemon's habitats 
inner join habitats using (habitat_id)
inner join part_of_egg_group using (poke_id) -- get the pokemon's egg group 
inner join egg_group using (egg_group_id);


-- Query 2: Get the moves that cause both damage and ailments 
	-- This means we have to filter for moves that appear twice in the inner joined table (once for Damage and once for the actual ailment)
	-- Next we have to filter out the moves that don't have any power (they're just status moves)
select all_moves.move_id as groupby_move, all_moves.* from all_moves
inner join causes_ailment using (move_id)
inner join ailments on causes_ailment.ailment_id = ailments.ailment_id
where move_power != 'None' 
group by groupby_move -- need the group by column to appear in the select statement 
having count(*) > 1;

-- Query 3: Find out the number of weaknesses per type 

with sums as 
(
	select ptype_id as identifier, *,
	count(*) filter (where weak_against_normal) as num_normal,
	count(*) filter (where weak_against_fire) as num_fire,
	count(*) filter (where weak_against_water) as num_water,
	count(*) filter (where weak_against_electric) as num_electric,
	count(*) filter (where weak_against_grass) as num_grass,
	count(*) filter (where weak_against_ice) as num_ice,
	count(*) filter (where weak_against_fighting) as num_fighting, 
	count(*) filter (where weak_against_poison) as num_poison,
	count(*) filter (where weak_against_ground) as num_ground,
	count(*) filter (where weak_against_flying) as num_flying,
	count(*) filter (where weak_against_psychic) as num_psychic,
	count(*) filter (where weak_against_bug) as num_bug,
	count(*) filter (where weak_against_rock) as num_rock,
	count(*) filter (where weak_against_ghost) as num_ghost,
	count(*) filter (where weak_against_dragon) as num_dragon,
	count(*) filter (where weak_against_dark) as num_dark,
	count(*) filter (where weak_against_steel) as num_steel,
	count(*) filter (where weak_against_fairy) as num_fairy
	from ptype
	group by identifier
)
select ptype_name, num_normal + num_fire + num_water + num_electric + num_grass + num_ice + num_fighting + num_poison +
num_ground + num_flying + num_psychic + num_bug + num_rock + num_ghost + num_dragon + num_dark + num_steel + num_fairy as sum_weaknesses_per_type
from sums;

-- Query 4: Find out the top 5 strongest pokemon (combine their attack and special attack and sort based on that sum total power)
select *, base_attack+base_special_attack as tot_power from pokemon 
order by tot_power desc 
limit 5; 

-- Query 5: Find out the strongest habitat based on the pokemon's overall power living there 

select habitat_name, tot_power from habitats 
inner join ( 
	select pk_habitat.habitat_id, sum(base_attack+base_special_attack) as tot_power from (
		select * from pokemon
		inner join lives_in using (poke_id)
		inner join habitats using (habitat_id)
	) as pk_habitat
	group by habitat_id
) habit_powers using (habitat_id)
order by tot_power desc;

---- TRIGGER WITH STORED FUNCTION -----------------------------

CREATE OR REPLACE FUNCTION getStrongest() RETURNS TRIGGER AS $getStrongest$ 
DECLARE 
overall_attack integer := 0;
BEGIN 
	overall_attack = NEW.base_attack + NEW.base_special_attack;
	if ((TG_OP = 'INSERT') AND (overall_attack > 200)) THEN 
 		RAISE NOTICE 'A new strong pokemon has entered with an overall attack of %', overall_attack;
		RETURN NEW;
END IF; 
RETURN NULL;
END;
$getStrongest$ LANGUAGE plpgsql; 


CREATE TRIGGER alertStrongPokemon
AFTER INSERT ON pokemon 
FOR EACH ROW
EXECUTE PROCEDURE getStrongest();

-- testing out the trigger (deleting the pokemon insertion right after along with the trigger)
insert into pokemon(poke_id,poke_name, poke_height, poke_weight, poke_catch_rate, poke_level_rate, base_health, base_attack, base_defense, base_special_attack, base_special_defense, base_speed) VALUES (200, 'blah', 0.7, 6.9, 45, 'medium',1000, 1000, 1000, 1000, 1000, 1000);
delete from pokemon where poke_id = 200; 
DROP TRIGGER alertStrongPokemon on pokemon;
------------------------- STORED FUNCTION ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION getDefensivePokemon (defense integer) 
RETURNS TABLE (
	poke_id INT , 
	poke_name VARCHAR, 
	poke_height NUMERIC,
	poke_weight NUMERIC,
	poke_catch_rate NUMERIC,
	poke_level_rate VARCHAR,
	base_health INT,
	base_attack INT,
	base_defense INT,
	base_special_attack INT ,
	base_special_defense INT,
	base_speed INT 
) AS $$
BEGIN
    RETURN QUERY 
    select * from pokemon
    where pokemon.base_defense + pokemon.base_special_defense > defense;
END; $$
LANGUAGE 'plpgsql';

-- testing out the stored function 
select * from getDefensivePokemon(200);