// Script de inicialização do MongoDB
// Cria o banco de dados e coleção se não existirem

// Conecta ao banco ocr_db
db = db.getSiblingDB('ocr_db');

// Cria a coleção de placas
db.createCollection('placas');

// Cria índices para melhor performance
db.placas.createIndex({ "placa": 1 });
db.placas.createIndex({ "hora_entrada": 1 });
db.placas.createIndex({ "hora_saida": 1 });

// Cria usuário para a aplicação (opcional)
db.createUser({
  user: "placaview_user",
  pwd: "placaview_pass",
  roles: [
    { role: "readWrite", db: "ocr_db" }
  ]
});

print('Banco de dados ocr_db inicializado com sucesso!');
