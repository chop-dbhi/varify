--
-- user: varify
-- database: varify
-- schemas: public, raw
--

begin;
--
-- acts as an eval for ``text''
--
create or replace function execute(text) returns void as
    $BODY$BEGIN execute $1; END;$BODY$
language plpgsql;

--
-- Schemata
--

-- Set schema owner
select execute('alter schema "' || schema_name || '" owner to varify;')
    from information_schema.schemata
    where schema_name not in ('information_schema', 'pg_catalog');

-- Revoke all schema permissions from 'varify' user
select execute('revoke all on schema "' || schema_name || '" from varify;')
    from information_schema.schemata
    where schema_name not in ('information_schema', 'pg_catalog');

-- Grant on schemas
select execute('grant usage, create on schema "' || schema_name || '" to varify;')
    from information_schema.schemata
    where schema_name not in ('information_schema', 'pg_catalog');

--
-- Tables
--

-- Ensure owner of all tables is postgres
select execute('alter table "' || table_schema || '"."' || table_name || '" owner to varify;')
    from information_schema.tables
    where table_schema not in ('information_schema', 'pg_catalog');

-- Revoke all table permissions from 'varify' user
select execute('revoke all on "' || table_schema || '"."' || table_name || '" from varify;')
    from information_schema.tables
    where table_schema not in ('information_schema', 'pg_catalog');

-- Grant on tables
select execute('grant select, insert, update, delete, truncate, references on "' || table_schema || '"."' || table_name || '" to varify;')
    from information_schema.tables
    where table_schema not in ('information_schema', 'pg_catalog');

--
-- Sequences
--

-- Revoke all sequence permissions from 'varify' user
select execute('revoke all on sequence "' || sequence_schema || '"."' || sequence_name || '" from varify;')
    from information_schema.sequences
    where sequence_schema not in ('information_schema', 'pg_catalog');

-- Grant all on sequences for 'varify' user
select execute('grant all on "' || sequence_schema || '"."' || sequence_name || '" to varify;')
    from information_schema.sequences
    where sequence_schema not in ('information_schema', 'pg_catalog');

commit;
