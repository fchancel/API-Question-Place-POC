# Tripeerz

## Instructions

The project use docker [buildkit](https://docs.docker.com/develop/develop-images/build_enhancements/), we have to use the DOCKER_BUILDKIT env variable.
`export DOCKER_BUILDKIT=1`    

We need a volume for the database, create it with:
`docker volume create --name=database_dev`

Build
`docker-compose   -f docker-compose.dev.yml build`  

Build and run by simply run
`docker-compose   -f docker-compose.dev.yml up -d `

#### Tests

Lancer les tests:
`docker exec -t <folder_name>_api_1 pytest --cli-log-level=INFO` 

`-t` act as a pseuo terminal, for output colors