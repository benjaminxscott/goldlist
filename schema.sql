
create table locations (
    place_id  serial primary_key,
    place_name text NOT NULL,
    )
    
create table stuff (
    item_id serial primary_key,
    name text NOT NULL,
    description text,
    price float,
    place_id foreign
)