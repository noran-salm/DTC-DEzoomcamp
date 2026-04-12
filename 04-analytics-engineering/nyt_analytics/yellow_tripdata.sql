{{ config(materialized='view') }}

select * from {{ source('raw_data', 'yellow_tripdata') }}
