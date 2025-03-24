En este proyecto trabajado con anterioridad se agregó Flask-login

Al correr el proyecto creará las tablas "pedido" y "usuario" de la base de datos llamada "examen" por lo que no se cuenta con usuario por default, para ello deberá crearlo en la base de datos de la siguiente manera:

INSERT INTO usuario (username, password) 
VALUES ('rangel19', 'scrypt:32768:8:1$pV2qAwE2Z3ycPlSN$907a943dc0705b43ef561cb9a9933c74bcc3766dcd32d254e02304cb08fe5fb53b8e751d870fdfcc9006206e6859da85337795e6864d997abbc86cbb402f51a5');

donde el usuario es "rangel19" y la contraseña desencriptada (utilizando hash) es "Mensaje@02313"
