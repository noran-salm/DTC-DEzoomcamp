variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "bucket_name" {
  type        = string
  description = "S3 bucket name (must be globally unique)"
}

variable "glue_database_name" {
  type        = string
  description = "Glue database name (dataset equivalent)"
}
