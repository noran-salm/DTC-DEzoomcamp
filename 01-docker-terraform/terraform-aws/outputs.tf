output "s3_bucket_name" {
  value = aws_s3_bucket.data_lake.bucket
}

output "glue_database_name" {
  value = aws_glue_catalog_database.dataset.name
}
