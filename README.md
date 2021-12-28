# CTF-SQL-Injection
Modeling SQL Injection Using Deep Neural Reinforcement Learning on POMDP(A Partially Observable Morkov Decision Process)

##  Installation

* Clone this repository on your local computer
* configure .env as needed 
* Run the `docker-compose up -d`.

```shell
git clone https://github.com/sataketatsuya/SQL_injection_pomdp.git
cd SQL_injection_pomdp/
cp sample.env .env
// modify sample.env as needed
docker-compose up -d
// visit localhost
```

Your LAMP stack is now ready!! You can access it via `http://localhost`.

## Setup
Check the database ip address with the command `docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq) | grep mysql`

If you get the ip address, you edit $DBipaddress in ./php/const.php. This setup is necessary to access successfully database. Please make sure.

## Experiment
Open neural_agent_model.ipynd on Jupyter Notebook.
