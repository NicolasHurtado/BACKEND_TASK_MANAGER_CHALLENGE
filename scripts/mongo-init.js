// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

print('🚀 Iniciando configuración de MongoDB para Task Manager...');

// Usar la base de datos taskmanager
db = db.getSiblingDB('taskmanager');

// Crear colecciones con validaciones básicas
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "full_name", "hashed_password", "is_active", "created_at"],
      properties: {
        email: {
          bsonType: "string",
          description: "Email debe ser un string y es requerido"
        },
        full_name: {
          bsonType: "string",
          description: "Nombre completo debe ser un string y es requerido"
        },
        hashed_password: {
          bsonType: "string",
          description: "Contraseña hasheada debe ser un string y es requerida"
        },
        is_active: {
          bsonType: "bool",
          description: "Estado activo debe ser booleano y es requerido"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación debe ser date y es requerida"
        }
      }
    }
  }
});

db.createCollection('tasks', {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "status", "priority", "user_id", "created_at"],
      properties: {
        title: {
          bsonType: "string",
          description: "Título debe ser un string y es requerido"
        },
        description: {
          bsonType: ["string", "null"],
          description: "Descripción debe ser string o null"
        },
        status: {
          enum: ["por_hacer", "en_progreso", "completada"],
          description: "Estado debe ser uno de los valores permitidos"
        },
        priority: {
          enum: ["baja", "media", "alta"],
          description: "Prioridad debe ser uno de los valores permitidos"
        },
        user_id: {
          bsonType: "objectId",
          description: "ID del usuario debe ser ObjectId y es requerido"
        },
        created_at: {
          bsonType: "date",
          description: "Fecha de creación debe ser date y es requerida"
        }
      }
    }
  }
});

// Crear índices para optimizar las consultas
print('📊 Creando índices...');

// Índices para usuarios
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

// Índices para tareas
db.tasks.createIndex({ "user_id": 1 });
db.tasks.createIndex({ "status": 1 });
db.tasks.createIndex({ "priority": 1 });
db.tasks.createIndex({ "created_at": -1 });
db.tasks.createIndex({ "due_date": 1 });
db.tasks.createIndex({ "user_id": 1, "status": 1 });

print('✅ Configuración de MongoDB completada exitosamente!');
print('📋 Colecciones creadas: users, tasks');
print('🔍 Índices creados para optimizar consultas');
print('🎯 Base de datos lista para Task Manager API');

// Mostrar información de la base de datos
print('\n📈 Estadísticas de la base de datos:');
printjson(db.stats()); 