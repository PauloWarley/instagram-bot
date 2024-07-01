Para executar use: 
python app.py


<!-- API -->

# login
curl --location 'http://localhost:5000/create-login' \
--header 'Content-Type: application/json' \
--header 'Authorization: "564c755e-d24f-41c3-9532-eccd8e061469"' \
--data-raw '{
    "username":"usuario_do_instagram",
    "password": "senha"
}'

# likes
curl --location 'http://localhost:5000/create-like' \
--header 'Content-Type: application/json' \
--header 'Authorization: "564c755e-d24f-41c3-9532-eccd8e061469"' \
--data '{
    "login": "usuario_do_instagram,
    "usernames": ["paginas_que_terão_like"]
}'

# get accounts
curl --location 'http://localhost:5000/get-accounts'\
--header 'Authorization: "564c755e-d24f-41c3-9532-eccd8e061469"' 


# double-auth-code
curl --location 'http://localhost:5000/double-auth' \
--header 'Content-Type: application/json' \
--header 'Authorization: ••••••' \
--data '{
    "login": "login",
    "code": "code_value"
}'